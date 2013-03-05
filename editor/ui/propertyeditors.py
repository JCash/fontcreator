
from PySide import QtGui, QtCore
from properties.propertytypes import IntProperty, AngleProperty, OpacityProperty, Size1DProperty, StringProperty, FileProperty, ColorProperty
from propertyview import property_editor


class PropertyEditor(QtGui.QWidget):

    # sent when the value changes
    valueChanged = QtCore.Signal(str)

    def __init__(self, parent=None, value=None, prop=None):
        super(PropertyEditor, self).__init__(parent=parent)

        assert prop is not None
        self.property = prop
        self.value = value if value is not None else prop.getDefault()
        self.type = type(self.value)

        self.createWidget()

    def changeValue(self, value):
        """ Call this when you wish to change the value
        """
        self.valueChanged.emit( self.value )
        self.value = self.type(value)

    def createWidget(self):
        assert False, 'Not implemented'


@property_editor([int, IntProperty, AngleProperty, OpacityProperty, Size1DProperty])
class NumericEditor(PropertyEditor):

    def createWidget(self):

        self.edit = QtGui.QLineEdit()
        self.edit.setText(unicode(self.value))
        self.edit.textEdited.connect(self.onTextEdited)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget( self.edit, 1 )
        self.setLayout(layout)

    def onTextEdited(self, value):
        self.changeValue(value)


@property_editor([str, unicode, StringProperty, FileProperty])
class StringEditor(PropertyEditor):
    def createWidget(self):
        self.edit = QtGui.QLineEdit()
        self.edit.setText(unicode(self.value))
        self.edit.textEdited.connect(self.onTextEdited)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget( self.edit, 1 )
        self.setLayout(layout)

    def onTextEdited(self, value):
        self.changeValue(value)


@property_editor([ColorProperty])
class ColorEditor(PropertyEditor):

    def createWidget(self):
        fm = QtGui.QApplication.fontMetrics()
        sz = fm.height()

        self.pixmap = QtGui.QPixmap(sz, sz)
        self.pixmap.fill( QtGui.QColor(self.value[0], self.value[1], self.value[2]) )

        self.icon = QtGui.QIcon(self.pixmap)

        self.bn = QtGui.QLabel()
        self.bn.setPixmap(self.pixmap)

        layout = QtGui.QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget( self.bn, 1 )
        self.setLayout(layout)

    def mousePressEvent(self, evt):
        #print "evt", evt.x(), evt.y()
        pass








