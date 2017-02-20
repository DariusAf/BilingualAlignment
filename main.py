# -*- coding:utf-8 -*-
import sys
import time
from mvc import *

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    # Initialize
    model = Model()
    view = View()
    controller = Controller()

    # Link
    link_mvc(model, [view], controller)
    model.mvc_link_texts()

    sys.exit(app.exec_())
