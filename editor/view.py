import sys
from PySide import QtGui, QtCore
from ui import PreviewWidget, LayerWidget, Toolbar, FunctionsWidget


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)

        self.m_Preview = PreviewWidget(self)
        self.setCentralWidget(self.m_Preview)

        self.m_Preview.LoadImage('')
        #self.m_Preview.LoadImage(r'B:\perforce\3rdparty\fontcreator\modified\doc\examples\build\03_layers_effects.png')
        #self.m_Preview.LoadImage('build/03_layers_effects.png')

        self.m_Toolbar = Toolbar(self)
        dw = QtGui.QDockWidget()
        dw.setWidget( self.m_Toolbar )
        dw.setWindowTitle("Toolbar")
        self.addDockWidget( QtCore.Qt.TopDockWidgetArea, dw )

        dw = QtGui.QDockWidget()
        dw.setWindowTitle('Layers')
        w = QtGui.QWidget()
        dw.setWidget( w )

        layout = QtGui.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        w.setLayout(layout)
        self.addDockWidget( QtCore.Qt.RightDockWidgetArea, dw )

        self.m_ColorFunctions = FunctionsWidget(self, title='Color Functions')
        layout.addWidget( self.m_ColorFunctions, 1 )

        self.m_ColorFunctions.m_BnAdd.clicked.connect(self.OnAddColorFunction)

        self.EffectFunctions = FunctionsWidget(self, title='Effect Functions')
        layout.addWidget( self.EffectFunctions, 1 )

        self.EffectFunctions.m_BnAdd.clicked.connect(self.OnAddEffectFunction)

        self.m_Layers = LayerWidget(self)
        layout.addWidget( self.m_Layers, 2 )

        layout.addStretch()

        self.setWindowTitle("FontCreator")

    def load_texture(self, path):
        self.m_Preview.LoadImage(path)

    def OnAddColorFunction(self):
        pass

    def OnAddEffectFunction(self):
        pass

    def _SetFunctions(self, widget, functions):
        widget.SetFunctions(functions)

    def SetColorFunctions(self, functions):
        self._SetFunctions(self.m_ColorFunctions, functions)


class View(object):
    def __init__(self):
        self.Documents = []

    def SetPresenter(self, presenter):
        self.Presenter = presenter

    def Exec(self):
        app = QtGui.QApplication(sys.argv)

        #style = 'gtk'
        #if sys.platform == 'linux2':
        #    style = 'gtk'
        #elif sys.platform in ['win32', 'win64']:
        #    style = 'WindowsVista'

        #app.setStyle( QtGui.QStyleFactory.create(style) )

        font = app.font()
        font.setPixelSize(10)
        app.setFont(font)

        self.mainwindow = MainWindow()
        self.mainwindow.show()
        self.mainwindow.raise_()  # bring it to the top

        self.Presenter.OnShow()
        return app.exec_()

    def SetColorFunctions(self, functions):
        self.mainwindow.SetColorFunctions(functions)

    def AddDocument(self, path):
        pass

    def load_texture(self, path):
        self.mainwindow.load_texture(path)


