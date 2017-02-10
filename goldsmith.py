# -*- coding: utf-8 -*-
"""
Created on Sun Dec  4 11:13:20 2016

In this module we define the Gold Class. A Gold object contains all the information
and tools needed to perform a humble morpheme segmentation.

The name of the class : Gold comes from the name John Goldsmith. In the beginning
of this attempt we tried to implement an algorithm he defined almost 20 years ago.

Our results were not conclusive so we decided to change angle of attack. However his
kind answer to many of our questions were incredibly useful for our quest. Thus we named this class
after him.

Hypothesis :
We assume that the computer has no prior knowledge about the language of the text
it receives.

Goal :
Our goal is to identify different morphemes and to classify each word of the text
into signatures.

A signature is defined as follows :

{stem1, stem2, stem3,... } <-> {suffix1, suffix2, ..}

Where for all 'i' and 'j' we have stem'i' + suffix'j' = a word in the text.

A word can not be encoded in more than one signature.
@author: Toulemont
"""

from math import log
import functions as func
import sys
import radixtrie as art
class Gold:
    def __init__(self):

        # Storage used during the construction of the signatures
        self._stems_to_signatures = None
        self._signatures_to_stems = None
        self._stems_to_words = None
        self._words_to_stems = None
        self._suff_to_words = None
        self._words_to_suff = None
        self._stems_to_suffixes = None
        self._suffixes_to_stems = None
        self._words_to_signatures = None
        self._signatures_to_words = None
        self._suffixes_to_signatures = None
        self._words = None
        self._suffixes = None
        self._stems = None

        # Some useful information
        self._number_of_words_analized = 0

        # Split segmentation Using the radixtrie module.
        self._initial_split = None
        self._split = None
        self._word_to_split = None
        self._split_to_word = None
        self._wo_bs = None # word to best splits

        # Words Left to do. (see .words_left() for construction)
        self._todo = None

        # Binary variables to indicate the use of a suffixe and of a stem
        self._suff_used = None
        self._stem_used = None

        # Information (see .evaluate_suff(), .evaluate_sigs() for construction)
        self._suff_info = None
        self._stem_info = None
        self._sig_info = None

        # Best stems, suff, splits (see .build_new_stem_suff() for construction)
        self._stems_to_keep = None
        self._suff_to_keep = None
        self._word_to_split_to_keep = None

        # Sorted sig etc..
        self._sorted_sig = None
        self._sorted_suff = None
        self._sorted_stem = None

        # Best sig (see .word_best_sig() for construction)
        self._word_bsig = None
        self._bsig_word = None
        #Text is list of words
        self._text = None
        self._set = None

###

###
    @property
    def stable_split(self):
        return self._stable_split


    @property
    def stable_sig(self):
        return self._stable_sig
###

###
    def initialize_text(self, words_list):
        """
        Initialize the list of words in self._text
        """
        self._text = words_list
        self._set = set(words_list)
###

###
    def initialize(self, art):
        """
        Art is a Adaptative Radix Tree (defined in radixtrie). Here we will show a possible solution
        to the segmentation problem.

        word = (stem, suff)

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
###

###
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
        self._suff_to_words = dict()
        self._words_to_suff = dict()
        self._stems_to_suffixes = dict()
        self._suffixes_to_stems = dict()
        self._words = dict()

        for word in self._text:
            # Count how many times each word appears
            length = len(word)
            if word not in self._words:
                self._words[word] = 1
            else:
                self._words[word] += 1

            if length > 4:
                if length < 7:
                    d = 3
                elif length >= 7 and length < 10:
                    d = 4
                else:
                    d = 5

                c = 1
                self._number_of_words_analized += 1

                while c <= d:
                    # Make a segmentation of the word
                    suff = word[length - c:]
                    stem = word[0 : length - c]

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

                    # Link between word and stem
                    if word not in self._words_to_suff:
                        self._words_to_suff[word] = set()
                        self._words_to_suff[word].add(suff)
                    else:
                        if suff not in self._words_to_suff[word]:
                            self._words_to_suff[word].add(suff)

                    # Link betwenn suff and word
                    if suff not in self._suff_to_words:
                        self._suff_to_words[suff] = set()
                        self._suff_to_words[suff].add(word)
                    else:
                        if word not in self._suff_to_words[suff]:
                            self._suff_to_words[suff].add(word)

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
###

###
    def update_suff_m(self, suff, n):
        """
        Update the number of time a suffix has been used.
        """
        if suff in self._suff_used:
            self._suff_used[suff] -= n
            self._suff_used[suff] <= 0
            del self._suff_used[suff]
###

###
    def update_suff_p(self, suff, n):
        """
        Update the number of time a suffix has been used.
        """
        if suff in self._suff_used:
            self._suff_used[suff] += n
            self._suff_used[suff] <= 0
            del self._suff_used[suff]
        else:
            self._suff_used[suff] = n
###

###
    def update_stem_m(self, stem, n):
        """
        Update the number of time a stem has been used.
        """
        if stem in self._stem_used:
            self._stem_used[stem] -= n
            self._stem_used[stem] <= 0
            del self._stem_used[stem]
###

###
    def update_stem_p(self, stem, n):
        """
        Update the number of time a suffix has been used.
        """
        if stem in self._stem_used:
            self._stem_used[stem] += n
            self._stem_used[stem] <= 0
            del self._stem_used[stem]
        else:
            self._stem_used[stem] = n
###

###
    def evaluate_suff(self):
        """
        How much information each suffix / stem holds, approximately.


        By [morpheme] we refer to the number of times the morpheme appears in the text.
        As a metric we use :

            for suffixes :
                 (-1) * sum (on stem) of log([stem + suff]/([stem]*[suff]), 2) * len(suff)

                 such that stem + suff = a word in the text.

                 As we want big suffixes rather than one letter suffixes.

            for stems :
                (-1) * sum (on suff) of log([stem + suff]/([stem]*[suff]), 2)

                such that stem + suff = a word in the text.

        """
        self._suff_info = dict()
        for (suff, oc) in self._suffixes.items():
            a = 0
            for stem in self._suffixes_to_stems[suff]:
                b = self._stems[stem]
                c = self._words[stem+suff]
                a -= log(c/(b*oc),2)*len(suff)
            self._suff_info[suff] = a
        self._stem_info = dict()

        for (stem, oc) in self._stems.items():
            a = 0
            for suff in self._stems_to_suffixes[stem]:
                b = self._suffixes[suff]
                c = self._words[stem + suff]
                a -= log(c/(b*oc),2)
            self._stem_info[stem] = a
###

###
    def evaluate_split(self,beta, suff_list):
        """
        Once a batch of words segmentation has been created we want to evaluate the
        accuracy of each segmentation.

        beta : same but for the likelihood of the segmentation

        quick_sort_dict is defined in functions.py.

        As a metric we use :

            (-1)* sum (on word, stem, suff) log([word]/([stem]*[suff]))

            such that word = stem + suff, stem and suff belonging to the signature.
        """
        if self._split is None:
            self._split = dict()
        if self._word_to_split is None:
            self._word_to_split = dict()
            self._split_to_word = dict()
            self._wo_bs = dict()
        for suff in self._suffixes_to_stems:
            for stem in self._suffixes_to_stems[suff]:

                if (stem, suff) not in self._split:
                    self._split[(stem, suff)] = 0
                if (stem + suff) not in self._word_to_split:
                    self._word_to_split[stem + suff] = list()
                if (stem, suff) not in self._split_to_word:
                    self._split_to_word[(stem, suff)] = list()

                # Occurence of each morpheme _n
                word_n = self._words[stem + suff]
                suff_n = self._suffixes[suff]
                stem_n = self._stems[stem]
                txt_n = len(self._text)
                a = 1
                b = 1
                if suff in suff_list:
                    # If the suffix is in the leaves of the Adaptative Radix tree
                    # Then we are sure it is a suffix. We give them a little boost.
                    a = 3
                if self._initial_split[stem +suff] == (stem,suff):
                    # Same here, if the split is also the one given by the Adapatative Radix
                    # tree, we give them a little boost.
                    b = beta
                self._split[(stem, suff)] =a*( b*(- log(word_n/(suff_n*stem_n),2)))

                self._word_to_split[stem + suff].append((stem, suff))
                self._split_to_word[(stem,suff)].append(stem+suff)
        for word in self._word_to_split:
            split_list = func.quick_sort_dict(self._split,
                                         self._word_to_split[word],
                                         0,
                                         len(self._word_to_split[word]) - 1,
                                         0
                                         )
            stem_list = func.quick_sort_dict(self._stem_info,
                                             list(self._words_to_stems[word]),
                                             0,
                                             len(self._words_to_stems[word])-1,
                                             0
                                             )
            slist = func.quick_sort_dict(self._suff_info,
                                             list(self._words_to_suff[word]),
                                             0,
                                             len(self._words_to_suff[word])-1,
                                             0
                                             )
            self._word_to_split[word] = [split_list, stem_list, slist]
            self._wo_bs[word] = [split_list[len(split_list)-1], # Best split according to self._split
                                 stem_list[len(stem_list)-1], # Best stem according to self._stem_info
                                 slist[len(slist)-1] # Best suff according to self._suff_info
                                 ]
###

###
    def evaluate_sigs(self, suff_list):
        self._sig_info = dict()

        for (sig, stems) in self._signatures_to_stems.items():
            self._sig_info[sig] = 0
            s = 0
            for suff in sig:
                b = self._suffixes[suff]
                for stem in stems:
                    a = self._words[stem + suff]
                    c = self._stems[stem]
                    s -= log(a/(b*c),2)
            self._sig_info[sig] += s
            self._sig_info[sig] *= log(len(stems),2)*log(len(sig),2)
###

###
    def sort(self):
        """
        Sort the suffixes, stems, sigs according to the information metric we are using.
        """
        sys.setrecursionlimit(10000)
        self._sorted_sig = list()
        self._sorted_sig = func.quick_sort_dict(self._sig_info, list(self._sig_info.keys()), 0, len(list(self._sig_info.keys()))- 1, 0)

        self._sorted_suff = list()
        self._sorted_suff = func.quick_sort_dict(self._suff_info, list(self._suff_info.keys()), 0, len(list(self._suff_info.keys()))- 1, 0)

        self._sorted_stem = list()
        self._sorted_stem = func.quick_sort_dict(self._stem_info, list(self._stem_info.keys()), 0, len(list(self._stem_info.keys()))- 1, 0)
###

###
    def build_new_stem_suff(self):
        """
        Given the results from evalute_split, we apply a decision tree for each word
        in order to keep only the best stems and suffixes.

        We want to keep only one split.
        All 3 are equal : fine
        2 are equal : we use this one
        None are equal, we use the one defined by stem. It usually gives a good split
        and tend to maximize the size of the stem, as wall as maximize the size of the suffix as a second objective.
        """
        self._stems_to_keep = dict()
        self._suff_to_keep = dict()
        self._word_to_split_to_keep = dict()

        for (word, results) in self._wo_bs.items():
            (split_stem, split_suff) = results[0]
            stem = results[1]
            suff = results[2]
            m = art.common_prefix_length(word, stem)
            if split_stem == stem and split_stem == suff:
                # Only one split
                if stem not in self._stems_to_keep:
                    self._stems_to_keep[stem] = set()
                self._stems_to_keep[stem].add(word)

                if suff not in self._suff_to_keep:
                    self._suff_to_keep[suff] = set()
                self._suff_to_keep[suff].add(word)

                self._word_to_split_to_keep[word] = (stem, suff)

            elif split_stem == stem :
                # Only two split
                if stem not in self._stems_to_keep:
                    self._stems_to_keep[stem] = set()
                self._stems_to_keep[stem].add(word)

                if split_suff not in self._suff_to_keep:
                    self._suff_to_keep[split_suff] = set()
                self._suff_to_keep[split_suff].add(word)

                self._word_to_split_to_keep[word] = (stem, split_suff)

            elif split_suff == suff:
                # same
                if split_stem not in self._stems_to_keep:
                    self._stems_to_keep[split_stem] = set()
                self._stems_to_keep[split_stem].add(word)

                if suff not in self._suff_to_keep:
                    self._suff_to_keep[suff] = set()
                self._suff_to_keep[suff].add(word)

                self._word_to_split_to_keep[word] = (split_stem, suff)

            elif word[m:] == suff:
                # same
                if stem not in self._stems_to_keep:
                    self._stems_to_keep[stem] = set()
                self._stems_to_keep[stem].add(word)

                if suff not in self._suff_to_keep:
                    self._suff_to_keep[suff] = set()
                self._suff_to_keep[suff].add(word)

                self._word_to_split_to_keep[word] = (stem, suff)

            else:
                # None are equal we use the one defined by stem
                if stem not in self._stems_to_keep:
                    self._stems_to_keep[stem] = set()
                self._stems_to_keep[stem].add(word)

                if word[m:] not in self._suff_to_keep:
                    self._suff_to_keep[word[m:]] = set()
                self._suff_to_keep[word[m:]].add(word)

                self._word_to_split_to_keep[word] = (stem, word[m:])
###

###
    def make_signatures_to_stems(self):
        """
        For each signatures, creates the set of stems it is linked to.
        """
        self._signatures_to_stems = dict()
        self._suff_used = dict()
        self._stem_used = dict()
        for stem in self._stems_to_keep:

            suffix_set = set()
            length = len(stem)
            a = 0
            for word in self._stems_to_keep[stem]:
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
###

###
    def word_best_sig(self):
        """
        We want to keep to keep only one signature per word. Let's choose the
        best one !!
        """
        self._word_bsig = dict()
        self._bsig_word = dict()
        for (word, sigs) in self._words_to_signatures.items():
            a = 0
            arg = []
            for sig in sigs:
                for suff in sig:
                    for stem in self._signatures_to_stems[sig]:
                        if stem + suff == word:
                            radical = stem
                            break
                if self._sig_info[sig] > a:
                    a = self._sig_info[sig]
                    arg = []
                    arg.append(sig)
            self._word_bsig[word] = (radical, sig)
            if sig not in self._bsig_word:
                    self._bsig_word[sig] = list()
            self._bsig_word[sig].append((word, radical))
###

###
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
###

###
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
###

###
    def words_left(self):
        """
        Find the words without a signature.
        """
        self._todo = dict()
        aset = set(self._text)
        for word in aset:
            if len(word) > 4:
                if word not in self._words_to_signatures:
                    self._todo[word] = self._word_to_split[word]
###

###
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
###

###
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
###

###
    def build_word_info(self, word):
        """
        When the user clicks on a word, this method is called. We want to show all the
        information we have on said word.
        """
        if len(word) > 4:
            (radical, suffixes) = self._word_bsig[word]

            words = self._signatures_to_words[suffixes]
            # TODO : find the radical and the suffixes
            text_info = "Morpheme clustering algorithm results on : {} : ".format(word)
            if len(suffixes) >= 1:

                for suff in suffixes:

                    info = "{}".format(radical)+"  {}".format(suff) + " appears : {}".format(self._words[radical + suff])  + "\n"

                    if info != word:

                        text_info = text_info + "{}{}{}".format(" \n ", "    - ", info)

            else:

                text_info += "{}".format(" No close words found ")

        else:

            text_info = "'" + word + "'" + " is too short, try a longer word."

        return text_info
###

###
    def write_sigs(self, wfile):
        """
        Saves each signatures in a file :
        Sig'k'

        Word'i' | stem'i'

        Sig 'k+1'
        """
        with open(wfile, "w") as f:
            for (sig, couple) in self._bsig_word.items():
                f.write("{} : \n".format(sig))
                for (word, radical) in couple:
                    f.write(" {} | {}\n".format(word, radical))
                f.write("\n \n")
###

###
    def write_suff(self, wfile):
        """
        Saves the different stems for each suffix in a file:
        Suff'k'

        stem'i' | stem'i'_info
                            .............
        suff'k+1'
        """
        with open(wfile, "w") as f:
            for suff in self._sorted_suff[::-1]:
                f.write("{} :  {} \n".format(suff, self._suff_info[suff]))
                for stem in self._suffixes_to_stems[suff]:
                    if len(self._stems_to_suffixes[stem])>1:
                        f.write(" {} | {}\n".format(stem, self._stem_info[stem]))
                f.write("\n \n")
###

###
    def write_seg(self, wfile):
        """
        Saves the different segmentations for each word in a file:
        Word'k'

        stem 'i' | stem'i'_info :+: suff'i' | suff'i'_info :=: (stem'i', suff'i')_info
                                .............
        Word'k+1'
                                .............
        """
        with open(wfile, "w") as f:
            for word in self._words:
                f.write("{} :".format(word))
                if len(word) > 4:
                    for stem in self._words_to_stems[word]:
                        m = art.common_prefix_length(stem, word)
                        f.write(" {} | {} :+: {} | {} : = : {} \n".format(stem,
                                                                 self._stem_info[stem],
                                                                 word[m:],
                                                                 self._suff_info[word[m:]],
                                                                 self._split[(stem, word[m:])]
                                                                 ))
                f.write("\n \n")
