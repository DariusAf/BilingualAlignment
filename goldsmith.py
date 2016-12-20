# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 11:13:20 2016
In this code we implement the algorithm defined by Goldsmith & al at : 
http://www.aclweb.org/anthology/J01-2001
@author: Toulemont
"""

# TODO : Build a function that computes the similarity between two signatures. 
# TODO : Build a User interface that shows the properties of the word cliked.
# TODO : Show other signatures that coud be linked to the word use. 
# TODO : Give the possibility to the user to eliminate translations, or associated words.
from math import log
import functions as func
import sys
class Goldsmith:
    def __init__(self):
        self._stems_to_signatures = None
        self._signatures_to_stems = None
        self._stems_to_words = None
        self._words_to_stems = None
        self._words_to_signatures = None
        self._signatures_to_words = None
        self._suffixes_to_signatures = None
        self._words_in_signatures = None
        self._suffixes = None
        self._stems = None
        
        self._signatures = None
        self._sorted_sig = None

        self._ngram = None 
        self._number_of_words_analized = 0
        self._letters = None
        
        self._suffix_likelihood = None
        self._stem_likelihood = None
        
        self._sorted_suffixes = None        
        
        
        #Classification
        self._stem_to_best_sig = None
        self._best_sig_to_stem = None
        self._word_best_split = None
        self._best_sig_word = None
        self._stable_sig = None
        
        #Similar signatures
        self._super_sig = None
        #An attempt to cluster verbs
        self._groups = None
        self._rate = None
        #Text is list of words
        self._text = None
        self._model = None
        
    def initialize_text(self, words_list):
        """
        Initialize the list of words in self._text
        """
        self._text = words_list
    
    def initialize_model(self, words_list):
        """
        Creates the stems, suffixes, words_to_stems, stems_to_words, self.ngram
        """
        if self._text is None:
            self.initialize_text(words_list)
        self._suffixes = dict()
        self._stems = dict()
        self._stems_to_words = dict()
        self._words_to_stems = dict()
        
        self._ngram = dict()
        for word in self._text:
            length = len(word)
            if length > 4:
                c = 1
                self._number_of_words_analized += 1
                while c < 5:
                    suff = word[length - c : length]
                    stem = word[0 : length - c]
                    
                    if str(c) not in self._ngram:
                        self._ngram[str(c)] = set()
                    if suff not in self._ngram[str(c)]:
                        self._ngram[str(c)].add(suff)
                    if str(len(word) - c) not in self._ngram:
                        self._ngram[str(len(word) - c)] = set()
                    if stem not in self._ngram[str(c)]:
                        self._ngram[str(len(word) - c)].add(stem)
                    
                    if suff not in self._suffixes:
                        self._suffixes[suff] = 1
                    else:
                        self._suffixes[suff] += 1
                    if stem not in self._stems:
                        self._stems[stem] = 1
                    else:
                        self._stems[stem] += 1
                    
                    if word not in self._words_to_stems:
                        self._words_to_stems[word] = set()
                        self._words_to_stems[word].add(stem)
                    else:
                        if stem not in self._words_to_stems[word]:
                            self._words_to_stems[word].add(stem)
                    if stem not in self._stems_to_words:
                        self._stems_to_words[stem] = set()
                        self._stems_to_words[stem].add(word)
                    else:
                        if word not in self._stems_to_words[stem]:
                            self._stems_to_words[stem].add(word)
                    c += 1
    def make_letter_count(self):
        """Returns a word containing all letters that are not suffixes."""
        self._letters = dict()
        word = []
        for letter in "abcdefghijklmnopqrstuvwxyzdÀÁÂÃÄÅàáâãäåÒÓÔÕÖØòóôõöøÈÉÊËèéêëÇçÌÍÎÏìíîïÙÚÛÜùúûüÿÑñœ":
            for word in self._text:
                length = len(word)
                if letter not in self._letters:
                    self._letters[letter] = [0, 0]
                if letter in word:
                    self._letters[letter][0] += 1
                    if length > 4:
                        self._letters[letter][1] += 1

    def make_signatures_to_stems(self):
        """
        For each signatures, creates the set of stems it is linked to.
        """
        self._signatures_to_stems = dict()
        for stem in self._stems_to_words:
            suffix_set = set()
            length = len(stem)
            
            for word in self._stems_to_words[stem]:
                if word == stem:
                    suffix_set.add("NULL")
                else:
                    suffix = word[length :]
                    
                    suffix_set.add(suffix)
            all_suffix = tuple(sorted(suffix_set))
            
            if all_suffix not in self._signatures_to_stems:
                self._signatures_to_stems[all_suffix] = set()
            
            self._signatures_to_stems[all_suffix].add(stem)

    def make_stems_to_signatures(self):
        """
        For each stem, creates the set containing all its signatures
        """
        self._stems_to_signatures = dict()
        for sig in self._signatures_to_stems:
            for stem in self._signatures_to_stems[sig]:
                if stem not in self._stems_to_signatures:
                    self._stems_to_signatures[stem] = set()
                if sig not in self._stems_to_signatures[stem]:
                    self._stems_to_signatures[stem].add(sig)

    def make_words_to_signatures(self):
        """
        For each word, creates the set containing all the signatures it is linked to.
        """
        self._words_to_signatures = dict()
        for stem in self._stems_to_signatures:
            for sig in self._stems_to_signatures[stem]:
                for suffix in sig:
                    if suffix == "NULL":
                        suffix = ""
                    word = stem + suffix

                    if word not in self._words_to_signatures:
                        self._words_to_signatures[word] = set()
                    if sig not in self._words_to_signatures[word]:
                        self._words_to_signatures[word].add(sig)

    def make_signatures_to_words(self):
        """
        For each signatures, creates the set containing all the signatures it is linked to.
        """
        self._signatures_to_words = dict()
        for word in self._words_to_signatures:
            for sig in self._words_to_signatures[word]:
                if sig not in self._signatures_to_words:
                    self._signatures_to_words[sig] = set()
                if word not in self._signatures_to_words[sig]:
                    self._signatures_to_words[sig].add(word)

    def make_suffixes_to_signatures(self):
        """
        For each suffix, creates the set containing all the signatures it is linkes to.
        """
        self._suffixes_to_signatures = dict()
        
        for sig in self._signatures_to_stems:
            for suffix in sig:
                if suffix not in self._suffixes_to_signatures:
                    self._suffixes_to_signatures[suffix] =set()
                if sig not in self._suffixes_to_signatures[suffix]:
                    self._suffixes_to_signatures[suffix].add(sig)

    def make_all_sigs(self, words_list):
        """
        Makes all signatures
        """
        self.initialize_model(words_list)
        self.make_letter_count()
        self.make_signatures_to_stems()
        self.make_stems_to_signatures()
        self.make_words_to_signatures()
        self.make_signatures_to_words()
        self.make_suffixes_to_signatures()

    def compute_morpheme_likelihood(self):
        """
        Compute the morpheme likelihood. ( Wighted mutual information)
        
        -[#morpheme]*log([#morpheme]/(product of [#letter] for letter in morpheme))/ [#text]
        """
        self._suffix_likelihood = dict()
        self._stem_likelihood = dict()
        
        for suff in self._suffixes:
            if suff not in self._suffix_likelihood:
                a = self._suffixes[suff]
                b = 1
                for letter in suff:
                    b *= self._letters[letter][0]
                c = len(self._ngram[str(len(suff))])
                self._suffix_likelihood[suff] = - a*log(a/b,2)/c
        for stem in self._stems:
            if stem not in self._stem_likelihood:
                a = self._stems[stem]
                b = 1
                for letter in suff:
                    b *= self._letters[letter][0]
                c = len(self._ngram[str(len(stem))])
                self._stem_likelihood[stem] = - a*log(a/b,2)/c
    
    def sort_suffixes(self):
        """
        Given their likelihood this method sorts suffixes/stems
        """
        sys.setrecursionlimit(10000)
        self._sorted_suffixes = list()
        
        list_suff = [ " " for suff in range(len(self._suffix_likelihood))]
        i = 0
        while i < len(self._suffix_likelihood):
            for suff in self._suffix_likelihood:            
                list_suff[i] = suff
                i += 1

        self._sorted_suffixes = func.quick_sort_dict(self._suffix_likelihood, list_suff, 0, len(list_suff)-1, 0)

    def signatures_info(self):
        """
        Using the wighted mutual information for the suffixes we deduce one for the signatures
        """
        if self._signatures is None:
            self._signatures = dict()
        for sig in self._signatures_to_stems:
            if sig not in self._signatures:
                self._signatures[sig] = 1
            s = 1
            p = 1
            for suff in sig:
                if suff != "NULL":
                    s += self._suffix_likelihood[suff]
                    p *= self._suffix_likelihood[suff]
            d = 1
            m = 1
            for stem in self._signatures_to_stems[sig]:
                if len(stem) > 1:
                    d += self._stem_likelihood[stem]
                    m *= self._stem_likelihood[stem]
            self._signatures[sig] = p/s + m/d

    def sort_sig(self):
        """
        Given their likelihood this method sorts suffixes/stems
        """
        sys.setrecursionlimit(10000)
        self._sorted_sig = list()
        
        list_sig = [ " " for suff in range(len(self._signatures))]
        i = 0
        while i < len(self._signatures):
            for sig in self._signatures:            
                list_sig[i] = sig
                i += 1

        self._sorted_sig = func.quick_sort_dict(self._signatures, list_sig, 0, len(list_sig)-1, 0)

    def best_sig(self):
        """
        For each stem, this method associate the best signature.
        """
        if self._stem_to_best_sig is None:
            self._stem_to_best_sig = dict()
        if self._best_sig_to_stem is None:
            self._best_sig_to_stem = dict()
        for stem in self._stems_to_signatures:
            argsig = None
            wmi = 0
            for sig in self._stems_to_signatures[stem]:
                if wmi < self._signatures[sig]:
                    wmi = self._signatures[sig]
                    argsig = sig
            self._stem_to_best_sig[stem] = argsig
            if argsig not in self._best_sig_to_stem:
                self._best_sig_to_stem[argsig] = list()
            self._best_sig_to_stem[argsig].append(stem)


    def best_split(self):
        """
        For a given word returns the best slit : stem + signature
        """
        if self._word_best_split is None:
            self._word_best_split = dict()
        if self._best_sig_word is None:
            self._best_sig_word = dict()
        for word in self._words_to_stems:
            if len(word) > 4:
                if word not in self._word_best_split:
                    self._word_best_split[word] = tuple()
                argstem = None
                argsig = None
                wmi = 0
                for stem in self._words_to_stems[word]:
                    if wmi < self._signatures[self._stem_to_best_sig[stem]]:
                        argstem = stem
                        argsig = self._stem_to_best_sig[stem]
                        wmi = self._signatures[self._stem_to_best_sig[stem]]
                self._word_best_split[word] = (argstem, argsig)
                if argsig not in self._best_sig_word:
                    self._best_sig_word[argsig] = list()
                self._best_sig_word[argsig].append((word, argstem))

    def rate_sig(self, sig):
        """
        An attempt to group morpheme that look alike according to the Jaro Winkler distance.
        """
        groups = set()
        for i in self._stable_sig[sig]:
            for j in self._stable_sig[sig]:
                if func.jaro_winkler(i[0], j[0]) == 1.0 and i != j \
                    and (i[0], j[0]) not in groups \
                    and (j[0], i[0]) not in groups:
                    groups.add((i[0], j[0]))
        return groups
    

    def check_stability(self):
        """
        Creates stable signatures.
        """
        self._stable_sig = dict()
        self._stable_split = dict()
        for word in self._word_best_split:
            (stem, sig) = self._word_best_split[word]
            suffix_set = set()
            for suff in sig:
                if self._word_best_split[stem+suff][1] == sig:
                    suffix_set.add(suff)
            if word not in self._stable_split:
                self._stable_split[word] = tuple()
            signature = tuple(sorted(suffix_set))
            self._stable_split[word] = (stem, signature)
            if signature not in self._stable_sig:
                self._stable_sig[signature] = list()
            self._stable_sig[signature].append((word, stem))

    def super_sig(self, alpha = 0.5):
        """
        Returns a dict containing groups of signatures.
        """
        self._super_sig = dict()
        for sig in self._stable_sig:
            l = len(sig)
            if sig not in self._super_sig:
                self._super_sig[sig] = list()
            for sig2 in self._stable_sig:
                sim = 0
                l2 = len(sig2)
                if sig != sig2:
                    if sig2 not in sig and sig not in sig2:
                        for suff1 in sig: 
                            if suff1 in sig2:
                                sim+=1
                if sim == l:
                    self._super_sig[sig].append(sig2)
        

    

            
        