'''
# Helper functions for HuggingFace, PyTorch, and text generation
#
# Andrew Zhou
#
'''

import numpy as np
from torch.utils.data import Dataset
import torch
from transformers.trainer_callback import TrainerCallback
from transformers.trainer_utils import EvaluationStrategy
import re
from collections import Counter

def clean_text_gen(text):
    clean = re.sub(r"’", "'", text)
    clean = re.sub(r"[“”]", "\"", clean)
    clean = re.sub(r"[^A-Za-z0-9' -;,!:?@\.\"]+", '', clean) # parens?
    clean = re.sub(r" +", " ", clean)
    return clean

def count_custom_tokens(texts, vocab, stopwords):
    token_counts = Counter()
    for text in texts:
        text_split = text.split(" ")
        for word in text_split:
            # remove quotation marks, periods, etc.
            word = re.sub("[^\w]", "", word)
            # account for GPT-2 treating words preceded by a space as different tokens
            word_prepend = " " + word

            if not word or word in vocab or word_prepend in vocab or word.lower() in stopwords:
                continue
            token_counts[word] += 1
    return token_counts

def chunk_docs(docs, tokenizer, max_tokens):
    chunked_docs = []
    for doc in docs:
        current_doc = ""
        current_tokens = 0

        punc_re = re.compile(r"[?!.]")
        punc_marks = list(re.finditer(r"[?!.]+", doc))
        for i in range(len(punc_marks)):
            if i == 0:
                prev_end = -1
            else:
                prev_end = punc_marks[i-1].span()[1]
            curr_end = punc_marks[i].span()[1]
            sentence = doc[prev_end+1:curr_end]
            tokenized = tokenizer.tokenize(sentence)

            if len(tokenized) >= max_tokens:
                continue
            if current_tokens + len(tokenized) <= max_tokens:
                current_doc += " " + sentence
                current_tokens += len(tokenized)
            else:
                chunked_docs.append(current_doc)
                current_doc = sentence
                current_tokens = len(tokenized)

            if i+1 == len(punc_marks):
                chunked_docs.append(current_doc)
    return chunked_docs

# Based on https://huggingface.co/transformers/custom_datasets.html
class FicDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings
        self.length = len(encodings["input_ids"])
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = item['input_ids']
        return item

    def __len__(self):
        return self.length

# Committed to the repo but hasn't been included in my install yet
# https://github.com/huggingface/transformers/blob/master/src/transformers/trainer_callback.py

class EarlyStoppingCallback(TrainerCallback):
    """
    A :class:`~transformers.TrainerCallback` that handles early stopping.
    Args:
       early_stopping_patience (:obj:`int`):
            Use with :obj:`metric_for_best_model` to stop training when the specified metric worsens for
            :obj:`early_stopping_patience` evaluation calls.
       early_stopping_threshold(:obj:`float`, `optional`):
            Use with TrainingArguments :obj:`metric_for_best_model` and :obj:`early_stopping_patience` to denote how
            much the specified metric must improve to satisfy early stopping conditions. `
    This callback depends on :class:`~transformers.TrainingArguments` argument `load_best_model_at_end` functionality
    to set best_metric in :class:`~transformers.TrainerState`.
    """

    def __init__(self, early_stopping_patience: int = 3, early_stopping_threshold: float = 0.0):
        self.early_stopping_patience = early_stopping_patience
        self.early_stopping_threshold = early_stopping_threshold
        # early_stopping_patience_counter denotes the number of times validation metrics failed to improve.
        self.early_stopping_patience_counter = 0

    def check_metric_value(self, args, state, control, metric_value):
        # best_metric is set by code for load_best_model
        operator = np.greater if args.greater_is_better else np.less
        if state.best_metric is None or (
            operator(metric_value, state.best_metric)
            and abs(metric_value - state.best_metric) > self.early_stopping_threshold
        ):
            self.early_stopping_patience_counter = 0
        else:
            self.early_stopping_patience_counter += 1

    def on_train_begin(self, args, state, control, **kwargs):
        assert args.load_best_model_at_end, "EarlyStoppingCallback requires load_best_model_at_end = True"
        assert (
            args.metric_for_best_model is not None
        ), "EarlyStoppingCallback requires metric_for_best_model is defined"
        assert (
            args.evaluation_strategy != EvaluationStrategy.NO
        ), "EarlyStoppingCallback requires EvaluationStrategy of steps or epoch"

    def on_evaluate(self, args, state, control, metrics, **kwargs):
        metric_to_check = args.metric_for_best_model
        if not metric_to_check.startswith("eval_"):
            metric_to_check = f"eval_{metric_to_check}"
        metric_value = metrics.get(metric_to_check)

        if metric_value is None:
            logger.warning(
                f"early stopping required metric_for_best_model, but did not find {metric_to_check} so early stopping is disabled"
            )
            return

        self.check_metric_value(args, state, control, metric_value)
        if self.early_stopping_patience_counter >= self.early_stopping_patience:
            control.should_training_stop = True