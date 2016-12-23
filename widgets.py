# -*- coding: utf-8 -*-

import re

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt


class OccurrenceSideBar(QtGui.QFrame):
    """
    A widget that display the occurence vector of a word.
    Can be clicked to scroll quickly to the iteration
    """

    def __init__(self, editor):
        super().__init__()

        # private
        self.editor = editor
        self.currentVect = [0, 1]

        # style
        self.setFixedWidth(20)
        self.setStyleSheet("QFrame {background-color:#e7dede; margin:0;}"
                           "QGraphicsView {border: none; margin:0; padding:0;}")

        # graphics container
        self.gView = QtGui.QGraphicsView(self)
        self.scene = QtGui.QGraphicsScene(self)
        self.scene.setSceneRect(QtCore.QRectF())
        self.gView.setScene(self.scene)

        # some pens
        self.cursorPen = QtGui.QPen(QtGui.QColor(255, 239, 115))
        self.cursorPen.setWidth(1)
        self.defaultPen = QtGui.QPen(QtGui.QColor(220, 75, 92))
        self.defaultPen.setWidth(2)
        self.matchPen = QtGui.QPen(QtGui.QColor(255, 255, 0))
        self.matchPen.setWidth(2)

    def resize_content(self, h):
        """
        Adjust the size of QGraphics-Scene/View when the window is resized
        """
        self.gView.setFixedSize(20, h)
        self.gView.fitInView(0, 0, 20, h, Qt.KeepAspectRatio)
        self.scene.setSceneRect(0, 0, 20, h)

    def draw_vector(self):
        """
        Draw lines corresponding to self.currentVect
        """
        h = self.frameRect().height()
        self.resize_content(h)
        self.scene.clear()
        for it in self.currentVect:
            p1 = self.gView.mapToScene(QtCore.QPoint(0, h * it))
            p2 = self.gView.mapToScene(QtCore.QPoint(20, h * it))
            l = QtGui.QGraphicsLineItem(p1.x(), p1.y(), p2.x(), p2.y())
            l.setPen(self.defaultPen)
            self.scene.addItem(l)
        self.gView.update()

    def mousePressEvent(self, mouse_event):
        """
        Scrolljump to the selected iteration.
        If the click is far from a line, just scroll to the clicked area.
        """
        h_editor = self.editor.document().size().height()
        clicked_freq = float(mouse_event.pos().y()) / self.frameRect().height()
        # find closest value
        i_mindist = 0
        mindist = 1
        for k in range(len(self.currentVect)):
            if abs(self.currentVect[k] - clicked_freq) < mindist:
                mindist = abs(self.currentVect[k] - clicked_freq)
                i_mindist = k
        # if 15px-close of a indicator, adjust click
        if self.frameRect().height() * mindist < 15:
            self.editor.verticalScrollBar().setValue(self.currentVect[i_mindist] * h_editor)
        else:
            self.editor.verticalScrollBar().setValue(clicked_freq * h_editor)


class TextEditor(QtGui.QPlainTextEdit):
    """
    The text editor where the text is displayed
    """

    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            "TextEditor {font-size:13px;border:none;border-left:1px solid #d6c2c5;padding-top:0;margin-top:0;}")

    @staticmethod
    def is_word(w):
        """
        Check if w only contains a full word
        """
        if w != "":
            match = re.search("[\w\dÀÁÂÃÄÅàáâãäåÒÓÔÕÖØòóôõöøÈÉÊËèéêëÇçÌÍÎÏìíîïÙÚÛÜùúûüÿÑñ]+", w)
            if match:
                if match.group(0) == w:
                    return True
        return False

    def get_clicked_word(self):
        """
        Enlarge the selection to get the word under cursor
        """
        cursor = self.textCursor()

        # go left until special caracter
        go_on = True
        n_left = 0
        while go_on:
            a = cursor.movePosition(QtGui.QTextCursor.Left, mode=QtGui.QTextCursor.KeepAnchor)
            b = cursor.selectedText()
            go_on = a and self.is_word(str(b))
            n_left += 1

        # come back home
        cursor.movePosition(QtGui.QTextCursor.Left, mode=QtGui.QTextCursor.MoveAnchor)
        if cursor.position() > 0:
            cursor.movePosition(QtGui.QTextCursor.Right, mode=QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Right, mode=QtGui.QTextCursor.KeepAnchor, n=n_left - 1)

        # go right until special caracter
        go_on = True
        while go_on:
            a = cursor.movePosition(QtGui.QTextCursor.Right, mode=QtGui.QTextCursor.KeepAnchor)
            b = cursor.selectedText()
            go_on = a and self.is_word(str(b))
        cursor.movePosition(QtGui.QTextCursor.Left, mode=QtGui.QTextCursor.KeepAnchor)

        # output clicked word
        return cursor.selectedText().lower()


class AlignmentDisplay(QtGui.QWidget):
    """
    A super-widget that combines TextEditor and the matching OccurenceSideBar
    """

    def __init__(self):
        super().__init__()

        # Private
        self.currentWord = ""

        # Sub-widgets
        self.editor = TextEditor()
        self.sidebar = OccurrenceSideBar(self.editor)
        self.setStyleSheet("AlignmentDisplay {border:1px solid #000}")

        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.sidebar)
        hbox.addWidget(self.editor)

        self.setLayout(hbox)

        # Event
        self.editor.cursorPositionChanged.connect(self.cursor_changed)

    def set_text(self, txt):
        self.editor.setPlainText(txt)

    def cursor_changed(self):
        w = self.editor.get_clicked_word()
        if w and w != "" and w != self.currentWord:
            self.currentWord = w

            # TODO : call controler
            print(self.currentWord)
            self.sidebar.draw_vector()

    def resizeEvent(self, resize_event):
        self.sidebar.draw_vector()
