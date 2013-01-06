
from PySide import QtGui, QtCore
from properties import PropertyValidateError


class property_editor(object):
    def __init__(self, *k, **kw):
        self.types_property = k[0]

    def __call__(self, *k, **kw):
        for t in self.types_property:
            PropertyView.RegisterClass(t.__name__, k[0])


class PropertyView(QtGui.QWidget):

    class_to_editor = dict()

    @classmethod
    def RegisterClass(cls, type_property, type_editor):
        cls.class_to_editor[type_property] = type_editor

    def __init__(self, *k, **kw):
        super(PropertyView, self).__init__(*k, **kw)

        self.layout = QtGui.QGridLayout()
        self.layout.setColumnMinimumWidth(0, 16)
        #self.layout.setColumnMinimumWidth(1, 80)
        self.layout.setHorizontalSpacing(3)
        self.layout.setSpacing( 4 )
        self.layout.setColumnStretch(2, 1)

        self.setLayout(self.layout)

    def _CreateEditorFromProperty(self, name, value, info):

        lbl = QtGui.QLabel(info.getVerboseName())
        lbl.setFont(QtGui.QApplication.font())

        editortype = self.class_to_editor[info.__class__.__name__]
        widget = editortype(parent=self, value=value, prop=info)

        #layout = QtGui.QHBoxLayout()
        #layout.addSpacing(16) # 'expand' button
        #layout.addWidget(lbl, 0)
        #layout.addWidget(widget, 1)

        #widgetwrapper = QtGui.QWidget()
        #widgetwrapper.setLayout(layout)

        #self.layout.addWidget(widget, 1)
        row = self.rowcount
        self.rowcount += 1
        lbl = QtGui.QLabel(info.getVerboseName())

        self.layout.addWidget(lbl, row, 1, alignment=QtCore.Qt.AlignRight)
        self.layout.addWidget(widget, row, 2, alignment=QtCore.Qt.AlignLeft)

        tooltip = info.getHelp()
        widget.setToolTip(tooltip)
        #widgetwrapper.setToolTip(tooltip)

        # hookup the event
        def _onValueChanged(value):
            self.onValueChanged(name, info, widgetwrapper, value)
        widget.valueChanged.connect(_onValueChanged)

    def validateProperty(self, info, widget, value):
        try:
            info.validate(value)
        except PropertyValidateError, e:
            widget.setToolTip(str(e))

            pal = QtGui.QPalette()
            pal.setColor(widget.backgroundRole(), QtCore.Qt.red)
            widget.setAutoFillBackground( True )
            widget.setPalette(pal)
            return False

        widget.setToolTip(info.getHelp())
        widget.setPalette(QtGui.QApplication.palette())

        return True

    def onValueChanged(self, name, info, widget, value):
        if not self.validateProperty(info, widget, value):
            return

        print name, value

    def clear(self):
        for i in xrange(self.layout.count()):
            layoutItem = self.layout.takeAt(0)
            if layoutItem.widget() is not None:
                layoutItem.widget().deleteLater()

        self.rowcount = 0

    def Populate(self, objects):
        """ Adds widgets for each property

        :param objects:    A list of objects with at least one property in common
        """
        assert isinstance(objects, list), "Objects must be a list"
        o = objects[0]

        self.clear()

        for name, value in o.iteritems():
            info = o.getPropertyInfo(name)
            self._CreateEditorFromProperty( name, value, info )





