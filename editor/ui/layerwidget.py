
from PySide import QtGui
import toolbar
import propertyview
from properties.propertyclass import property_class
from properties.propertytypes import IntProperty

def lerp(a,b,t):
    return (t * b) + ((1.0 - t) * a)


class LayerWidget(QtGui.QWidget):
    
    def __init__(self, parent=None):
        super(LayerWidget, self).__init__(parent=parent)
        
        self.setMinimumWidth( 240 )
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(2,2,2,2)
        
        self.Toolbar = toolbar.Toolbar(self)
        
        bn = QtGui.QToolButton(self)
        bn.setAutoRaise(True)
        bn.setIcon(QtGui.QIcon("icons:/additive.png"))
        bn.clicked.connect(self.OnAddLayer)
        self.Toolbar.AddWidget(bn) 
        
        self.PropertyView = propertyview.PropertyView()
        
        @property_class()
        class TestObject(object):
            int0 = IntProperty(0)
            int1 = IntProperty(1)
            int2 = IntProperty(2)
            int3 = IntProperty(3)
        
        self.testobject = TestObject()
        
        layout.addWidget(self.Toolbar)
        layout.addWidget(self.PropertyView)
        
        self.PropertyView.Populate([self.testobject])
        
        layout.addStretch()
        
        self.setLayout(layout)
        
    def OnAddLayer(self):
        pass
        
    def AddWidget(self):
        pass
    
    def paintEvent(self, ev):
        p = QtGui.QPainter(self)
        c1 = self.palette().color(QtGui.QPalette.Mid)
        c2 = self.palette().color(QtGui.QPalette.Window)
        t = 0.75
        c = QtGui.QColor.fromRgb(lerp(c1.red(), c2.red(), t), lerp(c1.green(), c2.green(), t), lerp(c1.blue(), c2.blue(), t))
        p.fillRect(1,1,self.width()-2,self.height()-2, c)
        
        super(LayerWidget, self).paintEvent(ev)
        