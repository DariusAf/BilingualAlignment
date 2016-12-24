# -*- coding: utf-8 -*-

import sys
from widgets import *

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
    def __init__(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(500, 480)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setMargin(0)

        # bouton Browse
        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)

        self.verticalLayout.addItem(QtGui.QSpacerItem(500, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))

        # éditeur de texte
        self.alDisplay = AlignmentDisplay()
        self.alDisplay.setObjectName(_fromUtf8("AlignmentDisplay"))
        self.verticalLayout.addWidget(self.alDisplay)

        self.verticalLayout.addItem(QtGui.QSpacerItem(500, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum))

        self.horizontalLayout.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.pushButton.setText(_translate("MainWindow", "Browse", None))
        self.pushButton.clicked.connect(self.browse)
        self.alDisplay.editor.setReadOnly(True)

    def browse(self):
        file_name = QtGui.QFileDialog.getOpenFileName()
        reader = open(file_name, 'r', encoding="utf-8").read()
        self.alDisplay.set_text(reader)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()  # <-- Instantiate QMainWindow object.
    ui = Ui_MainWindow(MainWindow)

    MainWindow.show()

    sys.exit(app.exec_())
