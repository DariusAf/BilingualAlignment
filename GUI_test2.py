# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'test1.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.QtGui import QFileDialog

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

class LineNumberArea(QtGui.QFrame):
    # inspired by http://doc.qt.io/qt-5/qtwidgets-widgets-codeeditor-example.html
    
    def __init__(self,editor):
        super().__init__()
        self.codeEditor = editor
        self.setFixedWidth(40)
        self.setStyleSheet("LineNumberArea {background-color:#F3E0CC; margin:0; padding-top:5px;}"
                           "QLabel {font-size:13px;padding:0px 5px;color:#866}")
        
        self.text = QtGui.QLabel("")
        self.text.setMinimumHeight(1)
        vbox = QtGui.QVBoxLayout(self)
        vbox.setSpacing(0)
        vbox.setMargin(0)
        vbox.addWidget(self.text)
        vbox.addStretch(1)
        self.setLayout(vbox)
                
        self.updateNumbers(0,0)
    
    def updateNumbers(self,mini,offset=22,currentLine=0):
        strT = ""
        if mini>1:
            self.setStyleSheet("QFrame {background-color:#F3E0CC; margin:0; padding-top:1px;}"
                               "QLabel {font-size:13px;padding:0px 4px;color:#866}")
        else:
            self.setStyleSheet("QFrame {background-color:#F3E0CC; margin:0; padding-top:5px;}"
                               "QLabel {font-size:13px;padding:0px 4px;color:#866}")
        for i in range(mini,mini+offset+1):
            if i == currentLine+1:
                strT += "<b>"+str(i)+"</b><br>"
            else:
                strT += str(i)+"<br>"
        self.text.setText(strT)

        
class CodeEditor(QtGui.QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("CodeEditor {font-size:13px;border:none;border-left:5px solid #DCC;padding-top:0;margin-top:0;}")
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.currentLine = 0
        self.setLineWrapMode(0)
        self.currentWord = "a"
    
    def lineNumberAreaWidth(self):
        digits = 2
        maxi = max(1,self.blockCount())
        while maxi >= 10:
            maxi /= 10
            digits += 1
        return 20 + self.fontMetrics().width('9')*digits
    
    def blockNumberVisible(self):
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()

        while block.isValid():
            blockNumber += 1
            if block.isVisible():
                return int(blockNumber)
            block.next()
        return 0
    
    def highlightCurrentLine(self):
        hi_selection = QtGui.QTextEdit.ExtraSelection()
        #hi_selection.format.setBackground(QtGui.QColor(255, 255, 0))
        #hi_selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        hi_selection.cursor = self.textCursor()
        self.currentLine = hi_selection.cursor.blockNumber()
        hi_selection.cursor.clearSelection()
    
        cursor = self.textCursor()
        self.setTextCursor(cursor)
        word = cursor.selectedText()
        if self.currentWord != word and word != "" :
            self.currentWord = word
            print(word)
    

class LNTextEdit(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        
        self.edit = CodeEditor()
        self.lineNumber = LineNumberArea(self.edit)
        self.setStyleSheet("LNTextEdit {border:1px solid #000}")
        
        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.lineNumber)
        hbox.addWidget(self.edit)
        
        self.setLayout(hbox)
        
        self.updateLineNumberAreaWidth()
        self.edit.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.edit.updateRequest.connect(self.updateLineNumberArea)
    
    def updateLineNumberAreaWidth(self):
        self.lineNumber.setFixedWidth(self.edit.lineNumberAreaWidth())
    
    def updateLineNumberArea(self,event):
        self.lineNumber.updateNumbers(self.edit.blockNumberVisible(),offset=int(self.edit.height()/12),currentLine=self.edit.currentLine)
    
    def setText(self,txt):
        self.edit.setPlainText(txt)
    
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(480, 408)
        #MainWindow.setMaximumHeight(900)
        
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setMargin(0)
        
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)
        
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        
        self.pushButton_2 = QtGui.QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.verticalLayout.addWidget(self.pushButton_2)
        self.verticalLayout.addItem(QtGui.QSpacerItem(10,5,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum))
        
        # self.plainTextEdit = QtGui.QPlainTextEdit(self.centralwidget)
        # self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        # self.verticalLayout.addWidget(self.plainTextEdit)
        
        self.plainTextEdit = LNTextEdit()
        self.plainTextEdit.setObjectName(_fromUtf8("LNTextEdit"))
        self.verticalLayout.addWidget(self.plainTextEdit)
        
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 480, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.pushButton.setText(_translate("MainWindow", "Browse", None))
        self.pushButton.clicked.connect(self.Browse)
        self.pushButton_2.setText(_translate("MainWindow", "Select", None))
        self.pushButton_2.clicked.connect(self.Select)
        self.plainTextEdit.edit.setReadOnly(True)

    def Browse(self):
        file_name = QFileDialog.getOpenFileName()
        reader = open(file_name,'r').read()
        self.plainTextEdit.setText(reader)

    def Select(self):
        cursor = self.plainTextEdit.textCursor()
        textSelected = cursor.selectedText()
        s = textSelected.lower()
        #self.plainTextEdit.appendPlainText(s)
        print(s)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow() # <-- Instantiate QMainWindow object.
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    sys.exit(app.exec_())