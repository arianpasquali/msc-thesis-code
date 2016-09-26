"""
========================================================
Compute topics interpretability
========================================================
"""

# Author: Arian Pasquali

from __future__ import print_function
from time import time
from scipy import stats
from topic_coherence import UCI, UMass
# from topic_coherence import UMass
import numpy as np
import re
import string
import sys
import logging
import csv
import os
import pickle
import lda
import numpy as np
import string
import sqlite3
import operator
import datetime

BASE_WORKDIR = "../../"

# external_index = "tmp"
external_index = "ptwiki"
# internal_index = "20newsgroup"
test_es_address = "localhost:9200"

database_name_classes = []
for i in range(1,7):
    database_name_classes.append("facebook_brazil_class_" + str(i))

def print_scores(scores):
    for topic in sorted(scores, key = lambda name:name["topic_id"]):
        logger.info('{},{},{},{},{},{}'.format(topic["topic_id"], 
                                            topic["ngrams"],
                                            topic["scores"]["extrinsic"]["pmi"], 
                                            topic["scores"]["extrinsic"]["cpp"], 
                                            topic["scores"]["intrinsic"]["pmi"], 
                                            topic["scores"]["intrinsic"]["cpp"]
                                            ))

def print_top_topics(scores, coherence_type, coherence_measure):
    # lambda_sortby = 

    logger.info("------------------------------------------------")
    logger.info("Most coherent topics using {} {}".format(coherence_type,coherence_measure))
    for topic in sorted(scores, key = lambda name:name["scores"][coherence_type][coherence_measure], reverse=True):
        logger.info('Topic {}: Coherence {}: {}'.format(topic["topic_id"], 
                                                        topic["scores"][coherence_type][coherence_measure], 
                                                        topic["ngrams"]))

    


def persist_results(c,results):
    tuples = []

    for item in results:
        doc = ( int(item["n_topics"]), 
                int(item["topic_id"]),
                item["ngrams"],
                item["dataset_name"],
                item["scores"]["extrinsic"]["cpp"],
                item["scores"]["extrinsic"]["pmi"],
                item["scores"]["intrinsic"]["cpp"],
                item["scores"]["intrinsic"]["pmi"]
                )
        tuples.append(doc)

    c.executemany('INSERT INTO `topic_coherence_scores`(`n_topics`,`topic_id`,`ngrams`,`dataset_name`,`extrinsic_umass`,`extrinsic_uci`,`intrinsic_umass`,`intrinsic_uci`) VALUES (?,?,?,?,?,?,?,?)',tuples)


def main():
    # for database_name_class in database_name_classes:
    for database_name_class in ["facebook_brazil_class_2"]:
        internal_index = database_name_class
        dataset_name = database_name_class

        intrinsic_uci = UCI(internal_index,"page",test_es_address)
        intrinsic_umass = UMass(internal_index,"page",test_es_address)
        # intrinsic_uci = UCI(internal_index,"post",test_es_address)
        # intrinsic_umass = UMass(internal_index,"post",test_es_address)
        extrinsic_uci = UCI(external_index,"page",test_es_address)
        extrinsic_umass = UMass(external_index,"page",test_es_address)

        # renomear database
        conn = sqlite3.connect(BASE_WORKDIR + 'data/20newsgroup.db')

        c = conn.cursor()

        logger.info("Clear data")
        c.execute('DELETE FROM `topic_coherence_scores` WHERE `dataset_name` == "'+ dataset_name +'" ')
        conn.commit()

        resultset = c.execute('SELECT * FROM `topics_facebook` WHERE `dataset_name` == "' + dataset_name + '" ORDER BY `topic_id` ASC')

        scores = []

        start = datetime.datetime.now()
        
        for row in resultset:
            topic_id = row[0]
            n_topics = row[1]
            dataset_name = row[2]    
            ngrams = row[3]

            print('[{}] Total Topics [{}], Topic {}: {}'.format(dataset_name,n_topics,topic_id,ngrams))

            ngrams_list = ngrams.split(" ")

            extrinsic_umass_result = extrinsic_umass.fit(ngrams_list)
            intrinsic_umass_result = intrinsic_umass.fit(ngrams_list)

            extrinsic_uci_result = extrinsic_uci.fit(ngrams_list)
            intrinsic_uci_result = intrinsic_uci.fit(ngrams_list)

            doc = {
                "n_topics":int(n_topics),
                "topic_id":int(topic_id),
                "dataset_name":dataset_name,
                "ngrams":ngrams,
                "scores":{
                    "intrinsic":{
                        "cpp":intrinsic_umass_result,
                        "pmi":intrinsic_uci_result
                    }, 
                    "extrinsic":{
                        "cpp":extrinsic_umass_result,
                        "pmi":extrinsic_uci_result
                    }}
                }
            scores.append(doc)

        stop = datetime.datetime.now()
        elapsed = stop - start
        print("Time spent " + str(elapsed))
        persist_results(c,scores)
        # print_top_topics(scores,"intrinsic","pmi")
        # print_top_topics(scores,"intrinsic","cpp")
        # print_top_topics(scores,"extrinsic","pmi")
        # print_top_topics(scores,"extrinsic","cpp")
        print_scores(scores)

        conn.commit()
        conn.close()

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)
    # logger.info('making final data set from raw data')

    # not used in this stub but often useful for finding various files
    # project_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())

    os.chdir(os.path.dirname(os.path.realpath(__file__)))    

    main()    