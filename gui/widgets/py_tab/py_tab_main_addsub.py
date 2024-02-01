# -*- coding: utf-8 -*-
import json
import os
import random
import tempfile
import time
import uuid
from datetime import datetime

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QLabel
from deepdiff import DeepHash

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import ADD_TO_PROCESS, ADD_TO_TABLE_PROCESS, VIDEO_RENDER_NOT_TTS, \
	TRANSLATE_SUB_FINISHED, SET_STATUS_BUTTON_START, RENDER_VIDEO_FFMPEG_NO_TTS_FINISHED, TOOL_CODE_MAIN, USER_DATA, \
	START_RENDER_VIDEO_TTS, RENDER_VIDEO_FINISHED, \
	TOGGLE_SPINNER, JOIN_PATH, PATH_VIDEO, TEXT_TO_SPEECH_PUSH_PATH_AUDIO, PATH_AUDIO, RENDER_VIDEOPRE_FINISHED, \
	RenderStyleEnum, PATH_LOGS, THEM_KY_TU_NEU_SUB_CO_HAI_KYTU, XOA_SUB_DONG_SO, \
	PATH_TEMP, TRIM_AUDIO_SLICE, LOAD_VIDEO_FROM_FILE_SRT, PREVIEW_PRE_RENDER, \
	UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS, UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, \
	UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, UPDATE_STATUS_TABLE_PROCESS, GOP_SUB_DONG_TREN, \
	GOP_SUB_DONG_DUOI, THAY_THE_SUB_NEU_SUB_CO_DO_LECH_LON, LOAD_SUB_IN_TABLE_FINISHED
from gui.helpers.handle_speech.text_to_speech import TextToSpeech
from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from ..py_dialogs.py_dialog_thoi_gian_sub import PyDialogThoiGianSub
from ..py_groupbox.groupbox_config_render import GroupBoxConfigRender
from ..py_groupbox.groupbox_load_sub import GroupBoxLoadSub
from ..py_groupbox.groupbox_save_config import GroupBoxSaveConfig
from ..py_groupbox.groupbox_show_screen_tab_add_sub import GroupBoxShowScreenTabAddSub
from ..py_groupbox.groupbox_text_to_speech import GroupBoxTextToSpeech
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_messagebox.py_massagebox import PyMessageBox
from ..py_resize.splitter_resize import Resize_Splitter
from ..py_table_widget.model_timeline_addsub import ColumnNumber
from ..py_table_widget.table_process_render import TableProcessRender
from ..py_table_widget.table_timeline import TableTimeline
from ...configs.config_resource import ConfigResource
from ...helpers.custom_logger import customLogger
from ...helpers.func_helper import getValueSettings, get_duaration_video, remove_dir, checkVideoOk, has_audio, \
	check_exsist_app, seconds_to_timestamp
# from ...helpers.get_data import GENDER_VOICE_FREE_TTS_ONLINE,
from ...helpers.render.progess_render import RenderVideo
from ...helpers.server import SERVER_TAB_TTS, voice_co_san, TabIndexTTS
from ...helpers.thread import ManageCMD
from ...helpers.translatepy import Language
from ...helpers.translatepy.translators import GoogleTranslateV2
from ...helpers.translatepy.translators.tts_online_free import TTSFreeOnlineTranslator


class PyTabAddSub(QWidget):
	def __init__ (self, manage_thread_pool: ManageThreadPool, manage_cmd: ManageCMD, file_run_app, settings, fileSRTCurrent, configCurrent):
		super().__init__()
		# PROPERTIES
		# st = QSettings(*SETTING_APP)
		
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		# settings =getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		# print(settings)
		self.settings = settings
		# self.fileSRTCurrent = fileSRTCurrent
		# self.configCurrent = configCurrent
		self.LANGUAGES_CHANGE_CODE = settings.get("language_support").get("language_code")
		self.GENDER_VOICE_FREE_TTS_ONLINE = settings.get("gender_voice").get("tts_free_v2")
		
		self.file_run_app = file_run_app
		# self.row_number = 0
		self.list_worker_tts = {}
		self.list_data_sub_new = {}
		self.list_data_sub = {}
		self.list_cau_hinh = {}
		self.list_folder_name = {}
		self.list_count_sub = {}
		self.list_total_sub = {}
		self.list_path_audio = {}
		self.render_tts_finished = {}
		self.check_sub_fail = {}
		self.list_sub_fail = {}
		self.total_character = 0
		self.manage_thread_pool = manage_thread_pool  # tạo trước ui
		self.manage_thread_pool.resultChanged.connect(self._resultThreadChanged)
		
		self.thread_pool_limit = ManageThreadPool()
		self.thread_pool_limit.setMaxThread(self.user_data["list_tool"][TOOL_CODE_MAIN]["thread"])
		
		self.thread_pool_limit_print_log = ManageThreadPool()
		self.thread_pool_limit_print_log.setMaxThread(1)
		
		self.thread_pool_limit_check_error = ManageThreadPool()
		self.thread_pool_limit_check_error.setMaxThread(20)
		
		self.manage_cmd = manage_cmd  # tạo trước ui
		
		self.setAcceptDrops(True)
		
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
		
		self.btnRun = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("start.png"),
			parent=self,
			app_parent=self,
			width=60,
			height=60,
			# icon_color="#18ff4e",
			# icon_color_hover="#08fa3b",
			# icon_color_pressed="#4fc65e",
			tooltip_text="Bắt Đầu",
		
		)
		self.btnRun.setProperty("class", "btnRun")
		
		self.btn_restart = QPushButton("ReStart")
		self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_restart.setDisabled(True)
		
		# =========== Layout bên  Trái ===========
		self.tab_addsub_left = QWidget()
		
		self.bg_left_frame = QFrame()
		self.bg_left_frame.setObjectName("bg_frame")
		
		self.groupbox_timeline = TableTimeline(self.manage_thread_pool)
		self.groupBox_showscreen = GroupBoxShowScreenTabAddSub(self.manage_thread_pool, self.groupbox_timeline)
		self.groupbox_timeline.getXCenterSub = self.groupBox_showscreen.viewer.getXCenterSub
		self.groupbox_process_render = TableProcessRender(self.manage_thread_pool)
		
		# =========== Layout bên  Phải ===========
		self.tab_addsub_right = QWidget()
		
		self.bg_right_frame = QFrame()
		self.bg_right_frame.setObjectName("bg_frame")
		# self.groupBox_load_file_srt = GroupBoxLoadFileSRT(self.manage_thread_pool, self.groupBox_showscreen)
		
		# self.groupBox_network = GroupBoxNetwork(self.manage_thread_pool)
		self.groupBox_text_to_speech = GroupBoxTextToSpeech(self.manage_thread_pool, self.manage_cmd,
			self.groupbox_timeline, self.settings)
		# self.groupBox_tranlate_sub = GroupBoxTranlateSub(self.manage_thread_pool, self.groupbox_timeline,self.settings)
		
		self.groupBox_load_sub = GroupBoxLoadSub(self.manage_thread_pool)
		self.groupBox_config_render = GroupBoxConfigRender(self.manage_thread_pool)
		self.groupBox_save_config = GroupBoxSaveConfig(self.manage_thread_pool)
		
		self.video_render = RenderVideo(self.manage_thread_pool, self.thread_pool_limit, self.manage_cmd, self.file_run_app, self.groupbox_timeline)
	
	
	# self.btnRun.set_icon(ConfigResource.set_svg_icon("start-disable.png"))
	
	def modify_widgets (self):
		setting_user = self.user_data["list_tool"].get(TOOL_CODE_MAIN)
		if not 'long_tieng' in setting_user.get("tab", []):
			self.groupbox_timeline.setDisabled(True)
			self.groupBox_save_config.setDisabled(True)
			self.groupBox_showscreen.setDisabled(True)
			self.groupBox_text_to_speech.setDisabled(True)
			self.groupBox_load_sub.setDisabled(True)
			self.groupbox_process_render.setDisabled(True)
			self.setDisabledButton(True)
		# pass
	
	def create_layouts (self):
		
		self.bg_layout = QVBoxLayout(self)  # lấy self làm cha , tức là bg_layout làm con của self
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		self.content_tab_layout = QHBoxLayout()
		
		# layout bên trái
		self.content_left_layout = QVBoxLayout(self.bg_left_frame)
		self.content_left_layout.setContentsMargins(0, 0, 0, 0)

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
		
		self.btn_start_layout = QVBoxLayout()
		self.btn_start_layout.setContentsMargins(0, 0, 0, 0)
		
		self.config_layout = QVBoxLayout()
		self.config_file_layout = QHBoxLayout()
		
		self.bottom_layout = QHBoxLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.resize_splitter.setOrientation(Qt.Orientation.Vertical)
		# self.resize_splitter.setStretchFactor(1, 10)
		
		self.resize_splitter_right_left.setOrientation(Qt.Orientation.Horizontal)
		
		self.tab_addsub.setLayout(self.content_tab_layout)
		# widget_main = QWidget()
		# content_layout = QVBoxLayout()
		# content_layout.addWidget(self.tab_addsub,70)
		# content_layout.addWidget(self.groupbox_timeline)
		widget_bottom = QWidget()
		widget_bottom.setLayout(self.bottom_layout)
		#
		self.resize_splitter.addWidget(self.tab_addsub)
		self.resize_splitter.addWidget(widget_bottom)
		# self.resize_splitter.addWidget(self.groupbox_timeline)
		# self.resize_splitter.addWidget(QLabel())
		self.bottom_layout.addWidget(self.groupBox_text_to_speech)
		self.bottom_layout.addLayout(self.btn_start_layout)
		self.bottom_layout.addLayout(self.config_layout)
		
		self.config_layout.addLayout(self.config_file_layout, 70)
		self.config_layout.addWidget(self.groupBox_config_render, 30)
		
		self.config_file_layout.addWidget(self.groupBox_load_sub, 70)
		self.config_file_layout.addWidget(self.groupBox_save_config, 30)
		
		# self.bottom_layout.addWidget(self.groupBox_tranlate_sub, 20)
		
		# self.bg_layout.addWidget(self.tab_addsub, 70)  # chiếm 70% vùng chứa
		self.bg_layout.addWidget(self.resize_splitter)
		
		widget_left = QWidget()
		widget_left.setLayout(self.tab_addsub_left_layout)
		widget_right = QWidget()
		widget_right.setLayout(self.tab_addsub_right_layout)
		self.resize_splitter_right_left.addWidget(widget_right)
		self.resize_splitter_right_left.addWidget(widget_left)
		
		self.content_tab_layout.addWidget(self.resize_splitter_right_left)
		# self.content_tab_layout.addWidget(widget_right, 60)
		
		# ====== layout bên trái=======
		self.tab_addsub_left_layout.addWidget(self.bg_left_frame)
		
		self.content_left_layout.addWidget(self.groupBox_showscreen, 85)
		# self.content_left_layout.addWidget(self.groupBox_load_file_srt, 15)
		# #====== layout bên phải =======
		
		self.tab_addsub_right_layout.addWidget(self.bg_right_frame)
		
		# self.content_right_layout.addLayout(self.content_config_layout, 13)
		# self.content_right_layout.addLayout(self.convert_layout, 18)
		# self.content_right_layout.addWidget(self.groupBox_text_to_speech, 35)
		self.content_right_layout.addWidget(self.groupbox_process_render, 50)
		self.content_right_layout.addWidget(self.groupbox_timeline, 50)
		
		# self.convert_layout.addWidget(self.groupBox_tranlate_sub, 70)
		# self.convert_layout.addWidget(self.groupBox_network)
		
		self.btn_start_layout.addWidget(QLabel())
		self.btn_start_layout.addWidget(self.btnRun)
		self.btn_start_layout.addWidget(self.btn_restart)
		self.btn_start_layout.addWidget(QLabel())
	
	
	# self.content_config_layout.addWidget(self.groupBox_load_file_srt, 30)
	
	# self.content_config_layout.addWidget(self.groupBox_network, 20)
	
	def setup_connections (self):
		
		self.groupBox_save_config.signalAddConfigDBChanged.connect(self.addDataConfig)
		
		# self.groupBox_save_config.signalAddNewClearDataChanged.connect(self.addConfigStatus)
		
		self.groupBox_save_config.signalDataConfigCurrentChanged.connect(self.loadDataConfigCurrent)
		
		# self.groupBox_save_config.loadConfig()  # tạo xong widgets thì mới đến connections  nên gọi loadConfig o đây mới nhận đc tín hiệu
		
		# self.groupBox_load_file_srt.loadSrtFished.connect(self.loadSrtFished)
		self.groupBox_showscreen.sliderChangeFrameChanged.connect(self.sliderChangeFrameChanged)
		
		self.manage_thread_pool.errorChanged.connect(self._errorThreadPoolChanged)
		self.manage_thread_pool.messageBoxChanged.connect(self._messageBoxChanged)
		self.thread_pool_limit_check_error.resultChanged.connect(self._resultThreadChanged)
		
		self.btn_restart.clicked.connect(lambda: self.setDisabledButton(False))
		
		self.btnRun.clicked.connect(self.startThread)
		self.btnRun.doubleClicked.connect(self.btnRunDoubleClick)
	
	# self.btnRunDoubleClick =self.btnRun.mouseDoubleClickEvent
	
	#
	# self.table_timeline.getConfigChanged.connect(self.get_config_changed)
	# self.table_timeline.statusButtonChanged.connect(self.status_button_changed)
	def btnRunDoubleClick (self):
		print("btnRunDoubleClick")
	
	def check_render_tts_finished (self, row_number, return_value=True, value=False):
		if return_value:
			# print(self.render_tts_finished)
			return self.render_tts_finished[(row_number)]
		else:
			self.render_tts_finished[(row_number)] = value
	
	def getFolderVideoRow (self, folder_name):
		# namevideo = os.path.basename(self.path_video[(row_number)])[:-4]
		path = JOIN_PATH(PATH_VIDEO, str(folder_name))
		
		if os.path.exists(path) is False:
			os.mkdir(path)
		
		return path
	
	
	def getFolderRow (self, folder_name):
		# namevideo = os.path.basename(self.path_video[(row_number)])[:-4]
		path = JOIN_PATH(PATH_AUDIO, str(folder_name))
		path_video = JOIN_PATH(PATH_VIDEO, str(folder_name))
		# file_output = JOIN_PATH(PATH_VIDEO, str(folder_name) + ext)
		if os.path.isdir(path):
			is_ok = PyMessageBox().show_question("Thông báo", "Đã tồn tại trạng thái Lấy Voice trước đó. Bạn có muốn lấy lại không ? Lấy lại sẽ gây lãng phí ký tự !")
			if is_ok:
				try:
					remove_dir(path)
				except:
					pass
		# else:
		# 	return path
		
		if os.path.exists(path) is False:
			os.mkdir(path)
		
		if os.path.exists(path_video) is False:
			os.mkdir(path_video)
		
		return path, path_video
	
	def removeFileLog (self):
		seconds = 86400
		# list_of_files = os.listdir()
		
		# get the current time
		current_time = time.time()
		# loop over all the files
		for f in os.scandir(PATH_LOGS):
			# get the location of the file
			if f.is_file():
				# if "uncompyle6" in f.path.lower():
				try:
					if os.path.splitext(f.path)[1].lower() in ['.txt']:
						file_location = f.path
						# file_time is the time when the file is modified
						file_time = os.stat(file_location).st_mtime
						
						# if a file is modified before N days then delete it
						if (file_time < current_time - seconds):
							# print(f" Delete : {file_location}")
							os.remove(file_location)
				except:
					pass
	
	def startThread (self):
		if self.folder_name and os.path.isdir(self.folder_name):

			cau_hinh: dict = json.loads(self.configCurrent.value)

			job_id = uuid.uuid4().hex
			row_number = self.groupbox_process_render.main_table.rowCount()
			
			data_sub = self.groupbox_timeline.getDataSub()

			detect_lang = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)

			sub_random = random.choice(data_sub)
			text_random = sub_random[ColumnNumber.column_sub_text.value]

			lang_code = cau_hinh["servers_tts"]["language_tts"].split("-")[0]
			if lang_code != voice_co_san:
				language_tts = Language(lang_code).in_foreign_languages.get('en')
				if language_tts == 'Filipino':
					language_tts = 'Tagalog'
					lang_code = 'tl'

				lang_source = detect_lang.language(text_random).result.in_foreign_languages.get('en')
				#
				print(lang_code)
				print(language_tts)
				print(lang_source)
				if not lang_source == language_tts:
					is_ok = PyMessageBox().show_question("Thông báo",
														 "Ngôn ngữ SUB không trùng với ngôn ngữ ĐỌC, Bạn có muốn tiếp tục RENDER ?")
					if is_ok:
						pass
					else:
						return
			else:
				language_tts = "Cosan"
				lang_code = "vi"
			self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)

			self.list_data_sub[(row_number)] = data_sub
			self.list_cau_hinh[(row_number)] = cau_hinh
			self.list_folder_name[(row_number)] = self.folder_name + ""
			self.list_total_sub[(row_number)] = len(data_sub)
			self.list_count_sub[(row_number)] = 0
			self.list_sub_fail = {}
			self.total_character = 0
			self.check_sub_fail[(row_number)] = False
			# print(self.check_sub_fail[(row_number)])

			tab_tts_active = cau_hinh["tab_tts_active"]
			gender_tts = cau_hinh["servers_tts"]["gender"]
			ky_tu_toi_thieu = 1
			if tab_tts_active == TabIndexTTS.FPTAI.value or 'f_' in gender_tts:
				ky_tu_toi_thieu = 3

			speed_giong_doc = cau_hinh["speed_giong_doc"]



			for index, sub in enumerate(data_sub):  # lọc sub vừa với video

				self.thread_pool_limit_check_error.start(self._funcCheckErrorTTS, "start-render-" + job_id,
														 ADD_TO_PROCESS,
														 ky_tu_toi_thieu=ky_tu_toi_thieu,
														 row_number=row_number,
														   index=index,   sub=sub,
														 detect_lang=detect_lang, language_tts=language_tts)

			self.btn_restart.setDisabled(False)
			
			self.setDisabledButton(True)
		else:
			PyMessageBox().show_error('Cảnh Báo', "Không tìm thấy folder image!")
	
	def _funcCheckErrorTTS (self, **kwargs):
		id_worker = kwargs["id_worker"]
		row_number = kwargs["row_number"]
		thread_pool = kwargs["thread_pool"]
		language_tts = kwargs["language_tts"]
		detect_lang = kwargs["detect_lang"]
		ky_tu_toi_thieu = kwargs["ky_tu_toi_thieu"]
		index = kwargs["index"]
		sub = kwargs["sub"]
		text = ''
		
		if self.check_sub_fail[(row_number)]:
			return
		# print("QUa")
		text = sub[ColumnNumber.column_sub_text.value]
		if len(text) < ky_tu_toi_thieu:
			return False, row_number, (
				"ERROR-TYPE-1\n- Dòng sub số {index} có nội dung dưới " + str(ky_tu_toi_thieu) + " ký tự\n- Bấm THAY THẾ để thay lại nội dung\n- Bấm SAVE để tự động thêm dấu chấm cho đủ " + str(ky_tu_toi_thieu) + " ký tự\n- Bấm DELETE để xóa",
				index,  text)
		
		if text[0] in '''.,;'"！.]:()·、>/\\{}，：".·-.*=（)^%#@?$&|\<+!【[''':
			return False, row_number, (
				"ERROR-TYPE-1\n- Dòng sub số {index} có ký tự đặc biệt\n- Bấm THAY THẾ để thay lại nội dung\n- Bấm DELETE để xóa",
				index,  text)
		
		# KIỂM TRA KÝ TỰ
		if len(text) > 500:
			return False, row_number, (
				"ERROR-TYPE-1\n- Dòng sub số {index} có nội dung " + f"{len(text)} ký tự, Quá mức cho phép" + "\n- Vui lòng chỉnh sửa dòng sub dưới 500 ký tự",
				index,  text)

		thread_pool.finishSingleThread(id_worker)
		return True, row_number, len(text)
	
	
	def _resultCMDSignal (self, id_worker, type_cmd, result, kwargs):
		pass
	
	def _resultThreadChanged (self, id_worker, id_thread, result):
		# print(result)
		
		if id_thread == ADD_TO_PROCESS:
			
			# try:
			is_ok, row_number, res = result
			# print(self.check_sub_fail[(row_number)])
			if self.check_sub_fail[(row_number)]:
				return
			
			if is_ok is False:
				message, ind_row,  text_sub = res
				
				self.list_sub_fail.update({(ind_row): (message,  text_sub)})
			
			elif is_ok is None:
				return
			
			self.list_count_sub[(row_number)] += 1
			# print(len_char)
			if isinstance(res, int):
				self.total_character += res
			
			if self.list_count_sub[(row_number)] == self.list_total_sub[(row_number)]:
				if len(self.list_sub_fail) > 0:
					self.setDisabledButton(False)
					# self.check_sub_fail[(row_number)] = True
					self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
					sorted_dict_by_key = dict(sorted(self.list_sub_fail.items()))
					# print(sorted_dict_by_key)
					count_delete = 0
					for ind_row, err in sorted_dict_by_key.items():
						message, text_sub = err
						# print(ind_row)
						row_curr = ind_row - count_delete
						self.groupbox_timeline.main_table.selectRow(row_curr)
						
						dial = PyDialogThoiGianSub(message.format(index=row_curr + 1), "Chỉnh sửa Dòng Sub",  text_sub, width=688, height=350)
						if dial.exec():
							if dial.is_delete:
								count_delete += 1
								self.manage_thread_pool.resultChanged.emit(XOA_SUB_DONG_SO, XOA_SUB_DONG_SO, row_curr)
							
							elif dial.is_top:
								count_delete += 1
								self.manage_thread_pool.resultChanged.emit(GOP_SUB_DONG_TREN, GOP_SUB_DONG_TREN, row_curr)
							
							elif dial.is_bottom:
								count_delete += 1
								self.manage_thread_pool.resultChanged.emit(GOP_SUB_DONG_DUOI, GOP_SUB_DONG_DUOI, row_curr)
							
							elif dial.is_auto_add:
								self.manage_thread_pool.resultChanged.emit(THEM_KY_TU_NEU_SUB_CO_HAI_KYTU, THEM_KY_TU_NEU_SUB_CO_HAI_KYTU, (
									row_curr, '..'))
							else:
								self.manage_thread_pool.resultChanged.emit(THAY_THE_SUB_NEU_SUB_CO_DO_LECH_LON, THAY_THE_SUB_NEU_SUB_CO_DO_LECH_LON, (
									row_curr, dial.getValue()))
					# else:
					# 	PyMessageBox().show_warning("Lỗi", message.format(index=row_curr))
					
					self.list_sub_fail = {}
					self.list_count_sub[(row_number)] = 0
					self.list_total_sub[(row_number)] = 0
					return
				
				self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
				self.list_count_sub[(row_number)] = 0
				self.list_total_sub[(row_number)] = 0
				
				total_character = self.total_character + 0  # tạo bản copy
				# print(total_character)
				folder_name = self.list_folder_name[(row_number)]
				cau_hinh = self.list_cau_hinh[(row_number)]
				data_sub = self.list_data_sub[(row_number)]
				
				data_sub_new = self.list_data_sub_new.get((row_number), None)
				
				self.list_worker_tts[(row_number)] = folder_name
				# _____________________________ KIỂM TRA SỐ LƯỢNG TỪ CÓ ĐỦ BÊN SERVER TRẢ PHÍ________________________________
				
				lamda_server_trans = SERVER_TAB_TTS.get(
					list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("server_trans")
				api_server = SERVER_TAB_TTS.get(
					list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("name_api_db")
				
				server_trans = lamda_server_trans(manage_thread_pool=self.manage_thread_pool, file_json=
				cau_hinh["servers_tts"][
					api_server])
				check_ok, mes = server_trans.check_token()
				if check_ok is False:
					return PyMessageBox().show_warning("Thông báo", mes)
				
				check_ok, balance, total_token = server_trans.check_balance()
				if check_ok is False:
					return PyMessageBox().show_warning("Thông báo", "Token API của bạn bị sai hoặc đã hết hạn")
				
				if isinstance(balance, dict):
					balance = -1 if isinstance(balance.get('characters'), str) else balance.get('characters')
				
				if not balance == -1:
					if total_character > int(balance) - 100:
						return PyMessageBox().show_warning("Thông báo", "Số ký tự còn lại trong tài khoản không đủ !")
				self.total_character = 0
				
				list_fonts, rect_blur, layers = self.groupBox_showscreen.viewer.list_fonts, self.groupBox_showscreen.viewer.list_blur, self.groupBox_showscreen.viewer.layers
				

				# thêm vào bảng
				'''Sau khi thêm vào bảng thì trả về số dòng đó để trong các thread push status cho đúng'''
				data_item_table = []
				data_item_table.append(cau_hinh['src_output'])
				self.manage_thread_pool.resultChanged.emit(ADD_TO_TABLE_PROCESS, ADD_TO_TABLE_PROCESS, data_item_table)
				#
				# self.manage_thread_pool.resultChanged.emit(RESET_FOLDER_VOICE, RESET_FOLDER_VOICE,'')
				
				self.render_tts_finished[(row_number)] = False
				
				list_layers = [list(layer.values())[0].itemToVariant() for layer in layers]
				# name_video, ext = os.path.basename(path_video)[:-4], os.path.basename(path_video)[-4:]
				
				data_save = {
					"folder_name": folder_name,
					"list_layers": list_layers,
					"sub_hien_thi": cau_hinh,
					"list_blur": [blur.itemToVariant().get('value') for blur in
								  rect_blur] if len(rect_blur) > 0 else "",
				}
				# a482ea79eb6afee5c67ade6179031ce4ebf7b445c680ed2e93549c8368a43928
				key_hash = str(data_save)
				
				folder_temp = DeepHash(key_hash)[key_hash]
				
				folder_audio, folder_video = self.getFolderRow(folder_temp )

				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
					"Đang Đợi...")
				self.thread_pool_limit.start(self.funcRenderTTS, START_RENDER_VIDEO_TTS, START_RENDER_VIDEO_TTS,
					data=(
						folder_audio, folder_video,  list_fonts, rect_blur, list_layers, folder_name,
						row_number, cau_hinh, data_sub, data_sub_new))
		
		# except:
		# pass
		
		if id_thread == PREVIEW_PRE_RENDER:
			if hasattr(self, 'path_video'):
				if not os.path.isfile(self.path_video):
					PyMessageBox().show_error('Cảnh Báo', "Không tìm thấy file 'Video' tương ứng!")
					return
				filters = self.groupBox_showscreen.viewer.list_fonts, self.groupBox_showscreen.viewer.list_blur, self.groupBox_showscreen.viewer.layers
				row_number = self.groupbox_process_render.main_table.rowCount()
				cau_hinh: dict = json.loads(self.configCurrent.value)
				data_sub = result
				self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
				cau_hinh_edit = json.loads(self.fileSRTCurrent.value)
				pos_add_sub = cau_hinh_edit.get('pos_add_sub')
				self.video_render.render_video_preview(self.path_video, filters, row_number, cau_hinh, data_sub, pos_add_sub)

		if id_thread == TRANSLATE_SUB_FINISHED or id_thread == LOAD_SUB_IN_TABLE_FINISHED:
			# print('ok')
			self.setDisabledButton(False)
		
		if id_thread == SET_STATUS_BUTTON_START:
			self.setDisabledButton(result)

		
		if id_thread == TEXT_TO_SPEECH_PUSH_PATH_AUDIO:
			row_number, folder_audio = result
			# print(row_number, folder_audio)
			self.list_path_audio[int(row_number)] = folder_audio
		
		if id_thread == RENDER_VIDEO_FINISHED:
			row_number = int(id_worker)
			# print(row_number)
			# print(self.list_worker_tts)
			id_WK = self.list_worker_tts[(row_number)]
			self.manage_thread_pool.finishSingleThread(id_WK)
	
	
	def funcRenderTTS (self, **kwargs):

		folder_audio, folder_video, list_fonts, rect_blur, list_layers, folder_name,row_number, cau_hinh, data_sub, data_sub_new = kwargs.get('data')
		cau_hinh_edit = json.loads(self.fileSRTCurrent.value)
		pos_add_sub = cau_hinh_edit.get('pos_add_sub')
		self.covertTTS.convertTextToSpeechChunk(row_number, cau_hinh, data_sub, folder_audio)

		self.video_render.render_video_image(folder_name, list_layers, list_fonts, rect_blur, row_number,cau_hinh, data_sub, data_sub_new, folder_audio, folder_video, pos_add_sub)
		if data_sub_new is not None:
			data_sub = data_sub_new

	def checkaudiovideo (self, cau_hinh, video_path):
		
		if cau_hinh['text_to_speech']:
			if cau_hinh['thuyet_minh'] and has_audio(video_path) is False:
				return False, "Bạn dùng chế độ thuyết minh, nhưng video không có âm thanh"
		
		if cau_hinh['no_sound'] is False and has_audio(video_path) is False:
			return False, 'Video không có âm thanh, vui lòng tích chọn vào "Render Video No Sound"'
		return True, ''
	
	def loadFileSRTCurrent (self, fileSRTCurrent, db_app, db_srt_file):
		self.fileSRTCurrent = fileSRTCurrent
		cau_hinh_edit: dict = json.loads(fileSRTCurrent.value)
		self.folder_name = cau_hinh_edit.get('folder_name')

		# path_video = cau_hinh_edit.get('video_file')
		# if os.path.isfile(path_video):
		# 	self.path_video = path_video
		# 	self.src_subtitle = cau_hinh_edit.get('srt_file')
		
		self.groupBox_load_sub.loadFileSRTCurrent(fileSRTCurrent, db_app, db_srt_file)
		self.groupbox_timeline.loadFileSRTCurrent(fileSRTCurrent)
		self.groupBox_showscreen.loadFileSRTCurrent(fileSRTCurrent)
		self.groupBox_text_to_speech.loadFileSRTCurrent(fileSRTCurrent)
	
	# print(fileSRTCurrent)
	# self.manage_thread_pool.resultChanged.emit(LOAD_CONFIG_TAB_ADD_SUB_CHANGED, LOAD_CONFIG_TAB_ADD_SUB_CHANGED, self.fileSRTCurrent)
	
	def loadDataConfigCurrent (self, configCurrent, list_config, db_app, db_cau_hinh):
		self.configCurrent = configCurrent
		# self.manage_thread_pool.resultChanged.emit(LOAD_CONFIG_CHANGED, LOAD_CONFIG_CHANGED, configCurrent)
		
		# self.cau_hinh: dict = json.loads(configCurrent.value)
		
		# self.groupBox_tranlate_sub.loadData(configCurrent)
		self.groupBox_save_config.loadDataConfigCurrent(configCurrent, list_config, db_app, db_cau_hinh)
		self.groupBox_config_render.loadDataConfigCurrent(configCurrent)
		
		self.groupbox_timeline.loadDataConfigCurrent(configCurrent)
		
		self.groupbox_process_render.loadDataConfigCurrent(configCurrent)
		# self.groupBox_network.loadData(configCurrent)
		# self.groupBox_load_file_srt.loadDataConfigCurrent(configCurrent)
		
		self.groupBox_text_to_speech.loadDataConfigCurrent(configCurrent)
		
		self.groupBox_showscreen.loadDataConfigCurrent(configCurrent)
		
		#
		# if not self.groupBox_load_file_srt.text_src_file == "":
		#     self.groupBox_showscreen.slider_change_frame.setValue(1)
		# self.groupBox_showscreen.
		#
		self.video_render.loadDataConfigCurrent(configCurrent)
		
		self.covertTTS = TextToSpeech(self.manage_thread_pool, self.manage_cmd,
			self.configCurrent, self.check_render_tts_finished)
		
		self.video_render.getVoiceRowErorr = self.covertTTS.getVoiceRow
	
	
	def addDataConfig (self):
		data_config = {
			**self.groupBox_text_to_speech.getValue(), **self.groupBox_config_render.getValue()}
		
		# print(data_config)
		self.groupBox_save_config.addNewConfig(data_config)
	
	def addConfigStatus (self):
		# self.groupBox_tranlate_sub.clearData()
		# self.groupBox_network.clearData()
		self.groupBox_text_to_speech.clearData()
		self.groupBox_config_render.clearData()
	
	def _messageBoxChanged (self, title, message, type):
		
		if type == "warning":
			PyMessageBox().show_warning(title, message)
		
		if type == "error":
			PyMessageBox().show_error(title, message)
		
		if type == "info":
			PyMessageBox().show_info(title, message)
	
	def _errorThreadPoolChanged (self, id_worker, typeThread, error):
		print(error)
		self.thread_pool_limit_print_log.start(self.print_log, "PRINT_LOG", "PRINT_LOG", error=error)
	
	# print("class/id_worker: "+ cls + 'function/typeThread: '+methodName+'\n'+error)
	# PyMessageBox().show_warning("Lỗi trong luồng",error)
	def print_log (self, **kwargs):
		try:
			fun_name, mess = kwargs.get('error')
			customLogger(fun_name).error(mess)
		except:
			pass
	
	def showData (self, data):
		pass
	
	def loadSrtFished (self, data):
		cau_hinh = json.loads(self.configCurrent.value)
		
		# self.groupbox_timeline.displayTable(data, self.db_app)
		
		# self.groupBox_tranlate_sub.load_file_srt_finished = True  # thông báo là file srt đã đc load
		# if cau_hinh["dich_tu_dong"] is True:
		# 	self.groupBox_tranlate_sub.tranlateSub()  # dịch sub lần đầu load
		
		self.setDisabledButton(False)
	
	def setDisabledButton (self, disabled):
		self.btnRun.setDisabled(disabled)
		
		if disabled is True:
			self.btnRun.set_icon_color = "#c3ccdf"
			self.btnRun.icon_color = "#c3ccdf"
			self.btnRun.icon_color_hover = "#dce1ec"
			self.btnRun.icon_color_pressed = "#edf0f5"
		else:
			self.btnRun.set_icon_color = "#03b803"
			self.btnRun.icon_color = "#03b803"
			self.btnRun.icon_color_hover = "#1be21b"
			self.btnRun.icon_color_pressed = "#4fc65e"
		
		self.btnRun.repaint()
	
	def sliderChangeFrameChanged (self, data):
		# self.groupbox_timeline.main_table.selectRow(data - 1)
		# self.groupbox_timeline.main_table.ke
		
		pass
	
	# PrintLog(data)
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
				name, ext = os.path.splitext(srt_path)
				if not ext.lower() in ['.srt']:
					return PyMessageBox().show_warning("Thông báo", f"File {ext} không được hỗ trợ")
				self.manage_thread_pool.resultChanged.emit(LOAD_VIDEO_FROM_FILE_SRT, LOAD_VIDEO_FROM_FILE_SRT, srt_path)
			else:
				return PyMessageBox().show_warning("Thông báo", "File SUB srt không không tồn tại ")
