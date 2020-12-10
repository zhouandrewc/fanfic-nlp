#
# Streamlit app for text generation for NLP Project
# Andrew Zhou
#
# Some code taken from demos from https://github.com/streamlit/
#

import streamlit as st
import torch
st.beta_set_page_config(layout="wide")

from transformers import GPT2Tokenizer, GPT2LMHeadModel
from streamlit.report_thread import get_report_ctx

# tokenizer and model must be in the directory
@st.cache(allow_output_mutation=True)
def init():
    tokenizer = GPT2Tokenizer.from_pretrained("tokenizer")
    model = GPT2LMHeadModel.from_pretrained("model")
    return {"tokenizer": tokenizer, "model": model}

ctx = get_report_ctx()
cache = init()
st.markdown("<h2 style='font-size: 32px; text-align: center';>Yip Yip!: A Fanfiction Generator</h2>", unsafe_allow_html=True)

st.markdown("<h3>Input a starting seed and I'll generate text in the style of an <em>Avatar: The Last Airbender</em> fanfiction!</h3>", unsafe_allow_html=True)
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

_, col_1, _, col_3, _ = st.beta_columns((0.1, 1, 0.1, 1, 0.1))


import streamlit.components.v1 as components


with col_1:
    starter_header = st.markdown("<h3>Give me some starter text!</h3>", unsafe_allow_html=True)
    starter_text = st.empty()
    generate_fic = st.button("Generate a fic!")
    length = st.number_input("How many tokens should the fic be?", 200)


with col_3:
    recommend_header = st.markdown("<h3>Your fic:</h3>", unsafe_allow_html=True)
    fic_container = st.beta_container()

with col_1:
    txt = starter_text.text_area("", "Zuko", height=375)

temperature = 0.8
top_p = 0.94
top_k = 60
rep_pen = 1.2
num_return = 1

if generate_fic:
    output_length = length
    md_recs = "<div style='overflow: scroll; height: 435px'>"
    input_ids = cache["tokenizer"].encode(str(txt), return_tensors="pt")#.cuda()

    output = cache["model"].generate(
        input_ids=input_ids,
        max_length=output_length,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repetition_penalty=rep_pen,
        do_sample=True,
        num_return_sequences=num_return
    )[0]
    md_recs += cache["tokenizer"].decode(output, skip_special_tokens=True)

    md_recs += "</div>"
    fic_container.markdown(md_recs, unsafe_allow_html=True)
