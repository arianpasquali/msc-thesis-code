Code related to my MSc thesis
=============================

This project contains source code related to my Msc thesis entitled `Automatic coherence evaluation applied to topic models'.
To explore it you can follow the following tutorial:  


20newsgroup demo
---------------
View detected topics and coherence scores from 20newsgroup: 

> cd demo/20newsgroup

> python app.py

open in your browser http://localhost:5000

facebook demo
---------------

Explore network from Facebook pages and their topics:

> cd demo/facebook

> open index.html


reproducing results
------------------------------

> make clean

You need an ElasticSearch instance, if not available, download and install elasticsearch executing:
> make install_elasticsearch

Make sure you have the instance up and running.  
> elasticsearch-2.4.0/bin/elasticsearch -d

Install third-party libraries:
> make requirements

Setup test data
> make data

Run data preparation script to compute documents into bag-of-words 
> make data_preparation

Run LDA to discover topics
> make topics

Compute coherence scores for the discovered topics
> make coherence


Project Organization
--------------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │   └── local_persistence.py
    │   │   └── create_database.sql
    │   │   └── install_elasticsearch.sh
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │   └── preprocessing.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   └── train_lda_model.py
    │   │   └── topic_coherence.py
    │   │   └── compute_topic_coherence.py
    │   │
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
