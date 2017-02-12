# -*- coding:utf-8 -*-
import math
import re
from virtual_mvc import *
from widgets import *
from functions import tolower
import goldsmith as gold
import radixtrie as art
"""
Here is the place everything happens.
"""

# Const var
LEFT_TEXT = 1
RIGHT_TEXT = 2

# ---------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- MODEL ------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


class FileNotFound(Exception):
    def __init__(self, s):
        super().__init__()
        self.name = s

    def __str__(self):
        return "Couldn't open '{}'".format(self.name)


class WordNotUpdated(Exception):
    def __init__(self, s):
        super().__init__()
        self.name = s

    def __str__(self):
        return "Word '{}' has not been updated !".format(self.name)


class DataNotProcessed(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Database not processed !"


class WordNotInDatabase(Exception):
    def __init__(self):
        super().__init__()

    def __str__(self):
        return "Word not found in the computed database"

# TODO : add a cluster type, addition is not suitable for the selection...


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
        self._gold = gold.Gold()  # Gold object (signature clustering)
        self._dart = art.Trie('direct')
        self._iart = art.Trie('inverse')

    @property
    def length(self):
        return self._length

    @property
    def str(self):
        return self._txt

    @property
    def data(self):
        return self._data.keys()

    @property
    def gold(self):
        return self._gold

    @property
    def sig(self):
        return self._gold.stable_sig

    @property
    def word_split(self):
        return self._gold.stable_split

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
        """ Compute the recency vector for each word with a nLog(n) complexity """

        for i in range(self._length):
            word = self._words[i].lower()
            if word not in self._data:
                self._data[word] = Word(word)
            self._data[word].add_occurrence(i / self._length)

            # Notify view
            for view in self._views:
                view.notify_progress(1 / self._length)

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

    def make_trie(self, column_side):
        """
        Build an Adaptative Radix Tree as in radixtrie.py
        """
        se = set(self._words)

        for w in se:
            self._dart.ajoute(w.lower())
            self._iart.ajoute(w.lower())

        self._dart.concatene_trie()
        self._dart.concatene_trie()
        self._dart.trouve_feuilles()

        self._iart.concatene_trie()
        self._iart.concatene_trie()

        if column_side == LEFT_TEXT:
            nom_fichier1 = 'save_data/left_trie_split.txt'
            nom_fichier2 = 'save_data/left_trie_dict.txt'
        else:
            nom_fichier1 = 'save_data/right_trie_split.txt'
            nom_fichier2 = 'save_data/right_trie_dict.txt'
        art.ecrit_segmentation(nom_fichier1, se, self._iart, self._dart)
        art.ecrit_dictionnaire(nom_fichier2, self._dart)

    def apply_goldsmith(self, beta, min_oc, side):
        """
        Apply the improved Goldsmith segmentation.

        Needed : self.open_raw()
        Needed : self.make_trie()
        """
        suff_list = list()
        for (leaf, oc) in self._dart.feuilles.items():
            if oc > min_oc:
                suff_list.append(leaf)
        alist = list(map(tolower, self._words))

        self._gold.initialize_text(alist)
        self._gold.initialize(self._dart)
        self._gold.initialize_model(alist)

        self._gold.evaluate_suff()
        self._gold.evaluate_split(beta, suff_list)
        self._gold.build_new_stem_suff()

        self._gold.make_signatures_to_stems()
        # self._gold.first_evaluation()
        self._gold.evaluate_sigs(suff_list)
        self._gold.make_stems_to_signatures()
        self._gold.make_words_to_signatures()
        self._gold.make_signatures_to_words()

        self._gold.word_best_sig()

        self._gold.sort()
        if side == LEFT_TEXT:
            self._gold.write_sigs('save_data/left_sig.txt')
            self._gold.write_suff('save_data/left_suff.txt')
            self._gold.write_seg('save_data/left_seg.txt')
        else:
            self._gold.write_sigs('save_data/right_sig.txt')
            self._gold.write_suff('save_data/right_suff.txt')
            self._gold.write_seg('save_data/right_seg.txt')
        # self._gold.check_stability()


def str_tuple(item):
    """ to be used with a map function when saving """
    return "{}:{}".format(item[0], item[1])


class Model(VirtualModel):
    def __init__(self):
        super().__init__()
        self._txt1 = Text()
        self._txt2 = Text()

        self._distWords = {}  # associated words and their distance
        self._groupFactor = 1.5  # quantifies how words are associated

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
        """Naive heuristic association between the words of the first database
           and the second database based on the frequencies of the words.
           We associate each word w1 of the first database to those of the second
           if its frequencies is in [1/factor,factor]*w1.freq.
           We add an initial distance of infinity. """

        self._groupFactor = factor

        for str1 in self._txt1.data:
            self._distWords[str1] = {}
            f1 = self._txt1[str1].freq
            for str2 in self._txt2.data:
                if f1 / factor < self._txt2[str2].freq < f1 * factor:
                    self._distWords[str1][str2] = float("inf")

            for view in self._views:
                    view.notify_progress(1 / len(self._txt1.data))

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
                dist = float(self._distWords[str1][str2])
                if dist == float("inf"):
                    # compute dtw
                    dist = self.dtw(warp, self.txt1[str1].rec, self.txt2[str2].rec)
                    self._distWords[str1][str2] = dist
                if dist < min_dist:
                    min_dist = dist
                    min_str = str2
        return min_dist, min_str

    def compute_dictionary(self, name, nb_process=1, process_number=0):
        """ It's high time to compute everything...
            Can be multiprocessed """
        self.mvc_check()
        with open(name, "w", encoding="utf-8") as f:
            count_word = 0
            for word in self._distWords:
                if count_word % nb_process == process_number:
                    dist, aligned_word = self.dist_word(word)
                    f.write("{} ; {} ; {} ; {} ; {} \n".format(dist, self._txt1[word].freq, self._txt2[aligned_word].freq, word, aligned_word))
                count_word += 1
                
                # notify the views
                for view in self._views:
                    view.notify_progress(1 / self._txt1.length)

    def save_dists(self, name):
        """Save the data into a txt file"""
        with open(name, "w", encoding="utf-8") as f:
            for word in self._distWords:
                f.write("{} | {}\n".format(word, ",".join(map(str_tuple, self._distWords[word].items()))))


# ---------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------- VIEW -------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


class View(VirtualView):
    def __init__(self):
        super().__init__()
        self._current_task = ""
        self._progress_bar = 0
        self._offset_bar = 0
        self._progress_window = None
        self._window = UiWindow()
        self._connect_ui()
        self._window.show()

    # -- GUI

    def _connect_ui(self):
        """
        Connect events
        """
        self._window.column1.columnInfo.open.clicked.connect(self.open_dialog1)
        self._window.column2.columnInfo.open.clicked.connect(self.open_dialog2)
        self._window.column1.align_disp.editor.cursorPositionChanged.connect(self.cursor_changed1)
        # TODO : reverse side of alignment
        # self._window.column2.align_disp.editor.cursorPositionChanged.connect(self.cursor_changed2)
        self._window.column1.align_disp.editor.verticalScrollBar().valueChanged.connect(self.scroll_highlight1)
        self._window.column2.align_disp.editor.verticalScrollBar().valueChanged.connect(self.scroll_highlight2)
        self._window.column1.columnInfo.search.clicked.connect(self.search_highlight1)
        self._window.column2.columnInfo.search.clicked.connect(self.search_highlight2)
    # -- Callback functions

    def open_dialog1(self):
        """ Open new file in column 1 """
        file_name = QtGui.QFileDialog.getOpenFileName()
        self.change_task("Computing recency vectors of text 1")
        txt = self.controller.process_raw_text(file_name, LEFT_TEXT)
        self.end_task()
        self._window.column1.align_disp.set_text(txt)

    def open_dialog2(self):
        """ Open new file in column 2 """
        file_name = QtGui.QFileDialog.getOpenFileName()
        self.change_task("Computing recency vectors of text 2")
        txt = self.controller.process_raw_text(file_name, RIGHT_TEXT)
        self.end_task()
        self._window.column2.align_disp.set_text(txt)

    def cursor_changed(self, column_side, bypass_selection=""):
        """ Process a clicked word on the text """

        column = None
        aligned_column = None
        if column_side == LEFT_TEXT:
            column = self._window.column1
            aligned_column = self._window.column2
        else:
            column = self._window.column2
            aligned_column = self._window.column1

        w = None
        if bypass_selection != "":
            # bypass the selection and process, used by search_highlight
            w = bypass_selection
        else:
            # else, just select the clicked word
            w = column.align_disp.editor.get_clicked_word()

        if w and w != "" and w != column.align_disp.currentWord:
            try:
                word, aligned_word, goldsmith_rslt = self.controller.process_word(w, column_side)

                # Highlighting
                column.align_disp.editor.clean_highlight(first_pos=column.align_disp.editor.first_highlighted_block,
                                                         last_pos=column.align_disp.editor.last_highlighted_block)
                column.align_disp.editor.refresh_highlight(word.str)
                aligned_column.align_disp.editor.clean_highlight(first_pos=aligned_column.align_disp.editor.first_highlighted_block,
                                                                 last_pos=aligned_column.align_disp.editor.last_highlighted_block)
                aligned_column.align_disp.editor.refresh_highlight(aligned_word.str, color=QtGui.QColor(255, 255, 100))

                align_rslt = "dist : <b>{}</b>".format(aligned_word.str)

                column.info_word.set_word(word.str)
                column.info_word.set_text(align_rslt)
                column.see_also.set_text(goldsmith_rslt)
                column.align_disp.currentWord = word.str
                column.align_disp.sidebar.currentVect = word.pos
                column.align_disp.sidebar.draw_vector()

                aligned_column.info_word.set_word(aligned_word.str)
                aligned_column.info_word.set_text("See also")
                # TODO : goldsmith on the second column, maybe paste the code or add eternal function
                aligned_column.see_also.set_text("Goldsmith algorithm results")
                aligned_column.align_disp.currentWord = aligned_word.str
                aligned_column.align_disp.sidebar.currentVect = aligned_word.pos
                aligned_column.align_disp.sidebar.draw_vector()

            except WordNotInDatabase:
                column.align_disp.editor.clean_highlight(first_pos=column.align_disp.editor.first_highlighted_block,
                                                         last_pos=column.align_disp.editor.last_highlighted_block)
                aligned_column.align_disp.editor.clean_highlight(first_pos=aligned_column.align_disp.editor.first_highlighted_block,
                                                                 last_pos=aligned_column.align_disp.editor.last_highlighted_block)
                column.info_word.set_word("Not found")
                column.info_word.set_text("Alignment results")
                column.see_also.set_text("Goldsmith algorithm results")
                column.align_disp.currentWord = None
                column.align_disp.sidebar.currentVect = [0, 1]
                column.align_disp.sidebar.draw_vector()

                aligned_column.info_word.set_word("Not found")
                aligned_column.info_word.set_text("See also")
                aligned_column.see_also.set_text("Goldsmith algorithm results")
                aligned_column.align_disp.currentWord = None
                aligned_column.align_disp.sidebar.currentVect = [0, 1]
                aligned_column.align_disp.sidebar.draw_vector()

            except DataNotProcessed:
                column.align_disp.editor.clean_highlight(first_pos=column.align_disp.editor.first_highlighted_block,
                                                         last_pos=column.align_disp.editor.last_highlighted_block)
                aligned_column.align_disp.editor.clean_highlight(first_pos=aligned_column.align_disp.editor.first_highlighted_block,
                                                                 last_pos=aligned_column.align_disp.editor.last_highlighted_block)

    def cursor_changed1(self):
        self.cursor_changed(LEFT_TEXT)

    def cursor_changed2(self):
        self.cursor_changed(RIGHT_TEXT)

    def scroll_highlight1(self):
        """ use the fast highlight algorithm developed in widget.py """
        self._window.column1.align_disp.editor.scroll_highlight(self._window.column1.align_disp.currentWord)

    def scroll_highlight2(self):
        """ use the fast highlight algorithm developed in widget.py """
        self._window.column2.align_disp.editor.scroll_highlight(self._window.column2.align_disp.currentWord)

    def search_highlight1(self):
        word = self._window.column1.columnInfo.searchLine.text().lower()
        self.cursor_changed(LEFT_TEXT, bypass_selection=word)

    def search_highlight2(self):
        word = self._window.column2.columnInfo.searchLine.text().lower()
        self.cursor_changed(RIGHT_TEXT, bypass_selection=word)

    # -- progress bar

    def change_task(self, ref):
        """Change the current task and the corresponding progress bar"""
        self._current_task = ref
        self._progress_bar = 0
        self._offset_bar = 0
        # display a progress bar
        self._progress_window = LoadingWindow(self._current_task)

    def end_task(self):
        if self._progress_window:
            self._progress_window.close()

    def notify_progress(self, ratio):
        """Update the current progress bar if one associated with the task"""
        self._progress_bar += ratio
        while self._progress_bar > self._offset_bar:
            self._offset_bar += 0.01
            self._progress_window.progress(100 * self._progress_bar)
            # print(100 * self._progress_bar)


# ---------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------- CONTROLLER ----------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------


class Controller(VirtualController):
    def __init__(self):
        super().__init__()
        self.opened_txt = {LEFT_TEXT: False, RIGHT_TEXT: False}
        self.can_align = False

    def process_raw_text(self, file_name, column_side):
        """ Open a file and process the text """
        self.mvc_check()

        model_txt = None
        if column_side == LEFT_TEXT:
            model_txt = self.model.txt1
        elif column_side == RIGHT_TEXT:
            model_txt = self.model.txt2

        model_txt.open_raw(file_name)
        model_txt.process_raw()
        self.opened_txt[column_side] = True
        self.can_align = self.opened_txt[LEFT_TEXT] and self.opened_txt[RIGHT_TEXT]

        # Goldsmith
        model_txt.make_trie(column_side)
        model_txt.apply_goldsmith(1.1, 20, column_side)

        # Associate word for alignment if both text were opened
        if self.can_align:
            for view in self.views:
                view.end_task()
                view.change_task("Associating words")
            self.model.associate_words(1.5)
            for view in self.views:
                view.end_task()

        # TODO : coherent saving to database using model.save_data

        return model_txt.str

    def process_word(self, str_word, column_side):
        """ Return the result of the model for a given string from the text str_word.
            Compute if the word doesn't exist. """
        self.mvc_check()

        if self.can_align:
            processed_txt = None
            translated_txt = None
            if column_side == LEFT_TEXT:
                processed_txt = self.model.txt1
                translated_txt = self.model.txt2
            elif column_side == RIGHT_TEXT:
                processed_txt = self.model.txt2
                translated_txt = self.model.txt1

            word_info = processed_txt.gold.build_word_info(str_word)
            if str_word in processed_txt.data:
                # the selected word is a regular word, just display information
                align_dist, align_str = self.model.dist_word(str_word)
                return processed_txt[str_word], translated_txt[align_str], word_info
            else:
                # TODO : a new entry, compute everything, but for now, raise an error
                raise WordNotInDatabase
        raise DataNotProcessed

