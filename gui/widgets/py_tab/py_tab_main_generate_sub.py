# -*- coding: utf-8 -*-
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QGroupBox, QCheckBox

from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import ConfigApp_DB, CauHinhTuyChon_DB
from gui.helpers.constants import LOAD_CONFIG_CHANGED, TOOL_CODE_MAIN, \
	USER_DATA, LOAD_VIDEO_FROM_DROP_FILE
from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from ..py_groupbox.groupbox_show_screen_tab_detect_sub import GroupBoxShowScreenTabDetectSub
from ..py_groupbox.groupbox_start_server_ffsub import GroupBoxStartServerFFsub
from ..py_groupbox.groupbox_tach_sub import GroupBoxTachSub
from ..py_messagebox.py_massagebox import PyMessageBox
from ..py_resize.splitter_resize import Resize_Splitter
from ..py_table_widget.table_process_extract import TableProcessExtractSUB
from ...db.sqlite import CauHinhTuyChonModel
from ...helpers.func_helper import getValueSettings
from ...helpers.thread import ManageCMD


class PyTabGenerateSub(QWidget):
	def __init__ (self, manage_thread_pool: ManageThreadPool, manage_cmd: ManageCMD, settings):
		super().__init__()
		# PROPERTIES
		# st = QSettings(*SETTING_APP)
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		# settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		self.settings = settings
		
		self.LANGUAGES_CHANGE_CODE = settings.get("language_support").get('language_code')
		
		self.db_cau_hinh = CauHinhTuyChon_DB()
		self.db_app = ConfigApp_DB()
		self.row_number = 0
		self.list_worker_tts = {}
		self.manage_thread_pool = manage_thread_pool  # tạo trước ui
		self.thread_pool_limit = ManageThreadPool()
		self.thread_pool_limit.setMaxThread(self.user_data["list_tool"][TOOL_CODE_MAIN]["thread"])
		# self.thread_pool_limit.setMaxThread(1)
		self.setAcceptDrops(True)
		self.manage_cmd = manage_cmd  # tạo trước ui
		
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		
		self.modify_widgets()
		
		self.create_layouts()
		
		self.add_widgets_to_layouts()
	
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		self.tab_addsub = QWidget()
		self.resize_splitter = Resize_Splitter()
		self.resize_splitter_right_left = Resize_Splitter()
		# =========== Layout bên  Trái ===========
		self.tab_addsub_left = QWidget()
		
		self.bg_left_frame = QFrame()
		self.bg_left_frame.setObjectName("bg_frame")
		# self.groupbox_timeline = TableTimelineExtract(self.manage_thread_pool, self.manage_cmd)
		self.groupbox_setting = QGroupBox("SETTING")
		self.check_box_auto_create = QCheckBox("Tự Động Tạo File Qua Tab Sửa Sub")
		self.check_box_auto_create.setChecked(True)
		
		self.groupbox_process_render = TableProcessExtractSUB(self.manage_thread_pool, self.thread_pool_limit, self.check_box_auto_create)
		
		self.gbox_preview = GroupBoxShowScreenTabDetectSub(self.manage_thread_pool, self.manage_cmd, self.thread_pool_limit, self.groupbox_process_render)
		
		# =========== Layout bên  Phải ===========
		self.tab_addsub_right = QWidget()
		self.bg_right_frame = QFrame()
		self.bg_right_frame.setObjectName("bg_frame")
		# self.groupBox_network = GroupBoxNetwork(self.manage_thread_pool, is_save_db=True)
		self.groupBox_start_server = GroupBoxStartServerFFsub(self.manage_thread_pool, self.manage_cmd)
		
		self.groupBox_extract_sub = GroupBoxTachSub(self.gbox_preview, self.manage_thread_pool, self.thread_pool_limit, self.manage_cmd,
			self.groupbox_process_render, self.groupBox_start_server, self.settings)
		

	# self.video_render = RenderVideo(self.manage_thread_pool,self.manage_cmd, self.db_app)
	# self.groupbox_features = GroupboxTranslateSub(self.manage_thread_pool, self.groupbox_timeline, self.groupBox_network,self.settings)
	# self.groupbox_features = GroupBoxTranlateSub(self.manage_thread_pool, self.groupbox_timeline, self.groupBox_network)
	
	def modify_widgets (self):
		setting_user = self.user_data["list_tool"].get(TOOL_CODE_MAIN)
		if not 'tach_sub' in setting_user.get("tab", []):
			self.groupBox_start_server.setDisabled(True)
			self.gbox_preview.setDisabled(True)
			self.groupBox_extract_sub.setDisabled(True)
			self.groupbox_process_render.setDisabled(True)
	
	def create_layouts (self):
		self.bg_layout = QVBoxLayout(self)  # lấy self làm cha , tức là bg_layout làm con của self
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_tab_layout = QHBoxLayout()
		
		# layout bên trái
		self.content_left_layout = QVBoxLayout(self.bg_left_frame)
		self.tab_addsub_left_layout = QVBoxLayout()
		self.tab_addsub_left_layout.setContentsMargins(0, 0, 0, 0)
		
		# layout bên phải
		self.content_right_layout = QVBoxLayout(self.bg_right_frame)
		# self.content_right_layout.setContentsMargins(0, 0, 0, 0)
		
		self.tab_addsub_right_layout = QVBoxLayout()
		self.tab_addsub_right_layout.setContentsMargins(0, 0, 0, 0)
		
		self.convert_layout = QHBoxLayout()
		self.convert_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_config_layout = QHBoxLayout()
		self.content_config_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_setting_layout = QHBoxLayout()
		# self.content_setting_layout.setContentsMargins(0, 0, 0, 0)
		
		self.bottom_layout = QHBoxLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.resize_splitter.setOrientation(Qt.Orientation.Vertical)
		self.resize_splitter_right_left.setOrientation(Qt.Orientation.Horizontal)
		
		self.tab_addsub.setLayout(self.content_tab_layout)
		widget_bottom = QWidget()
		widget_bottom.setLayout(self.bottom_layout)
		
		self.resize_splitter.addWidget(self.tab_addsub)
		# self.resize_splitter.addWidget(widget_bottom)
		
		self.bg_layout.addWidget(self.resize_splitter)  # chiếm 70% vùng chứa
		# self.bg_layout.addLayout(self.bottom_layout, 30)
		
		# self.bottom_layout.addWidget(self.groupbox_timeline, 80)
		# self.bottom_layout.addWidget(self.groupbox_features, 20)
		
		widget_left = QWidget()
		widget_left.setLayout(self.tab_addsub_left_layout)
		widget_right = QWidget()
		widget_right.setLayout(self.tab_addsub_right_layout)
		self.resize_splitter_right_left.addWidget(widget_left)
		self.resize_splitter_right_left.addWidget(widget_right)
		
		self.content_tab_layout.addWidget(self.resize_splitter_right_left)
		# self.content_tab_layout.addLayout(self.tab_addsub_right_layout, 60)
		
		# ====== layout bên trái=======
		self.tab_addsub_left_layout.addWidget(self.bg_left_frame)
		self.content_left_layout.addWidget(self.groupBox_start_server, 10)
		self.content_left_layout.addWidget(self.groupBox_extract_sub, 40)
		self.content_left_layout.addWidget(self.groupbox_setting, 10)
		self.content_left_layout.addWidget(self.groupbox_process_render, 40)
		
		self.groupbox_setting.setLayout(self.content_setting_layout)
		
		self.content_setting_layout.addWidget(self.check_box_auto_create)
		# #====== layout bên phải =======
		self.tab_addsub_right_layout.addWidget(self.bg_right_frame)
		self.content_right_layout.addWidget(self.gbox_preview)
	
	
	def setup_connections (self):
		self.gbox_preview.sliderChangeFrameChanged.connect(self.sliderChangeFrameChanged)
		self.manage_thread_pool.resultChanged.connect(self._resultThreadChanged)
	
	def sliderChangeFrameChanged (self, data):
		pass
	
	# self.groupbox_timeline.main_table.selectRow(data - 1)
	
	def _resultThreadChanged (self, id_worker, id_thread, result):
		# print(id_worker, id_thread)
		if id_thread == LOAD_CONFIG_CHANGED:
			self.loadDataConfigCurrent(result)
	
	def loadDataConfigCurrent (self, configCurrent: CauHinhTuyChonModel):
		# print("loadDataConfigCurrent")
		
		self.configCurrent = configCurrent
		
		# self.groupBox_network.loadData(configCurrent)
		self.groupBox_extract_sub.loadData(configCurrent)
		self.gbox_preview.loadData(configCurrent)
		# self.groupbox_features.loadData(configCurrent)
		self.groupbox_process_render.loadData(configCurrent)
	
	# print(json.loads(self.configCurrent.value))
	
	# self.video_render.loadData(configCurrent)
	
	def showData (self, data):
		pass
	
	def dragEnterEvent (self, event):
		# print('drag-enter')
		if event.mimeData().hasUrls():
			# print('has urls')
			event.accept()
		else:
			event.ignore()
	
	def dropEvent (self, event):
		lines = []
		for url in event.mimeData().urls():
			lines.append(url.toLocalFile())
		if len(lines) > 0:
			srt_path = lines[0]
			if os.path.isfile(srt_path) is True:
				# filter = 'File Video (*.mp4 *.avi *wmv *mkv *mov)')
				name, ext = os.path.splitext(srt_path)
				if not ext.lower() in ['.mp4', '.avi', '.wmv', '.mkv', '.mov']:
					return PyMessageBox().show_warning("Thông báo", f"File {ext} không được hỗ trợ")
				self.manage_thread_pool.resultChanged.emit(LOAD_VIDEO_FROM_DROP_FILE, LOAD_VIDEO_FROM_DROP_FILE, srt_path)
			else:
				return PyMessageBox().show_warning("Thông báo", "File video không không tồn tại ")
