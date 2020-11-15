from nltk.tokenize import word_tokenize
import spacy
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords as nltk_stopwords
from nltk import pos_tag, bigrams as nltk_bigrams, trigrams as nltk_trigrams
import re
from collections import Counter

def clean(text):
    clean = re.sub(r"’", "'", text)
    clean = re.sub(r"[^\w\d' ]+", '', clean)
    clean = re.sub(r" +", " ", clean)
    # clean words with accents and such
    return clean

# https://stackoverflow.com/questions/15586721/wordnet-lemmatization-and-pos-tagging-in-python
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return ''

def lemmatize_tokens(tokens, stopwords):
    lemmatizer = WordNetLemmatizer()
    tagged = map(lambda x: (x[0], get_wordnet_pos(x[1])), pos_tag(tokens))
    lemmas = [lemmatizer.lemmatize(x[0], x[1]).lower() if x[1] else lemmatizer.lemmatize(x[0]).lower() for x in tagged]
    lemmas = [lemma for lemma in lemmas if lemma not in stopwords]
    return lemmas

def merge_ngrams(doc_lemm, ngrams, stop_after):
    doc_lemm_grams = []
    
    bigrams = ngrams["bigrams"] if "bigrams" in ngrams else []
    trigrams = ngrams["trigrams"] if "trigrams" in ngrams else []
    exceptions_dict = ngrams["exceptions"] if "exceptions" in ngrams else {}
    
    i = 0
    while i < len(doc_lemm):
        uni = doc_lemm[i]
        bi = ' '.join(doc_lemm[i:i+2])
        tri = ' '.join(doc_lemm[i:i+3])
        if tri in exceptions_dict:
            doc_lemm_grams.append(exceptions_dict[tri])
            i += 3      
        elif bi in exceptions_dict:
            doc_lemm_grams.append(exceptions_dict[bi])
            i += 2
        elif uni in exceptions_dict:
            doc_lemm_grams.append(exceptions_dict[uni])
            i += 1
        elif tri in trigrams:
            doc_lemm_grams.append(tri)
            i += 3
        elif bi in bigrams:
            doc_lemm_grams.append(bi)
            i += 2
        else:
            if uni not in stop_after:
                doc_lemm_grams.append(uni)
            i += 1
    return doc_lemm_grams


def find_ngrams(docs, custom_stop = None, stop_exceptions = []):
    stopwords = get_stopwords(custom_stop, stop_exceptions)
    
    docs_tok_lower = [word_tokenize(clean(text).lower()) for text in docs]

    c_bi = Counter()
    for doc in docs_tok_lower:
        for bigram in nltk_bigrams(doc):
            if bigram[0] not in stopwords and bigram[1] not in stopwords:
                c_bi[bigram] += 1
    c_tri = Counter()
    for doc in docs_tok_lower:
        for trigram in nltk_trigrams(doc):
            if trigram[0] not in stopwords and trigram[1] not in stopwords and trigram[2] not in stopwords:
                c_tri[trigram] += 1
    return c_bi, c_tri

def process_text(text, ngrams={}, custom_stop=None, stop_exceptions=[], stop_after=[]):
    stopwords = get_stopwords(custom_stop, stop_exceptions)
    return merge_ngrams(lemmatize_tokens(word_tokenize(clean(text)), stopwords), ngrams, stop_after)

# docs is list (or series) of strings
def process_texts(docs, ngrams={}, custom_stop=None, stop_exceptions=[], stop_after=[]):
    
    stopwords = get_stopwords(custom_stop, stop_exceptions)
    return [process_text(text, ngrams, custom_stop=stopwords, stop_after=stop_after) for text in docs]

def get_stopwords(custom_stop=None, stop_exceptions=[]):
    if not custom_stop:
        stop_1 = set(nltk_stopwords.words('english'))
        stop_2 = spacy.load('en_core_web_sm').Defaults.stop_words
        stopwords = stop_1.union(stop_2)
    else:
        stopwords = custom_stop

    for exc in stop_exceptions:
        stopwords.discard(exc)
    
    return stopwords