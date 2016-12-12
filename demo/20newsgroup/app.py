from flask import Flask
from flask import render_template

import csv




app = Flask(__name__)

def load_topics():
	f_topics = open('data/topics_scores.csv', 'rb')
	reader = csv.reader(f_topics,delimiter=",")

	headers = reader.next()
	topics = []


	for row in reader:
		topic = {}
		topic["topic_id"] = row[headers.index("topic_id")]
		topic["topic_ngrams"] = row[headers.index("topic_ngrams")]
		topic["extrinsic_umass"] = row[headers.index("extrinsic_umass")]
		topic["extrinsic_uci"] = row[headers.index("extrinsic_uci")]
		topic["intrinsic_umass"] = row[headers.index("intrinsic_umass")]
		topic["intrinsic_uci"] = row[headers.index("intrinsic_uci")]

		topics.append(topic)
	    # topic_id = row[0]
	    # ngrams = row[1]

	    # print('Topic {}: {}'.format(topic_id,ngrams))

	    # ngrams_list = ngrams.split(" ")

	    # extrinsic_umass_result = extrinsic_umass.fit(ngrams_list)
	    # intrinsic_umass_result = intrinsic_umass.fit(ngrams_list)

	    # extrinsic_uci_result = extrinsic_uci.fit(ngrams_list)
	    # intrinsic_uci_result = intrinsic_uci.fit(ngrams_list)

	    # doc = {
	    #     "n_topics":20,
	    #     "topic_id":int(topic_id),
	    #     "ngrams":ngrams,
	    #     "scores":{
	    #         "intrinsic":{
	    #             "cpp":intrinsic_umass_result,
	    #             "pmi":intrinsic_uci_result
	    #         },
	    #         "extrinsic":{
	    #             "cpp":extrinsic_umass_result,
	    #             "pmi":extrinsic_uci_result
	    #         }}
	    #     }
	    # scores.append(doc)

	return topics

@app.route("/")
def hello():
    return render_template('topics.html',topics=load_topics())

if __name__ == "__main__":
    app.run()