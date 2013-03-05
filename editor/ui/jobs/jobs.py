import os
import sys
import time
import multiprocessing
import threading
import Queue
from PySide import QtCore, QtGui, QtUiTools


class JobProgress(int):
    pass


class JobString(object):
    def __init__(self, string, level=0):
        self.string = string
        self.level = level

    def __repr__(self):
        return "JobString(%s, %d)" % (self.string, self.level)

    def __str__(self):
        return self.string


class QueueStream(object):
    def __init__(self, owner, queue, level=0):
        assert isinstance(queue, multiprocessing.queues.Queue)
        self.owner = owner
        self.queue = queue
        self.level = level

    def write(self, data):
        self.queue.put( JobString(data, self.level) )
        self.owner.output.emit()

    def close(self):
        self.owner.output.emit()
        self.queue.close()

    def flush(self):
        self.owner.output.emit()


class _JobProcess(QtCore.QThread):

    progress = QtCore.Signal(int)  # Signals the percentage completed
    output = QtCore.Signal()  # Signals that there is output

    def __init__(self, target, callback, name, args, kwargs):
        super(_JobProcess, self).__init__()

        assert isinstance(args[0], multiprocessing.queues.Queue)

        self.name = name
        self.queue = args[0]

        self.pid = 0
        self.function = target
        self.args = [self] + args[1:]
        self.kwargs = kwargs
        self.callback = callback

    def __del__(self):
        sys.stdout.close()
        sys.stderr.close()

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def run(self):
        sys.stdout = QueueStream(self, self.queue, 0)
        sys.stderr = QueueStream(self, self.queue, 1)

        self.function(*self.args, **self.kwargs)

    def set_progress(self, value):
        self.progress.emit(value)


class JobView(QtGui.QWidget):
    def __init__(self, job_service, parent=None):
        super(JobView, self).__init__(parent=parent)
        self.job_service = job_service

        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)

        vlayout = QtGui.QVBoxLayout()
        vlayout.addLayout(self.layout)
        vlayout.addStretch(1)
        self.setLayout(vlayout)

        self._populate(self.job_service.get_jobs())

        p = os.path.normpath( os.path.abspath( os.path.join( os.path.dirname(__file__), 'icons') ) )
        QtCore.QDir.addSearchPath("icons", p)

    def _populate(self, jobs):
        for job in jobs:
            self._add_job(job)

    def _add_job(self, job):

        loader = QtUiTools.QUiLoader()
        widget = loader.load( os.path.dirname(__file__) + "/task.ui")
        widget.label.setText(job.name.capitalize())
        widget.progress.setValue(0)
        widget.bottom.setHidden(True)
        widget.text.setPlainText('')
        widget.pid.setText(str(job.pid))

        job.widget = widget
        job.time_start = time.time()

        print >>sys.__stdout__, job.name, id(job.widget.text), 'text'

        def _on_progress(progress):
            job.widget.progress.setValue(progress)
        job.progress.connect(_on_progress, QtCore.Qt.QueuedConnection)

        def _on_output():

            #print >>sys.__stdout__, job.name, id(job.widget.text), 'flush'

            def _flush_data(widget, data, level):
                color = ''
                if level > 0:
                    color = 'red'

                html = '<font color="%s">%s</font>' % (color, data.replace('\n', '<br/>'))
                job.widget.text.insertHtml( html )

            datalevel = 0
            data = ''

            while True:
                try:
                    item = job.queue.get_nowait()
                    if datalevel != item.level:
                        _flush_data(widget, data, datalevel)
                        data = ''
                        datalevel = item.level
                    data += item.string
                except Queue.Empty:
                    break
            _flush_data(widget, data, datalevel)

        job.output.connect(_on_output, QtCore.Qt.QueuedConnection)

        self.layout.addWidget(widget)


class JobService(object):

    def __init__(self):
        self.jobs = []
        self.timer = None
        self.listeners = []
        self._start_timer()

    def add_job(self, run, name=None, callback=None, args=(), kwargs={}):
        """ Adds a job to the list
        """
        assert isinstance(args, tuple)
        assert isinstance(kwargs, dict)

        q = multiprocessing.Queue()
        job = _JobProcess(run, callback, name, [q] + list(args), kwargs)
        setattr(job, 'queue', q)

        def _on_started():
            job.callback(job, 'started')

        def _on_finished():
            job.callback(job, 'done')

        def _on_terminated():
            job.callback(job, 'terminated')

        job.started.connect(_on_started, QtCore.Qt.QueuedConnection)
        job.finished.connect(_on_finished, QtCore.Qt.QueuedConnection)
        job.terminated.connect(_on_terminated, QtCore.Qt.QueuedConnection)

        job.start()
        self.jobs.append(job)

        self._start_timer()

    def _start_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(0.3, self._on_timer)
        self.timer.start()

    def get_jobs(self):
        return self.jobs

    def is_alive(self):
        for job in self.jobs:
            if job.isRunning():
                return True
        return False

    def terminate(self):
        """

        .. note:: Note that descendant processes of the process will not be terminated they will simply become orphaned
        """
        for job in self.jobs:
            if job.isRunning():
                job.terminate()
        self.jobs = []

    def _on_timer(self):
        # This is on the main thread

        def _flush_data(job, widget, data, level):
            if not data:
                return

            #if level == 0:
            #    sys.stdout.write(data)
            #else:
            #    sys.stderr.write(data)

            if not widget:
                return

            color = ''
            if level > 0:
                color = 'red'

            html = '<font color="%s">%s</font>' % (color, data.replace('\n', '<br/>'))

            widget.text.insertHtml( html )

        for job in self.jobs:
            widget = getattr(job, 'widget', None)
            print >>sys.__stdout__, job.name, id(widget)

            """
            datalevel = 0
            data = ''
            progress = None

            while True:
                try:
                    item = job.queue.get_nowait()
                    if isinstance(item, JobProgress):
                        progress = item
                    elif isinstance(item, JobString):
                        if datalevel != item.level:
                            _flush_data(widget, data, datalevel)
                            data = ''
                            datalevel = item.level
                        data += item.string
                except Queue.Empty:
                    break
            """

            if widget:

                #if progress:
                #    widget.progress.setValue(progress)

                #_flush_data(job, widget, data, datalevel)

                if not job.isRunning():
                    widget.label.setEnabled(False)
                    widget.bn_stop.setEnabled(False)
                    widget.progress.setEnabled(False)
                elif widget:
                    time_current = time.time()
                    widget.elapsed.setText( '%.2f' % (time_current - job.time_start) )

        self.jobs = [job for job in self.jobs if job.isRunning()]

        if self.jobs:
            self._start_timer()
        else:
            if self.timer:
                self.timer.cancel()
            self.timer = None

    def add_listener(self, listener):
        assert listener not in self.listeners, "The listener is already added"
        self.listeners.append( listener )

    def remove_listener(self, listener):
        self.listeners.remove(listener)


def longrun(ctx, count, msg):
    print 'longrun', 'pid', os.getpid()

    for i in range(count):
        percent = int(i / float(count-1) * 100)
        ctx.set_progress(percent)

        #ctx.queue.put(JobString(ctx.name + 'hello world', 0))
        #ctx.output.emit()

        time.sleep(0.10)
        print msg, i, 'pid', os.getpid()

        if i % 7 == 0:
            print >>sys.stderr, i, 'an error message'


def longrun_cbk(ctx, reason):
    print ctx.name, "CALLBACK", reason, 'pid', os.getpid()
    print 'visit: <a href="http://www.google.com">http://www.google.com</a>'


if __name__ == '__main__':

    print "main", os.getpid()
    print ""

    app = QtGui.QApplication(sys.argv)

    js = JobService()

    """
    print "theme", QtGui.QIcon.themeName()
    print "search paths", QtGui.QIcon.themeSearchPaths()
    print ""

    it = QtCore.QDirIterator(':', QtCore.QDirIterator.Subdirectories)
    while it.hasNext():
        print it.filePath()
        it.next()

    sys.exit(0)
    """

    js.add_job( longrun, 'myname 1', longrun_cbk, (100, 'msg 1',) )
    js.add_job( longrun, 'myname 2', longrun_cbk, (30, 'msg 2',) )
    js.add_job( longrun, 'myname 3', longrun_cbk, (60, 'msg 3',) )
    js.add_job( longrun, 'myname 4', longrun_cbk, (45, 'msg 4',) )

    mainWindow = QtGui.QMainWindow()
    mainWindow.setMinimumSize( 500, 300 )
    mainWindow.setWindowTitle('Jobs')

    cw = JobView(js)
    mainWindow.setCentralWidget( cw )

    mainWindow.show()
    mainWindow.raise_()

    sys.exit(app.exec_())
