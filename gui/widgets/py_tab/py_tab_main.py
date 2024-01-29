# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QTabWidget

from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import CauHinhTuyChon_DB, ConfigApp_DB, ConfigEditSub_DB
from gui.helpers.constants import TOOL_CODE_MAIN, USER_DATA, \
	TOGGLE_SPINNER, REFRESH_CONFIG_FILE_SRT, REFRESH_CONFIG_DATA_APP, \
	NOTIFICATION_TOGGLE_CHANGED, REFRESH_REMOVE_CONFIG_FILE_SRT
from gui.helpers.func_helper import getValueSettings
from gui.helpers.thread import ManageCMD
from gui.widgets.py_graphics.py_graphic_view_notify import GraphicViewNotify
from gui.widgets.py_groupbox.overlay_widget import TextOverlayWidget
from gui.widgets.py_spinner.spinner import WaitingSpinner
from gui.widgets.py_tab.py_tab_main_addsub import PyTabAddSub
from gui.widgets.py_tab.py_tab_main_edit_sub import PyTabEditSub
from gui.widgets.py_tab.py_tab_shop import PyTabShop


class PyTab(QWidget):
	def __init__ (self, file_run_app, manage_thread_pool, settings):
		super().__init__()
		# st = QSettings(*SETTING_APP)
		self.settings = settings
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		self.file_run_app = file_run_app
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self.resultChanged)
		
		self.manage_cmd = ManageCMD(self.manage_thread_pool)  # tạo trước ui
		self.count_split_sub = 0
		self.fileSRTCurrent = None
		self.configCurrent = None
		self.isLoaded = False
		self.db_cau_hinh = CauHinhTuyChon_DB()
		self.db_app = ConfigApp_DB()
		self.db_list_file_srt = ConfigEditSub_DB()
		
		self.loadConfigDB()
		self.loadFileSrt()
		
		self.setup_ui()
	
	def loadConfigDB (self):
		list_config_db = self.db_cau_hinh.select_all()
		configNameActive = self.db_app.select_one_name("configNameActive")
		self.list_config = []
		
		for idx, cf in enumerate(list_config_db):
			self.list_config.append(cf)
		# print(configNameActive.configValue)
		
		for idex, cf in enumerate(self.list_config):  # kiểm tra trạng thai cấu hình nào được active
			if cf.id == int(configNameActive.configValue):
				self.configCurrent = cf
	
	def loadFileSrt (self):
		list_file_srt_db = self.db_list_file_srt.select_all()
		configEditSubActive = self.db_app.select_one_name("configEditSubActive")
		
		# xoá dữ liệu cũ
		self.list_srt = []
		
		for idx, cf in enumerate(list_file_srt_db):
			self.list_srt.insert(0, cf)
		
		for idex, cf in enumerate(self.list_srt):  # kiểm tra trạng thai cấu hình nào được active
			if self.isLoaded:
				if idex == int(configEditSubActive.configValue):
					self.fileSRTCurrent = cf
			else:
				if cf.id == 1:
					self.fileSRTCurrent = cf
					self.isLoaded = True
	
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		# BG FRAME
		self.bg_frame = QFrame()
		self.bg_frame.setObjectName("bg_frame")
		# Tạo Tab Main
		self.tabWidget = QTabWidget()
		self.tabWidget.setObjectName("tabWidget")
		
		self.view_notify = GraphicViewNotify(self.manage_thread_pool)
		
		if self.user_data["list_tool"].get(TOOL_CODE_MAIN) is not None:
			self.tab_add_sub = PyTabAddSub(self.manage_thread_pool, self.manage_cmd, self.file_run_app, self.settings, self.fileSRTCurrent, self.configCurrent)
			# self.tab_genenate_sub = PyTabGenerateSub(self.manage_thread_pool, self.manage_cmd, self.settings)  # cái này phải được khởi tạo trước add sub
			
			self.tab_edit_sub = PyTabEditSub(self.manage_thread_pool, self.manage_cmd, self.settings)  # cái này phải được khởi tạo trước add sub
			
			self.loadConfigCurrent()
			self.loadFileSRTCurrent()
			
			self.tab_shop = PyTabShop(self.manage_thread_pool, self.user_data.get('token'))
			
			# self.tabWidget.addTab(self.tab_genenate_sub, "B1: TÁCH SUB")
			
			self.tabWidget.addTab(self.tab_edit_sub, "B2: SỬA Và DỊCH SUB")
			# if 'long_tieng' in setting_user.get('tab'):
			self.tabWidget.addTab(self.tab_add_sub, "B3: Lồng Tiếng")
			self.tabWidget.addTab(self.tab_shop, "NTS SHOP")
		
		# if 'tach_sub' in setting_user.get('tab'):
		
		self.spiner = WaitingSpinner(
			self.tabWidget,
			roundness=100.0,
			# opacity=24.36,
			fade=15.719999999999999,
			radius=20,
			lines=12,
			line_length=22,
			line_width=12,
			speed=1.1,
			color=QColor(85, 255, 127),
			modality=Qt.ApplicationModal,
			disable_parent_when_spinning=True
		)
		self.spiner.stop()
	
	# self.text_overlay =
	
	def setup_connections (self):
		pass
	
	def loadConfigCurrent (self):
		# print(self.configCurrent.ten_cau_hinh)
		self.tab_add_sub.loadDataConfigCurrent(self.configCurrent, self.list_config, self.db_app, self.db_cau_hinh)
		self.tab_edit_sub.loadDataConfigCurrent(self.configCurrent)
	
	def loadFileSRTCurrent (self):
		self.tab_edit_sub.loadFileSRTCurrent(self.fileSRTCurrent, self.list_srt, self.db_app, self.db_list_file_srt)
		self.tab_add_sub.loadFileSRTCurrent(self.fileSRTCurrent, self.db_app, self.db_list_file_srt)
	
	#
	# 	self.configCurrent = fileSRTCurrent
	# 	self.tab_add_sub.loadFileSRTCurrent(fileSRTCurrent)
	
	def resultChanged (self, id_worker, typeThread, result):
		#
		if typeThread == REFRESH_CONFIG_DATA_APP:
			self.loadConfigDB()
			self.loadConfigCurrent()
			self.loadFileSRTCurrent()
		
		if typeThread == REFRESH_REMOVE_CONFIG_FILE_SRT:
			# print("dddddddddđ")
			self.isLoaded = False
			self.loadFileSrt()
			self.loadFileSRTCurrent()
		if typeThread == REFRESH_CONFIG_FILE_SRT:
			# print(REFRESH_CONFIG_FILE_SRT)
			self.loadFileSrt()
			self.loadFileSRTCurrent()
		
		if typeThread == TOGGLE_SPINNER:
			if result is True:
				self.spiner.start()
			elif result is False:
				self.spiner.stop()
			# self.text_overlay.stop()
		# elif isinstance(result, str):
		# self.text_overlay.update_text(result)
		# self.text_overlay.start()
		
		if typeThread == NOTIFICATION_TOGGLE_CHANGED:
			if result:
				self.view_notify.show()
			else:
				self.view_notify.hide()
	
	def modify_widgets (self):
		setting_user = self.user_data["list_tool"].get(TOOL_CODE_MAIN)
		# print(setting_user)
		
		if not 'tach_sub' in setting_user.get("tab", []):
			tex_overlay = TextOverlayWidget(self.tab_genenate_sub, "Bấm vào Tab NTS SHOP để nâng cấp chức năng TÁCH SUB", overlay_width=800, overlay_height=100)
			tex_overlay.show()
			
		if not 'long_tieng' in setting_user.get("tab", []):
			tex_overlay = TextOverlayWidget(self.tab_add_sub, "Bấm vào Tab NTS SHOP để nâng cấp chức năng LỒNG TIẾNG",overlay_width=800, overlay_height=100)
			tex_overlay.show()
	
	# pass
	
	# self.tabWidget.setStyleSheet(tab_main_style())
	
	def create_layouts (self):
		self.widget_layout = QHBoxLayout()
		self.widget_layout.setContentsMargins(0, 0, 0, 0)
		
		self.bg_layout = QVBoxLayout(self)
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
	
	
	def add_widgets_to_layouts (self):
		# self.widget_layout.addWidget(self.bg_frame)
		self.bg_layout.addWidget(self.view_notify, 3, alignment=Qt.AlignmentFlag.AlignVCenter)
		self.bg_layout.addWidget(self.tabWidget)
	
	def mouseDoubleClickEvent (self, e):
		
		if self.spiner.is_spinning:
			self.spiner.stop()
			print("stop")
			# if self.text_overlay.is_showing:
			# 	self.text_overlay.stop()
			print("stop")
