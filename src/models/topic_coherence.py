from __future__ import division
from elasticsearch import Elasticsearch
from scipy import stats
import math
import operator
from pathos.pools import ProcessPool, ThreadPool
import datetime
from sklearn import preprocessing
import numpy as np
from abc import ABCMeta, abstractmethod

N_CPUS = 8

class TopicCoherence(object):
	__metaclass__ = ABCMeta
	
	epsilon = 1

	pairwise_probability = {}
	word_probability = {}
	pairwise_hits = {}
	word_hits = {}
	coherence_scores = {}	

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
		return stats.entropy(scores)

	@abstractmethod
	def compute_pairwise_hits(self,pairwise_key): pass

	@abstractmethod
	def compute_coherence(self, prob_ngrams, prob_ngram_a, prob_ngram_b): pass

	@abstractmethod
	def fit(self, words): pass

	def get_hit_count_for_terms(self, es_index_name, field, terms):
		must_query = []
		exact_terms = ["\"" + x + "\"" for x in terms]
		lucene_query = " AND ".join(exact_terms)
		
		res = self.es.search(index=es_index_name, 
		                     q=lucene_query,
		                     doc_type=self.doc_type)

		return res['hits']['total']

	def compute_probability(self, hits):
		0 if(hits is None) else hits

		return float(hits)  / float(self.collection_size)

	def get_collection_size(self,index_name, _doc_type):
		res = self.es.search(index=index_name, 
		                        doc_type=_doc_type, 
		                        body={"query": {"match_all": {}}})

		return res['hits']['total']

	def compute_word_hits(self,word):
		self.word_hits[word] = self.get_hit_count_for_terms(self.index_name,"text",[word])
		self.word_probability[word] = self.compute_probability(self.word_hits[word])	

class UCI(TopicCoherence):

	def compute_pairwise_hits(self,pairwise_key):
		word_i = pairwise_key.split("_")[0]
		word_j = pairwise_key.split("_")[1]
		self.pairwise_hits[pairwise_key] = self.get_hit_count_for_terms(self.index_name,"text",[word_i,word_j])
		self.pairwise_probability[pairwise_key] = self.compute_probability(self.pairwise_hits[pairwise_key])
		self.coherence_scores[pairwise_key] = self.compute_coherence(
                                                     self.pairwise_probability[pairwise_key],
                                                     self.word_probability[word_i],
                                                     self.word_probability[word_j])
	
	
	def compute_coherence(self, prob_ngrams, prob_ngram_a, prob_ngram_b):
		1 if (prob_ngram_a == 0) else prob_ngram_a
		1 if (prob_ngram_b == 0) else prob_ngram_b
		    
		prob_product = (prob_ngrams + self.epsilon) / (prob_ngram_a * prob_ngram_b)

		1 if (prob_product == 0.0) else prob_product
			
		res = math.log(prob_product)
		return res	

	def fit(self, words):
		self.words = words

		self.coherence_scores = {}

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

		pool = ThreadPool(N_CPUS)
		pool.map(self.compute_word_hits, self.words)
		pool.map(self.compute_pairwise_hits, self.pairwise)

		return sum(self.coherence_scores.values())

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

		self.coherence_scores[pairwise_key] = self.compute_coherence( 
												self.pairwise_probability[pairwise_key],
												self.word_probability[most_common_ngram],
												self.word_probability[most_rare_ngram])

	
	def compute_coherence(self, prob_ngrams, prob_ngram_a, prob_ngram_b):
		1 if(prob_ngram_a == 0) else prob_ngram_a
		1 if(prob_ngram_b == 0) else prob_ngram_b

		# e = math.pow(10,-12)
		prob_product = (prob_ngrams + self.epsilon) / (prob_ngram_a)
		1 if(prob_product == 0.0) else prob_product

		res = math.log(prob_product)
		return res

	def fit(self, words):
		self.words = words
		self.coherence_scores = {}
		self.word_scores = {}

		self.pairwise_probability = {}
		self.word_probability = {}

		self.pairwise_hits = {}
		self.word_hits = {}

		self.pairwise = {}
		
		pool = ThreadPool(N_CPUS)
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

		pool.map(self.compute_pairwise_hits, self.pairwise.keys())		

		return sum(self.coherence_scores.values())

		def __init__(self, index_name, doc_type,es_address):
		    super(UMass,self).__init__(index_name, doc_type,es_address)
		

