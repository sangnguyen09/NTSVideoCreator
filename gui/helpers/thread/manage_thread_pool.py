import sys
import time
import traceback

from PySide6.QtCore import QObject, Signal, QThreadPool, Slot, QRunnable

from gui.configs.config_thread import STATUS_WAITING, STATUS_COMPLETE, STATUS_RUNNING, STATUS_STOPPED, \
	STATUS_PAUSED
from gui.helpers.custom_logger import customLogger

DEFAULT_STATE = {"progress": 0, "status": STATUS_WAITING}


class ManageThreadPool(QObject):
	resultChanged = Signal(str, str, object)  # id_worker,typeThread,data khi worker có sự thay đổi thì emit ra ngoài
	statusChanged = Signal(str, str,
		str)  # id_worker,typeThread,status khi worker có sự thay đổi trạng thái thì emit ra ngoài để thay đổi giao diện
	progressChanged = Signal(str, str, int)  # str là id để xác định giữa các thread , int khi worker có sự thay đổi tiến trình thì emit ra ngoài để thay đổi giao diện
	errorChanged = Signal(str, str, object)  # id_worker,typeThread,error
	messageBoxChanged = Signal(str, str, str)  # title,message,type hiển thị thông báo ngoài thằng cha
	finishSingleThreadChanged = Signal(str)  # id_worker,
	
	stopAllThreadChanged = Signal(str)  # khi tất cả các thiết hoàn thành
	
	# _list_worker = {}
	
	def __init__ (self, thread_number=100):
		super().__init__()
		self.thread_number = thread_number
		self.threadpool = QThreadPool()
		# print(self.threadpool())
		self.threadpool.setMaxThreadCount(self.thread_number)
		
		self.is_stop_all_thread = False
		self.ids_thread_is_stop_single = []
		self.ids_thread_is_pause_single = []
		self._list_worker = {}
		# các sự kiện của 1 worker
		self.statusChanged.connect(self.receive_status)
		self.finishSingleThreadChanged.connect(self.finishSingleThread)
		self.errorChanged.connect(self._errorChanged)
		self.stopAllThreadChanged.connect(self.stop_all_thread_changed)
	
	# def start(self, fnRun,id_worker,thread_pool,typeThread, **kwargs):
	#     worker = Worker(fnRun,id_worker,thread_pool,typeThread, **kwargs)
	#     self.threadpool.start(worker)
	
	def start (self, fnRun, id_worker, typeThread, limit_thread=False, **kwargs):
		
		if id_worker in self.ids_thread_is_stop_single:
			self.ids_thread_is_stop_single.remove(id_worker)  # xoá trạng thái cũ nếu trước đó no ở trạng thái stop
		
		worker = Worker(fnRun, id_worker, self, typeThread, **kwargs)
		# if limit_thread is False:
		# 	self.threadpool.setMaxThreadCount(len(self._list_worker) + 1)
		self.threadpool.start(worker)
	
	def receive_status (self, id_worker, status):
		
		if status == STATUS_STOPPED and id_worker in self.ids_thread_is_stop_single:
			self.ids_thread_is_stop_single.remove(id_worker)
	
	def _errorChanged (self, id_worker, typeThread, error):  # xoá thread_number đi 1 đơn vị
		if id_worker in self._list_worker.keys():
			del self._list_worker[id_worker]
	
	# self.threadpool.setMaxThreadCount(len(self._list_worker))
	
	def finishSingleThread (self, id_worker, limit_thread=False):  # xoá thread_number đi 1 đơn vị
		
		if id_worker in self._list_worker.keys():
			del self._list_worker[id_worker]
	
	# if limit_thread is False:
	# 	self.threadpool.setMaxThreadCount(len(self._list_worker))
	
	# print(self._list_worker)
	# print("_list_worker: " + str(len(self._list_worker)) + " số thread " + str(self.threadpool.maxThreadCount()))
	
	def stop_all_thread_changed (self, id_worker):
		
		if id_worker in self._list_worker.keys():
			del self._list_worker[id_worker]
			self.is_stop_all_thread = False
	
	# if self.is_stop_all_thread and len(self._list_worker) == 0:
	#     self.is_stop_all_thread = False
	#     self._list_worker = {}
	
	def stop_all_thead (self):
		self.is_stop_all_thread = True
		self.ids_thread_is_pause_single = []
	
	# self._list_worker.clear()
	
	def stop_single_thead (self, id_worker):
		self.ids_thread_is_stop_single.append(id_worker)
		if id_worker in self.ids_thread_is_pause_single:
			self.ids_thread_is_pause_single.remove(id_worker)
		
		if id_worker in self._list_worker.keys():
			del self._list_worker[id_worker]
	
	def pause_single_thead (self, id_worker):
		self.ids_thread_is_pause_single.append(id_worker)
	
	def resume_single_thead (self, id_worker):
		self.ids_thread_is_pause_single.remove(id_worker)
	
	def setMaxThread (self, numb_thread):
		self.threadpool.setMaxThreadCount(numb_thread)
	
	def runFunctionThread (self, fnRun, id_worker, thread_pool, typeThread='', status="", **kwargs):
		if id_worker in thread_pool.ids_thread_is_pause_single:
			thread_pool.statusChanged.emit(id_worker, typeThread, STATUS_PAUSED)
			while id_worker in thread_pool.ids_thread_is_pause_single:
				# print("đang pause trong run_action")
				time.sleep(0.5)  # <1> chế độ ngủ sẽ giúp giải phóng tài nguyên tốt hơn, có thể tăng lên
		
		# khi dừng tất cả hoặc dừng từng thread thì sẽ ném ra lỗi dể dừng thread đó
		if id_worker in thread_pool.ids_thread_is_stop_single:
			raise StopSingleWorkerException
		
		if thread_pool.is_stop_all_thread:
			raise StopAllWorkerException
		# chay code
		thread_pool.statusChanged.emit(id_worker, typeThread, status)
		
		result = fnRun(**kwargs)
		return result


class StopSingleWorkerException(Exception):
	pass


class StopAllWorkerException(Exception):
	pass


class Worker(QRunnable):
	
	def __init__ (self, fnRun, id_worker, parent, typeThread, **kwargs):
		super().__init__()
		# Store constructor arguments (re-used for processing)
		self.fnRun = fnRun  # hàm được thêm vào
		self.kwargs = kwargs
		
		self.id_worker = str(id_worker)
		self.typeThread = str(typeThread)
		self.thread_pool = parent
		self.kwargs["thread_pool"] = parent
		self.kwargs["id_worker"] = id_worker
		self.kwargs["typeThread"] = typeThread
		
		self.thread_pool._list_worker[
			self.id_worker] = self  # self là 1 worker thêm vào danh sách để quản lý , thêm trước khi có trạng thái
		
		self.thread_pool.statusChanged.emit(self.id_worker, self.typeThread, STATUS_WAITING)
	
	@Slot()
	def run (self):  # phương thức chạy chính của worker
		if not self.thread_pool.is_stop_all_thread and self.id_worker not in self.thread_pool.ids_thread_is_stop_single:
			
			try:
				# kiểm tra trạng thái đang chạy hoặc dừng lại
				if self.id_worker in self.thread_pool.ids_thread_is_pause_single:

					self.thread_pool.statusChanged.emit(self.id_worker, self.typeThread, STATUS_PAUSED)
					while self.id_worker in self.thread_pool.ids_thread_is_pause_single:
						# print("đang pause trong run")
						time.sleep(0.5)  # <1> chế độ ngủ sẽ giúp giải phóng tài nguyên tốt hơn, có thể tăng lên

				# khi dừng tất cả hoặc dừng từng thread thì sẽ ném ra lỗi dể dừng thread đó
				if self.id_worker in self.thread_pool.ids_thread_is_stop_single:
					# print("row stop ")
					raise StopSingleWorkerException

				if self.thread_pool.is_stop_all_thread:
					# print("row stop ", self.kwargs["row"])
					raise StopAllWorkerException

				# bắt đầu chạy code chính
				self.thread_pool.statusChanged.emit(self.id_worker, self.typeThread, STATUS_RUNNING)
				result = self.fnRun(**self.kwargs)

			except StopSingleWorkerException:
				# print("vao trong stop")
				self.thread_pool.statusChanged.emit(self.id_worker, self.typeThread, STATUS_STOPPED)

			except StopAllWorkerException:
				self.thread_pool.stopAllThreadChanged.emit(self.id_worker)
				self.thread_pool.statusChanged.emit(self.id_worker, self.typeThread,
					STATUS_STOPPED)  # cho status cập nhật sau để reload lại giao diện
			except Exception as e:

				# customLogger(self.fnRun.__name__, traceback.extract_tb(exc_tb)[-1][1]).error(str(e))
				try:
					exc_type, exc_obj, exc_tb = sys.exc_info()
					mess = 'Func: ' + self.fnRun.__name__ + '\nDòng: ' + str(
						traceback.extract_tb(exc_tb)[-1][1]) + '\n' + str(e)
					print(mess)

					self.thread_pool.errorChanged.emit(self.id_worker, self.typeThread, (self.fnRun.__name__, mess))
				except:
					self.thread_pool.errorChanged.emit(self.id_worker, self.typeThread, (self.fnRun.__name__, str(e)))

			else:
				self.thread_pool.finishSingleThreadChanged.emit(self.id_worker)
				self.thread_pool.statusChanged.emit(self.id_worker, self.typeThread,
					STATUS_COMPLETE)  # trạng thái được cập nhật sau cập nhật hoàn thành để cập nhật lại giao giền lần cuối
				self.thread_pool.resultChanged.emit(self.id_worker, self.typeThread, result)  # Trả về kết quả của việc gọi hàm
		
		# elif self.thread_pool.is_stop_all_thread:
		# 	print("stop all")
		# 	self.thread_pool.stopAllThreadChanged.emit(self.id_worker)
		# 	self.thread_pool.statusChanged.emit(self.id_worker, self.typeThread, STATUS_STOPPED)
		#
		# elif self.id_worker in self.thread_pool.ids_thread_is_stop_single:
		# 	print("vao stop")
		# 	self.thread_pool.statusChanged.emit(self.id_worker, self.typeThread, STATUS_STOPPED)

# class WorkerSignals(QObject):
#     """
#     Defines the signals available from a running worker thread.
#
#     Supported signals are:
#
#     finished
#         No data
#
#     error
#         `tuple` (exctype, value, traceback.format_exc() )
#
#     result
#         `object` data returned from processing, anything
#
#     progress
#         `int` indicating % progress
#
#     """
#     error = Signal(int, str)
#     result = Signal(int, object)  # We can send anything back.
#
#     finished = Signal(int)
#     progress = Signal(int, int)
#     status = Signal(int, str)
