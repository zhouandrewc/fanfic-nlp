#
# Streamlit app for NLP Project
# Andrew Zhou
#
# Some code taken from demos from https://github.com/streamlit/
#

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import sys
import re
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from PIL import Image
from gensim.test.utils import get_tmpfile
from gensim.similarities import Similarity
import pickle
import sys
import numpy as np
sys.path.append("..")
from util.preprocess import process_text
from util.scrape import scrape_fic

from collections import Counter
st.beta_set_page_config(layout="wide")

from streamlit.report_thread import get_report_ctx

@st.cache(allow_output_mutation=True)
def init():
    stopwords = pickle.load(open("../stopwords.pickle", "rb"))
    fic_info = pickle.load(open("../fic_info_fixed.pickle", "rb"))
    model_info = pickle.load(open("../models/model_11_topics_2.pickle", "rb"))

    model = model_info["model"]
    dictionary = model_info["dict"]
    corpus = model_info["corpus"]
    index = Similarity.load("../sim_index_2.pickle")
    index_temp = get_tmpfile("index")
    index = Similarity(index_temp, model[corpus], num_features = model.num_topics)
    index.save("similarity_index.pickle")
    # todo: save words as frequencies to save time/space

    return {"fic_list": [], "model": model, "dictionary": dictionary, "index": index, "fic_topics": [], "words": "", "recs": [], "fic_info": fic_info, "clicked_rec": False, "stopwords": stopwords, "show_wc": False}

ctx = get_report_ctx()
cache = init()
st.markdown("<h2 style='font-size: 32px; text-align: center';>Yip Yip!: A Fanfiction Recommendation App(a)</h2>", unsafe_allow_html=True)

st.markdown("<h3>Input your favorite <em>Avatar: The Last Airbender</em> fanfics and I'll recommend similar ones from my database.</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

def get_topics_and_words(doc):

    doc_pro = process_text(doc)
    topics = cache["model"][cache["dictionary"].doc2bow(doc_pro)]
    return topics, ' '.join(doc_pro)

def get_recs(favorites_topics, top_n = 5):
    sims = np.zeros(len(cache["index"]))
    for similarities in cache["index"][favorites_topics]:
        sims += similarities

    best_idx = np.argsort(sims)[::-1][:top_n]
    best_sim = sims[best_idx]

    return best_idx

css = """
    <style>
        .title h1{
          user-select: none;
          font-size: 43px;
          color: white;
        }

        body {
        }

        .toolbar {
            display: None !important;
        }

        .stImage {
            width: 800px !important;
        }

        .control {
            display: none !important;
        }

        .block-container{
            padding-top: 0rem !important;
        }

        .stMarkdown {
            padding-top: 0px !important;
            padding-bottom: 0px !important;
        }

        .markdown-text-container {

        }

        h2 {
            margin: 20px 0 7px 0 !important;
            padding: 0 0 0 0 !important;
        }

        h3 {
            font-size: 26px !important;
            margin: 0 0 0 0 !important;
            padding: 0 0 0 0;
        }

        hr {

            margin: 0em 0em 0em 0em !important;
            padding: 0 0 0 0 !important;
            border-bottom: 3px solid black !important;
        }
    </style>
    """

st.markdown(css, unsafe_allow_html=True)

_, col_1, _, col_2, _, col_3 = st.beta_columns((0.1, 1, 0.1, 1, 0.1, 1))


import streamlit.components.v1 as components


with col_1:
    favorites_header = st.markdown("<h3>Copy paste a favorite fanfic!</h3>", unsafe_allow_html=True)
    fanfic_text = st.empty()
    favorites_id = st.markdown("<h3>Or enter a work's AO3 URL:</h3>", unsafe_allow_html=True)
    fanfic_id = st.empty()
    add_fanfic = st.button("Add to Favorites")



with col_2:
    favorites_header = st.markdown("<h3>Favorite Fanfics:</h3>", unsafe_allow_html=True)
    faves_container = st.beta_container()
    clear_favorites = st.button("Clear Favorites")

rec_button_text = "Recommend Some Fics!" if not cache["clicked_rec"] else "Refresh Recommendations"

with col_3:
    recommend_header = st.markdown("<h3>I recommend:</h3>", unsafe_allow_html=True)
    recs_container = st.beta_container()
    give_recs = st.empty()
    clicked_rec = give_recs.button("Recommend Some Fics!")

if clicked_rec or cache["clicked_rec"]:
    clicked_rec = give_recs.button("Refresh Recommendations")


    if (not cache["clicked_rec"] or cache["clicked_rec"]) and cache["fic_list"]:
        cache["recs"] = get_recs(cache["fic_topics"])
        md_recs = "<div style='overflow: scroll; height: 435px'>"

        for i in range(len(cache["recs"])):
            idx = cache["recs"][i]
            if i != 0:
                md_recs += "<hr>"
            this_fic_info = cache["fic_info"][idx]
            title = this_fic_info["title"]
            authors = this_fic_info["all_authors"]
            authors_str = ', '.join(authors)
            starting_text = this_fic_info["starting_text"]
            this_id = this_fic_info["work_id"]
            md_recs += f"<a href='https://archiveofourown.org/works/{this_id}'><em>{title}</em></a> by {authors_str}:<br>"
            md_recs += f"{starting_text[:75]}...<br>"

        md_recs += "</div>"
        recs_container.markdown(md_recs, unsafe_allow_html=True)
    else:
        recs_container.markdown("<div style='overflow: scroll; height: 435px'>You haven't added any favorites!<div>", unsafe_allow_html=True)

    cache["clicked_rec"] = True

else:
    recs_container.markdown("<div style='overflow: scroll; height: 435px'>Add some favorites to get recommendations!<div>", unsafe_allow_html=True)

if clear_favorites:
    cache["fic_list"] = []
    cache["fic_topics"] = []
    cache["words"] = Counter(int)
    cache["show_wc"] = False
    cache["recs"] = []


with col_1:
    txt = fanfic_text.text_area("", height=375)
    url = fanfic_text.text_
    #fanfic_id.number_input('...or enter an AO3 ID', value=0)


if add_fanfic:
    if txt:
        cache["fic_list"].append(txt[:200])
        topics, words = get_topics_and_words(txt)
        cache["fic_topics"].append(topics)
        cache["words"] += words
    # if url:
    # todo
    # else:



with col_2:
    md_faves = "<div style='overflow: scroll; height: 435px'>"

    for i in range(len(cache["fic_list"])):
        if i != 0:
            md_faves += "<hr>"
        fic_text = cache["fic_list"][i]
        cleaned_text = re.sub("\s+", " ", fic_text)[:100] + "..."
        md_faves += cleaned_text + "<br>"

    md_faves += "</div>"

    faves_container.markdown(md_faves, unsafe_allow_html=True)


st.markdown("<hr>", unsafe_allow_html=True)
_, col_4,col_6, _ = st.beta_columns((0.2, 0.4, 0.8, 0.1))
with col_4:

    show_wordcloud = st.markdown("<h3 style='text-align: center; font-size: 36px; padding-top: 150px; padding-right: 150px'>What words do<br> my favorite fics use?</h3>", unsafe_allow_html=True)

with col_6:

    fave_wordcloud = st.empty()

text = cache["words"]
cache["show_wc"] = True

if text != "":

    appa_mask = np.array(Image.open("appa_outline_crop.png"))
    wordcloud = WordCloud(height=800, width=1000, mask=appa_mask, contour_width=3, contour_color="black", stopwords=cache["stopwords"], background_color="white", colormap="OrRd", random_state=0).generate(text)

    fig, ax = plt.subplots(figsize=(30, 30))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    fave_wordcloud.pyplot(fig)
else:
    fave_wordcloud.markdown("<div style='text-align: center; font-size: 48px; line-height: 50px; padding-top: 150px; padding-right: 100px'>Add to your favorites<br> to show a wordcloud!</div>", unsafe_allow_html=True)
