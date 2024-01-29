import os
import re
import subprocess
import time
import uuid

import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QGroupBox, QCheckBox

from gui.helpers.constants import FILE_NAME_FFSUB_EXE, START_SERVER_FFSUB, USER_DATA, \
	TOOL_CODE_MAIN, START_SERVER_FFSUB_FINISHED, PROCESS_FFSUB_THREAD, SETTING_APP_DATA
from gui.helpers.ect import cr_pc, mh_ae_w
from gui.helpers.func_helper import which, getValueSettings
from gui.helpers.get_data import   URL_API_BASE,  PATH_TOOL_FFSUB
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox


def check_cuda_version ():
	# return False,'11'
	cuda_ok = False
	version_card = ''
	try:
		nvidia = subprocess.check_output(['nvidia-smi']).decode()
		version = re.findall(r'CUDA Version: (\d+.\d)', nvidia)
		if len(version) > 0:
			version_card = version[0].strip()
		else:
			version_card = "NVIDIA OLD"
	except:
		version_card = "NO CARD NVIDIA"
	
	try:
		nvidia = subprocess.check_output('nvcc --version'.split(' ')).decode()
		version = re.findall(r'release (\d+.\d),', nvidia)
		if len(version) > 0:
			if float(version[0]) >= 11.7:
				cuda_ok = True
			# print("Dùng GPU")
			else:
				cuda_ok = False
		else:
			cuda_ok = False
	except:
		cuda_ok = False
	return cuda_ok, version_card


class GroupBoxStartServerFFsub(QWidget):
	def __init__ (self, manage_thread_pool, manage_cmd):
		super().__init__()
		self.manage_thread_pool = manage_thread_pool
		self.manage_cmd = manage_cmd
		
		self.setup_ui()
		self.isStop = False
		self.isRuning = False
		settings =getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')

		self.PORT_FFSUB = settings.get("port_ffsub")
		self.URL_LOCAL_SERVER =  f"http://localhost:{self.PORT_FFSUB}"
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	
	def create_widgets (self):
		self.groupbox = QGroupBox("Khởi Tạo Server")
		
		self.btn_start = QPushButton("Start Server")
		self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_start.setDisabled(True)
		
		self.btn_stop = QPushButton("Stop Server")
		self.btn_stop.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_stop.setDisabled(True)
		
		self.btn_restart = QPushButton("ReStart")
		self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_restart.setDisabled(True)
		self.lb_status = QLabel()
		self.lb_use_gpu = QLabel()
		self.checkbox_use_gpu = QCheckBox("Use GPU")
		
	
	# self.lb_status = QLabel()
	
	def modify_widgets (self):
		self.btn_start.setDisabled(False)
		if os.path.exists(PATH_TOOL_FFSUB):
			if which(os.path.join(PATH_TOOL_FFSUB, FILE_NAME_FFSUB_EXE)) is None:
				self.lb_status.setText('''<a style="color:#eb3232">Tình trạng: Tool Chưa Cài Đặt</a>''')
			
			else:
				# self.btn_stop.setDisabled(False)
				self.btn_start.setDisabled(False)
				# self.btn_restart.setDisabled(False)
				self.lb_status.setText('''<a style="color:#eb3232">Tình trạng: Chưa Start Server</a>''')
		
		
		else:
			self.lb_status.setText('''<a style="color:#eb3232">Tình trạng: Tool Chưa Cài Đặt</a>''')
		
		cuda_ok, version_card = check_cuda_version()
		if cuda_ok:
			self.lb_use_gpu.setText('''<a style="color:#4dfc55">Có thể dùng GPU để tăng tốc</a>''')

			self.checkbox_use_gpu.setDisabled(False)
		else:
			self.lb_use_gpu.setText(f'''<a style="color:#eb3232">Chưa cài CUDA, Version Card: {version_card}</a>''')

			self.checkbox_use_gpu.setDisabled(True)
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		# self.file_input_layout = QHBoxLayout()
		self.groupbox_server_layout = QHBoxLayout()
		
		self.content_groupbox_layout = QVBoxLayout()
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		self.setLayout(self.bg_layout)
		
		self.groupbox.setLayout(self.content_groupbox_layout)
		
		self.content_groupbox_layout.addWidget(QLabel())
		self.content_groupbox_layout.addLayout(self.groupbox_server_layout)
		
		self.groupbox_server_layout.addWidget(self.checkbox_use_gpu, 10)
		self.groupbox_server_layout.addWidget(self.lb_use_gpu, 25)
		self.groupbox_server_layout.addWidget(self.btn_start, 10)
		self.groupbox_server_layout.addWidget(self.btn_stop, 10)
		self.groupbox_server_layout.addWidget(self.btn_restart, 10)
		self.groupbox_server_layout.addWidget(self.lb_status, 35, alignment=Qt.AlignmentFlag.AlignRight)
	
	
	def setup_connections (self):
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.btn_start.clicked.connect(self._click_start)
		self.btn_stop.clicked.connect(self._click_stop)
		self.btn_restart.clicked.connect(self._click_restart)
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == START_SERVER_FFSUB:
			try:
				is_ok, message = result
				if is_ok is False:
					self.lb_status.setText('''<a style="color:#eb3232">Status: Lỗi Xung Đột Reset Lại Máy Tính...</a>''')
					PyMessageBox().show_warning("Cảnh báo", message)
			except:
				pass
	def _funStart (self, **kwargs):
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		cmd = kwargs["cmd"]

 
		try:
			res = requests.get(self.URL_LOCAL_SERVER + "/check-gpu",timeout=0.5)
			if res.status_code == 200:
				return False, "Server Xung đột vui lòng Reset lại máy tính"
		except:
			pass
		self.lb_status.setText('''<a style="color:#ff8417">Status: Starting...</a>''')
		self.manage_thread_pool.start(self._check_server, "check_server" + uuid.uuid4().__str__(),
														  "check_server" + START_SERVER_FFSUB)
		
		# return
		self.process = subprocess.Popen(
			cmd,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			shell=False,
			creationflags=0x08000000,
			encoding='utf-8',
			errors='replace',
			# cwd='E:\Project\Python\TachSubVideo\\videocr-gpu\\ffusb_build\dist\\ffsub\\'
			# cwd=
		)
		self.manage_thread_pool.resultChanged.emit(PROCESS_FFSUB_THREAD, PROCESS_FFSUB_THREAD, self.process)
		while True:
			realtime_output = self.process.stdout.readline()
			if realtime_output == '' and self.process.poll() is not None:
				break
			if realtime_output:
				print(realtime_output.strip())
	
	
	def _check_server (self, **kwargs):
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		while self.isRuning:
			# print("check")
			try:
				res = requests.get(self.URL_LOCAL_SERVER + "/check-gpu")
				if res.status_code == 200:
					# data = res.json()
					# if data.get("cuda"):
					text = f"Running"
					# else:
					# 	text = f"Đang Chạy Bằng CPU, Driver Card: {data.get('driver')}"
					
					self.lb_status.setText(f'''<a style="color:#4dfc55">Status: {text} </a>''')
					self.manage_thread_pool.resultChanged.emit(START_SERVER_FFSUB_FINISHED, START_SERVER_FFSUB_FINISHED, True)
					# self.btn_start.setDisabled(True)
					self.btn_stop.setDisabled(False)
					self.btn_restart.setDisabled(False)
					return
			except:
				pass
			time.sleep(0.5)
	
	def _click_start (self):

		if self.isRuning is False:
			path_tool = os.path.join(PATH_TOOL_FFSUB, FILE_NAME_FFSUB_EXE)
			# path_tool = r"E:\Project\Python\TachSubVideo\videocr-gpu\ffusb_build\ffsub.py"
			# path_tool = r'E:\Project\Python\_APP\autosub\ffsub\\ffsub.exe'
			# # print(path_tool)cwd="/"
			user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
			# print(mh_ae({"cp":cr_pc(),"tc":TOOL_CODE_AUTOSUB,'t': int(float(time.time()))}))
			cmd = f'"{path_tool}" -p {self.PORT_FFSUB} -a {URL_API_BASE} -t {user_data.get("token")} -c {mh_ae_w({"cp":cr_pc("tool_code"),"tc":TOOL_CODE_MAIN, "t": int(float(time.time()))})}'
			# print(cmd)

			# if which(path_tool):
			self.btn_start.setDisabled(True)
			self.btn_stop.setDisabled(False)
			self.btn_restart.setDisabled(True)
			self.isRuning = True
			
			self.manage_thread_pool.start(self._funStart, START_SERVER_FFSUB,
				START_SERVER_FFSUB, cmd=cmd)

			
		# 	else:
		# 		PyMessageBox().show_error("Lỗi", "Tool Tách Sub Chưa Được Cài Đặt, Vui Lòng Liên Hệ Admin")
		else:
			PyMessageBox().show_warning("Cảnh báo", "Server Running")
	
	def _click_stop (self):
		if self.isRuning:
			self.isStop = True
			self.isRuning = False
			# print('vào')
			if hasattr(self, "process"):
				self.process.kill()
				self.process.terminate()
				self.lb_status.setText('''<a style="color:#eb3232">Status: Please, Start Server</a>''')
				self.btn_start.setDisabled(False)
				self.btn_stop.setDisabled(True)
	
	# print(self.process.pid)
	# try:
	# 	subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self.process.pid))
	# except:
	# 	pass
	
	def _click_restart (self):
		# if self.isRuning:
		# print(self.isRuning)
		self._click_stop()
		self._click_start()
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
