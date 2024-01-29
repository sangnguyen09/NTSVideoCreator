from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QTabWidget

from gui.helpers.server import TYPE_EXTRACT_SUB


class GroupBoxTachSub(QWidget):
	def __init__ (self, gbox_preview, manage_thread_pool, thread_pool_limit, manage_cmd, table_process, groupBox_start_server,settings):
		super().__init__()
		self.manage_thread_pool = manage_thread_pool
		self.thread_pool_limit = thread_pool_limit
		self.table_process = table_process
		self.groupBox_start_server = groupBox_start_server
		self.settings = settings
		self.manage_cmd = manage_cmd
		self.gbox_preview = gbox_preview
		
		self.list_server = []
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	
	def create_widgets (self):
		self.groupbox = QGroupBox("Phương Pháp Tách Sub")
		
		self.tab_extract = QTabWidget()
		self.tab_extract.setObjectName("tabWidget")
		self.tab_extract.setProperty("class", "tabSmall")
		
		for name, server in TYPE_EXTRACT_SUB.items():
			# self.tab_texttospeech.addTab(QWidget(), value)
			sv = server(self.gbox_preview, self.manage_thread_pool, self.thread_pool_limit, self.manage_cmd, self.table_process, self.groupBox_start_server,self.settings)
			self.tab_extract.addTab(sv, name)
			self.list_server.append(sv)
	
	
	def modify_widgets (self):
		self.groupbox.setDisabled(False)
	
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
		# self.manage_thread_pool.resultChanged.connect(self._resultThread)
		pass
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		for server in self.list_server:
			server.loadDataConfigCurrent(configCurrent)
