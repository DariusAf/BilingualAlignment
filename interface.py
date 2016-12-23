# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fen.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!
import sys
import re

from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QTextFormat

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(546, 465)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.textEdit1 = QtGui.QTextEdit(self.centralwidget)
        self.textEdit1.setObjectName(_fromUtf8("textEdit_2"))
        self.gridLayout.addWidget(self.textEdit1, 3, 1, 1, 1)
        self.textEdit2 = QtGui.QTextEdit(self.centralwidget)
        self.textEdit2.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout.addWidget(self.textEdit2, 3, 2, 1, 1)
        self.lineEdit = QtGui.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
        self.pushButton_3 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(_fromUtf8("pushButton_3"))
        self.gridLayout.addWidget(self.pushButton_3, 0, 1, 1, 1)
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.gridLayout.addWidget(self.pushButton_2, 0, 2, 1, 1)
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.gridLayout.addWidget(self.pushButton, 1, 2, 1, 1)
        self.pushButton_4 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_4.setObjectName(_fromUtf8("pushButton_4"))
        self.gridLayout.addWidget(self.pushButton_4, 2, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 3, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 546, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionNew = QtGui.QAction(MainWindow)
        self.actionNew.setObjectName(_fromUtf8("actionNew"))
        self.actionOpen = QtGui.QAction(MainWindow)
        self.actionOpen.setObjectName(_fromUtf8("actionOpen"))
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        self.currentWord = "0"
        self.currentLine = 0
        self.textEdit1.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.lastMatch = None


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.pushButton_3.setText(_translate("MainWindow", "Text1", None))
        self.pushButton_3.clicked.connect(self.Browse1)
        self.pushButton_2.setText(_translate("MainWindow", "Text2", None))
        self.pushButton_2.clicked.connect(self.Browse2)
        self.lineEdit.setPlaceholderText("search")
        self.pushButton.setText(_translate("MainWindow", "Search", None))

        self.pushButton.clicked.connect(self.find)
        self.pushButton_4.setText(_translate("MainWindow", "Retour", None))
        self.pushButton_4.clicked.connect(self.Select)
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.actionNew.setText(_translate("MainWindow", "New", None))
        self.actionOpen.setText(_translate("MainWindow", "Open", None))

    def find(self):
        self.Search()
        # Grab the  text
        text = self.textEdit1.toPlainText().lower()


        #  the text to find
        query = self.lineEdit.text().lower()

        # If the 'Whole Words' checkbox is checked, we need to append
        # and prepend a non-alphanumeric character
        #if self.wholeWords.isChecked():
        query = r'\W' + query + r'\W'

        # By default regexes are case sensitive but usually a search isn't
        # case sensitive by default, so we need to switch this around here
        flags = 0 #if self.caseSens.isChecked() else re.I

        # Compile the pattern
        pattern = re.compile(query,flags)

        # If the last match was successful, start at position after the last
        # match's start, else at 0
        start = self.lastMatch.start() + 1 if self.lastMatch else 0



        # The actual search
        self.lastMatch = pattern.search(text,start)

        if self.lastMatch:

            start = self.lastMatch.start()
            end = self.lastMatch.end()

            # If 'Whole words' is checked, the selection would include the two
            # non-alphanumeric characters we included in the search, which need
            # to be removed before marking them.
            #if self.wholeWords.isChecked():
            start += 1
            end -= 1

            self.moveCursor(start,end)

        else:

            # We set the cursor to the end if the search was unsuccessful
            self.textEdit1.moveCursor(QtGui.QTextCursor.End)


    def moveCursor(self,start,end):

        format = QtGui.QTextCharFormat()
        format.setBackground((QtGui.QBrush(QtGui.QColor("yellow"))))
        # We retrieve the QTextCursor object from the parent's QTextEdit
        cursor = self.textEdit1.textCursor()

        # Then we set the position to the beginning of the last match
        cursor.setPosition(start)
        if not (cursor.isNull()):
            cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor, end - start)

            cursor.mergeCharFormat(format)

        # Next we move the Cursor by over the match and pass the KeepAnchor parameter
        # which will make the cursor select the the match's text

        # And finally we set this new cursor as the parent's
        self.textEdit1.setTextCursor(cursor)

    def Browse1(self):
        file_name = QFileDialog.getOpenFileName()
        reader = open(file_name, 'r', encoding="utf-8").read()
        self.textEdit1.setText(reader)
        self.textEdit1.setReadOnly(True)

    def Browse2(self):
        file_name = QFileDialog.getOpenFileName()
        reader = open(file_name, 'r', encoding="utf-8").read()
        self.textEdit2.setText(reader)
        self.textEdit2.setReadOnly(True)

    def Select(self):
        """cursor = self.textEdit1.textCursor()
        textSelected = cursor.selectedText()
        s = textSelected.lower()
        self.textEdit1.append(s)
        print(s)
        self.highlight(self.textEdit1,s)"""
        self.textEdit1.undo()


    def highlight(self, textEdit, text):
        cursor = textEdit.textCursor()
        format = QtGui.QTextCharFormat()
        format.setBackground((QtGui.QBrush(QtGui.QColor("yellow"))))

        pattern = text
        regex = QtCore.QRegExp(pattern)
        # Process the displayed document
        pos = 0
        index = regex.indexIn(textEdit.toPlainText().lower(), pos)
        cursor.beginEditBlock()
        while (index != -1):
            # Select the matched text and apply the desired format

            cursor.setPosition(index)
            if not (cursor.isNull()):
                cursor.movePosition(QtGui.QTextCursor.WordRight, QtGui.QTextCursor.KeepAnchor)

                cursor.mergeCharFormat(format)
                # Move to the next match
                pos = index + regex.matchedLength()
                index = regex.indexIn(textEdit.toPlainText().lower(), pos)
        cursor.endEditBlock()

    def Search(self):
        self.textEdit1.undo()
        self.lineEdit.selectAll()
        text = self.lineEdit.text().lower()
        self.highlight(self.textEdit1,text)

    def isAcceptable(self, w, side=0):
        if w != "":
            l = [" ", ",", ";", ":", "$", "%", "!", "?", "'", "."]
            for sep in l:
                if w[side] == sep:
                    return False
        return True

    def highlightCurrentLine(self):
        hi_selection = QtGui.QTextEdit.ExtraSelection()
        hi_selection.format.setBackground(QtGui.QBrush(QtGui.QColor("red")))
        # hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        hi_selection.cursor = self.textEdit1.textCursor()
        self.currentLine = hi_selection.cursor.blockNumber()
        hi_selection.cursor.clearSelection()

        cursor = self.textEdit1.textCursor()
        goOn = True
        nLeft = 0
        while goOn:
            a = cursor.movePosition(QtGui.QTextCursor.Left, mode=QtGui.QTextCursor.KeepAnchor)
            b = cursor.selectedText()
            goOn = a and self.isAcceptable(str(b))
            nLeft += 1
        cursor.movePosition(QtGui.QTextCursor.Left, mode=QtGui.QTextCursor.MoveAnchor)
        cursor.movePosition(QtGui.QTextCursor.Right, mode=QtGui.QTextCursor.MoveAnchor)
        cursor.movePosition(QtGui.QTextCursor.Right, mode=QtGui.QTextCursor.KeepAnchor, n=nLeft - 1)

        goOn = True
        while goOn:
            a = cursor.movePosition(QtGui.QTextCursor.Right, mode=QtGui.QTextCursor.KeepAnchor)
            b = cursor.selectedText()
            goOn = a and self.isAcceptable(str(b), side=-1)
        cursor.movePosition(QtGui.QTextCursor.Left, mode=QtGui.QTextCursor.KeepAnchor)

        word = cursor.selectedText()
        # self.setTextCursor(cursor)

        if self.currentWord != word and word != "":
            self.currentWord = word
            print(word)



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()  # <-- Instantiate QMainWindow object.
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    sys.exit(app.exec_())