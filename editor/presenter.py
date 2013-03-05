
import sys, os, logging
from PySide import QtCore
import model
from ui.jobs import JobService
import fontutils


class Presenter(object):
    def __init__(self):
        self.model = None
        self.documents = dict()
        self.jobs = JobService()

    def SetView(self, view):
        self.view = view

    def Exec(self):
        p = os.path.normpath( os.path.abspath( os.path.join( os.path.dirname(__file__), 'icons') ) )
        QtCore.QDir.addSearchPath("icons", p)

        return self.view.Exec()

    def OnShow(self):
        if self.model is None:
            return

        #print self.model.fontinfo.functionlist.values()
        self.view.SetColorFunctions( self.model.fontinfo.functionlist.values() )

        self.jobs.add_job(self._compile, name='Compile', callback=self._on_compile_finished, args=(self.model.options, ))

    def _create_options(self, path):
        class Options(object):
            pass
        options = Options()
        options.input = path
        options.output = 'build/' + os.path.basename(os.path.splitext(path)[0]) + '.out'
        options.datadir = 'examples'
        return options

    def _compile(self, ctx, options):
        fontcreator = os.path.join(os.path.dirname(__file__), '..', 'fontcreator.py')
        cmd = '%s %s -i %s -o %s -d %s -v' % (sys.executable, fontcreator, options.input, options.output, options.datadir)
        print "CMD", cmd

        #proc = subprocess.Popen(cmd, shell=False)
        #retcode = proc.wait()
        retcode = os.system(cmd)
        print 'return value', retcode
        print ''

    def _on_compile_finished(self, ctx, reason):
        if reason == 'done':
            self.view.load_texture('build/03_layers_effects.png')

            from PySide import QtCore
            print 'current thread (done)', QtCore.QThread.currentThread()
            print 'app thread (done)', QtCore.QCoreApplication.instance().thread()

    def LoadFile(self, path):
        try:
            options = self._create_options(path)
            self.model = model.Model(options)
            self.documents[path] = self.model
            self.view.AddDocument(path)
        except fontutils.FontException:
            logging.exception("The file %s failed to open", path)

        print 'pid main', os.getpid()
