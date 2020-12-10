#
# Flask/d3 APp for visual analytics for NLP Project
# Andrew Zhou
#


import flask
import numpy as np
import pandas as pd
import pickle
from flask import Flask, request, render_template, abort, jsonify
import spacy
import itertools
from util.analytics import char_freq, pair_freq, get_overlap_sentences, get_sentiments, alone_time, process_helper

# Initialize the app
app = flask.Flask(__name__)

# Homepage
@app.route("/")
def viz_page():
    """
    Homepage
    """
    return "My Flask App!"

# Streamlit app passes in text
@app.route("/fic_viz/<text>")
def chart(text):
    return render_template("fic_viz.html", text=text)

# Allow the d3 app to request text processing
@app.route("/process_text", methods=["POST"])
def process_text():
    data = flask.request.json
    text = data["text"]

    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    gaang = ["Aang", "Sokka", "Zuko", "Katara", "Toph"]
    results = process_helper(doc, gaang, 80)

    for i in range(len(results["pair_freqs"])):
        results["pair_freqs"][i][i] = 0

    return flask.jsonify(results)

#--------- RUN WEB APP SERVER ------------#

# Starurl_forthe app server on port 80
# (The default website port)
if __name__ == '__main__':
    app.run()