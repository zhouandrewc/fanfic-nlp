# "My Honor!": A Language Model for <em>Avatar: The Last Airbender</em> Fanfiction
## by Andrew Zhou

Code, data, documentation, and app for my NLP project for the Fall 2020 Metis Data Science Bootcamp.

## Problem Statement

We employ NLP and unsupervised learning methods to construct a topic model for <em>Avatar: The Last Airbender</em> fanfiction. This topic model is used to cluster our fanfiction corpus and to make recommendations in our app.

## Methods

We train classification models, using the f<sub>0.5</sub>-score metric to evaluate performance for hyperparameter tuning and model selection.

### Tools Used

* NLTK
* Spacy
* Gensim

### Techniques Used

* Latent Dirichlet Allocation (LDA)
* Clustering
* t-SNE
* Content-based Recommendation

### Data

Our data are from the website [Archive of Our Own](http://archiveofourown.org), or AO3. We have chosen to focus on <em>Avatar: The Last Airbender</em> fanfiction.

## Contents

* [Utilities](util)

Utility functions for Jupyter notebooks. Includes separate routines for scraping data, processing data, and model training and evaluation.

* [Notebooks](notebooks)

Notebooks for scraping, preprocessing, modeling, and clustering.

* [Application](app)

A Streamlit app that implementing a recommender system for fanfiction. Documentation to be fleshed out.

* [Presentation](presentation)

Contains the slides for the presentation I gave on my work.

Note that various stored ```.pickle``` files and directories for storing those files are omitted due to lack of space.

## Acknowledgments

Thanks to the awesome staff and students at Metis who were a huge help during this project.