#
# Functions for text generation for my Flask/d3 Visual Analytics App
# Andrew Zhou
#
#

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import itertools
from collections import Counter

# Allows our flask app to pass in a SpaCy-processed document and a list of
# characters; will search for character and character-pair frequencies and
# return those frequencies as well as sentence pairs and sentiments between
# each pair.
def process_helper(doc, characters, window_size = 50):
    # Initial pass - should be refactored
    char_freqs = {char: char_freq(doc, char, window_size) for char in characters}

    # Filter to only characters that are present in the text
    chars_in = list(filter(lambda x: char_freqs[x] > 0, characters))

    char_freqs, pair_freqs = pair_freq_fast(doc, chars_in, window_size)

    pairs = itertools.combinations(chars_in, 2)
    indices = itertools.combinations(range(len(chars_in)), 2)

    sentence_mat = [[[] for i in range(len(chars_in))] for j in range(len(chars_in))]
    sentiments = [[0.0 for i in range(len(chars_in))] for j in range(len(chars_in))]
    for idx, pair in zip(indices, pairs):
        sentences = get_overlap_sentences(doc, pair[0], pair[1], window_size)
        sentence_sentiments = get_sentiments(sentences)
        sentence_mat[idx[0]][idx[1]] = sentence_sentiments
        sentence_mat[idx[1]][idx[0]] = sentence_sentiments

        total_sum = 0
        total_len = 0
        for sentence_sentiment in sentence_sentiments:
            total_sum += sentence_sentiment[1] * len(sentence_sentiment[0])
            total_len += len(sentence_sentiment[0])

        avg_sent = total_sum/total_len if total_len else 0

        sentiments[idx[0]][idx[1]] = avg_sent
        sentiments[idx[1]][idx[0]] = avg_sent

    results = {"char_freqs": char_freqs, "char_list": chars_in, "pair_freqs": pair_freqs, "pair_sentences": sentence_mat, "pair_sentiments": sentiments}

    return results

# Given a list of characters, finds alone frequencies and pairwise frequencies
# for all characters in the given text
def pair_freq_fast(doc, chars, window_size):

    indices = {char: i for i, char in enumerate(chars)}
    char_freq = [0.0 for i in range(len(chars))]
    pair_freq = [[0.0 for i in range(len(chars))] for j in range(len(chars))]

    counter = Counter()
    for i in range(window_size):
        if doc[i].text in chars:
            counter[doc[i].text] += 1

    windows = 0
    total_windows = len(doc) - window_size + 1

    for i in range(total_windows):
        if i != 0:
            next_word = doc[i - 1 + window_size].text
            prev_word = doc[i - 1].text

            if next_word in chars:
                counter[next_word] += 1
            if prev_word in chars:
                counter[prev_word] -= 1

        chars_present = [char for char in chars if counter[char] > 0]

        for char in chars_present:
            char_freq[indices[char]] += 1
            if len(chars_present) == 1:
                pair_freq[indices[char]][indices[char]] += 1
        for (c1, c2) in itertools.combinations(chars_present, 2):
            pair_freq[indices[c1]][indices[c2]] += 1
            pair_freq[indices[c2]][indices[c1]] += 1

    char_freq = [ct/total_windows for ct in char_freq]
    pair_freq = [[(pair_freq[i][j])/total_windows for i in range(len(chars))] for j in range(len(chars))]

    return char_freq, pair_freq

def char_freq(doc, char, window_size):
    windows = 0
    total_windows = len(doc)-window_size+1
    for i in range(total_windows):
        span = doc[i:i+window_size]
        words = [token.text for token in span]
        if char in words:
            windows += 1
    return windows/total_windows


# Some fairly complicated routines to find overlapping sentences
# Needs refactoring
def get_overlap_sentences(doc, char1, char2, window_size):
    overlaps = find_overlaps(doc, char1, char2, window_size)
    spans = []
    for overlap in overlaps:
        begin_token = doc[overlap[0]]
        end_token = doc[overlap[1]]
        spans.append(doc[begin_token.sent.start:end_token.sent.end])

    merged_spans = merge_spans(doc, spans)
    merged_sentences = [sent.text for sent in merged_spans]
    return merged_sentences

def find_overlaps(doc, char1, char2, window_size):
    indices_1 = get_char_indices(doc, char1)
    indices_2 = get_char_indices(doc, char2)

    i, j = 0, 0

    windows = []

    window_begin = -1
    window_end = -1

    while True:
        i1, i2 = indices_1[i], indices_2[j]

        if abs(i1 - i2) < window_size:
            if window_begin == -1:
                window_begin = min(i1, i2)
            window_end = max(i1, i2)
        else:
            if window_begin != -1:
                windows.append((window_begin, window_end))
            window_begin, window_end = -1, -1

        if i == len(indices_1) - 1 and j == len(indices_2) - 1:
            if window_begin != -1:
                windows.append((window_begin, max(i1, i2)))
            break
        elif i == len(indices_1) - 1:
            j += 1
        elif j == len(indices_2) - 1:
            i += 1
        else:
            if indices_1[i+1] < indices_2[j+1]:
                i += 1
            else:
                j += 1
    return windows

def merge_spans(doc, spans):
    if not spans:
        return []
    merge_spans = [spans[0]]
    for span in spans[1:]:
        if merge_spans[-1].end > span.start:
            merge_spans[-1] = doc[merge_spans[-1].start:span.end]
        else:
            merge_spans.append(span)
    return merge_spans

def get_sentiments(sentences):
    analyzer = SentimentIntensityAnalyzer()
    scores = []
    for sentence in sentences:
        vs = analyzer.polarity_scores(sentence)
        scores.append((sentence, float(vs["compound"])))
        if sentence.startswith("And then"):
            print(sentence, vs["compound"])
    return scores