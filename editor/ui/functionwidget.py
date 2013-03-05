
from PySide import QtGui

import propertyview

class FunctionWidget(QtGui.QWidget):
    
    def __init__(self, parent=None, fncls='', title=''):
        super(FunctionWidget, self).__init__(parent=parent)
        
        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        

        hlayout = QtGui.QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)

        # TODO: Create a show/hide button

        lbl = QtGui.QLabel(title + "  (%s)" % fncls )
        lbl.setFont(QtGui.QApplication.font())
        lbl.setStyleSheet( 'background-color: darkGray; color: white; margin: 4,0,0,0')
        hlayout.addWidget(lbl)
        
        self.property_view = propertyview.PropertyView()
 
        layout.addLayout(hlayout)
        layout.addWidget(self.property_view)
        layout.addStretch()
        
        self.setLayout( layout )
        
    def SetFunction(self, function):
        self.property_view.Populate([function])
        self.layout().invalidate()


class FunctionsWidget(QtGui.QWidget):
    
    def __init__(self, parent=None, title=''):
        super(FunctionsWidget, self).__init__(parent=parent)

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        
        hboxlayout = QtGui.QHBoxLayout()
        hboxlayout.setContentsMargins(0,0,0,0)
        lbl = QtGui.QLabel(title)
        lbl.setFont(QtGui.QApplication.font())
        hboxlayout.addWidget(lbl)
        
        self.m_BnAdd = QtGui.QToolButton(self)        
        self.m_BnAdd.setAutoRaise(True)
        self.m_BnAdd.setIcon(QtGui.QIcon("icons:/additive.png"))
        
        hboxlayout.addWidget(self.m_BnAdd)
        
        hboxlayout.addStretch()
        
        layout.addLayout( hboxlayout )

        self.functions = QtGui.QVBoxLayout()
        layout.addLayout(self.functions)

        layout.addStretch()
        self.setLayout( layout )

    def clear(self, layout):
        for i in xrange(layout.count()):
            layoutItem = layout.takeAt(0)
            if layoutItem.widget() is not None:
                layoutItem.widget().deleteLater()
        
    def OnAddFunction(self):
        pass

    def SetFunctions(self, functions):
        self.clear(self.functions)

        for fn in functions:
            w = FunctionWidget(parent=self, fncls=fn.__class__.__name__, title=fn.name)
            w.SetFunction( fn )
            self.functions.addWidget( w )

