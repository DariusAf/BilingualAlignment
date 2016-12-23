# -*- coding:utf-8 -*-

import math
import re
from virtual_mvc import *
from widgets import *


# ------------------------------ MODEL ------------------------------


class FileNotFound(Exception):
    def __init__(self, s):
        super.__init__()
        self.name = s

    def __str__(self):
        return "Couldn't open '{}'".format(self.name)


class WordNotUpdated(Exception):
    def __init__(self, s):
        super.__init__()
        self.name = s

    def __str__(self):
        return "Word '{}' has not been updated !".format(self.name)


class DataNotProcessed(Exception):
    def __init__(self):
        super.__init__()

    def __str__(self):
        return "Database not processed !"


class Word:
    def __init__(self, s):
        self._str = s
        self._frequency = 0
        self._position = []
        self._recency = []
        self._clusterSize = 1
        self._isUpdated = False

    @property
    def str(self):
        return self._str

    @property
    def pos(self):
        return self._position

    @pos.setter
    def pos(self, l):
        self._position = l
        self._isUpdated = False

    @property
    def rec(self):
        if not self._isUpdated:
            raise WordNotUpdated(self._str)
        return self._recency

    @property
    def freq(self):
        if not self._isUpdated:
            raise WordNotUpdated(self._str)
        return self._frequency

    def add_occurrence(self, item):
        """Add an occurrence of the word to the occurrence vector"""
        self._isUpdated = False
        self._position.append(item)

    def __iadd__(self, x, sep=", "):
        """Merge two words"""
        self._isUpdated = False
        self._str += sep + x.str
        # merge occurrences
        j = 0
        l_x = len(x.pos)
        for i in range(len(self._position)):
            while j < l_x:
                if x.pos[j] < self._position[i]:
                    self._position.insert(i + j, x.pos[j])
                    j += 1
                else:
                    break
        for k in range(j, l_x):
            self._position.append(x.pos[k])

        self._clusterSize += 1
        return self

    def update(self):
        """Process the position vector
           To be called after each operation between words """
        if self._position:
            self._frequency = len(self._position)
            for i in range(len(self._position)):
                # convert from text file
                self._position[i] = float(self._position[i])
            self._recency = [self._position[0]]
            for i in range(1, self._frequency):
                self._recency.append(self._position[i] - self._position[i - 1])
            self._recency.append(1 - self._position[self._frequency - 1])
            self._isUpdated = True

    def dist_jaro(self, str2, alpha=0.8):
        """Jaro Winkler distance
           alpha to adjust the weight of the prefix """
        max_corr = int(max(len(self._str), len(str2)) / 2) - 1
        m = 0
        t = 0
        last_corr = -1
        for i, chr1 in enumerate(self._str):
            for j in range(max(i - max_corr, 0), min(i + max_corr + 1, len(str2))):
                if chr1 == str2[j]:
                    m += 1
                    if j > last_corr:
                        last_corr = j
                    else:
                        t += 1
                        last_corr = j
        dist = (m / len(self._str) + m / len(str2) + (m - t) / max(1, m)) / 3

        # prefix
        common_prefix = 0
        while common_prefix < min([5, len(self._str), len(str2)]) \
                and self._str[common_prefix] == str2[common_prefix]:
            common_prefix += 1

        return dist * alpha + (1 - dist * alpha) * common_prefix / 5

    def __str__(self):
        return "{} (f={})".format(self._str, self._frequency)


class Text(VirtualModel):
    def __init__(self):
        super().__init__()
        self._length = 0
        self._words = []
        self._txt = ""  # useful for the gui
        self._data = {}
        self._canOperate = False

    @property
    def length(self):
        return self._length

    @property
    def data(self):
        return self._data.keys()

    def __getitem__(self, key):
        """Quick access"""
        if not self._canOperate:
            raise DataNotProcessed
        return self._data[key]

    # -- Methods

    def open_raw(self, name):
        """Open a file and store it."""
        self._canOperate = False
        self._txt = ""
        try:
            with open(name, mode="r", encoding="utf-8") as f:
                for line in f:
                    l = line.strip("\n")
                    if l != "":
                        self._txt += l + " "
                    else:
                        # paragraphing
                        self._txt += "\n"
            # cut the source into words
            self._words = re.findall("[\w\dÀÁÂÃÄÅàáâãäåÒÓÔÕÖØòóôõöøÈÉÊËèéêëÇçÌÍÎÏìíîïÙÚÛÜùúûüÿÑñ]+", self._txt)
            self._length = len(self._words)
        except:
            raise FileNotFound(name)

    def process_raw(self):
        """Compute the recency vector for each word with a linear complexity """

        # count
        for i in range(self._length):
            word = self._words[i].lower()
            if word not in self._data:
                self._data[word] = Word(word)
            self._data[word].add_occurrence(i / self._length)

        # process
        for word in self._data:
            self._data[word].update()

        # allow access
        self._canOperate = True

    def select_range(self, minfreq=0, maxfreq=float("inf")):
        if self._canOperate:
            poplist = []
            for word in self._data:
                if not minfreq < self._data[word].freq < maxfreq:
                    poplist.append(word)
            for word in poplist:
                self._data.pop(word)
            self._length = len(self._data)

    def cluster_data(self, method="jaro", offset=0.95):
        """Group words with respect to a chosen metric"""
        self.mvc_check()
        if self._canOperate and method == "jaro":
            newdata = {}
            for str1 in list(self._data.keys()):
                if str1 in self._data:
                    newcluster = self._data.pop(str1)
                    cluster_list = []
                    for str2 in self._data:
                        if self._data[str2].dist_jaro(str1) > offset:
                            newcluster += self._data[str2]
                            cluster_list.append(str2)

                            for view in self._views:
                                view.notify_progress(1 / self._length)

                    newcluster.update()
                    newdata[newcluster.str] = newcluster

                    # pop elements to accelerate process
                    for el in cluster_list:
                        self._data.pop(el)

                    for view in self._views:
                        view.notify_progress(1 / self._length)

            self._data = newdata
        self._length = len(self._data)

    def save_data(self, name, minfreq=0):
        """Save the data into a txt file"""
        if self._canOperate:
            with open(name, "w", encoding="utf-8") as f:
                for word in self._data:
                    if self._data[word].freq > minfreq:
                        f.write("{}\n{}\n".format(self._data[word].str, ",".join(map(str, self._data[word].pos))))

    def open_data(self, name):
        """
        Read the pre-calculated self.data from a file.
        Do not use this method to open a raw file !
        """
        self._data = {}
        with open(name, "r", encoding="utf-8") as f:
            line_is_name = True
            currentword = ""
            self._length = 0
            for line in f:
                if line_is_name:
                    currentword = line.strip("\n")
                    self._data[currentword] = Word(currentword)
                    self._length += 1
                else:
                    self._data[currentword].pos = line.strip("\n").split(",")
                    self._data[currentword].update()
                line_is_name = not line_is_name
            self._canOperate = True


def str_tuple(item):
    return "{}:{}".format(item[0], item[1])


class Model(VirtualModel):
    def __init__(self):
        super().__init__()
        self._txt1 = Text()
        self._txt2 = Text()

        self._distWords = {}  # associated words and their distance
        self._groupFactor = 1  # quantifies how words are associated

    @property
    def txt1(self):
        return self._txt1

    @property
    def txt2(self):
        return self._txt2

    # -- Bind texts

    def mvc_link_texts(self):
        self.mvc_check()
        self.txt1.mvc_link_views(self._views)
        self.txt2.mvc_link_views(self._views)
        self.txt1.mvc_link_controller(self._controller)
        self.txt2.mvc_link_controller(self._controller)

    # -- Methods

    def associate_words(self, factor):
        """Naive heuristical association between the words of the first database
           and the second database based on the frequence of the words.
           We associate each word w1 of the first database to those of the second
           if its frequence is in [1/factor,factor]*w1.freq.
           We add an initial distance of infinity. """

        self._groupFactor = factor

        for str1 in self._txt1.data:
            self._distWords[str1] = {}
            f1 = self._txt1[str1].freq
            for str2 in self._txt2.data:
                if f1 / factor < self._txt2[str2].freq < f1 * factor:
                    self._distWords[str1][str2] = float("inf")

    @staticmethod
    def dtw(warp, v1, v2, mode="naive"):
        """Dynamic Time Wrapping
           use pre-allocated warp list to avoid multiple allocation """

        # init warp
        for j in range(len(v2)):
            warp[0][j] = 1
        for i in range(len(v1)):
            warp[i][0] = 1
        warp[0][0] = 0

        # recurrence
        if mode == "naive":
            for i in range(len(v1) - 1):
                for j in range(len(v2) - 1):
                    warp[i + 1][j + 1] = abs(v1[i] - v2[j]) + min([warp[i][j + 1], warp[i + 1][j], warp[i][j]])
            return warp[len(v1) - 1][len(v2) - 1]
        else:
            return float("inf")

    def dist_word(self, str1):
        """ Compute the distance between a word and the associated words,
            store the distances and return the minimum """

        min_dist = float("inf")
        min_str = ""

        if str1 in self._txt1.data:
            # allocate list for computation of the maximum size
            warp = [[1 for j in range(int(self._txt1[str1].freq * self._groupFactor) + 1)]
                    for i in range(self._txt1[str1].freq + 1)]

            for str2 in self._distWords[str1]:
                dist = self.dtw(warp, self.txt1[str1].rec, self.txt2[str2].rec)
                self._distWords[str1][str2] = dist
                if dist < min_dist:
                    min_dist = dist
                    min_str = str2
        return min_dist, min_str

    def compute_dictionary(self, name):
        """ It's high time to compute everything..."""
        self.mvc_check()
        with open(name, "w", encoding="utf-8") as f:
            for word in self._distWords:
                dist, aligned_word = self.dist_word(word)
                f.write("{} -> ({}) {}\n".format(word, dist, aligned_word))
                for view in self._views:
                    view.notify_progress(1 / self._txt1.length)

    def save_dists(self, name):
        """Save the data into a txt file"""
        with open(name, "w", encoding="utf-8") as f:
            for word in self._distWords:
                f.write("{} | {}\n".format(word, ",".join(map(str_tuple, self._distWords[word].items()))))


# ------------------------------ VIEW ------------------------------


class View(VirtualView):
    def __init__(self):
        super().__init__()
        self._current_task = ""
        self._progress_bar = 0
        self._offset_bar = 0

    def change_task(self, ref):
        """Change the current task and the corresponding progress bar"""
        self._current_task = ref
        self._progress_bar = 0
        self._offset_bar = 0

    def notify_progress(self, ratio):
        """Update the current progress bar if one associated with the task"""
        self._progress_bar += ratio
        while self._progress_bar > self._offset_bar:
            self._offset_bar += 0.01

            # DISPLAY ON GUI
            print("{} : {}%".format(self._current_task, math.floor(self._progress_bar * 100)))


# ------------------------------ CONTROL ------------------------------


class Controller(VirtualController):
    def __init__(self):
        super().__init__()
