import json
import os

from PySide6.QtCore import Qt, Signal, QPersistentModelIndex
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QProgressBar, QTableWidgetItem, QAbstractItemView, \
	QAbstractScrollArea, QTableWidget, QHeaderView

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import UPDATE_VALUE_PROGRESS_TABLE_PROCESS, UPDATE_STATUS_TABLE_PROCESS, \
	UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS, ADD_TO_TABLE_PROCESS, RENDER_VIDEO_FFMPEG_NO_TTS_FINISHED, \
	RENDER_VIDEO_FFMPEG_FINISHED_V1, UPDATE_FILENAME_OUTPUT_RENDER, \
	UPDATE_VALUE_PROGRESS_PLUS_TABLE_PROCESS, RENDER_VIDEO_FFMPEG_TTS_CHUNK, \
	UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS, \
	UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS, \
	RESET_VALUE_PROGRESS_TABLE_PROCESS, STOP_GET_VOICE, TOOL_CODE_MAIN, SETTING_APP_DATA, UPDATE_STATUS_TABLE_RENDER, \
	UPDATE_RANGE_PROGRESS_TABLE_PROCESS
from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_messagebox.py_massagebox import PyMessageBox
from ...helpers.custom_logger import decorator_try_except_class
from ...helpers.func_helper import open_and_select_file, getValueSettings
from ...helpers.server import SERVER_TAB_TTS


class TableProcessRender(QWidget):
	getConfigChanged = Signal()
	statusButtonChanged = Signal(str)
	rowSelectionChanged = Signal(int)
	
	def __init__ (self, manage_thread_pool: ManageThreadPool):
		super().__init__()
		# SET STYLESHEET
		
		self.manage_thread_pool = manage_thread_pool  # tạo trước ui
		settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		self.list_gender_voice = settings.get('gender_voice')
		
		self.listIItemAction = {}
		self.count_result_trans = 0
		self.resultThread = {}
		self.isLoad = True
		self.list_progress = {}  # danh sách các progess tiến trình
		self.list_total_progress = {}  # danh sách các progess tiến trình
		self.list_progress_old = {}
		self.list_range_progress = {}
		self.list_percent_range = {}
		self.init_ui()
		self.end_video = {}
	
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
	
	# menu ngữ cảnh
	
	
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
		self.main_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
		
		self.main_table.setColumnCount(7)  # số lượng cột
		# ==================Thiết lập tên cột ========
		# self.column_checkbox = 0
		self.column_action = 0
		self.column_name_video_ouput = 1
		self.column_progress = 2
		self.column_status = 3
		self.column_tts = 4
		self.column_network = 5
		self.column_music = 6
		# self.column_lach_BQ = 7
		# self.column_intro_outro = 7
		
		# self.main_table.setHorizontalHeaderItem(self.column_checkbox, QTableWidgetItem(self.icon_check_all, ""))
		self.main_table.setHorizontalHeaderItem(self.column_action, QTableWidgetItem("Chức năng"))
		self.main_table.setHorizontalHeaderItem(self.column_name_video_ouput, QTableWidgetItem("Video Output"))
		self.main_table.setHorizontalHeaderItem(self.column_progress, QTableWidgetItem("Tiến trình"))
		self.main_table.setHorizontalHeaderItem(self.column_status, QTableWidgetItem("Trạng Thái"))
		self.main_table.setHorizontalHeaderItem(self.column_tts, QTableWidgetItem("Lồng Tiếng"))
		self.main_table.setHorizontalHeaderItem(self.column_network, QTableWidgetItem("Network"))
		self.main_table.setHorizontalHeaderItem(self.column_music, QTableWidgetItem("Nhạc Nền"))
		# self.main_table.setHorizontalHeaderItem(self.column_intro_outro, QTableWidgetItem("Intro+Outro"))
		# self.main_table.setHorizontalHeaderItem(self.column_lach_BQ, QTableWidgetItem("Lách BQ"))
		
		
		# self.main_table.setHorizontalHeaderItem(self.column_status, QTableWidgetItem("Trạng thái"))
		
		# ------------------------ Set FIxed tiêu đề ko cho di chuyển
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_action, QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_status,
			QHeaderView.ResizeMode.ResizeToContents)
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_tts,
			QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_network,
			QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_music,
			QHeaderView.ResizeMode.ResizeToContents)
		
		# self.main_table.horizontalHeader().setSectionResizeMode(self.column_intro_outro,
		# 	QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_progress,
			QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.horizontalHeader().setSectionResizeMode(self.column_name_video_ouput,
			QHeaderView.ResizeMode.ResizeToContents)
		
		self.main_table.verticalHeader().setDefaultSectionSize(40)
		self.main_table.horizontalHeader().setDefaultSectionSize(180)
	
	def setup_connections (self):
		##==================Các sự kiện của table ========
		# self.main_table.cellDoubleClicked.connect(self.cellDoubleClicked)  # nhận đc row và colum
		# self.main_table.itemDoubleClicked.connect(self.itemDoubleClicked)  # nhận đc item
		# self.main_table.itemChanged.connect(self.itemDataChanged)  # nh# nhận đc item
		
		
		# ========== Các sự kiện cho thread ============
		self.manage_thread_pool.statusChanged.connect(self.statusThreadChanged)
		self.manage_thread_pool.resultChanged.connect(self.resultThreadChanged)
		self.manage_thread_pool.progressChanged.connect(self.progressThreadChanged)
	
	
	# ========== Chạy lại code sau khoảng thời gian ============
	# self.timer.timeout.connect(self.checkOnlineDeviceTimeout)
	#
	
	def _rowSelectionChanged (self):  # emit bên widget kia kết nối với resultChanged  để nhận thông tin qua các widget khác nhau
		pass
	
	
	def create_layouts (self):
		self.widget_layout = QVBoxLayout(self)
		self.widget_layout.setContentsMargins(0, 0, 0, 0)
	
	def add_widgets_to_layouts (self):
		self.widget_layout.addWidget(self.main_table)
	
	def loadDataConfigCurrent (self, configCurrent):
		
		self.configCurrent = configCurrent
	
	# @decorator_try_except_class
	def addItemRowInTable (self, row_data) -> int:  # thêm 1 dòng vào bẳng dữ liệu
		# print(row_data)
		""" Thêm 1 tiến trình render vào bảng """
		row_number = self.main_table.rowCount()  # lấy ra số dòng hiện tại
		self.main_table.insertRow(row_number)  # thêm 1 dòng vào cuối bảng
		# ============== thêm nút chức năng=======
		
		cau_hinh = json.loads(self.configCurrent.value)
		
		# tạo nút action
		item_widget_action = self.itemButtonAction(row_number, row_data)
		self.main_table.setCellWidget(row_number, self.column_action, item_widget_action)
		# tạo progess
		item_widget_progess = self.itemProgess()
		self.main_table.setCellWidget(row_number, self.column_progress, item_widget_progess)
		
		# ============== cho hiện dữ liệu =======
		# []
		# video_output = str(row_number) +'-'+ row_data[0][:-4] + f"-{cau_hinh['ten_hau_to_video']}"+ f".{cau_hinh['dinh_dang_video']}"
		if cau_hinh["text_to_speech"] is True:
			server_trans = SERVER_TAB_TTS.get(
				list(SERVER_TAB_TTS.keys())[cau_hinh.get("tab_tts_active")])
			# print(server_trans)
			key_gender = server_trans.get("gender")
			list_gender = self.list_gender_voice.get(key_gender)
			gender_voice = list_gender.get(cau_hinh.get("servers_tts").get("language_tts"))
			#
			# 	list(SERVER_TAB_TTS.keys())[
			# 		cau_hinh.get("tab_tts_active")]).get("gender").get(cau_hinh.get("servers_tts").get("language_tts"))
			#
			# print(gender_voice)
			try:
				gender = gender_voice[cau_hinh.get("servers_tts").get("gender")].get("name")
			except:
				try:
					gender = gender_voice[cau_hinh.get("servers_tts").get("gender")]
				except:
					pass
		# gender = gender_voice.get(cau_hinh.get("servers_tts").get("gender"))
		
		else:
			gender = "Không"
		item1 = QTableWidgetItem("")
		self.main_table.setItem(row_number, self.column_name_video_ouput, item1)  # video output
		# print(self.main_table.item(row_number,self.column_name_video_ouput))
		item2 = QTableWidgetItem(str(gender))
		self.main_table.setItem(row_number, self.column_tts, item2)  # lồng tiếng
		
		# item3 = QTableWidgetItem(cau_hinh["network_actived"])
		item3 = QTableWidgetItem('wifi')
		self.main_table.setItem(row_number, self.column_network, item3)  # network
		
		music = "Có" if cau_hinh['them_nhac'] is True else "Không"
		item4 = QTableWidgetItem(music)
		self.main_table.setItem(row_number, self.column_music, item4)  # network
		
		# intro = "Intro" if cau_hinh['them_intro'] is True else ""
		# outro = "Outro" if cau_hinh['them_outro'] is True else ""
		# if cau_hinh['them_intro_outro'] is True:
		# 	concat = intro + "-" + outro if not intro == "" and not outro == "" else intro + outro
		# else:
		# 	concat = "Không"
		# item5 = QTableWidgetItem(concat)
		# self.main_table.setItem(row_number, self.column_intro_outro, item5)  # network
		
		return row_number
	
	def itemProgess (self):
		
		widget = QWidget()
		
		layout = QHBoxLayout(widget)
		# bb=QProgressBar(self,objectName="RedProgressBar")
		# bb.maximum()
		widget.progess = QProgressBar(self, objectName="RedProgressBar")
		widget.progess.setMaximum(1)
		widget.progess.hide()
		# index1 = QPersistentModelIndex(self.main_table.model().index(row_number, self.column_action))
		# widget.progess.clicked.connect(lambda: self.stop_single_thread(index1))
		
		layout.addWidget(widget.progess)
		layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
		layout.setContentsMargins(5, 0, 5, 0)
		widget.setLayout(layout)
		return widget
	
	def itemButtonAction (self, row_number, data):
		
		widget = QWidget()
		
		layout_action = QHBoxLayout()
		
		widget.btn_open_folder_file = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-folder1.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
			app_parent=self,
			tooltip_text="Mở thư mục lưu"
		
		)
		
		# widget.btn_open_folder_file.setDisabled(True)
		index2 = QPersistentModelIndex(self.main_table.model().index(row_number, self.column_action))
		widget.btn_open_folder_file.clicked.connect(lambda: self.clickButtonAction(data, index2, "btn_open_folder_file"))
		
		widget.btn_play = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("play.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#03b803",
			icon_color_hover="#1be21b",
			icon_color_pressed="#4fc65e",
			app_parent=self,
			tooltip_text="Play"
		
		)
		
		# widget.btn_play.setObjectName("btn_pause")
		index3 = QPersistentModelIndex(self.main_table.model().index(row_number, self.column_action))
		widget.btn_play.clicked.connect(lambda: self.clickButtonAction(data, index3, "btn_play"))
		
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
		
		layout_action.addWidget(widget.btn_play)
		layout_action.addWidget(widget.btn_open_folder_file)
		layout_action.addWidget(widget.btn_stop)
		# layout_action.setAlignment(Qt.AlignmentFlag.AlignHCenter)
		layout_action.setAlignment(Qt.AlignmentFlag.AlignVCenter)
		layout_action.setContentsMargins(0, 0, 10, 0)
		
		widget.setLayout(layout_action)
		self.setDisabledButton(widget, True)
		self.listIItemAction[(row_number)] = widget
		return widget
	
	# @decorator_try_except_class
	def clickButtonAction (self, data: str, index: QPersistentModelIndex, type, **kwargs):
		path_output = data[0]  # co 1 phần tu, cái này được cấu hình sẵn
		# print(file_ouput)
		
		if type == "btn_stop":
			print("Stop")
			kwargs.get("btn").set_icon_color = "#c3ccdf"
			kwargs.get("btn").icon_color = "#c3ccdf"
			kwargs.get("btn").icon_color_hover = "#c3ccdf"
			kwargs.get("btn").icon_color_pressed = "#c3ccdf"
			self.manage_thread_pool.resultChanged.emit(STOP_GET_VOICE, STOP_GET_VOICE, index.row())
		
		if type == "btn_open_folder_file":
			file_ouput = self.main_table.item(index.row(), self.column_name_video_ouput).text()
			
			open_and_select_file(file_ouput)
		# webbrowser.open(path_output)
		
		elif type == "btn_play":
			file_ouput = self.main_table.item(index.row(), self.column_name_video_ouput).text()
			
			# file_output = JOIN_PATH(path_output,name_video)
			
			if os.path.isfile(file_ouput):
				os.startfile(file_ouput)
			else:
				return PyMessageBox().show_warning("Thông báo", "File Không Tồn Tại")
	
	def setDisabledButton (self, widget: QWidget, status):
		
		widget.btn_open_folder_file.setDisabled(status)
		widget.btn_play.setDisabled(status)
		
		if status is True:  # disabled
			
			widget.btn_open_folder_file.set_icon_color = "#c3ccdf"
			widget.btn_open_folder_file.icon_color = "#c3ccdf"
			widget.btn_open_folder_file.icon_color_hover = "#c3ccdf"
			widget.btn_open_folder_file.icon_color_pressed = "#c3ccdf"
			
			widget.btn_play.set_icon_color = "#c3ccdf"
			widget.btn_play.icon_color = "#c3ccdf"
			widget.btn_play.icon_color_hover = "#c3ccdf"
			widget.btn_play.icon_color_pressed = "#c3ccdf"
		else:
			
			widget.btn_open_folder_file.set_icon_color = "#f5ca1e"
			widget.btn_open_folder_file.icon_color = "#f5ca1e"
			widget.btn_open_folder_file.icon_color_hover = "#ffe270"
			widget.btn_open_folder_file.icon_color_pressed = "#d1a807"
			
			widget.btn_play.set_icon_color = "#03b803"
			widget.btn_play.icon_color = "#03b803"
			widget.btn_play.icon_color_hover = "#1be21b"
			widget.btn_play.icon_color_pressed = "#4fc65e"
		
		widget.btn_open_folder_file.repaint()
		widget.btn_play.repaint()
	
	# sự kiện cho context menu
	
	def resultThreadChanged (self, id_worker, typeThread, result):
		
		# if typeThread == STOP_GET_VOICE:
		# 	# print(result)
		# 	row_number = result
		# self.list_run_fail[(row_number)] = True
		
		if typeThread == UPDATE_STATUS_TABLE_RENDER:
			row_number, status, progress, time_new = result
			# item = QTableWidgetItem(str(status)+f" Thời gian dự kiến: {time_new}")
			text = str(status) + f" Thời gian dự kiến: {time_new}"
			self.main_table.item(int(row_number), self.column_status).setText(text)
			widget = self.main_table.cellWidget(int(row_number), self.column_progress)
			prog: QProgressBar = widget.progess
			prog.show()
			# print(prog.maximum())
			prog.setValue(float(progress))
		# self.main_table.setItem(int(id_row), self.column_status, item)
		
		if typeThread == UPDATE_RANGE_PROGRESS_TABLE_PROCESS:
			try:
				widget = self.main_table.cellWidget(result["id_row"], self.column_progress)
				widget.progess.show()
				widget.progess.setMaximum(result["range"])
			except:
				pass
		if typeThread == UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS:
			try:
				widget = self.main_table.cellWidget(result["id_row"], self.column_progress)
				widget.progess.show()
				value_old = widget.progess.maximum()
				# print(value_old)
				# print(result)
				widget.progess.setMaximum(value_old + result["range"])
			except:
				pass
		
		if typeThread == UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS and not result == None:
			row_number, index_chunk, range = result.get('row_number'), result.get('index_chunk'), result.get('range')
			# print(row_number, index_range, range)
			
			if self.list_total_progress.get((row_number)) is None:
				self.list_total_progress[(row_number)] = []
			
			if self.list_range_progress.get((row_number, index_chunk)) is None:
				self.list_range_progress[(row_number, index_chunk)] = range
				
				widget = self.main_table.cellWidget(row_number, self.column_progress)
				widget.progess.show()
				# if widget.maximum() == 100
				widget.progess.setMaximum(100)
			else:
				self.list_range_progress[(row_number, index_chunk)] = range
		
		# self.list_progress[(result.get('row_number'))][(result.get('index_range'))] = result.get('range')
		
		if typeThread == UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS:
			self.list_percent_range[result.get('row_number')] = result.get('percent_range')
		# print(self.list_percent_range[result.get('row_number')])
		# self.addItemRowInTable(result)
		
		if typeThread == ADD_TO_TABLE_PROCESS:
			# self.list_progress[self.main_table.rowCount()] = 0
			self.addItemRowInTable(result)
		
		if typeThread == RENDER_VIDEO_FFMPEG_NO_TTS_FINISHED or typeThread == RENDER_VIDEO_FFMPEG_FINISHED_V1:
			if (int(id_worker)) in self.listIItemAction.keys():
				if os.path.isfile(self.main_table.item(int(id_worker), self.column_name_video_ouput).text()):
					widget = self.listIItemAction[(int(id_worker))]
					self.setDisabledButton(widget, False)
				else:
					self.main_table.item(int(id_worker), self.column_name_video_ouput).setText("Lỗi Render")
		
		if typeThread == UPDATE_FILENAME_OUTPUT_RENDER:
			item = QTableWidgetItem(str(result))
			self.main_table.setItem(int(id_worker), self.column_name_video_ouput, item)
		
		if typeThread == RENDER_VIDEO_FFMPEG_TTS_CHUNK:
			widget = self.main_table.cellWidget(int(result.get('row_number')), self.column_progress)
			widget.progess.show()
			
			if self.end_video.get((result.get('row_number'))) is None:
				self.end_video[(result.get('row_number'))] = 0
			
			if self.list_progress.get((result.get('row_number'))) is None:
				self.list_progress[(result.get('row_number'))] = []
			# self.list_progress_old[(int(result.get('row_number')))] = 0
			
			try:
				del self.list_progress[(result.get('row_number'))][result.get('index_chunk')]
			except IndexError:
				pass
			
			self.list_progress[
				(result.get('row_number'))].insert(result.get('index_chunk'), result.get('progress_time'))
			# extra = result.get('progress_time') - self.list_progress_old[(int(result.get('row_number')))]
			# print(self.list_progress[(result.get('row_number'))])
			if result.get('end_video') is True:
				self.end_video[(result.get('row_number'))] = result.get('progress_time')
				widget.progess.setValue(sum(self.list_progress[(result.get('row_number'))]))
			else:
				widget.progess.setValue(sum(self.list_progress[(result.get('row_number'))]) + self.end_video[
					(result.get('row_number'))])
		
		if typeThread == RESET_VALUE_PROGRESS_TABLE_PROCESS:
			widget = self.main_table.cellWidget(int(result), self.column_progress)
			prog: QProgressBar = widget.progess
			prog.show()
			prog.setValue(0)
	
	def statusThreadChanged (self, id_row, typeThread, status):
		if typeThread == UPDATE_STATUS_TABLE_PROCESS:
			item = QTableWidgetItem(str(status))
			self.main_table.setItem(int(id_row), self.column_status, item)
	
	def progressThreadChanged (self, typeProgress, id_row, progress):
		
		
		if typeProgress == UPDATE_VALUE_PROGRESS_PLUS_TABLE_PROCESS:
			widget = self.main_table.cellWidget(int(id_row), self.column_progress)
			prog: QProgressBar = widget.progess
			prog.show()
			old_progress = prog.value()
			prog.setValue(progress + old_progress)
		
		if typeProgress == UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS:
			kwargs: dict = json.loads(id_row)
			# print(kwargs)
			row_number = int(kwargs.get('row_number'))
			index_chunk = int(kwargs.get('index_chunk'))
			widget = self.main_table.cellWidget(row_number, self.column_progress)
			prog: QProgressBar = widget.progess
			prog.show()
			# cur_progress = prog.value()
			#
			# index_progress = tuple(kwargs.values())
			
			# print(self.list_range_progress[(row_number, index_chunk)])
			try:
				progress_index_range = self.list_range_progress[(row_number, index_chunk)]
				percent_range = self.list_percent_range[row_number]
				cur_percent = (progress * percent_range) / progress_index_range
			# print(progress_index_range)
			# print(progress)
			except:
				cur_percent = 0
			
			try:
				del self.list_total_progress[(row_number)][index_chunk]
			except IndexError:
				pass
			self.list_total_progress[
				(row_number)].insert(index_chunk, cur_percent)
			
			# self.list_total_progress[(row_number)][(index_chunk)]=cur_percent
			#
			# print(self.list_total_progress[(row_number)])
			# print(self.list_total_progress[(row_number)])
			# print("Luong so: "+str(kwargs.get("index_chunk")))
			
			total_progress = 0
			for vl in self.list_total_progress[(row_number)]:
				total_progress += vl
			# print(total_progress)
			widget.progess.setValue(round(total_progress))
		# if self.list_progress_old.get(index_progress) is None:
		# 	self.list_progress_old[index_progress] = 0
		#
		# extra = progress - self.list_progress_old.get(index_progress)
		# if extra > 0:
		# 	widget.progess.setValue(cur_progress + extra)
		#
		# self.list_progress_old[index_progress] = progress
		
		if typeProgress == UPDATE_VALUE_PROGRESS_TABLE_PROCESS:
			widget = self.main_table.cellWidget(int(id_row), self.column_progress)
			prog: QProgressBar = widget.progess
			prog.show()
			cur_progress = prog.value()
			if self.list_progress_old.get((int(id_row))) is None:
				self.list_progress_old[(int(id_row))] = 0
			
			extra = progress - self.list_progress_old[(int(id_row))]
			if extra > 0:
				widget.progess.setValue(cur_progress + extra)
			
			self.list_progress_old[(int(id_row))] = progress
		
		if typeProgress == UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS:
			widget = self.main_table.cellWidget(int(id_row), self.column_progress)
			prog: QProgressBar = widget.progess
			prog.show()
			old_progress = prog.maximum()
			prog.setValue(old_progress)
