from PySide import QtGui


class PreviewWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(PreviewWidget, self).__init__(parent=parent)

        self.m_PixmapLabel = QtGui.QLabel()

        image = QtGui.QImage(512, 512, QtGui.QImage.Format_ARGB32)
        image.fill( 0x44FF66FF )

        self.SetImage( image )

        box = QtGui.QVBoxLayout()
        box.addWidget(self.m_PixmapLabel)
        self.setLayout(box)

    def SetImage(self, image):
        """ Updates the view with a
        :param image: A QImage
        """
        self.m_Image = image
        self.m_PixmapLabel.setPixmap( QtGui.QPixmap.fromImage(image) )

    def LoadImage(self, path):
        image = QtGui.QImage()
        if image.load(path):
            self.SetImage(image)
