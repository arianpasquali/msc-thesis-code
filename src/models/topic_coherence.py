from __future__ import division
from elasticsearch import Elasticsearch
from scipy import stats
import math
import operator
from pathos.pools import ProcessPool, ThreadPool
import datetime
from sklearn import preprocessing
import numpy as np

N_THREADS = 1

class TopicCoherence(object):

    pairwise_scores = {}
    pairwise_probability = {}
    word_probability = {}
    pairwise_hits = {}
    word_hits = {}

    def __init__(self, index_name, doc_type,es_address="localhost:9200"):
        self.index_name = index_name
        self.doc_type = doc_type

        self.es = Elasticsearch(es_address)
        self.collection_size = self.get_collection_size(index_name, doc_type)

    @staticmethod
    def normalize(scores):
    	scores = np.array(scores)
    	scores = scores.reshape(1,-1)
    	
    	min_max_scaler = preprocessing.Normalizer()
    	# min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0,1))

    	normalized_scores = min_max_scaler.fit_transform(scores)

    	return normalized_scores[0].tolist()

    @staticmethod
    def entropy(scores):
    	# min_max_scaler = preprocessing.MinMaxScaler(feature_range=(0,1))
    	return stats.entropy(scores)

    def get_hit_count_for_terms(self, es_index_name, field, terms):
        must_query = []
        # print(terms)
        exact_terms = ["\"" + x + "\"" for x in terms]
        lucene_query = " AND ".join(exact_terms)
        # lucene_query = "\"" + lucene_query + "\"~10"

        # query_doc_type = "page"

        res = self.es.search(index=es_index_name, 
                             q=lucene_query,
                             doc_type=self.doc_type)

        return res['hits']['total']

	def compute_probability(self, hits):
		if(hits is None):
			hits = 0	

        return float(hits) / float(self.collection_size)

    def get_collection_size(self,index_name, _doc_type):
        res = self.es.search(index=index_name, 
                                doc_type=_doc_type, 
                                body={"query": {"match_all": {}}})

        return res['hits']['total']

class UCI(TopicCoherence):

	def compute_pairwise_hits(self,pairwise_key):
		word_i = pairwise_key.split("_")[0]
		word_j = pairwise_key.split("_")[1]
		self.pairwise_hits[pairwise_key] = self.get_hit_count_for_terms(self.index_name,"text",[word_i,word_j])
		self.pairwise_probability[pairwise_key] = self.compute_probability(self.pairwise_hits[pairwise_key])
		self.pairwise_scores[pairwise_key] = self.compute_pairwise_score(
                                                     self.pairwise_probability[pairwise_key],
                                                     self.word_probability[word_i],
                                                     self.word_probability[word_j])
	
	def compute_word_hits(self,word):
		self.word_hits[word] = self.get_hit_count_for_terms(self.index_name,"text",[word])
		self.word_probability[word] = self.compute_probability(self.word_hits[word])

	def compute_probability(self, hits):
		if(hits is None):
			hits = 0	
		return float(hits) / float(self.collection_size)

	def get_collection_size(self,index_name, _doc_type):
	    res = self.es.search(index=index_name, 
	                            doc_type=_doc_type, 
	                            body={"query": {"match_all": {}}})

	    return res['hits']['total']

	def compute_pairwise_score(self, prob_ngrams, prob_ngram_a, prob_ngram_b):
		if(prob_ngram_a == 0):
		    prob_ngram_a = 1 

		if(prob_ngram_b == 0):
		    prob_ngram_b = 1 

		# e = math.pow(10,-12)
		e = 1
		prob_product = (prob_ngrams + e) / (prob_ngram_a * prob_ngram_b)

		if(prob_product == 0.0):
			prob_product = 1

		res = math.log(prob_product)
		return res	

	def fit(self, words):
		self.words = words

		self.pairwise_scores = {}

		self.pairwise_probability = {}
		self.word_probability = {}

		self.pairwise_hits = {}
		self.word_hits = {}

		self.pairwise = []

		for word_i in self.words:
		    for word_j in self.words:
		        if(word_i is not word_j):
		            pairwise_key = "_".join(sorted([word_i,word_j]))
		            if(pairwise_key not in self.pairwise_probability.keys()):		            
		                self.pairwise.append(pairwise_key)

		pool = ThreadPool(N_THREADS)
		pool.map(self.compute_word_hits, self.words)

		# pool1 = ThreadPool(N_THREADS)
		pool.map(self.compute_pairwise_hits, self.pairwise)

		return sum(self.pairwise_scores.values())

	def __init__(self, index_name, doc_type,es_address):
	    super(UCI,self).__init__(index_name, doc_type,es_address)


class UMass(TopicCoherence):

	def compute_pairwise_hits(self,pairwise_key):
		
		most_rare_hits = self.pairwise[pairwise_key]["most_rare_hits"]
		most_common_hits = self.pairwise[pairwise_key]["most_common_hits"]
		most_common_ngram = self.pairwise[pairwise_key]["most_common_ngram"]
		most_rare_ngram = self.pairwise[pairwise_key]["most_rare_ngram"]

		self.pairwise_hits[pairwise_key] = self.get_hit_count_for_terms(self.index_name, 
																 "text", 
																 [most_rare_ngram,most_common_ngram])

		self.pairwise_probability[pairwise_key] = self.compute_probability(self.pairwise_hits[pairwise_key])

		self.word_probability[most_rare_ngram] = self.compute_probability(most_rare_hits)

		self.word_probability[most_common_ngram] = self.compute_probability(most_common_hits)

		self.pairwise_scores[pairwise_key] = self.compute_pairwise_score( 
												self.pairwise_probability[pairwise_key],
												self.word_probability[most_common_ngram],
												self.word_probability[most_rare_ngram])

	def compute_word_hits(self,word):
		self.word_hits[word] = self.get_hit_count_for_terms(self.index_name,"text",[word])
		self.word_probability[word] = self.compute_probability(self.word_hits[word])


	def compute_probability(self, hits):
		if(hits is None):
			hits = 0

		return float(hits) / float(self.collection_size)

	def get_collection_size(self,index_name, _doc_type):
		res = self.es.search(index=index_name, 
		                        doc_type=_doc_type, 
		                        body={"query": {"match_all": {}}})

		return res['hits']['total']

	def compute_pairwise_score(self, prob_ngrams, prob_ngram_a, prob_ngram_b):
		if(prob_ngram_a == 0):
		    prob_ngram_a = 1 

		if(prob_ngram_b == 0):
		    prob_ngram_b = 1 

		# e = math.pow(10,-12)
		e = 1	
		prob_product = (prob_ngrams + e) / (prob_ngram_a)
		
		if(prob_product == 0.0):
		    prob_product = 1

		res = math.log(prob_product)
		return res

	# def combinatory_analysis():

	def fit(self, words):
		self.words = words
		self.pairwise_scores = {}
		self.word_scores = {}

		self.pairwise_probability = {}
		self.word_probability = {}

		self.pairwise_hits = {}
		self.word_hits = {}

		self.pairwise = {}
		
		pool = ThreadPool(N_THREADS)
		pool.map(self.compute_word_hits, self.words)

		for word_i in self.words:
			
			sorted_desc = sorted(self.word_hits.items(), key=operator.itemgetter(1),reverse=True)
			sorted_asc = sorted(self.word_hits.items(), key=operator.itemgetter(1))

			for most_common in sorted_desc:
				most_common_ngram = most_common[0] 
				most_common_hits = most_common[1]

				for most_rare in sorted_asc:
					most_rare_ngram = most_rare[0] 
					most_rare_hits = most_rare[1]

					if(most_common_ngram is not most_rare_ngram):
						if(most_rare_hits < most_common_hits):
							pairwise_key = most_rare_ngram + "_" + most_common_ngram

							if(pairwise_key not in self.pairwise_probability.keys()):

								self.pairwise[pairwise_key]= {
									"most_common_ngram":most_common_ngram,
									"most_rare_ngram":most_rare_ngram,
									"most_rare_hits":most_rare_hits,
									"most_common_hits":most_common_hits,
									}		

		# pool1 = ThreadPool(N_THREADS)
		pool.map(self.compute_pairwise_hits, self.pairwise.keys())
		
		return sum(self.pairwise_scores.values())

		def __init__(self, index_name, doc_type,es_address):
		    super(UMass,self).__init__(index_name, doc_type,es_address)
		

# from models.topic_coherence import ExtrinsicUCI, IntrisicUMass
# import logging
# log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# logging.basicConfig(level=logging.INFO, format=log_fmt)
# logger = logging.getLogger(__name__)

# IMPORTANTE
# remover queries redundantes pra melhorar a performance
# suportar cache local das queries
# incluir na tese a formula da combinatoria (factorial)
# combinacoes de 2 em um conjunto de 10 elementos da 45 combinacoes possiveis. 
# colocar isso na tese. pegar formula online
# test_word_set = "card windows monitor video mac com mouse pc dos apple".split(" ")

# external_index = "tmp"
# internal_index = "20newsgroup"
# test_es_address = "localhost:9200"

# start = datetime.datetime.now()
# extrinsic_uci = UCI(external_index,"page",test_es_address)
# intrinsic_uci = UCI(internal_index,"page",test_es_address)

# intrinsic_uci.fit(test_word_set)
# print("UCI scores : ")
# print("		Extrinsic : " + str(extrinsic_uci.fit(test_word_set)))
# print("		Intrinsic : " + str(intrinsic_uci.fit(test_word_set)))		

# stop = datetime.datetime.now()
# elapsed = stop - start

# print("uci " + str(elapsed))

# start = datetime.datetime.now()
# extrinsic_umass = UMass(external_index,"page",test_es_address)
# intrinsic_umass = UMass(internal_index,"page",test_es_address)


# intrinsic_umass.fit(test_word_set)
# print("UMass scores : ")
# print("		Extrinsic : " + str(extrinsic_umass.fit(test_word_set)))
# print("		Intrinsic : " + str(intrinsic_umass.fit(test_word_set)))		

# stop = datetime.datetime.now()
# elapsed = stop - start

# print("umass " + str(elapsed))
# scores = [432.271083961,461.426691487,429.971345045,446.414313959,379.716627031,405.89737182,366.990366469,361.852959292,329.815378425,334.170518947,312.518867844,291.030767201,288.21575812,326.295192285,323.680871595,309.859856707,284.889898939,271.064573885,261.778338627,225.376870553]

# print("norm l2", TopicCoherence.normalize(scores))
# print("entropy", TopicCoherence.entropy(scores))