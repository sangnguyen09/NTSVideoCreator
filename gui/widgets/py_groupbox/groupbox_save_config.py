import json
import os

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGroupBox

from gui.db.sqlite import CauHinhTuyChon_DB
from gui.helpers.constants import SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, REFRESH_CONFIG_DATA_APP
from gui.helpers.custom_logger import decorator_try_except_class
from gui.helpers.func_helper import getValueSettings, setValueSettings
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_combobox import PyComboBox

style = '''
QRadioButton {{
    color: #c3f0ff;
    
}}
QRadioButton:hover {{

            color: #ff0000;

}}
QRadioButton:checked  {{
            color: #34c950;

}}

'''
# APPLY STYLESHEET
style_format = style.format()


class GroupBoxSaveConfig(QWidget, QObject):
	signalDataConfigCurrentChanged = Signal(object)  # object cấu hình hiện tại , chỉ cần khởi tạo db tại 1 cái rồi chuyền qua các Widget còn lại
	signalAddConfigDBChanged = Signal(str)
	signalAddNewClearDataChanged = Signal()
	
	def __init__ (self, manage_thread_pool: ManageThreadPool ):
		super().__init__()
 
		self.manage_thread_pool = manage_thread_pool
		# self.settings = QSettings(*SETTING_CONFIG)
		
		self.list_config = {}
		self.addConfig = False
		self.name_edit = ""
		self.configCurrent = None
		self.loadConfigFinish = False

		self.setup_ui()
		
		# self.loadConfig()
		self.button_save.setDisabled(True)
	
	def loadDataConfigCurrent (self, configCurrent,list_config, db_app, db_cau_hinh):
		
		self.loadConfigFinish = False
		
		self.cb_config_list.clear()
		
		self.configCurrent = configCurrent
		self.db_app = db_app
		self.db_cau_hinh = db_cau_hinh
		self.list_config = list_config
		self.cb_config_list.addItems([cf.ten_cau_hinh for cf in self.list_config])
		
		for idex, cf in enumerate(self.list_config):  # kiểm tra trạng thai cấu hình nào được active
			# print(int(configActive.configValue))
			if cf is configCurrent:
				self.cb_config_list.setCurrentIndex(idex)
				if idex == 0:
					self.configIndexChanged(idex)
				self.loadConfigFinish = True
				return
		# print('ddđ')
		self.loadConfigFinish = True
	
	def configIndexChanged (self, index):
		if len(self.list_config) > 0 and index >= 0 and (self.loadConfigFinish):  # cấu hình hiện tại
			
			self.saveConfigActive(self.list_config[index].id)
			# self.button_save.setDisabled(True)
			print('qua')
			self.manage_thread_pool.resultChanged.emit(REFRESH_CONFIG_DATA_APP, REFRESH_CONFIG_DATA_APP, "")
			
			print(REFRESH_CONFIG_DATA_APP)
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		self.text_edit_config_name = QLineEdit()
		self.cb_config_list = PyComboBox()
		self.button_save = QPushButton("Add")
		self.button_save.setCursor(Qt.CursorShape.PointingHandCursor)
		self.button_remove = QPushButton("Delete")
		self.button_remove.setCursor(Qt.CursorShape.PointingHandCursor)
	
	
	def modify_widgets (self):
		self.setStyleSheet(style_format)
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		self.groupbox = QGroupBox("Lưu Cấu Hình Tùy Chỉnh")
		
		self.gbox_layout = QVBoxLayout()
		self.content_layout = QVBoxLayout()
		self.btn_layout = QHBoxLayout()
		
		self.groupbox.setLayout(self.gbox_layout)
	
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		self.setLayout(self.bg_layout)
		self.gbox_layout.addWidget(QLabel(""))
		self.gbox_layout.addLayout(self.content_layout)
		
		self.content_layout.addWidget(QLabel("Chọn Cấu Hình"))
		self.content_layout.addWidget(self.cb_config_list)
		# self.content_layout.addWidget(QLabel("Đổi Tên Khác"))
		self.content_layout.addWidget(self.text_edit_config_name)
		self.content_layout.addLayout(self.btn_layout)
		
		self.btn_layout.addWidget(self.button_save)
		self.btn_layout.addWidget(self.button_remove)
	
	def setup_connections (self):
		self.cb_config_list.currentIndexChanged.connect(self.configIndexChanged)
		self.button_save.clicked.connect(self.saveConfig)
		self.button_remove.clicked.connect(self._removeConfig)
		self.text_edit_config_name.textChanged.connect(self.check_button_disabled)
	
	def check_button_disabled (self):
		text_edit = self.text_edit_config_name.text()
		self.button_save.setDisabled(True)
		if self.addConfig == True:  # thêm mới
			if not text_edit == "":
				self.button_save.setDisabled(False)
		elif self.addConfig is False:
			if not self.name_edit == text_edit:
				self.button_save.setDisabled(False)
	
	def saveConfigActive (self, id):
		if hasattr(self, "db_app") and self.db_app:
			configActive = self.db_app.select_one_name(
				"configNameActive")  # chọn cấu hình với tên được lưu configNameActive để lấy ra giá trị
			configActive.configValue = id
			configActive.save()
	
	# @decorator_try_except_class
	def addNewConfig (self, data_config):
		data_db = {}
		data_config.update({
			"remember_me": False,
			"lat_video": False,
			"change_md5": False,
			"tang_speed": False,
			"toc_do_tang_speed": 1.0,
			"ti_le_khung_hinh": "16:9",
			"chat_luong_video": "1920|1080",
			"dinh_dang_video": "mp4",
			"ten_hau_to_video": "finished",
			
			"vi_tri_sub_dich": 6,
			"style_sub_dich": False,
			"add_mau_sub_dich": False,
			"mau_sub_dich": "#ffffff",
			"opacity_mau_sub_dich": 100,
			"vien_sub_dich": False,
			"mau_vien_sub_dich": "#000000",
			"do_day_vien_sub_dich": "1px",
			"nen_sub_dich": False,
			"mau_nen_sub_dich": "#000000",
			"opacity_nen_sub_dich": 80,
			"font_sub_dich": False,
			"font_family_sub_dich": "Arial",
			"font_size_sub_dich": "12px",
			
			"vi_tri_sub": 2,
			"style_sub": False,
			"add_mau_sub": False,
			"mau_sub": "#ffffff",
			"opacity_mau_sub": 100,
			"vien_sub": False,
			"mau_vien_sub": "#000000",
			"do_day_vien_sub": "1px",
			"nen_sub": False,
			"mau_nen_sub": "#000000",
			"opacity_nen_sub": 80,
			"font_sub": False,
			"font_family": "Arial",
			"font_size": "12px",
		})
		if data_config is not None:
			data_db["ten_cau_hinh"] = self.text_edit_config_name.text()
			data_db["value"] = json.dumps(data_config)
			
			dataAdd, created = self.db_cau_hinh.insert_one(data_db)
			if created is False:
				self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", "Tên cấu hình đã bị trùng!", "warning")
			
			if created == True:
				self.saveConfigActive(dataAdd.id)
				self.text_edit_config_name.clear()
				self.manage_thread_pool.resultChanged.emit(REFRESH_CONFIG_DATA_APP, REFRESH_CONFIG_DATA_APP, "")
	
	
	# @decorator_try_except_class
	def saveConfig (self):
		self.signalAddConfigDBChanged.emit(self.text_edit_config_name.text())
 
	
	
	#
	# new_file = os.path.join(db_path, self.config_current.ten_cau_hinh + '.dat')
	# # rename file
	# if os.path.isfile(old_file):
	#     os.rename(old_file, new_file)
	
	# @decorator_try_except_class
	def _removeConfig (self):
		if self.configCurrent.ten_cau_hinh == 'default':
			return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", "không thể xoá cấu hình default", "warning")
		
		id_remove = self.configCurrent.id
		
		result = self.db_cau_hinh.remove_one(id_remove)
		if result == 1:
			self.cb_config_list.setCurrentText("default")
			conf = self.list_config[self.cb_config_list.currentIndex()]
			self.saveConfigActive(conf.id)
			
			list_cofig = getValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN)
			if list_cofig is not None:
				if str(id_remove) in list_cofig.keys():
					del list_cofig[str(id_remove)]
					setValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, list_cofig)
			# self.settings.remove((str(id_remove)))
			
			self.manage_thread_pool.resultChanged.emit(REFRESH_CONFIG_DATA_APP, REFRESH_CONFIG_DATA_APP, "")
