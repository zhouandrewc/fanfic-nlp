# "My Honor!": Natural Language Processing for Modeling <em>Avatar: The Last Airbender</em> Fanfiction
## by Andrew Zhou

Code, data, documentation, and app for my NLP project (projects 4 and 5) for the Fall 2020 Metis Data Science Bootcamp.

## Problem Statement

We employ NLP to construct a topic model and language model for <em>Avatar: The Last Airbender</em> fanfiction. We use the insights from these models to develop an application that can recommend, generate, and present visual analytics for fanfiction.

### Tools Used

* NLTK
* Spacy
* Gensim
* HuggingFace
* PyTorch
* GPT-2
* Streamlit
* Flask
* d3

### Techniques Used

* Non-supervised Learning
* Latent Dirichlet Allocation (LDA)
* Clustering
* t-SNE
* Content-based Recommendation
* Fine-tuning Neural Networks

### Data

Our data are from the website [Archive of Our Own](http://archiveofourown.org), or AO3. We have chosen to focus on <em>Avatar: The Last Airbender</em> fanfiction.

## Contents

* [Utilities](util)

Utility functions for Jupyter notebooks. Includes separate routines for scraping data, processing data, and model training and evaluation.

* [Notebooks](notebooks)

Notebooks for scraping, preprocessing, modeling, and clustering (project 4) and text generation (project 5).

* [Application](app)

A Streamlit app with a recommender, generator, and analyzer for fanfiction. Includes a separate [util](app/util) directory for utility functions for the visual analytics app.

* [Presentation](presentation)

Contains the slides for the presentation I gave on my work.

Note that various stored ```.pickle``` files and directories for storing those files are omitted due to lack of space.

## Acknowledgments

Thanks to the awesome staff and students at Metis who were a huge help during this project.