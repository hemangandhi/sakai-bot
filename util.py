import re
from collections import Counter

#Thanks to http://norvig.com/spell-correct.html

def P(word, words, N=None):
    "Probability of `word`."
    if N is None:
        N = len(words)
    return words[word] / N

def correction(word, words):
    "Most probable spelling correction for word."
    can, d = candidates(word, words)
    return max(can, key=lambda x: P(x, words)), d

def candidates(word, d):
    "Generate possible spelling corrections for word."
    k = known([word], d)
    if len(k) > 0:
        return k, 0
    k = known(edits1(word), d)
    if len(k) > 0:
        return k, 1
    k = known(edits2(word), d)
    if len(k) > 0:
        return k, 2
    return [word], 3

def known(words, d):
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in d)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word):
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))

def most_likely_match(key, values):
    return correction(key.lower(), Counter(v.lower() for v in values))

if __name__ == "__main__":
    print(most_likely_match("allo", ["hello", "nihao", "bonjour"]))
