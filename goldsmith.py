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
import radixtrie as art
class Goldsmith:
    def __init__(self):
        self._stems_to_signatures = None
        self._signatures_to_stems = None
        self._stems_to_words = None
        self._words_to_stems = None
        self._stems_to_suffixes = None
        self._suffixes_to_stems = None
        self._words_to_signatures = None
        self._signatures_to_words = None
        self._suffixes_to_signatures = None
        self._words_in_signatures = None
        self._words = None
        self._suffixes = None
        self._stems = None

        self._signatures = None

        self._ngram = None
        self._number_of_words_analized = 0
        self._letters = None

        self._suffix_likelihood = None
        self._stem_likelihood = None


        # Second heuristic
        self._sorted_suffixes = None
        self._sorted_stems = None
        self._sig_to_stem = None
        self._word_to_sig = None
        self._sig_info = None
        self._sorted_sig = None


        # Split segmentation
        self._initial_split = None
        self._split = None
        self._word_to_split = None
        self._wo_bs = None

        # Binary variables to indicute the use of a suffixe and of a stem
        self._suff_used = None
        self._stem_used = None

        # Global scores
        self._gscore = 0
        #Classification
        self._stem_to_best_sig = None
        self._best_sig_to_stem = None
        self._word_best_split = None
        self._best_sig_word = None
        self._stable_sig = None
        self._stable_split = None

        #Similar signatures
        self._super_sig = None
        #An attempt to cluster verbs
        self._groups = None
        self._rate = None
        #Text is list of words
        self._text = None
        self._model = None



    @property
    def stable_split(self):
        return self._stable_split


    @property
    def stable_sig(self):
        return self._stable_sig


    def initialize_text(self, words_list):
        """
        Initialize the list of words in self._text
        """
        self._text = words_list
        self._set = set(words_list)

    def initialize(self, art):
        """
        Art is a adaptative radix tree. Here we will show a possible solution
        to the segmentation problem.

        word = (stem, suff)

        if stem happens to be in self._set then we will have
        word = ((stem, suff1), suff2)
        """
        self._initial_split = dict()

        for word in self._set:
            b = 0
            if len(word) > 7:
                min_stem_length = 4
            elif len(word) < 5:
                min_stem_length = 2
            else:
                min_stem_length = 3
            m = art.trouve_rad_max(word, min_stem_length)
            self._initial_split[word] = (word[:m], word[m:])



    def initialize_model(self, words_list):
        """
        Creates the stems, suffixes, words_to_stems, stems_to_words, self.ngram

        The idea here is to create a first batch of segmentation word = (prefix, suffix)
        The we will get rid of those that do not contain enough information
        """
        if self._text is None:
            self.initialize_text(words_list)
        self._suffixes = dict()
        self._stems = dict()
        self._stems_to_words = dict()
        self._words_to_stems = dict()
        self._stems_to_suffixes = dict()
        self._suffixes_to_stems = dict()
        self._words = dict()

        self._ngram = dict()
        for word in self._text:
            # Count how many times each word appears
            if word not in self._words:
                self._words[word] = 1
            else:
                self._words[word] += 1

            length = len(word)
            if length > 4:
                c = 1
                self._number_of_words_analized += 1
                b = 0
                if length > 7:
                    b = 1

                while c < 5*(1 - b) + b*7:
                    # Make a segmentation of the word
                    suff = word[length - c : length]
                    stem = word[0 : length - c]

                    # Count the number of ngram
                    if str(c) not in self._ngram:
                        self._ngram[str(c)] = set()
                    # Add suffix to the corresponding ngram list
                    if suff not in self._ngram[str(c)]:
                        self._ngram[str(c)].add(suff)
                    # same for stem
                    if str(len(word) - c) not in self._ngram:
                        self._ngram[str(len(word) - c)] = set()
                    if stem not in self._ngram[str(c)]:
                        self._ngram[str(len(word) - c)].add(stem)

                    # Count the number of times each suffix appears
                    if suff not in self._suffixes:
                        self._suffixes[suff] = 1
                    else:
                        self._suffixes[suff] += 1
                    # Count the number of times each stem appears
                    if stem not in self._stems:
                        self._stems[stem] = 1
                    else:
                        self._stems[stem] += 1

                    # Link between word and stem
                    if word not in self._words_to_stems:
                        self._words_to_stems[word] = set()
                        self._words_to_stems[word].add(stem)
                    else:
                        if stem not in self._words_to_stems[word]:
                            self._words_to_stems[word].add(stem)
                    # Link between stem and word
                    if stem not in self._stems_to_words:
                        self._stems_to_words[stem] = set()
                        self._stems_to_words[stem].add(word)
                    else:
                        if word not in self._stems_to_words[stem]:
                            self._stems_to_words[stem].add(word)

                    # Link between suffix and stem
                    if suff not in self._suffixes_to_stems:
                        self._suffixes_to_stems[suff]= dict()
                    if stem not in self._suffixes_to_stems[suff]:
                        self._suffixes_to_stems[suff][stem] = 1
                    else:
                        self._suffixes_to_stems[suff][stem] += 1

                    # Link between stem and suffix
                    if stem not in self._stems_to_suffixes:
                        self._stems_to_suffixes[stem] = dict()
                    if suff not in self._stems_to_suffixes[stem]:
                        self._stems_to_suffixes[stem][suff] = 1
                    else:
                        self._stems_to_suffixes[stem][suff] += 1

                    c += 1

    def make_letter_count(self):
        """Count each occurence of any letter."""
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

    def compute_morpheme_likelihood(self):
        """
        Compute the morpheme likelihood. ( Weighted mutual information)

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
                self._suffix_likelihood[suff] = - a*log(a/b,2)/c*log(len(suff)*1.1/2)

        for stem in self._stems:

            if stem not in self._stem_likelihood:

                a = self._stems[stem]
                b = 1

                for letter in suff:

                    b *= self._letters[letter][0]

                c = len(self._ngram[str(len(stem))])
                self._stem_likelihood[stem] = - a*log(a/b,2)/c
    def evaluate_split(self, alpha, beta, suff_list):
        """
        Once a batch of words segmentation has been created we want to evaluate the
        accuracy of each segmentation.

        alpha : Degree of importance given to the likelihood of the suffix
        beta : same but for the likelihood of the segmentation
        """
        if self._split is None:
            self._split = dict()
        if self._word_to_split is None:
            self._word_to_split = dict()
            self._wo_bs = dict()
        for suff in self._suffixes_to_stems:
            for stem in self._suffixes_to_stems[suff]:

                if (stem, suff) not in self._split:
                    self._split[(stem, suff)] = 0
                if (stem + suff) not in self._word_to_split:
                    self._word_to_split[stem + suff] = list()

                word_n = self._words[stem + suff]
                suff_n = self._suffixes[suff]
                stem_n = self._stems[stem]
                txt_n = len(self._text)
                a = 1
                b = 1
                if suff in suff_list:
                    a = 3
                if self._initial_split[stem +suff] == (stem,suff):
                    b = beta
                self._split[(stem, suff)] =a*( b*(- log(word_n/(suff_n*stem_n),2)) \
                                            + alpha * self._suffix_likelihood[suff])

                self._word_to_split[stem + suff].append((stem, suff))
        for word in self._word_to_split:
            alist = func.quick_sort_dict(self._split,
                                         self._word_to_split[word],
                                         0,
                                         len(self._word_to_split[word]) - 1,
                                         0
                                         )
            self._word_to_split[word] = alist
            self._wo_bs[word] = alist[len(alist)-1]

###
###
    def make_signatures_to_stems(self):
        """
        For each signatures, creates the set of stems it is linked to.
        """
        self._signatures_to_stems = dict()
        self._suff_used = dict()
        self._stem_used = dict()
        for stem in self._stems_to_words:

            suffix_set = set()
            length = len(stem)

            for word in self._stems_to_words[stem]:
                if word == stem:

                    suffix_set.add("NULL")

                else:
                    suffix = word[length :]
                    suffix_set.add(suffix)
                    if suffix not in self._suff_used:
                        self._suff_used[suffix] = 1
                    else:
                        self._suff_used[suffix] += 1

            all_suffix = tuple(sorted(suffix_set))

            if all_suffix not in self._signatures_to_stems:

                self._signatures_to_stems[all_suffix] = set()

            self._signatures_to_stems[all_suffix].add(stem)
            if stem not in self._stem_used:
                self._stem_used[stem] = 1
            else:
                self._stem_used[stem] += 1

    def first_evaluation(self):
        todel = set()
        for (sig, stems) in self._signatures_to_stems.items():
            if log(len(sig),2)*log(len(stems),2) == 0:
                todel.add(sig)
        for sig in todel:
            for suff in sig :
                self._suff_used[suff] -= 1
                if self._suff_used[suff] <= 0:
                    del self._suff_used[suff]
            for stem in self._signatures_to_stems[sig]:
                self._stem_used[stem] -= 1
                if self._stem_used[stem] <= 0:
                    del self._stem_used[stem]
            del self._signatures_to_stems[sig]

    def score(self):
        for suff in self._suff_used:
            self._gscore -= self._suff_used[suff]*log(len(suff),26)
        for stem in self._stem_used:
            self._gscore -= self._stem_used[stem]*log(len(stem),26)
        for (sig, stems) in self._signatures_to_stems.items():
            self._gscore += log(len(sig),2)*log(len(stems),2)

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

    def check_sig_p_w(self):
        """
        Check that each word has only one signature
        """

    def check_beginning(self):
        """
        One type of signature we would like to eliminate is :
        ('sa', 'sait', 'se', 'ser', 'sé')
        we would like to replace it by :
        (' ', 'a', 'ait', 'ant', 'er', 'é')
        """
        toadd = list()
        for sig in self._sig_to_stem:

            first_letter = []
            nb_letters = 0
            suffixes = set()
            suffixes.add('')
            stems = list()
            for suff in sig:

                if suff[0] not in first_letter:

                    first_letter.append(suff[0])
                    nb_letters += 1

                suffixes.add(suff[1:len(suff)])

            if nb_letters == 1 and '' not in first_letter:

                atuple = tuple(sorted(suffixes))
                for stem in self._sig_to_stem[sig]:

                    stems.append(stem + first_letter[0])

                if atuple not in self._sig_to_stem:

                    toadd.append((atuple, stems))

                else:

                    for stem in stems:

                        if stem not in self._sig_to_stem[atuple]:

                            self._sig_to_stem[atuple].append(stem)

        for new in toadd:

            self._sig_to_stem[new[0]] = new[1]



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


    def super_sig(self):
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
                if sig != sig2:

                    if sig2 not in sig and sig not in sig2:

                        for suff1 in sig:

                            if suff1 in sig2:

                                sim+=1
                if sim == l:

                    self._super_sig[sig].append(sig2)


    def build_word_info(self, word):
        """
        We assume all the information is contained inside the atuple object.
        Where  : atuple = (word, signature)
        """
        if len(word) > 4:

            (radical, suffixes) = self._stable_split[word]
            text_info = "Goldsmith algorithm results on : {} : ".format(word)
            if len(suffixes) > 1:

                for suff in suffixes:

                    info = "{}".format(radical)+"{}".format(suff)

                    if info != word:

                        text_info = text_info + "{}{}{}".format(" \n ", "    - ", info)

            else:

                text_info += "{}".format(" No close words found ")

        else:

            text_info = "'" + word + "'" + " is too short, try a longer word."

        return text_info


    def goldsmith_clustering(self, words_list):
        """
        Cluster words into signatures.
        """
        self.initialize_model(words_list)
        self.make_letter_count()
        self.compute_morpheme_likelihood()
        self.sort_suffixes(300)
        self.sort_stems(5000)
        self.make_stems_to_top_suff()
        #self.make_suffixes_to_top_stem()
        #self.check_beginning()
        self.sig_info()
        self.sort_sig(200)


        #self.make_signatures_to_stems()
        #self.make_stems_to_signatures()
        #self.make_words_to_signatures()
        #self.make_signatures_to_words()
        #self.make_suffixes_to_signatures()
        #self.signatures_info()
        #self.best_sig()
        #self.best_split()
        #self.check_stability()
        #self.super_sig()
