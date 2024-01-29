# -*- coding: utf-8 -*-
import uuid

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, \
	QFileDialog
from pytube import YouTube

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	ADD_TO_TABLE_EXTRACT_PROCESS, SETTING_APP_DATA, TOOL_CODE_MAIN, \
	APP_PATH, RESULT_EXTRACT_SUB_LINK_YOUTUBE, EXTRACT_SUB_FINISHED, UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, \
	EXTRACT_SUB_YOUTUBE_BY_GOOGLE
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from ..py_combobox import PyComboBox
from ..py_dialogs.py_dialog_show_info import PyDialogShowInfo
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_table_widget.table_process_extract import TableProcessExtractSUB
from ...configs.config_resource import ConfigResource
from ...helpers.custom_logger import decorator_try_except_class
from ...helpers.func_helper import getValueSettings
from ...helpers.handle_speech.extract_sub_voice import ExtractSubVoice
from ...helpers.http_request.check_proxy import ProxyChecker
from ...helpers.thread import ManageThreadPool


class PyTabExtractSubServerYoutube(QWidget):
	def __init__ (self, group_parent, manage_thread_pool, thread_pool_limit, manage_cmd, table_process: TableProcessExtractSUB, groupBox_start_server, LANGUAGES_TRANS, CACH_LAY_SUB_YOUTUBE,CachLaySubYoutubeEnum):
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
		self.CACH_LAY_SUB_YOUTUBE: dict = CACH_LAY_SUB_YOUTUBE
		self.LANGUAGES_TRANS: dict = LANGUAGES_TRANS
		self.CachLaySubYoutubeEnum = CachLaySubYoutubeEnum
		self.extractVoice = ExtractSubVoice(self.manage_thread_pool, self.manage_cmd)
		self.count = 0
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
		
		self.lb_link_video = QLabel("Link Video:")
		self.input_link_video = QLineEdit()
		
		self.lb_server_editsub = QLabel("Cách Lấy Sub:")
		self.cb_server_editsub = PyComboBox()
		
		self.lb_server_language = QLabel("Ngôn Ngữ Sub Cần Lấy:")
		self.cb_language = PyComboBox()
		
		self.lb_notify = QLabel("Sau khi upload video hãy đợi cho sub tự động xuất hiện trên video trước sau đó mới tách sub")
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
		self.btn_start = QPushButton("Start")
		self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
		
		text = "Bước 1. Tải video lên Youtube ở chế độ không công khai, cài đặt ngôn ngữ video"
		text += "\n\n"
		
		text += "Bước 2. Đợi cho video hiện nút phụ đề thì copy link cho vào tool"
		text += "\n\n"
		
		text += "Bước 3. Chọn ngôn ngữ cần lấy sub"
		text += "\n\n"
		text += "Bước 4. Chọn cách lấy sub bằng 1 trong các cách. Test thử để xem cách nào lấy xát nghĩa nhất"
		text += "\n\n"
		
		text += "Bước 5. Bấm START rồi ngồi uống ly cà phê đợi kết quả"
		text += "\n\n"
		
		text += "LƯU Ý: Hãy đợi cho sub tự động xuất hiện trên video trước sau đó mới tách sub"
		
		self.dialog_info = PyDialogShowInfo(text, 370)
	
	def modify_widgets (self):
		self.cb_language.addItems(list(self.LANGUAGES_TRANS.values()))
		self.cb_server_editsub.addItems(list(self.CACH_LAY_SUB_YOUTUBE.values()))
	
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
		
		# self.content_layout.addWidget(QLabel(""), 5)
		self.content_layout.addLayout(self.content_link_layout)
		self.content_layout.addLayout(self.content_status)
		self.content_layout.addLayout(self.content_btn_layout)
		
		self.content_link_layout.addWidget(self.lb_link_video)
		self.content_link_layout.addWidget(self.input_link_video)
		self.content_link_layout.addWidget(self.lb_server_language)
		self.content_link_layout.addWidget(self.cb_language)
		
		self.content_link_layout.addWidget(self.lb_server_editsub)
		self.content_link_layout.addWidget(self.cb_server_editsub)
		
		self.content_status.addWidget(self.lb_notify)
		
		self.content_btn_layout.addWidget(QLabel(), 0, 0, 1, 4)
		self.content_btn_layout.addWidget(self.btn_start, 0, 4, 1, 4)
		self.content_btn_layout.addWidget(QLabel(), 0, 8, 1, 3)
		
		self.content_btn_layout.addWidget(self.btn_info_frame, 0, 11)
	
	def setup_connections (self):
		self.thread_pool_limit_convert.resultChanged.connect(self._resultThread)
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.thread_pool_limit.resultChanged.connect(self._resultThread)
		# self.manage_thread_pool.progressChanged.connect(self._progressChanged)
		# self.checker.finishedCheckLiveProxySignal.connect(self._finishedCheckLiveProxySignal)
		
		self.btn_start.clicked.connect(self.clickStart)
		self.btn_info_frame.clicked.connect(self._click_info)
	
	def _click_info (self):
		self.dialog_info.exec()
	
	def loadData (self, configCurrent):
		
		self.configCurrent = configCurrent
		
		self.isLoad = False
	
	def loadFileInput (self, path):
		self.path_input = path
	
	
	def check_url_video (self, url):
		yt = YouTube(url)
		try:
			yt.check_availability()
			return True
		except Exception:
			return False
	
	
	@decorator_try_except_class
	def clickStart (self):
		# try:
		url = self.input_link_video.text()
		
		if url == '':
			return PyMessageBox().show_warning("Thông Báo", "Vui lòng nhập link video")
		
		if not self.check_url_video(url):
			return PyMessageBox().show_warning("Thông Báo", "Vui lòng nhập đúng link youtube hoặc mở video thành không công khai")
		
		file_name, _ = QFileDialog.getSaveFileName(self, caption='Nhập tên file muốn lưu',
			dir=(APP_PATH),
			filter='File sub (*.srt)')
		
		if file_name == "":
			return PyMessageBox().show_warning("Thông Báo", "Vui lòng chọn file để lưu")
		
		row_number = self.table_process.main_table.rowCount()
		language = list(self.LANGUAGES_TRANS.keys())[self.cb_language.currentIndex()]
		cach_lay = list(self.CACH_LAY_SUB_YOUTUBE.keys())[self.cb_server_editsub.currentIndex()]
		
		data_item_table = []
		data_item_table.append(url)
		data_item_table.append(language)
		data_item_table.append("Trích xuất từ Link Youtube")
		
		self.manage_thread_pool.resultChanged.emit(str(row_number), ADD_TO_TABLE_EXTRACT_PROCESS, data_item_table)
		
		# cau_hinh = json.loads(self.configCurrent.value)
		
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Đang đợi...")
		
		self.thread_pool_limit.start(self._funcExtractThread, "_extractStartThreadLinkYoutube" + uuid.uuid4().__str__(), RESULT_EXTRACT_SUB_LINK_YOUTUBE, limit_thread=True, row_number=row_number, file_name=file_name, language=language, url_video=url, cach_lay=cach_lay)
	
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == RESULT_EXTRACT_SUB_LINK_YOUTUBE:
			if result is not None:
				is_ok, row_number, file_srt = result
				if is_ok:
					self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
						"Hoàn Thành")
					
					self.manage_thread_pool.resultChanged.emit(str(row_number), EXTRACT_SUB_FINISHED, file_srt)
				# else:
				# 	self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
				# 		"Lỗi không lấy được sub")
		
		if id_thread == EXTRACT_SUB_YOUTUBE_BY_GOOGLE:
			row_number = result['row_number']
			self.extractVoice.count_result_convert[(row_number)] += 1
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS,
				str(row_number), self.extractVoice.count_result_convert[(row_number)])
			
			if self.extractVoice.count_result_convert[(row_number)] == self.extractVoice.total_region[(row_number)]:
				self.extractVoice.count_result_convert[(row_number)] = 0
				self.extractVoice.total_region[(row_number)] = 0
				
				origin_language = self.extractVoice.list_origin_language[(row_number)]
				audio_filename = self.extractVoice.list_audio_filename[(row_number)]
				source_path = self.extractVoice.list_source_path[(row_number)]
				regions = self.extractVoice.list_regions[(row_number)]
				
				transcripts = []
				for index, region in enumerate(regions):
					transcript = self.extractVoice.list_transcripts[(row_number, index)]
					transcripts.append(transcript)
				
				timed_subtitles = [(r, t) for r, t in zip(regions, transcripts) if t]
				
				for i, ((start, end), prediction) in enumerate(timed_subtitles, start=1):
					for pred in prediction:
						time_begin =pred.get('time_begin')
						time_end =pred.get('time_end')
						text =pred.get('transcription')
						
				# formatted_subtitles = srt_formatter(timed_subtitles)
				
				# base, ext = os.path.splitext(source_path)
				# subtitle_file = "{base}.{format}".format(base=base, format='srt')
				# if os.path.exists(subtitle_file) is True:
				# 	os.remove(subtitle_file)
				#
				# with open(subtitle_file, 'wb') as f:
				# 	f.write(formatted_subtitles.encode("utf-8"))
				#
				# with open(subtitle_file, 'a') as f:
				# 	f.write("\n")
				#
				# os.remove(audio_filename)
				# remove_folder_music_temp(row_number)
				#
				# if origin_language in LANGUAGES_FORMAT:
				# 	print("vào")
				# 	reformat(subtitle_file)
				#
				# self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
				# 	"Hoàn Thành!")
				# self.manage_thread_pool.resultChanged.emit(str(row_number), EXTRACT_SUB_FINISHED, subtitle_file)
	
	# @decorator_try_except_class
	def _funcExtractThread (self, **kwargs):
		# try:
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		row_number = kwargs["row_number"]
		file_name = kwargs["file_name"]
		language = kwargs["language"]
		url_video = kwargs["url_video"]
		cach_lay = kwargs["cach_lay"]
		
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Bắt đầu lấy sub...")
		
		done = self.extractVoice.extractSrtFromYoutube(url_video, language, file_name, row_number, cach_lay, self.thread_pool_limit_convert, self.CachLaySubYoutubeEnum)
		thread_pool.finishSingleThread(id_worker, limit_thread=True)
		return done, row_number, file_name
