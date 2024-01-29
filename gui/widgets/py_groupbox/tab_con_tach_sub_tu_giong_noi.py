# from gui.helpers.server import SERVER_EXTRACT_VOICE
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QGroupBox, QTabWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel

from gui.helpers.constants import LOAD_FILE_EXTRACT_FINISHED, START_SERVER_FFSUB_FINISHED


class TabConTachSubTuGiongNoi(QWidget):
	
	def __init__ (self, gbox_preview, manage_thread_pool, thread_pool_limit, manage_cmd,
				  table_process,
				  groupBox_start_server, settings, SERVER_EXTRACT_VOICE, NAME_AI_LOCAL):
		super().__init__()
		self.manage_thread_pool = manage_thread_pool
		self.thread_pool_limit = thread_pool_limit
		self.table_process = table_process
		self.groupBox_start_server = groupBox_start_server
		self.manage_cmd = manage_cmd
		self.server_extract_voice = SERVER_EXTRACT_VOICE
		self.NAME_AI_LOCAL = NAME_AI_LOCAL
		self.settings = settings
		self.list_server = {}
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	
	def create_widgets (self):
		self.groupbox = QGroupBox("Chuyển giọng nói thành chữ")
		
		self.tab_extract = QTabWidget()
		self.tab_extract.setObjectName("tabWidget")
		self.tab_extract.setProperty("class", "tabSmall")
		#
		# self.tab_con_google = PyTabExtractSubGoogle(self.groupbox, self.manage_thread_pool, self.thread_pool_limit, self.manage_cmd, self.table_process, self.groupBox_network)
		# self.tab_con_ai = PyTabExtractSubAI(self.groupbox, self.manage_thread_pool, self.thread_pool_limit, self.manage_cmd, self.table_process, self.groupBox_network)
		#
		
		for name, server in self.server_extract_voice.items():
			# self.tab_texttospeech.addTab(QWidget(), value)
			sv = server(self.groupbox, self.manage_thread_pool, self.thread_pool_limit, self.manage_cmd, self.table_process, self.groupBox_start_server, self.settings)
			self.tab_extract.addTab(sv, name)
			self.list_server[name] = sv
		# print(1)
		# self.tab_extract.addTab(self.tab_con_ai, "Dùng AI")
		
		self.btn_convert = QPushButton("Convert")
		self.btn_convert.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_convert.setProperty("class", "small_button")
	
	def modify_widgets (self):
		# self.groupbox.setDisabled(True)
		pass
	
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
		self.content_groupbox_layout.addWidget(self.tab_extract)
	
	def setup_connections (self):
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
	
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == START_SERVER_FFSUB_FINISHED:  # start server finish
			self.list_server.get(self.NAME_AI_LOCAL).setDisabled(False)
		
		if id_thread == LOAD_FILE_EXTRACT_FINISHED:  # khi load file xong truyền biến file vào các tab
			# self.groupbox.setDisabled(False)
			for name, server in self.list_server.items():
				if name != self.NAME_AI_LOCAL:
					server.setDisabled(False)
				server.loadFileInput(result)
	
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		for name, server in self.list_server.items():
			server.loadDataConfigCurrent(configCurrent)
# print(2)
