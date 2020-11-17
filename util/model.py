'''
# Helper functions for LDA modeling and #tuning.
#
# Andrew Zhou
#
# Sources of advice, code, and information:
# https://radimrehurek.com/gensim/auto_examples/tutorials/run_lda.html
# https://towardsdatascience.com/evaluate-topic-model-in-python-latent-dirichlet-allocation-lda-7d57484bb5d0
'''
#

from gensim.models import LdaModel
from gensim.corpora import Dictionary
from gensim.models import CoherenceModel
import logging

class LDATuner():
    '''
    Class to train and tune the LDA topic model.
    '''
    def __init__(self, docs, corpus_file=None, print_progress=True, verbose=True):
        self.docs = docs
        self.dictionary = None
        self.corpus = None
        self.model = None
        self.print_progress = print_progress

        if verbose:
            logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

    def train_model(self, num_topics=5, min_thresh=0, max_thresh=1.0, chunksize=2000, alpha='auto', beta='auto', iterations=400, passes=20, eval_every=None, random_state=0,  save_model=True):
        '''
        Train a model with the provided parameters, and optionally save as private variables.
        '''
        dictionary = Dictionary(self.docs)
        dictionary.filter_extremes(no_below=min_thresh, no_above=max_thresh)
        
        temp = dictionary[0]  # This is only to "load" the dictionary.
        id2word = dictionary.id2token
        corpus = [dictionary.doc2bow(doc) for doc in self.docs]

        model = LdaModel(
            corpus=corpus,
            id2word=id2word,
            chunksize=chunksize,
            alpha=alpha,
            eta=beta,
            iterations=iterations,
            num_topics=num_topics,
            passes=passes,
            eval_every=eval_every,
            random_state=random_state
        )

        if save_model:
            self.dictionary = dictionary
            self.model = model
            self.corpus = corpus
        
        return model, dictionary, corpus
    
    def tune_hyper(self, keywords, param_grid, iterations=400, passes=20):
        '''
        Give a list of keywords and a parameter grid (as an itertools product),
        trains a model for each set of parameters, storing and returning the 
        coherence scores for each model.
        '''
        count = 0
        model_scores = {}
        if self.print_progress:
            print(f"beginning parameter evaluation...")
        
        for params in param_grid:
            kwargs = dict(zip(keywords, params))

            count += 1

            model, dictionary, _ = self.train_model(**kwargs, iterations=iterations, passes=passes, random_state=0, save_model=False)

            model_scores[params] = self.get_coherence(model=model, dictionary=dictionary)
            if self.print_progress:
                print(f"trained model {count} with params {kwargs}") 
                print(f"coherence {model_scores[params]}")
        return model_scores
    
    def train_model_params(self, params, keywords, iterations=500, passes=30):
        '''
        Train a model, as above, except take in a set of parameters and keywords in
        the same format as tune_hyper
        '''
        kwargs = dict(zip(keywords, params))
        if self.print_progress:
            print(f"training model with params {kwargs}")
        model, dictionary, corpus = self.train_model(**kwargs, iterations=iterations, passes=passes, random_state=0)
        coherence = self.get_coherence()
        
        model_info = {"model": model, "dict": dictionary, "corpus": corpus, "coherence": coherence}
        
        return model_info        
        
    def get_coherence(self, model=None, dictionary=None, texts=None):
        '''
        Get the model coherence, as measured by the c_v metric
        '''
        if not model:
            model = self.model
        if not dictionary:
            dictionary = self.dictionary
        if not texts:
            texts = self.docs
        coherence_model_lda = CoherenceModel(model=model, texts=texts, dictionary=dictionary, coherence='c_v')
        coherence_lda = coherence_model_lda.get_coherence()
        return coherence_lda

