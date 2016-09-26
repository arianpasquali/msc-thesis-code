from __future__ import print_function

import pysolr

import logging
from optparse import OptionParser
import sys
from time import time

import numpy as np
import pandas as pd


import nltk
import string
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.stem.porter import PorterStemmer
import csv
from elasticsearch import Elasticsearch
import os
from os.path import join
from pymongo import MongoClient

es = Elasticsearch()


# Display progress logs on stdout
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s %(levelname)s %(message)s')

group_types = 	["GRUPO_1_CAUSAS",
				 "GRUPO_2_MIDIA_ATIVISMO",
				 "GRUPO_3_MIDIA_GOVERNISMO",
				 "GRUPO_4_MIDIA_PRO_IMPEACHMENT",
				 "GRUPO_5_MEMES_PRO_IMPEACHMENT",
				 "GRUPO_6_MEMES_PROGRESSISTA"]

# curl -XDELETE 'http://localhost:9200/grupo_1_causas/'
# curl -XDELETE 'http://localhost:9200/grupo_2_midia_ativismo/'
# curl -XDELETE 'http://localhost:9200/grupo_3_midia_governismo/'
# curl -XDELETE 'http://localhost:9200/grupo_4_midia_pro_impeachment/'
# curl -XDELETE 'http://localhost:9200/grupo_5_memes_pro_impeachment/'
# curl -XDELETE 'http://localhost:9200/grupo_6_memes_progressista/'

database_name_classes = []
for i in range(1,7):
    database_name_classes.append("facebook_brazil_class_" + str(i))

import pymongo
mongo = MongoClient('mongodb://localhost:27017/')

for group_type in group_types:

	group_type_dbname = group_type.replace("-","_")
	db = mongo[group_type_dbname]
	posts_collection = db['facebook_posts']

	dataset = []

	# for post in posts_collection.find({"type": { "$in": [ "status", "photo","link","note","video"] }}):

	i = 0
	for post in posts_collection.find({"language":"pt","type": { "$in": [ "status", "photo","link","note","video"] }}):
		
		try:
			index_name = database_name_classes[group_types.index(group_type)]

			doc = post["post_message"]
			body = {'text': doc }
			es.create(index=index_name, doc_type='page', body=body, id=i)
			print("index " + index_name, i)
		except:
			print("already exists")

		i+=1
	

# files = (join(d, f) for d, _, fnames in os.walk('/Volumes/disco_mac_a/thesis/elastic/tr20news-bydate-train')
#          for f in fnames)

# for i, f in enumerate(files):
#     body = {'text': open(f).read().decode('utf-8', errors='ignore')}
#     es.create(index='20news', doc_type='post', body=body, id=i)

# http://qpleple.com/topic-coherence-to-evaluate-topic-models/

# http://localhost:9200/wiki/_count?q=*:*
# http://localhost:9200/20news/_count?q=*:*
# http://localhost:9200/20news/
# http://localhost:9200/wiki/
# http://localhost:9200/wiki/_search?q=*:*
# http://localhost:9200/20news/_search?q=*:*


# Do machines can think?
