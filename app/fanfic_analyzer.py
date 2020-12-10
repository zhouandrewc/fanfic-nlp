#
# Streamlit app for NLP Project: Visual Analytics
# Andrew Zhou
#
# Some code taken from demos from https://github.com/streamlit/
#

import streamlit as st
st.beta_set_page_config(layout="wide")
import streamlit.components.v1 as components
import urllib
import re

from streamlit.report_thread import get_report_ctx

@st.cache(allow_output_mutation=True)
def init():
    return {"hide_input": False, "text": ""}

ctx = get_report_ctx()
cache = init()
st.markdown("<h2 style='font-size: 32px; text-align: center';>Yip Yip!: Visual Analytics for Fanfiction</h2>", unsafe_allow_html=True)

st.markdown("<h3>Input the text of an <em>Avatar: The Last Airbender</em> fanfiction and I'll generate visual insights about character interactions!</h3>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)


css = """
    <style>
        .title h1{
          user-select: none;
          font-size: 43px;
          color: white;
        }

        body {
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


big_container = st.beta_container()

_, col_1, _, col_2, _ = st.beta_columns((0.3, 0.2, 0.1, 0.2, 0.3))

def clean_text(text):
    clean = re.sub(r"’", "'", text)
    clean = re.sub(r"[“”]", "\"", clean)
    clean = re.sub(r"[^A-Za-z0-9' -;,!:?@\.\"]+", '', clean) # parens?
    clean = re.sub(r" +", " ", clean)
    return clean

with col_1:
    get_analytics = st.button("Show me analytics!")
with col_2:
    input_fic = st.button("Back to Input")

with big_container:
    if input_fic or (not get_analytics and not input_fic):
        _, col_3, _, col_4, _ = st.beta_columns((0.1, 1, 0.1, 1, 0.1))
        with col_3:
            input_header = st.markdown("<h3>Input a fanfiction!</h3>", unsafe_allow_html=True)
            input_text = st.empty()
            txt = input_text.text_area("", "Zuko", height=375)
            cache["text"] = clean_text(txt)
    elif get_analytics:
        _, col_5, _ = st.beta_columns((0.1, 1, 0.1))
        with col_5:
            # Render the Flask app in our container
            flask_app = "http://127.0.0.1:5000/fic_viz/" + urllib.parse.quote(str(cache["text"]))
            components.iframe(flask_app, width=1500, height=700, scrolling=True)