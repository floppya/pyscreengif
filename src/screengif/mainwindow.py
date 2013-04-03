import os
from PyQt4 import QtCore, QtGui
from .ui.ui_recording import Ui_RecordingDialog


def rectFromPoints(pa, pb):
    dp = pb - pa
    topLeft = QtCore.QPoint()
    bottomRight = QtCore.QPoint()
    topLeft.setX(min(pa.x(), pb.x()))
    topLeft.setY(min(pa.y(), pb.y()))
    bottomRight.setX(max(pa.x(), pb.x()))
    bottomRight.setY(max(pa.y(), pb.y()))
    return QtCore.QRect(topLeft, bottomRight)


class ScreengifMainWindow(QtGui.QMainWindow):
    """
    The main window is basically a big mask for the desktop.
    All of the controls are in RecordingDialog.
    """
    selectionChanged = QtCore.pyqtSignal(QtCore.QRect)

    def __init__(self, *args, **kwargs):
        super(ScreengifMainWindow, self).__init__(*args, **kwargs)
        self.setCursor(QtCore.Qt.CrossCursor)
        self.setWindowOpacity(0.4)
        self.showFullScreen()
        self.selectedArea = QtCore.QRect()
        self.pointA = self.pointB = self.selectedRect = None
        recording = self.recordingDialog = RecordingDialog(self)
        recording.finished.connect(self.close)
        recording.show()
        self.selectionChanged.connect(recording.updateSelection)

    def mousePressEvent(self, event):
        pos = event.pos()
        self.pointA = QtCore.QPoint(event.pos())
        self.pointB = QtCore.QPoint(event.pos())
        self._updateSelection()

    def mouseMoveEvent(self, event):
        pos = event.pos()
        self.pointB.setX(pos.x())
        self.pointB.setY(pos.y())
        self._updateSelection()

    def mouseReleaseEvent(self, event):
        pos = event.pos()
        self.pointB.setX(pos.x())
        self.pointB.setY(pos.y())
        self.selectionChanged.emit(self.selectedRect)

    def _updateSelection(self):
        self.selectedRect = rectFromPoints(self.pointA, self.pointB)
        r = QtGui.QRegion(self.geometry())
        self.selectedRegion = r.subtracted(QtGui.QRegion(self.selectedRect))
        self.setMask(self.selectedRegion)
        self.update()
    
    def paintEvent(self, event):
        super(ScreengifMainWindow, self).paintEvent(event)
        rect = self.selectedRect
        if rect:
            painter = QtGui.QPainter(self)
            brush = QtGui.QBrush(QtCore.Qt.transparent)
            painter.fillRect(QtCore.QRectF(rect), brush)
            painter.drawRect(QtCore.QRectF(rect))
            painter.end()


class RecordingDialog(QtGui.QDialog, Ui_RecordingDialog):
    pixmapAdded = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, *args, **kwargs):
        super(RecordingDialog, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.recordTimer = QtCore.QTimer(self)
        self.playbackTimer = QtCore.QTimer(self)
        self._imageOutputBuffer = []
        self.selectedRect = None
        self.setWindowTitle('Screengif')
        self._wire()
        self.playbackFrame = self.frame = 0
        self.cursorStack = []
        self.updatePreviewSize()

    def _wire(self):
        self.butRecord.toggled.connect(self.onRecordToggled)
        self.butSaveSequence.clicked.connect(self.onSaveSequence)
        self.butSaveGif.clicked.connect(self.onSaveGif)
        self.recordTimer.timeout.connect(self.onRecordTick)
        self.playbackTimer.timeout.connect(self.onPlaybackTick)
        
        self.pixmapAdded.connect(self.previewImage.updatePixmap)
        self.butPlay.toggled.connect(self.onPlaybackToggled)
        self.playbackSlider.valueChanged.connect(self.onPlaybackSliderChanged)
        self.spinOutWidth.valueChanged.connect(self.onOutWidthChanged)
        self.spinOutHeight.valueChanged.connect(self.onOutHeightChanged)

    def onRecordToggled(self, isRecording):
        if isRecording:
            if self.selectedRect:
                self.butRecord.setText('Stop recording')
                self._startRecording()
            else:
                self.butRecord.setChecked(False)
        else:
            self.butRecord.setText('Record')
            numFrames = len(self._imageOutputBuffer)
            self.playbackSlider.setMaximum(numFrames)
            self.playbackSlider.setValue(min(numFrames, self.playbackFrame))
            self.playbackSlider.setMinimum(min(numFrames, 1))
            self._stopRecording()

    def _startRecording(self):
        self.frame = 0
        self._imageOutputBuffer = []
        fps = int(self.spinFps.value())
        self.recordTimer.start(1000/fps)
        
    def _stopRecording(self):
        self.recordTimer.stop()
    
    def onRecordTick(self):
        rect = self.selectedRect
        image = QtGui.QPixmap.grabWindow(
            QtGui.QApplication.desktop().winId(),
            rect.x(), rect.y(), rect.width(), rect.height())
        self._imageOutputBuffer.append(image)
        self.pixmapAdded.emit(image)
        self.frame += 1        

    def onSaveSequence(self):
        self.pushCursor(QtCore.Qt.BusyCursor)
        if not self._imageOutputBuffer:
            return
        path = QtGui.QFileDialog.getExistingDirectory(
            self, 'Choose target')
        if not path:
            return
        outputPath = unicode(path)

        width = int(self.spinOutWidth.value())
        height = int(self.spinOutHeight.value())        
        for i, frame in enumerate(self._imageOutputBuffer):
            filename = '%05d.png' % i
            full_filename = os.path.join(outputPath, filename)
            frame = frame.scaled(
                QtCore.QSize(width, height),
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.SmoothTransformation)
            frame.save(full_filename)
        self.popCursor()

    def onSaveGif(self):
        self.pushCursor(QtCore.Qt.BusyCursor)

        from PIL import Image
        from images2gif import writeGif
        import cStringIO

        if not self._imageOutputBuffer:
            return

        path = QtGui.QFileDialog.getSaveFileName(
            self, 'Save as', 'new.gif', 'GIF images (*.gif)')
        if not path:
            return
        outputPath = unicode(path)

        width = int(self.spinOutWidth.value())
        height = int(self.spinOutHeight.value())
        frames = []
        for i, frame in enumerate(self._imageOutputBuffer):
            frame = frame.scaled(
                QtCore.QSize(width, height),
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.SmoothTransformation)
            img = frame.toImage()
            buffer = QtCore.QBuffer()
            buffer.open(QtCore.QIODevice.ReadWrite)
            img.save(buffer, 'PNG')
            strio = cStringIO.StringIO()
            strio.write(buffer.data())
            buffer.close()
            strio.seek(0)
            frame = Image.open(strio)
            frames.append(frame)
        fps = float(self.spinFps.value()) / 1000.0
        writeGif(path, frames, fps)
        self.popCursor()

    def updateSelection(self, rect):
        self.selectedRect = rect
        self.spinOutWidth.setValue(self.selectedRect.width())
        self.spinOutHeight.setValue(self.selectedRect.height())
        self.updatePreviewSize()

    def onPlaybackToggled(self, isPlaying):
        if isPlaying:
            if self._imageOutputBuffer:
                self.butPlay.setText('Stop playing')
                self._startPlaying()
            else:
                self.butPlay.setChecked(False)
        else:
            self.butPlay.setText('Play')
            self._stopPlaying()

    def _startPlaying(self):
        fps = int(self.spinFps.value())
        self.playbackTimer.start(1000 / fps)
        
    def _stopPlaying(self):
        self.playbackTimer.stop()

    def onPlaybackTick(self):
        self.playbackSlider.setValue(self.playbackFrame)
        self.updatePreview()
        self.playbackFrame += 1

    def onPlaybackSliderChanged(self):
        nextFrame = int(self.playbackSlider.value())
        if nextFrame != self.playbackFrame:
            self.playbackFrame = nextFrame
            self.updatePreview()

    def updatePreview(self):
        if not self.playbackFrame:
            return
        self.playbackFrame %= (len(self._imageOutputBuffer) + 1)
        frameNum = self.playbackFrame - 1
        #self.playbackFrame %= len(self._imageOutputBuffer)
        frame = self._imageOutputBuffer[frameNum]
        self.previewImage.updatePixmap(frame)

    def updatePreviewSize(self):
        width = int(self.spinOutWidth.value())
        height = int(self.spinOutHeight.value())
        self.previewImage.outputSize = QtCore.QSize(width, height)
        self.previewImage.updateGeometry()

    def onOutWidthChanged(self):
        ratio = self.selectedRect.height() / float(self.selectedRect.width())
        newHeight = max(1, ratio * self.spinOutWidth.value())
        self.spinOutHeight.blockSignals(True)
        self.spinOutHeight.setValue(newHeight)
        self.spinOutHeight.blockSignals(False)
        self.updatePreviewSize()

    def onOutHeightChanged(self):
        ratio = self.selectedRect.width() / float(self.selectedRect.height())
        newWidth = max(1, ratio * self.spinOutHeight.value())
        self.spinOutHeight.blockSignals(True)
        self.spinOutWidth.setValue(newWidth)
        self.spinOutHeight.blockSignals(False)
        self.updatePreviewSize()

    def pushCursor(self, cursor):
        self.cursorStack.append(self.cursor())
        self.setCursor(cursor)

    def popCursor(self):
        try:
            lastCursor = self.cursorStack.pop()
        except IndexError:
            pass
        else:
            self.setCursor(lastCursor)

