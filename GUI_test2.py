# -*- coding: utf-8 -*-

# a = ui.textEdit.lineNumber

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.QtGui import QFileDialog

import re

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
    def __init__(self,editor):
        super().__init__()
        
        # private
        self.editor = editor
        self.currentVect = [0,0.1,0.3,0.6,0.8,0.9,1] # TODO : adapt
        
        # style
        self.setFixedWidth(20)
        self.setStyleSheet("QFrame {background-color:#e7dede; margin:0;}"
        "QGraphicsView {border: none; margin:0; padding:0;}")
        
        # graphics container
        self.gView = QtGui.QGraphicsView(self)
        self.scene = QtGui.QGraphicsScene(self)
        self.scene.setSceneRect(QtCore.QRectF())
        self.gView.setScene(self.scene)
        
        # pens
        self.cursorPen = QtGui.QPen(QtGui.QColor(255,239,115))
        self.cursorPen.setWidth(1)
        self.defaultPen = QtGui.QPen(QtGui.QColor(220,75,92))
        self.defaultPen.setWidth(2)
        self.matchPen = QtGui.QPen(QtGui.QColor(50,150,255))
        self.matchPen.setWidth(2)

    def resizeContent(self,h):
        self.gView.setFixedSize(20,h)
        self.gView.fitInView(0,0,20,h,Qt.KeepAspectRatio);
        self.scene.setSceneRect(0,0,20,h)
    
    def drawVector(self):
        h = self.frameRect().height()
        self.resizeContent(h)
        self.scene.clear()
        for it in self.currentVect:
            p1 = self.gView.mapToScene(QtCore.QPoint(0,h*it))
            p2 = self.gView.mapToScene(QtCore.QPoint(20,h*it))
            l = QtGui.QGraphicsLineItem(p1.x(),p1.y(),p2.x(),p2.y())
            l.setPen(self.defaultPen)
            self.scene.addItem(l)
        self.gView.update()
    
    def mousePressEvent(self,QMouseEvent):
        hEditor = self.editor.document().size().height()
        clickedFreq = float(QMouseEvent.pos().y())/self.frameRect().height()
        # find closest value
        imin = 0
        min = 1
        for k in range(len(self.currentVect)):
            if abs(self.currentVect[k]-clickedFreq)<min:
                min = abs(self.currentVect[k]-clickedFreq)
                imin = k
        # if close enough of a indicator, adjust click
        if min<0.02:
            self.editor.verticalScrollBar().setValue(self.currentVect[imin]*hEditor)
        else:
            self.editor.verticalScrollBar().setValue(clickedFreq*hEditor)


class CodeEditor(QtGui.QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("CodeEditor {font-size:13px;border:none;border-left:1px solid #d6c2c5;padding-top:0;margin-top:0;}")
        
        # TODO : pour le debug, à supprimer
        reader = open("livres/HP1_en.txt",'r',encoding="utf-8").read()
        self.setPlainText(reader)

    def isAcceptable(self,w,side=0):
        if w != "":
            match = re.search("[\w\dÀÁÂÃÄÅàáâãäåÒÓÔÕÖØòóôõöøÈÉÊËèéêëÇçÌÍÎÏìíîïÙÚÛÜùúûüÿÑñ]+",w)
            if match:
                if match.group(0) == w:
                    return True
        return False
    
    def getClickedWord(self):
        cursor = self.textCursor()
        
        # go left until special caracter
        goOn = True
        nLeft = 0
        while goOn:
            a = cursor.movePosition(QtGui.QTextCursor.Left,mode=QtGui.QTextCursor.KeepAnchor)
            b = cursor.selectedText()
            goOn = a and self.isAcceptable(str(b))
            nLeft += 1
        
        # TODO : gérer le cas du premier et dernier mot du texte avec un if
        # come back home
        cursor.movePosition(QtGui.QTextCursor.Left,mode=QtGui.QTextCursor.MoveAnchor)
        cursor.movePosition(QtGui.QTextCursor.Right,mode=QtGui.QTextCursor.MoveAnchor)
        cursor.movePosition(QtGui.QTextCursor.Right,mode=QtGui.QTextCursor.KeepAnchor,n=nLeft-1)
        
        # go right until special caracter
        goOn = True
        while goOn:
            a = cursor.movePosition(QtGui.QTextCursor.Right,mode=QtGui.QTextCursor.KeepAnchor)
            b = cursor.selectedText()
            goOn = a and self.isAcceptable(str(b),side=-1)
        cursor.movePosition(QtGui.QTextCursor.Left,mode=QtGui.QTextCursor.KeepAnchor)
        
        # output clicked word
        return cursor.selectedText().lower()
    

class LNTextEdit(QtGui.QWidget):
    def __init__(self):
        super().__init__()
        
        # Private
        self.currentWord = ""
        
        # GUI
        self.edit = CodeEditor()
        self.lineNumber = LineNumberArea(self.edit)
        self.setStyleSheet("LNTextEdit {border:1px solid #000}")
        
        hbox = QtGui.QHBoxLayout(self)
        hbox.setSpacing(0)
        hbox.setMargin(0)
        hbox.addWidget(self.lineNumber)
        hbox.addWidget(self.edit)
        
        self.setLayout(hbox)
        
        # Event
        self.edit.cursorPositionChanged.connect(self.cursorChanged)

    def setText(self,txt):
        self.edit.setPlainText(txt)
    
    def cursorChanged(self):
        w = self.edit.getClickedWord()
        if w and w != "" and w != self.currentWord:
            self.currentWord = w
            
            # TODO : get Vector through model
            print(self.currentWord)
            self.lineNumber.drawVector()
    
    def resizeEvent(self,resizeEvent):
        self.lineNumber.drawVector()
    
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(500, 480)
        
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
        
        # bouton Browse
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)
        self.verticalLayout.addItem(QtGui.QSpacerItem(500,5,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum))
        
        # éditeur de texte
        self.textEdit = LNTextEdit()
        self.textEdit.setObjectName(_fromUtf8("LNTextEdit"))
        self.verticalLayout.addWidget(self.textEdit)
        self.verticalLayout.addItem(QtGui.QSpacerItem(500,5,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Minimum))

        self.horizontalLayout_2.addLayout(self.verticalLayout)
        
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.pushButton.setText(_translate("MainWindow", "Browse", None))
        self.pushButton.clicked.connect(self.Browse)
        self.textEdit.edit.setReadOnly(True)

    def Browse(self):
        file_name = QFileDialog.getOpenFileName()
        reader = open(file_name,'r',encoding="utf-8").read()
        self.textEdit.setText(reader)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow() # <-- Instantiate QMainWindow object.
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    MainWindow.show()

    sys.exit(app.exec_())