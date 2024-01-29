# -*- coding: utf-8 -*-
import os
import uuid

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import CHECK_LIVE_PROXY_ON_EXTRACT_SUB, UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	RESULT_EXTRACT_SUB, \
	ADD_TO_TABLE_EXTRACT_PROCESS, SETTING_APP_DATA, EXTRACT_SUB_FINISHED, \
	EXTRACT_SUB_SPEECH_TO_TEXT, UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, LANGUAGES_FORMAT, TOOL_CODE_MAIN
from gui.helpers.get_data import LANGUAGES_EXTRACT_AI
from gui.helpers.handle_speech.extract_sub_voice import ExtractSubVoice, srt_formatter, remove_folder_music_temp
from gui.helpers.translatepy.utils.request import Request
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from ..py_combobox import PyComboBox
from ..py_dialogs.py_dialog_show_info import PyDialogShowInfo
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_table_widget.table_process_extract import TableProcessExtractSUB
from ...configs.config_resource import ConfigResource
from ...helpers.custom_logger import decorator_try_except_class
from ...helpers.func_helper import reformat, getValueSettings
from ...helpers.http_request.check_proxy import ProxyChecker
from ...helpers.thread import ManageThreadPool


class PyTabExtractSubServerSTT(QWidget):
	def __init__ (self, group_parent, manage_thread_pool, thread_pool_limit, manage_cmd, table_process: TableProcessExtractSUB, groupBox_start_server, server_stt):
		super().__init__()
		
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		# self.group_parent = group_parent
		self.manage_thread_pool = manage_thread_pool
		self.thread_pool_limit = thread_pool_limit
		self.thread_pool_limit_convert = ManageThreadPool()
		self.thread_pool_limit_convert.setMaxThread(10)
		self.manage_cmd = manage_cmd
		self.table_process = table_process
		self.checker = ProxyChecker(manage_thread_pool)
		self.groupBox_start_server = groupBox_start_server
		self.server_stt = server_stt
		
		self.extractVoice = ExtractSubVoice(self.manage_thread_pool, self.manage_cmd)
		self.count = 0
		# PROPERTIES
		self.languages = LANGUAGES_EXTRACT_AI
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
		
		self.lb_language_origin = QLabel("Ngôn Ngữ Giọng Nói:")
		self.cb_languages_origin = PyComboBox()
		
		self.lb_server_STT = QLabel("Server Speech To Text:")
		self.cb_server_STT = PyComboBox()
		
		self.lb_notify = QLabel("Tip: Nên sử dụng proxy khi chạy nhiều luồng request lên google")
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
		
		text = "Bước 1. Chọn Ngôn Ngữ Giọng Nói"
		text += "\n\n"
		
		text += "Bước 2. Chọn Server chuyển giọng nói thành text, mặc định có server Free Google nhưng khuyến nghị nên dùng thêm proxy để tránh bị block IP, sẽ update server trả phí sẽ chính xác hơn theo yêu cầu của các sếp."
		text += "\n\n"
		
		text += "Bước 3. Lựa chọn sử dụng wifi hay proxy để request"
		text += "\n\n"
		text += "Bước 4. Bấm START rồi ngồi uống ly cà phê đợi kết quả"
		text += "\n\n"
		text += "LƯU Ý: Sử dụng cách này giống tool autosub kinh điển, độ chính xác không cao nhưng được cái tốc độ nhanh, chỉ phù hợp với giọng nói không có tạp âm hoặc không có nhạc nền"
		
		self.dialog_info = PyDialogShowInfo(text, 370)
	
	def modify_widgets (self):
		self.setDisabled(True)
		
		self.cb_languages_origin.addItems(list(self.languages.values()))
		
		self.cb_languages_origin.setCurrentText("English")
		
		self.cb_server_STT.addItems(list(self.server_stt.keys()))
	
	
	def create_layouts (self):
		self.content_layout = QVBoxLayout()
		self.content_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_status = QHBoxLayout()
		self.content_language_layout = QHBoxLayout()
		
		self.progess_convert_layout = QHBoxLayout()
		self.content_btn_layout = QGridLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.setLayout(self.content_layout)
		
		self.content_layout.addWidget(QLabel(""), 5)
		self.content_layout.addLayout(self.content_language_layout, 55)
		self.content_layout.addLayout(self.content_status, 20)
		self.content_layout.addLayout(self.content_btn_layout, 20)
		
		self.content_language_layout.addWidget(self.lb_language_origin, 20)
		self.content_language_layout.addWidget(self.cb_languages_origin, 30)
		self.content_language_layout.addWidget(self.lb_server_STT, 20)
		self.content_language_layout.addWidget(self.cb_server_STT, 30)
		
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
		self.checker.finishedCheckLiveProxySignal.connect(self._finishedCheckLiveProxySignal)
		
		self.btn_start.clicked.connect(self.clickStart)
		self.btn_info_frame.clicked.connect(self._click_info)
	
	def _click_info (self):
		self.dialog_info.exec()
	
	def loadData (self, configCurrent):
		# print(3)
		self.configCurrent = configCurrent
		
		self.isLoad = False
	
	def loadFileInput (self, path):
		self.path_input = path
	
	@decorator_try_except_class
	def clickStart (self):
		# try:
		
		self.setDisabled(True)
		row_number = self.table_process.main_table.rowCount()
		source_path = self.path_input
		server_STT_index = self.cb_server_STT.currentIndex()
		server_STT = list(self.server_stt.values())[server_STT_index]
		origin_language = list(self.languages.keys())[self.cb_languages_origin.currentIndex()]
		data_item_table = []
		data_item_table.append(source_path)
		data_item_table.append(origin_language)
		data_item_table.append("Trích xuất từ server Speech To Text")
		
		self.manage_thread_pool.resultChanged.emit(str(row_number), ADD_TO_TABLE_EXTRACT_PROCESS, data_item_table)
		
		base, ext = os.path.splitext(source_path)
		subtitle_file = "{base}.{format}".format(base=base, format='srt')
		if os.path.isfile(subtitle_file):
			os.remove(subtitle_file)
		
		# if hasattr(self, 'configCurrent'):
		# 	cau_hinh = json.loads(self.configCurrent.value)
		#
		# 	list_proxy: list = cau_hinh["proxy_raw"].split("\n")
		# else:
		# 	list_proxy: list = self.groupBox_start_server.getValue().get('proxy_raw').split("\n")
		# # print(json.loads(self.configCurrent.value))
		# # print(self.groupBox_start_server.rad_proxy.isChecked())
		# if self.groupBox_start_server.rad_proxy.isChecked() is True:
		# 	if not list_proxy == ['']:
		# 		self.checker.checkLiveProxyOnThread(self.manage_thread_pool, list_proxy, CHECK_LIVE_PROXY_ON_EXTRACT_SUB, url="https://www.google.com", row_number=row_number, source_path=source_path, server_STT=server_STT, origin_language=origin_language)
		# 	else:
		# 		self.manage_thread_pool.messageBoxChanged.emit("Lỗi", "Vui lòng cung cấp thêm proxy", "error")
		#
		# 	'''Sau này thêm các dạng proxy khác ở đây'''
		# else:
		# 	'''Khi không dùng proxy'''
		request = Request()
		
		self._extractStartThread(request, source_path, server_STT, origin_language, row_number)
	
	# except Exception as e:
	#     try:
	#         PyMessageBox().show_warning('Cảnh Báo', str(e))
	#     finally:
	#         e = None
	#         del e
	
	
	def _finishedCheckLiveProxySignal (self, id_thread, result):
		
		if id_thread == CHECK_LIVE_PROXY_ON_EXTRACT_SUB:
			''' kết quả kiểm tra live proxy'''
			if len(result['proxy_live']) == 0:
				return PyMessageBox().show_warning("Cảnh báo", "Tất cả proxy đã die hoặc bị google block IP")
			kwargs = result["kwargs"]
			# print(result['proxy_live'])
			request = Request(proxy_urls=["http://" + item for item in result['proxy_live']])
			self._extractStartThread(request,
				kwargs["source_path"], kwargs["server_STT"], kwargs["origin_language"], kwargs["row_number"])
	
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == RESULT_EXTRACT_SUB:
			if not result is None:  # return ve row_number
				pass
		
		if id_thread == EXTRACT_SUB_SPEECH_TO_TEXT:
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
				
				formatted_subtitles = srt_formatter(timed_subtitles)
				
				base, ext = os.path.splitext(source_path)
				subtitle_file = "{base}.{format}".format(base=base, format='srt')
				if os.path.exists(subtitle_file) is True:
					os.remove(subtitle_file)
				
				with open(subtitle_file, 'wb') as f:
					f.write(formatted_subtitles.encode("utf-8"))
				
				with open(subtitle_file, 'a') as f:
					f.write("\n")
				
				os.remove(audio_filename)
				remove_folder_music_temp(row_number)
				
				if origin_language in LANGUAGES_FORMAT:
					print("vào")
					reformat(subtitle_file)
				
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
					"Hoàn Thành!")
				self.manage_thread_pool.resultChanged.emit(str(row_number), EXTRACT_SUB_FINISHED, subtitle_file)
	
	# @decorator_try_except_class
	def _funcExtractThread (self, **kwargs):
		# try:
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		row_number = kwargs["row_number"]
		origin_language = kwargs["origin_language"]
		source_path = kwargs["source_path"]
		server_STT = kwargs["server_STT"]
		request = kwargs["request"]
		if "request" in kwargs.keys():
			self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
				"Bắt đầu extract sub...")
			
			done = self.extractVoice.extractSrtServerSTT(source_path, request, origin_language, row_number, server_STT, self.thread_pool_limit_convert)
			thread_pool.finishSingleThread(id_worker, limit_thread=True)
			return row_number if done is True else None
	
	
	def _extractStartThread (self, request, source_path, server_STT, origin_language, row_number):
		# try:
		
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Đang đợi...")
		
		self.thread_pool_limit.start(self._funcExtractThread, "_extractStartThreadGoogle" + uuid.uuid4().__str__(), RESULT_EXTRACT_SUB, limit_thread=True, row_number=row_number, request=request, origin_language=origin_language, source_path=source_path, server_STT=server_STT)
