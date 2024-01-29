from PySide6.QtCore import QThread, Signal, Slot, QObject

from gui.widgets.py_messagebox.py_massagebox import PyMessageBox


class ManageQThread(QObject):
    resultChanged = Signal(str, object)
    statusChanged = Signal(str, str)
    progressChanged = Signal(str, int)
    _errorChanged = Signal(str, str)

    def __init__(self, ):
        super().__init__()

        self._list_worker = {}

        # các sự kiện của 1 worker
        self.resultChanged.connect(self._finish_single_thread)
        self._errorChanged.connect(self._showMessageBox)

    def start(self, fnRun, id_worker, **kwargs):
        worker = Worker(self, fnRun, id_worker, **kwargs)
        worker.start()
        # worker.finished.connect(lambda :self.finish_single_thread(id_worker))

    def _finish_single_thread(self,id_worker,  typeThread, result):  # xoá thread_number đi 1 đơn vị
        if id_worker in self._list_worker.keys():
            self._list_worker[id_worker].quit()
            del self._list_worker[id_worker]

    def stop_single_thead(self, id_worker):
        if id_worker in self._list_worker.keys():
            self._list_worker[id_worker].terminate()
            self._list_worker[id_worker].quit()
            del self._list_worker[id_worker]

    def _showMessageBox(self, id_worker, message):
        if id_worker in self._list_worker.keys():
            del self._list_worker[id_worker]



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
        self.id_worker = str(id_worker)
        self.kwargs = kwargs
        self.kwargs["parent"]= parent
        self.kwargs["id_worker"]= id_worker
        self.parent._list_worker[
            self.id_worker] = self
    @Slot()
    def run(self):
        try:
            result = self.fnRun(**self.kwargs)
        except Exception as e:
            PyMessageBox().show_error("Lỗi", str(e))

            # self.parent._errorChanged.emit(self.id_worker, str(e))
        else:
            # trạng thái được cập nhật sau cập nhật hoàn thành để cập nhật lại giao giền lần cuối

            self.parent.resultChanged.emit(self.id_worker, result)

