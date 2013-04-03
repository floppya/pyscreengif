from PyQt4 import QtCore, QtGui


class QPixmapWidget(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(QPixmapWidget, self).__init__(*args, **kwargs)
        self.pixmap = None
        self.outputSize = QtCore.QSize(64, 64)

    def updatePixmap(self, pixmap):
        self.pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        super(QPixmapWidget, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        if self.pixmap:
            pixmap = self.pixmap.scaled(
                self.size(),
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.SmoothTransformation)
            painter.drawPixmap(0, 0, pixmap)
        else:
            pass
        painter.end()

    def sizeHint(self):
        return self.outputSize

