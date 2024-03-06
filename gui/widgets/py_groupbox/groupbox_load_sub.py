import json
import os
import subprocess

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QFileDialog

from gui.helpers.constants import CHANGE_HIEN_THI_TAB_EDIT_SUB, ADDNEW_SRT_FILE_EDIT_SUB, \
	CHANGE_HIEN_THI_TAB_ADD_SUB, REMOVE_CONFIG_FILE_SRT, LOAD_VIDEO_FROM_FILE_SRT, JOIN_PATH, REFRESH_CONFIG_FILE_SRT
from gui.helpers.server import TYPE_TTS_SUB
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_combobox import PyComboBox
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox

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


class GroupBoxLoadSub(QWidget, QObject):
	signalDataConfigCurrentChanged = Signal(object)  # object cấu hình hiện tại , chỉ cần khởi tạo db tại 1 cái rồi chuyền qua các Widget còn lại
	signalAddConfigDBChanged = Signal(str)
	signalAddNewClearDataChanged = Signal()
	
	def __init__ (self, manage_thread_pool: ManageThreadPool):
		super().__init__()
		# self.db_app = db_app
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		
		# self.settings = QSettings(*SETTING_CONFIG)
		
		self.list_config = []
		self.loadConfigFinish = False
		self.name_edit = ""
		self.fileSRTCurrent = None

		self.setup_ui()
	
	# self.loadConfig()
	
	
	def loadFileSRTCurrent (self, fileSRTCurrent, list_project, db_app, db_cau_hinh):
		self.loadConfigFinish = False

		self.cb_config_list.clear()

		self.fileSRTCurrent = fileSRTCurrent
		# self.text_edit_config_name.setText(fileSRTCurrent.ten_cau_hinh)
		# self.name_edit = fileSRTCurrent.ten_cau_hinh
		cau_hinh = json.loads(fileSRTCurrent.value)
		sub_hien_thi = cau_hinh.get('sub_hien_thi', 'origin')
		self.cbox_sub_hien_thi.setCurrentText(TYPE_TTS_SUB.get(sub_hien_thi))

		# self.checkbox_auto_play.setChecked(cau_hinh.get('auto_play', True))
		# self.slider_volume.setValue(cau_hinh.get('volume_phat', 100))

		self.db_app = db_app
		self.db_cau_hinh = db_cau_hinh
		self.list_config = list_project
		self.cb_config_list.addItems([cf.ten_cau_hinh for cf in self.list_config])

		for idex, cf in enumerate(self.list_config):  # kiểm tra trạng thai cấu hình nào được active
			# print(int(configActive.configValue))
			if cf is fileSRTCurrent:
				self.cb_config_list.setCurrentIndex(idex)
				if idex == 0:
					self.configIndexChanged(idex)

				self.loadConfigFinish = True

				return
		# print('ddđ')
		self.loadConfigFinish = True
		# self.db_srt_file = db_srt_file
		# self.db_app = db_app
		
		# self.fileSRTCurrent = fileSRTCurrent

		# self.refreshData()
		# self.loadConfigFinish = True
	
	
	# self.signalDataConfigCurrentChanged.emit(self.db_cau_hinh, self.list_config[idex]) # bỏ load dữ liệu qua các widgets khác
	def configIndexChanged(self, index):

		if len(self.list_config) > 0 and index >= 0 and (self.loadConfigFinish):  # cấu hình hiện tại
			# print('1111111')
			self.saveConfigActive(index)

			self.manage_thread_pool.resultChanged.emit(REFRESH_CONFIG_FILE_SRT, REFRESH_CONFIG_FILE_SRT, "")
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		self.groupbox = QGroupBox("Project Info")
		
		# self.text_src_file = PyComboBox()
		self.cb_config_list = PyComboBox()
		# self.text_src_file.setReadOnly(True)  # chỉ đọc
		# self.cb_config_list = PyComboBox()

		self.cbox_sub_hien_thi = PyComboBox()
		self.cbox_sub_hien_thi.addItems(list(TYPE_TTS_SUB.values()))

		
		# self.lb_file_srt = QLabel("Load File .SRT có sẵn:")
		self.btn_dialog_file_srt = QPushButton("Load Folder Image")
		self.btn_dialog_file_srt.setCursor(Qt.CursorShape.PointingHandCursor)
		
		# self.btn_dialog_file_srt = QPushButton("Show Dữ Liệu")
		self.button_remove = QPushButton("Xóa Project")
		self.button_remove.setCursor(Qt.CursorShape.PointingHandCursor)
	
	
	def modify_widgets (self):
		self.setStyleSheet(style_format)
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		self.gbox_layout = QVBoxLayout()
		self.content_layout = QVBoxLayout()
		self.content_top_layout = QHBoxLayout()
		self.content_mid_layout = QHBoxLayout()
		self.content_btn_layout = QHBoxLayout()
		self.groupbox.setLayout(self.gbox_layout)
	
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		self.setLayout(self.bg_layout)
		self.gbox_layout.addLayout(self.content_layout)
		
		self.content_layout.addWidget(QLabel(""))
		self.content_layout.addLayout(self.content_top_layout)
		self.content_layout.addLayout(self.content_mid_layout)
		# self.content_layout.addLayout(self.content_btn_layout)
		
		
		self.content_top_layout.addWidget(QLabel("Chọn Project Hiển Thị: "), 10)
		self.content_top_layout.addWidget(self.cb_config_list, 45)
		self.content_top_layout.addWidget(self.btn_dialog_file_srt, 30)
		self.content_top_layout.addWidget(self.button_remove, 15)
		
		self.content_mid_layout.addWidget(QLabel("Hiển Thị Văn Bản:"))
		self.content_mid_layout.addWidget(self.cbox_sub_hien_thi)
		self.content_mid_layout.addWidget(QLabel(""), 20)
	
	
	def setup_connections (self):
		self.cb_config_list.currentIndexChanged.connect(self.configIndexChanged)
		self.cbox_sub_hien_thi.currentIndexChanged.connect(self.cbox_sub_hien_thiChanged)
		# self.button_save.clicked.connect(self.saveConfig)
		self.button_remove.clicked.connect(self._removeConfig)
		# self.text_edit_config_name.textChanged.connect(self.check_button_disabled)
		self.btn_dialog_file_srt.clicked.connect(self._openDialogFileSrt)
	
	# self.btn_export_srt.clicked.connect(self.clickSaveFile)
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == LOAD_VIDEO_FROM_FILE_SRT:
			self.loadVideoData(result)
			
		if id_thread == CHANGE_HIEN_THI_TAB_EDIT_SUB:
			self.cbox_sub_hien_thi.setCurrentText(TYPE_TTS_SUB.get(result))
		
		# if id_thread == LOAD_CONFIG_TAB_EDIT_SUB_CHANGED:
		#
		# 	if result:
		# 		# print(result)
		# 		self.fileSRTCurrent = result
		# 		self.refreshData()
	
	# def refreshData (self):
	# 	# print(self.fileSRTCurrent)
	# 	if hasattr(self, 'fileSRTCurrent') and self.fileSRTCurrent:
	# 		self.cb_config_list.setText(self.fileSRTCurrent.ten_cau_hinh)
	
	# @decorator_try_except_class
	def _removeConfig (self):
		
		self.manage_thread_pool.resultChanged.emit(REMOVE_CONFIG_FILE_SRT, REMOVE_CONFIG_FILE_SRT, "")
	
	def loadVideoData (self, folder_name):
		if os.path.isdir(folder_name):
			cmd = '''powershell -Command "(Get-ChildItem | Sort-Object { [regex]::Replace($_.Name, '\d+', { $args[0].Value.PadLeft(20) }) }).Name"'''
			process = subprocess.Popen(cmd, shell=True,
									   cwd=rf'{folder_name}',
									   stdout=subprocess.PIPE,
									   stderr=subprocess.PIPE)
			out = process.communicate()[0].decode('ascii').split('\r\n')
			# list_file_image = []
			data_table = []

			# num_max=1
			for file_name_ in out:
				name, ext = os.path.splitext(file_name_)
				if ext.lower() in ['.jpg', '.png', '.jpeg']:
					data_table.append([JOIN_PATH(folder_name, file_name_), "", ""])

			# print(data_table)
			if len(data_table) < 1:
				return PyMessageBox().show_error('Cảnh Báo', "Không tìm thấy file hình ảnh nào!")

			self.manage_thread_pool.resultChanged.emit(ADDNEW_SRT_FILE_EDIT_SUB, ADDNEW_SRT_FILE_EDIT_SUB, (
				folder_name, data_table))
	
	def _openDialogFileSrt (self):
		folder_name = QFileDialog.getExistingDirectory(self, caption='Chọn thư mục hình ảnh')
		# if os.path.isdir(folder_name):
		self.loadVideoData(folder_name)
	

	
	def cbox_sub_hien_thiChanged (self, index):
		if hasattr(self, "fileSRTCurrent") and self.fileSRTCurrent:
			cau_hinh = json.loads(self.fileSRTCurrent.value)
			cau_hinh["sub_hien_thi"] = list(TYPE_TTS_SUB.keys())[index]  # vi,en
			self.fileSRTCurrent.value = json.dumps(cau_hinh)
			self.fileSRTCurrent.save()
			self.manage_thread_pool.resultChanged.emit(CHANGE_HIEN_THI_TAB_ADD_SUB, CHANGE_HIEN_THI_TAB_ADD_SUB,
				cau_hinh["sub_hien_thi"])
	
	
	def saveConfigActive (self, id):
		# print(id)
		if hasattr(self, "db_app") and self.db_app:
			configActive = self.db_app.select_one_name(
				"configEditSubActive")
			configActive.configValue = id
			configActive.save()
