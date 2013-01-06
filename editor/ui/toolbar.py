
from PySide import QtGui

class Toolbar(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Toolbar, self).__init__(parent=parent)
        
        layout = QtGui.QHBoxLayout()
        
        hl = QtGui.QHBoxLayout()
        hl.setContentsMargins(0,0,0,0)
        
        vl = QtGui.QVBoxLayout()
        vl.setContentsMargins(0,0,0,0)
        
        self.LayoutHorizontal = hl
        self.LayoutVertical = vl
        
        layout.addLayout(self.LayoutHorizontal)
        layout.addStretch()
        
        self.setLayout(layout)
        
    def AddWidget(self, widget):
        self.LayoutHorizontal.addWidget(widget)
        self.LayoutVertical.addWidget(widget)
       
    def resizeEvent(self, ev):
        if self.width() > self.height():
            self.setLayout(self.LayoutHorizontal)
        else:
            self.setLayout(self.LayoutVertical)
            