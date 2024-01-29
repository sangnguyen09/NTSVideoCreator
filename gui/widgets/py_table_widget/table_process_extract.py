import os

from PySide6.QtCore import Qt, Signal, QPersistentModelIndex
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QProgressBar, QTableWidgetItem, QAbstractItemView, \
	QAbstractScrollArea, QTableWidget, QHeaderView, QCheckBox

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS, UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, \
	ADD_TO_TABLE_EXTRACT_PROCESS, LOAD_VIDEO_FROM_FILE_SRT, \
	EXTRACT_SUB_FINISHED, DETECT_LANGUAGE_AISUB, \
	TOOL_CODE_MAIN, STOP_EXTRACT_SUB_TABLE, SETTING_APP_DATA
from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_messagebox.py_massagebox import PyMessageBox
from ...helpers.custom_logger import decorator_try_except_class
from ...helpers.func_helper import getValueSettings, open_and_select_file


class TableProcessExtractSUB(QWidget):
	getConfigChanged = Signal()
	statusButtonChanged = Signal(str)
	rowSelectionChanged = Signal(int)
	
	def __init__ (self, manage_thread_pool: ManageThreadPool,thread_pool_limit:ManageThreadPool,check_box_auto_create:QCheckBox):
		super().__init__()
		# SET STYLESHEET
		
		self.manage_thread_pool = manage_thread_pool  # tạo trước ui
		self.thread_pool_limit = thread_pool_limit  # tạo trước ui
		self.check_box_auto_create = check_box_auto_create  # tạo trước ui
		# self.groupbox_timeline = groupbox_timeline  # tạo trước ui
		
		settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		self.LANGUAGES_EXTRACT_AI = settings.get("language_support").get("language_code")
		self.LANGUAGES_DETECT = settings.get("language_support").get("language_detect")
		self.listIItemAction = {}
		self.count_result_trans = 0
		self.isLoad = True
		self.init_ui()
	
	def init_ui (self):
		self.create_widgets()
		
		self.create_layouts()
		self.add_widgets_to_layouts()
		
		self.setup_table()
		
		self.setup_connections()
	
	def create_widgets (self):
		self.main_table = QTableWidget()
		self.main_table.setObjectName(u"tableWidget")
		self.main_table.setAlternatingRowColors(True)
	
	# tạo Nút CheckBox trên tiêu đề
	
	def setup_table (self):
		# ========== Cài đặt cho table============
		# self.main_table.verticalHeader().setVisible(False)  # ko hiện số thứ tự ở các dòng
		self.main_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # cái này là khi focus vào thì ko hiện cái viền
		self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)  # cái này là ko cho bấm vào chọn
		self.main_table.horizontalHeader().setHighlightSections(False)  # không Highlight khi chọn vào tiêu đề
		# .horizontalHeader().setSectionsClickable(True)
		self.main_table.horizontalHeader().setStretchLastSection(True)  # cái này cho kéo dãn full table
		self.main_table.horizontalHeader().setDefaultSectionSize(126)
		self.main_table.horizontalHeader().setMinimumSectionSize(37)
		self.main_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
		# QHeaderView.setSectionsClickable()
		
		self.main_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # cho phép chọn thành dòng
		self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # cho phép chọn 1 dòng
		self.main_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # không cho edit
		
		self.main_table.setColumnCount(7)  # số lượng cột
		# ==================Thiết lập tên cột ========
		# self.column_checkbox = 0
		self.column_action = 0
		self.column_name_video_input = 6
		self.column_name_srt_file = 5
		self.column_language = 1
		self.column_server = 2
		# self.column_concurrency = 3
		
		self.column_status = 4
		self.column_progress = 3
		
		self.main_table.setHorizontalHeaderItem(self.column_action, QTableWidgetItem("Chức năng"))
		self.main_table.setHorizontalHeaderItem(self.column_name_video_input, QTableWidgetItem("Video Input"))
		self.main_table.setHorizontalHeaderItem(self.column_language, QTableWidgetItem("Ngôn Ngữ"))
		# self.main_table.setHorizontalHeaderItem(self.column_concurrency, QTableWidgetItem("Số luồng"))
		self.main_table.setHorizontalHeaderItem(self.column_server, QTableWidgetItem("Server"))
		self.main_table.setHorizontalHeaderItem(self.column_progress, QTableWidgetItem("Tiến trình"))
		
		self.main_table.setHorizontalHeaderItem(self.column_status, QTableWidgetItem("Trạng Thái"))
		
		self.main_table.setHorizontalHeaderItem(self.column_name_srt_file, QTableWidgetItem("File SRT"))
		
		# ------------------------ Set FIxed tiêu đề ko cho di chuyển
		# self.main_table.horizontalHeader().setSectionResizeMode(self.column_checkbox,
		#                                                         QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
		# self.main_table.horizontalHeader().setSectionResizeMode(self.column_action, QHeaderView.ResizeMode.Stretch)  # gian cách đều
		# self.main_table.horizontalHeader().setSectionResizeMode(self.column_idphone, QHeaderView.ResizeMode.Stretch)  # gian cách đều
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_action, QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_status,
			QHeaderView.ResizeMode.ResizeToContents)
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_language,
			QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_server,
			QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_name_video_input,
			QHeaderView.ResizeMode.ResizeToContents)
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_name_srt_file,
			QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_status,
			QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
		self.main_table.verticalHeader().setDefaultSectionSize(40)
		self.main_table.horizontalHeader().setDefaultSectionSize(180)
	
	
	def setup_connections (self):
		##==================Các sự kiện của table ========
		
		self.main_table.itemChanged.connect(self.itemDataChanged)  # nh# nhận đc item
		
		# ========== Các sự kiện cho thread ============
		self.manage_thread_pool.statusChanged.connect(self.statusThreadChanged)
		self.manage_thread_pool.resultChanged.connect(self.resultThreadChanged)
		self.manage_thread_pool.progressChanged.connect(self.progressThreadChanged)
	
	
	def create_layouts (self):
		self.widget_layout = QVBoxLayout(self)
		self.widget_layout.setContentsMargins(0, 0, 0, 0)
	
	def add_widgets_to_layouts (self):
		self.widget_layout.addWidget(self.main_table)
	
	# @decorator_try_except_class
	def addItemRowInTable (self, row_data) -> int:  # thêm 1 dòng vào bẳng dữ liệu
		
		""" Thêm 1 tiến trình render vào bảng """
		row_number = self.main_table.rowCount()  # lấy ra số dòng hiện tại
		self.main_table.insertRow(row_number)  # thêm 1 dòng vào cuối bảng
		# ============== thêm nút chức năng=======
		
		# tạo nút action
		item_widget_action = self.itemButtonAction(row_number, row_data)
		self.main_table.setCellWidget(row_number, self.column_action, item_widget_action)
		# tạo progess
		item_widget_progess = self.itemProgess()
		self.main_table.setCellWidget(row_number, self.column_progress, item_widget_progess)
		
		# ============== cho hiện dữ liệu =======
		# []
		# print(row_data)
		# name_video = row_data[0].replace("\\", "/").split("/")[-1]
		item1 = QTableWidgetItem(str(row_data[0]))
		self.main_table.setItem(row_number, self.column_name_video_input, item1)  # name
		
		language = self.LANGUAGES_DETECT.get(row_data[1])
		
		if language is None:
			language = self.LANGUAGES_EXTRACT_AI.get(row_data[1])
			
		if language is None:
			language = "Đang detect..."
		item2 = QTableWidgetItem(str(language))
		self.main_table.setItem(row_number, self.column_language, item2)  # language
		
		item3 = QTableWidgetItem(str(row_data[2]))
		self.main_table.setItem(row_number, self.column_server, item3)  # server
		
		item4 = QTableWidgetItem("")
		self.main_table.setItem(row_number, self.column_status, item4)  # status
	 
		item5 = QTableWidgetItem("")
		self.main_table.setItem(row_number, self.column_name_srt_file, item5)  # srt
	 

		return row_number
	
	def itemProgess (self):
		
		widget = QWidget()
		
		layout = QHBoxLayout(widget)
		
		widget.progess = QProgressBar(self, objectName="RedProgressBar")
		widget.progess.hide()
		# index1 = QPersistentModelIndex(self.main_table.model().index(row_number, self.column_action))
		# widget.progess.clicked.connect(lambda: self.stop_single_thread(index1))
		
		layout.addWidget(widget.progess)
		layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
		layout.setContentsMargins(5, 0, 5, 0)
		widget.setLayout(layout)
		return widget
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		
	def itemButtonAction (self, row_number, data):
		
		widget = QWidget()
		
		layout_action = QHBoxLayout()
		# print(self.main_table.item(row_number,self.column_action))
		widget.btn_view_sub = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("file-preview.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#f7f8e8",
			icon_color_hover="#fffffe",
			icon_color_pressed="#e7e8de",
			app_parent=self,
			tooltip_text="View Subtitle"
		
		)
		
		index1 = QPersistentModelIndex(self.main_table.model().index(row_number, self.column_action))
		widget.btn_view_sub.clicked.connect(lambda: self.clickButtonAction(data, index1, "btn_view_sub"))
		
		widget.btn_open_folder_file = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-folder1.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
			app_parent=self,
			tooltip_text="Open Folder"
		
		)
		
		# widget.btn_open_folder_file.setDisabled(True)
		index2 = QPersistentModelIndex(self.main_table.model().index(row_number, self.column_action))
		widget.btn_open_folder_file.clicked.connect(lambda: self.clickButtonAction(data, index2, "btn_open_folder_file"))
		
		widget.btn_add_tab_sub = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("new-tab.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#42e05c",
			icon_color_hover="#5ee874",
			icon_color_pressed="#54cd68",
			app_parent=self,
			tooltip_text="Tạo File Sửa Sub"
		
		)
		# widget.btn_add_tab_sub.setObjectName("btn_pause")
		index3 = QPersistentModelIndex(self.main_table.model().index(row_number, self.column_action))
		widget.btn_add_tab_sub.clicked.connect(lambda: self.clickButtonAction(data, index3, "btn_add_tab_sub"))
		
		
		widget.btn_stop = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("stop.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#f24646",
			icon_color_hover="#f24646",
			icon_color_pressed="#790a1a",
			app_parent=self,
			tooltip_text="Stop"
		
		)
		
		index4 = QPersistentModelIndex(self.main_table.model().index(row_number, self.column_action))
		widget.btn_stop.clicked.connect(lambda: self.clickButtonAction(data, index4, "btn_stop", btn=widget.btn_stop))
		

		# layout_action.addWidget(widget.btn_view_sub)
		layout_action.addWidget(widget.btn_add_tab_sub)

		layout_action.addWidget(widget.btn_open_folder_file)
		
		# user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		# setting_user = user_data["list_tool"].get(TOOL_CODE_MAIN)
		
		# print(setting_user)
		# if 'long_tieng' in setting_user.get('tab'):
		
		layout_action.addWidget(widget.btn_stop)


		# layout_action.setAlignment(Qt.AlignmentFlag.AlignHCenter)
		layout_action.setAlignment(Qt.AlignmentFlag.AlignVCenter)
		layout_action.setContentsMargins(0, 0, 10, 0)
		
		widget.setLayout(layout_action)
		self.setDisabledButton(widget, True)
		self.listIItemAction[(row_number)] = widget
		return widget
	
	@decorator_try_except_class
	def clickButtonAction (self, data: str, index: QPersistentModelIndex, type, **kwargs):
		base, ext = os.path.splitext(data[0])
		item_column_srt = self.main_table.item(index.row(),self.column_name_srt_file)
		srt_path = item_column_srt.text()
		
		# if type == "btn_view_sub":
		# 	if os.path.isfile(srt_path) is True:
		# 		if ext in LIST_FILE_MUSIC:
		# 			return PyMessageBox().show_warning("Thông báo", "Không hỗ trợ view file nhạc")
		#
		# 		if "youtube" in data[0].lower():
		# 			return PyMessageBox().show_warning("Thông báo", "Không hỗ trợ view từ link Youtube")
		#
		# 		if "capcut" in data[0].lower():
		# 			return PyMessageBox().show_warning("Thông báo", "Không hỗ trợ view từ Project Capcut")
		#
		# 		# with open(srt_path, 'r', encoding='UTF-8') as f:
		# 		# 	content = f.read()
		# 		sequences = filter_sequence_srt(srt_path,data[0])
		# 		data_table = []
		# 		for (count, item) in enumerate(sequences):
		# 			stt_, time_, content_ = item[0], item[1], item[2]
		# 			data_table.append([time_, content_,""])
		#
		# 		self.groupbox_timeline.displayTable(data_table, data[0],sequences)
		#
		# 			# self.manage_thread_pool.resultChanged.emit(LOAD_VIDEO_FROM_FILE_SRT_EXTRACT, LOAD_VIDEO_FROM_FILE_SRT_EXTRACT, {
		# 			# 	'sequences': sequences, 'path_video': data[0]})
		# 			# self.main_table.selectRow(0)
		# 	else:
		# 		return PyMessageBox().show_warning("Thông báo", "File SUB srt không không tồn tại ")
		# print(index.row(), type,source_path)
		
		if type == "btn_open_folder_file":
			
			# path = "/".join(srt_path.replace("\\", "/").split("/")[:-1])
			
			open_and_select_file(srt_path)
			# webbrowser.open(path)
		
		elif type == "btn_add_tab_sub":

			if os.path.isfile(srt_path) is True:
				self.manage_thread_pool.resultChanged.emit(LOAD_VIDEO_FROM_FILE_SRT, LOAD_VIDEO_FROM_FILE_SRT, srt_path)
			else:
				return PyMessageBox().show_warning("Thông báo", "File SUB srt không không tồn tại ")
			
		elif type == "btn_stop":
			kwargs.get("btn").set_icon_color = "#c3ccdf"
			kwargs.get("btn").icon_color = "#c3ccdf"
			kwargs.get("btn").icon_color_hover = "#c3ccdf"
			kwargs.get("btn").icon_color_pressed = "#c3ccdf"
			self.manage_thread_pool.resultChanged.emit(STOP_EXTRACT_SUB_TABLE, STOP_EXTRACT_SUB_TABLE, index.row())
	# print(index.row(), type,source_path)
	
	def setDisabledButton (self, widget: QWidget, status):
		widget.btn_view_sub.setDisabled(status)
		widget.btn_open_folder_file.setDisabled(status)
		widget.btn_add_tab_sub.setDisabled(status)
		
		if status is True:  # disabled
			
			widget.btn_view_sub.set_icon_color = "#c3ccdf"
			widget.btn_view_sub.icon_color = "#c3ccdf"
			widget.btn_view_sub.icon_color_hover = "#c3ccdf"
			widget.btn_view_sub.icon_color_pressed = "#c3ccdf"
			
			widget.btn_open_folder_file.set_icon_color = "#c3ccdf"
			widget.btn_open_folder_file.icon_color = "#c3ccdf"
			widget.btn_open_folder_file.icon_color_hover = "#c3ccdf"
			widget.btn_open_folder_file.icon_color_pressed = "#c3ccdf"
			
			widget.btn_add_tab_sub.set_icon_color = "#c3ccdf"
			widget.btn_add_tab_sub.icon_color = "#c3ccdf"
			widget.btn_add_tab_sub.icon_color_hover = "#c3ccdf"
			widget.btn_add_tab_sub.icon_color_pressed = "#c3ccdf"
		else:
			
			widget.btn_view_sub.set_icon_color = "#f7f8e8"
			widget.btn_view_sub.icon_color = "#f7f8e8"
			widget.btn_view_sub.icon_color_hover = "#fffffe"
			widget.btn_view_sub.icon_color_pressed = "#e7e8de"
			
			widget.btn_open_folder_file.set_icon_color = "#f5ca1e"
			widget.btn_open_folder_file.icon_color = "#f5ca1e"
			widget.btn_open_folder_file.icon_color_hover = "#ffe270"
			widget.btn_open_folder_file.icon_color_pressed = "#d1a807"
			
			widget.btn_add_tab_sub.set_icon_color = "#42e05c"
			widget.btn_add_tab_sub.icon_color = "#42e05c"
			widget.btn_add_tab_sub.icon_color_hover = "#5ee874"
			widget.btn_add_tab_sub.icon_color_pressed = "#54cd68"
		
		widget.btn_view_sub.repaint()
		widget.btn_open_folder_file.repaint()
		widget.btn_add_tab_sub.repaint()
	
	# sự kiện cho context menu
	
	
	def resultThreadChanged (self, id_worker, typeThread, result):
		
		# if typeThread == RESULT_EXTRACT_SUB:
		#     widget =self.listIItemAction[(int(result))]
		#     self.setDisabledButton(widget, False)
		
		if typeThread == UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS and not result == None:
			widget = self.main_table.cellWidget(result["id_row"], self.column_progress)
			widget.progess.show()
			widget.progess.setRange(0, result["range"])
		
		if typeThread == ADD_TO_TABLE_EXTRACT_PROCESS:
			self.addItemRowInTable(result)
		
		if typeThread == DETECT_LANGUAGE_AISUB:
			widget = self.main_table.item(int(id_worker), self.column_language)
			widget.setText(result)
		
		if typeThread == EXTRACT_SUB_FINISHED:
			# if len(self.thread_pool_limit._list_worker) == 0:
			# 	rp_f()
			
			if (int(id_worker)) in self.listIItemAction.keys():
				# base, ext = os.path.splitext(self.main_table.item(int(id_worker), self.column_name_video_input).text())
				# srt_path = "{base}.{format}".format(base=base, format='srt')
				srt_path = result
				if os.path.isfile(srt_path):
					self.main_table.item(int(id_worker), self.column_name_srt_file).setText(srt_path)
					
					widget = self.listIItemAction[(int(id_worker))]
					self.setDisabledButton(widget, False)
					if self.check_box_auto_create.isChecked():
						self.manage_thread_pool.resultChanged.emit(LOAD_VIDEO_FROM_FILE_SRT, LOAD_VIDEO_FROM_FILE_SRT, srt_path)
				
				else:
					self.main_table.item(int(id_worker), self.column_status).setText("Lỗi Trích Xuất")
				
			
	def statusThreadChanged (self, id_row, typeThread, status):
		if typeThread == UPDATE_STATUS_TABLE_EXTRACT_PROCESS:
			item = QTableWidgetItem(str(status))
			self.main_table.setItem(int(id_row), self.column_status, item)
	
	def progressThreadChanged (self, typeProgress, id_row, progress):
		
		if typeProgress == UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS:
			widget = self.main_table.cellWidget(int(id_row), self.column_progress)
			widget.progess.show()
			widget.progess.setValue(progress)
	
	def itemDataChanged (self, item):
		pass
