.PHONY: clean data lint requirements sync_data_to_s3 sync_data_from_s3

#################################################################################
# GLOBALS                                                                       #
#################################################################################

#################################################################################
# COMMANDS                                                                      #
#################################################################################

requirements:
	pip install -r requirements.txt

install_elasticsearch:
	src/data/install_elasticsearch.sh

# index_wikipedia_en:
	# src/data/install_elasticsearch.sh	

data: requirements
	python src/data/make_dataset.py

train: data
	python src/data/train_lda_model.py

coherence: train
	python src/models/compute_coherence.py

clean:
	find . -name "*.pyc" -exec rm {} \;

lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################
