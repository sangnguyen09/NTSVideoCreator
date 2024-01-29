import time

from PySide6.QtCore import QThread, Signal, pyqtSlot

from gui.helpers.func_helper import PrintLog
from gui.helpers.thread import ManageQThread
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox


class LongThread(QThread):
    # end::thread[]
    """
    Worker thread
    """
    statusChanged = Signal(str, str)
    progressChanged = Signal(str, int)
    # _errorChanged = Signal(str, str)
    resultSignal = Signal(str, object)
    _resultSignalChildren = Signal(str, object)

    def __init__(self):
        super().__init__()
        self.manage_thread = QThread()
        self.fnRun = None
        self.id_worker = None
        self.list_loop = None
        self.kwargs = None
        self._setup_connections()

    @pyqtSlot()
    def run(self):
        """
        Your code goes in this method
        """
        print("Thread start")
        self.is_running = True
        self.waiting_for_data = True
        while True:
            while self.waiting_for_data:
                if not self.is_running:
                    return  # Exit thread.
                time.sleep(0.1)  # wait for data <1>.

            if not self.fnRun == None and not self.id_worker == None and not self.list_loop == None and not self.kwargs == None:
                for indx, item in enumerate(self.list_loop):
                    worker = Worker(self, self.fnRun, self.id_worker, **self.kwargs)
                    worker.start()
                    # print("vong lập thread")
                    # self.kwargs["item"] = item
                    # self.manage_thread.start(self.fnRun, id_worker=self.id_worker, **self.kwargs)

                    self.resultSignal.emit(self.id_worker, f"The cumulative total is {item}")
            self.waiting_for_data = True

    def _setup_connections(self):
        # self.manage_thread.statusChanged.connect(self._status)
        # self.manage_thread.progressChanged.connect(self._progress)
        # self.manage_thread.resultChanged.connect(self._result)

        self._resultSignalChildren.connect(self._result)

    def _result(self, id_worker, result):
        PrintLog(id_worker, result)
        # self.resultSignal.emit(id_worker, result)

    def _status(self, id_worker, status):
        self.statusChanged.emit(id_worker, status)

    def _progress(self, id_worker, prog):
        self.progressChanged.emit(id_worker, prog)

    def release(self, fnRun, id_worker: str, list_loop: list, **kwargs):  #
        '''Load dữ liệu và mở khoá để thực thi code'''
        self.fnRun = fnRun
        self.id_worker = id_worker
        self.list_loop = list_loop
        self.kwargs =kwargs

        self.waiting_for_data = False  # Release the lock & calculate.

    # end::data_methods[]
    def stop(self):
        self.is_running = False


class Worker(QThread):
    # end::thread[]
    """
    Worker thread
        self.thread.result.connect()
        self.thread.finished.connect()
        tạo ra 1 luồng riêng biệt để xử lý , mà ko cần phải tạo nhiều luồng cùng lúc
    """

    def __init__(self, parent: ManageQThread, fnRun, id_worker, **kwargs):
        super().__init__()
        self.parent = parent
        self.fnRun = fnRun
        self.id_worker = id_worker
        self.kwargs = kwargs
        self.kwargs["parent"]= parent
        self.kwargs["id_worker"]= id_worker
        # self.parent._list_worker[
        #     self.id_worker] = self
    @pyqtSlot()
    def run(self):
        try:
            result = self.fnRun(**self.kwargs)
        except Exception as e:
            PyMessageBox().show_error("Lỗi", str(e))

            # self.parent._errorChanged.emit(self.id_worker, str(e))
        else:
            # trạng thái được cập nhật sau cập nhật hoàn thành để cập nhật lại giao giền lần cuối

            self.parent._resultSignalChildren.emit(self.id_worker, result)

