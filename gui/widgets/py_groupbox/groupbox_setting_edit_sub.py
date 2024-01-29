# -*- coding: utf-8 -*-
import json

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout

from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import ConfigEditSub_DB, ConfigApp_DB
from gui.helpers.constants import USER_DATA, TOOL_CODE_MAIN, TRANSLATE_SUB_PART_TAB_EXTRACT, \
	LOAD_CONFIG_TAB_EDIT_SUB_CHANGED
from gui.helpers.func_helper import getValueSettings
from gui.helpers.thread import ManageThreadPool
from gui.helpers.translatepy.utils.lru_cacher import LRUDictCache
from gui.widgets.py_groupbox.groupbox_config_edit_sub import GroupBoxConfigEditSub


class GroupboxSetting(QWidget):
	def __init__ (self, manage_thread_pool, table_timeline, settings):
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		
		self.thread_pool_limit = ManageThreadPool()
		self.thread_pool_limit.setMaxThread(10)
		self.table_timeline_editsub = table_timeline
		self.translate_cache = LRUDictCache()
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		
		self.isStop = False
		self.isStatusTranslate = False
		super().__init__()
		# PROPERTIES
		# settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		
		self.path_srt = ''
		self.path_video = ''
		self.isLoad = True
		self.load_file_srt_finished = False
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		self.groupbox = QGroupBox("Phụ trợ")
		
		self.groupbox_config = GroupBoxConfigEditSub(self.manage_thread_pool)
		
		self.lb_token_chatgpt = QLabel("")
	
	def modify_widgets (self):
		# self.progess_convert.hide()
		pass
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_layout = QVBoxLayout()
		# self.content_layout.setContentsMargins(0, 0, 0, 0)
		
		# self.gbox_layout = QVBoxLayout()
		self.groupbox.setLayout(self.content_layout)
		
		self.content_chat_language = QHBoxLayout()
		self.content_language_layout = QHBoxLayout()
		
		self.progess_convert_layout = QHBoxLayout()
		self.content_file_layout = QHBoxLayout()
		self.content_btn_layout = QGridLayout()
		self.content_status = QGridLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		# self.bg_layout.addWidget(self.groupbox)
		self.bg_layout.addWidget(self.groupbox_config)
		self.setLayout(self.bg_layout)
	
	# self.setLayout(self.content_layout)
	
	
	def setup_connections (self):
		# self.groupbox_config.signalRefeshChanged.connect(self.refeshDataConfig)
		
		# self.groupbox_config.signalDataConfigCurrentChanged.connect(self.loadDataConfigCurrent)
		
		# self.groupbox_config.loadConfig()  # tạo xong widgets thì mới đến connections  nên gọi loadConfig o đây mới nhận đc tín hiệu
		
		# self.btn_dialog_file_srt.clicked.connect(self._openDialogFileSrt)
		
		# self.btn_save_srt.clicked.connect(self.save_srt)
		pass
	
	
	# #
	# def refeshDataConfig (self):
	# 	print('refeshDataConfig')
	
	def addConfigStatus (self):
		print(111)
	
	
	def loadDataConfigCurrent (self, configCurrent):
		# print("loadDataConfigCurrent")
		
		self.configCurrent = configCurrent
		self.groupbox_config.loadDataConfigCurrent(configCurrent)
	
	def loadFileSRTCurrent (self, fileSRTCurrent, list_srt, db_app, db_list_file_srt):
		self.fileSRTCurrent = fileSRTCurrent
		
		# cau_hinh: dict = json.loads(fileSRTCurrent.value)
		
		self.groupbox_config.loadFileSRTCurrent(fileSRTCurrent, list_srt, db_app, db_list_file_srt)
	
	def _resultThread (self, id_worker, id_thread, result):
		if id_thread == LOAD_CONFIG_TAB_EDIT_SUB_CHANGED:
			print("LOAD_CONFIG_TAB_EDIT_SUB_CHANGED")
# self.loadFileSRTCurrent(result)

# self.btn_convert.setDisabled(False)
# self._translateStartThread(list_sequences=result)
