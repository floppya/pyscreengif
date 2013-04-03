#!/usr/bin/env python

from PyQt4 import QtGui
from screengif.mainwindow import ScreengifMainWindow


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = ScreengifMainWindow()
    app.setActiveWindow(window)
    window.show()
    app.exec_()
