# -*- coding: utf-8 -*-
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, \
	QFileDialog
from platformdirs import user_data_dir

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	ADD_TO_TABLE_EXTRACT_PROCESS, SETTING_APP_DATA, TOOL_CODE_MAIN, \
	APP_PATH, RESULT_EXTRACT_SUB_LINK_YOUTUBE, EXTRACT_SUB_FINISHED, JOIN_PATH
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from ..py_combobox import PyComboBox
from ..py_dialogs.py_dialog_show_info import PyDialogShowInfo
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_table_widget.table_process_extract import TableProcessExtractSUB
from ...configs.config_resource import ConfigResource
from ...helpers.func_helper import getValueSettings, exportSRTCapCut
from ...helpers.http_request.check_proxy import ProxyChecker
from ...helpers.thread import ManageThreadPool


class PyTabExtractSubCapCut(QWidget):
	def __init__ (self, group_parent, manage_thread_pool, thread_pool_limit, manage_cmd, table_process: TableProcessExtractSUB, groupBox_start_server,LANGUAGES_TRANS):
		super().__init__()
		
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.group_parent = group_parent
		
		self.manage_thread_pool = manage_thread_pool
		self.thread_pool_limit = thread_pool_limit
		self.thread_pool_limit_convert = ManageThreadPool()
		self.thread_pool_limit_convert.setMaxThread(10)
		self.manage_cmd = manage_cmd
		self.table_process = table_process
		self.checker = ProxyChecker(manage_thread_pool)
		self.groupBox_start_server = groupBox_start_server
		self.count = 0
		
		self.project_folder = "User Data\Projects\com.lveditor.draft"
		
		# PROPERTIES
		self.isLoad = True
		self.load_file_srt_finished = False
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	# Too many requests, please try again later.
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		self.lb_src_capcut = QLabel("Src CapCut:")
		self.input_src_capcut = QLineEdit()
		
		self.lb_project = QLabel("Tên Project:")
		self.cb_project = PyComboBox()
		
		# self.lb_server_language = QLabel("Ngôn Ngữ Sub Cần Lấy:")
		# self.cb_language = PyComboBox()
		
		self.lb_notify = QLabel("Sau khi bấm Tạo phụ đề tự động trong CapCut thì lưu dự án lại và vào tool load chọn vào dự án đó")
		self.btn_info_frame = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("info.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#2678ff",
			icon_color_hover="#4d8df6",
			icon_color_pressed="#6f9deb",
			app_parent=self,
			tooltip_text="Hướng dẫn"
		
		)
		
		# self.lb_file_srt = QLabel("Load File SRT:")
		self.btn_open_folder_capcut = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
			tooltip_text="Mở Thư Mục CapCut"
		
		)
		self.btn_start = QPushButton("Lấy Phụ Đề")
		self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
		
		text = "Bước 1. Mở Phần Mềm CapCut"
		text += "\n\n"
		
		text += "Bước 2. Load Video Lên Kéo Xuống TimeLine ở vị trí đầu tiên"
		text += "\n\n"
		
		text += "Bước 3. Chọn vào TAB Văn Bản và chọn vào Phụ Đề Tự Động"
		text += "\n\n"
		text += "Bước 4. Chọn Ngôn ngữ video sau đó bấm Tạo"
		text += "\n\n"
		
		text += "Bước 5. Sau khi có phụ đề thì lưu dự án đó lại"
		text += "\n\n"
		
		text += "Bước 6. Vào Tool NTS Autosub chọn dự án khi nãy và bấm Lấy Phụ Đề"
		text += "\n\n"
		
		text += "Bước 7. Đặt tên và lưu file vào nơi bạn muốn"
		text += "\n\n"
		
		self.dialog_info = PyDialogShowInfo(text, 370)
	
	def modify_widgets (self):
		pass
	
	# self.cb_language.addItems(list(self.LANGUAGES_TRANS.values()))
	# self.cb_server_editsub.addItems(list(self.CACH_LAY_SUB_YOUTUBE.values()))
	
	def create_layouts (self):
		self.content_layout = QVBoxLayout()
		self.content_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_status = QHBoxLayout()
		self.content_link_layout = QHBoxLayout()
		
		self.progess_convert_layout = QHBoxLayout()
		self.content_btn_layout = QGridLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.setLayout(self.content_layout)
		
		self.content_layout.addWidget(QLabel(""))
		self.content_layout.addLayout(self.content_link_layout)
		self.content_layout.addWidget(QLabel(""))
		
		self.content_layout.addLayout(self.content_status)
		self.content_layout.addWidget(QLabel(""))
		
		self.content_layout.addLayout(self.content_btn_layout)
		
		self.content_link_layout.addWidget(self.lb_src_capcut, 10)
		self.content_link_layout.addWidget(self.input_src_capcut, 40)
		self.content_link_layout.addWidget(self.btn_open_folder_capcut, 10)
		
		# self.content_link_layout.addWidget(self.lb_server_language)
		# self.content_link_layout.addWidget(self.cb_language)
		
		self.content_link_layout.addWidget(QLabel(),40)
		# self.content_link_layout.addWidget(self.lb_project)
		# self.content_link_layout.addWidget(self.cb_project, 40)
		
		self.content_status.addWidget(self.lb_notify)
		
		self.content_btn_layout.addWidget(QLabel(), 0, 0, 1, 4)
		self.content_btn_layout.addWidget(self.btn_start, 0, 4, 1, 4)
		self.content_btn_layout.addWidget(QLabel(), 0, 8, 1, 3)
		
		self.content_btn_layout.addWidget(self.btn_info_frame, 0, 11)
	
	def setup_connections (self):
		self.thread_pool_limit_convert.resultChanged.connect(self._resultThread)
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.thread_pool_limit.resultChanged.connect(self._resultThread)
		
		self.btn_start.clicked.connect(self.clickStart)
		self.btn_info_frame.clicked.connect(self._click_info)
		self.btn_open_folder_capcut.clicked.connect(self.open_folder_capcut)
		self.input_src_capcut.textChanged.connect(self.input_src_capcut_changed)
	
	def input_src_capcut_changed (self):
		
		path_project = JOIN_PATH(self.input_src_capcut.text(), self.project_folder)
		if os.path.isdir(path_project):
			list_project = []
			for f in os.scandir(path_project):
				try:
					if f.is_dir():
						list_project.append(os.path.basename(f.path))
				except:
					pass
			self.cb_project.addItems(list_project)
		else:
			self.cb_project.clear()
	
	def open_folder_capcut (self):
		folder_name = QFileDialog.getExistingDirectory(self, caption='Chọn thư mục Data CapCut',
			dir=(user_data_dir()))
		self.input_src_capcut.setText(folder_name)
	
	def _click_info (self):
		self.dialog_info.exec()
	
	def loadData (self, configCurrent):
		
		self.configCurrent = configCurrent
		appCapCut = JOIN_PATH(user_data_dir(), "CapCut")
		self.input_src_capcut.setText(appCapCut)
		
		self.isLoad = False
	
	def loadFileInput (self, path):
		self.path_input = path
	
	
	# @decorator_try_except_class
	def clickStart (self):
		# try:
		folder_project = self.input_src_capcut.text()
		if os.path.exists(folder_project):
			file_data_project = JOIN_PATH(folder_project, "draft_content.json")
			
			if not os.path.exists(file_data_project):
				return PyMessageBox().show_warning("Thông Báo", "File SRT CapCut không tồn tại")
				
			file_name, _ = QFileDialog.getSaveFileName(self, caption='Nhập tên file muốn lưu',
				dir=(APP_PATH),
				filter='File sub (*.srt)')
			
			if file_name == "":
				return PyMessageBox().show_warning("Thông Báo", "Vui lòng chọn file để lưu")
			
			row_number = self.table_process.main_table.rowCount()
			
			data_item_table = []
			data_item_table.append(f"Project CapCut: {self.cb_project.currentText()}")
			data_item_table.append("Không Xác Định")
			data_item_table.append("Trích xuất từ CapCut")
			
			self.manage_thread_pool.resultChanged.emit(str(row_number), ADD_TO_TABLE_EXTRACT_PROCESS, data_item_table)
			# print(file_data_project)
			is_ok, data_sub = exportSRTCapCut(file_data_project)
			if is_ok is False:
				return PyMessageBox().show_warning("Thông Báo", data_sub)
			
			with open(file_name, 'w', encoding="utf-8") as file:
				file.write(data_sub)
			
			self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
				"Hoàn Thành")
			self.manage_thread_pool.resultChanged.emit(str(row_number), EXTRACT_SUB_FINISHED, file_name)
			return PyMessageBox().show_info("Thông Báo", "Xuất File SRT thành công!, Bấm vào nút hình thư mục ở bảng bên dưới để xem file")
		else:
			return PyMessageBox().show_warning("Thông Báo", "Project Này Không Có")
	
	# cau_hinh = json.loads(self.configCurrent.value)
	
	# self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
	# 	"Đang đợi...")
	#
	# self.thread_pool_limit.start(self._funcExtractThread, "_extractStartThreadLinkYoutube" + uuid.uuid4().__str__(), RESULT_EXTRACT_SUB_LINK_YOUTUBE, limit_thread=True, row_number=row_number, file_name=file_name, language=language, url_video=src, cach_lay=cach_lay)
	#
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == RESULT_EXTRACT_SUB_LINK_YOUTUBE:
			if result is not None:
				is_ok, row_number, file_srt = result
				if is_ok:
					self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
						"Hoàn Thành")
					
					self.manage_thread_pool.resultChanged.emit(str(row_number), EXTRACT_SUB_FINISHED, file_srt)
