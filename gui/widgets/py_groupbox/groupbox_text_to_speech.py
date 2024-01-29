import base64
import json
import os
import shutil
import tempfile
import uuid
from datetime import datetime

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QCheckBox, \
	QLineEdit, QHBoxLayout, QVBoxLayout, QGroupBox, QSlider, QFileDialog, QProgressBar

from gui.configs.config_resource import ConfigResource
from gui.helpers.audiostretchy.stretch import stretch_audio
from gui.helpers.constants import TEXT_TO_SPEECH_DEMO, JOIN_PATH, APP_PATH, UPDATE_BALANCE_API_TTS, PATH_DB, \
	GET_TOKEN_SERVER_TTS, CHECK_DO_LECH_VIDEO, PATH_TEMP, UPDATE_VALUE_PROGRESS_CHECK_LECH_SUB, \
	RESULT_CHECK_DO_LECH_VIDEO, TRIM_AUDIO_SLICE, CHECK_DO_LECH_PART_SUB, RESULT_CHECK_DO_LECH_VIDEO_PART, \
	CHECK_DO_LECH_TABLE_CHANGED_PART, CHECK_DO_LECH_DIALOG_SUMMARY, CHECK_DO_LECH_PART_SUMMARY, \
	RESULT_CHECK_DO_LECH_VIDEO_SUMMARY, PATH_VOICE, USER_DATA, TOOL_CODE_MAIN, RESET_FOLDER_VOICE, CLICK_DOC_THU_VOICE, \
	TTS_GET_VOICE_FINISHED, CHECK_LECH_SUB_FINISHED
from gui.helpers.func_helper import get_duaration_video, remove_dir, pitch_shift, play_media_preview, check_exsist_app, \
	getValueSettings, seconds_to_timestamp
from gui.helpers.get_data import URL_API_BASE
from gui.helpers.server import SERVER_TAB_TTS, TabIndexTTS, \
	voice_co_san
from gui.helpers.thread import ManageThreadPool
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators import GoogleTranslateV2
from gui.helpers.translatepy.translators.tts_online_free import TTSFreeOnlineTranslator
from gui.widgets.py_checkbox import PyCheckBox
from gui.widgets.py_combobox import PyComboBox
from gui.widgets.py_dialogs.py_dialog_config_smart_cut import PyDialogConfigSmartCut
from gui.widgets.py_dialogs.py_dialog_config_thuyet_minh import PyDialogConfigThuyetMinh
from gui.widgets.py_dialogs.py_dialog_get_int import PyDialogGetInt
from gui.widgets.py_dialogs.py_dialog_show_info import PyDialogShowInfo
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_spinner.spinner import WaitingSpinner
from gui.widgets.py_table_widget.model_timeline_addsub import ColumnNumber


class GroupBoxTextToSpeech(QWidget):
	def __init__ (self, manage_thread_pool: ManageThreadPool, manage_cmd, groupbox_timeline, settings):
		super().__init__()
		
		self.list_language_support = settings.get("language_support")
		self.LANGUAGES_CHANGE_CODE = settings.get("language_support").get('language_code')
		self.LINK_DEMO_VOICE = settings.get("link_demo_voice")
		self.MODE_TTS = settings.get("mode_render_tts")
		self.list_gender_voice = settings.get('gender_voice')
		self.GENDER_VOICE_FREE_TTS_ONLINE = settings.get("gender_voice").get("tts_free_v2")
		
		self.STYLE_LIST_TTS = {}
		gender_tts_pro = {}
		for code, value in self.list_gender_voice.get('tts_pro').items():
			temp = {}
			for key, vl in value.items():
				if vl.get("style_list") is not None:
					# print(json.loads(vl.get("style_list")))
					self.STYLE_LIST_TTS.update({key: json.loads(vl.get("style_list"))})
					temp.update({key: vl.get("name") + " - Style"})
				
				else:
					temp.update({key: vl.get("name")})
			
			gender_tts_pro.update({code: temp})
		
		self.list_gender_voice.update({"tts_pro": gender_tts_pro})
		GENDER_VOICE_COSAN = {}
		for lang, value in self.list_language_support.get("language_code").items():
			GENDER_VOICE_COSAN.update({
				lang: {
					value: "Có Sẵn"
				}
			})
		self.list_gender_voice.update({"cosan": GENDER_VOICE_COSAN})
		
		self.manage_thread_pool = manage_thread_pool
		self.manage_cmd = manage_cmd
		self.groupbox_timeline = groupbox_timeline
		self.isClearData = False
		self.isChanged = False
		self.isCheckingDoLech = False
		self.isStopCheckDoLech = False
		self.total_acc = 0
		self.count_thread_get_token = 0
		self.list_data_token = {}
		self.count_result_check_lech = 0
		self.thread_pool_limit = ManageThreadPool()
		self.thread_pool_limit.setMaxThread(1)
		# self.languages = LANGUAGES_TRANS
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		
		self.create_layouts()
		
		self.add_widgets_to_layouts()
		
		self.setup_connections()
	
	def create_widgets (self):
		self.groupbox = QGroupBox("Lồng Tiếng Và Thuyết Minh")
		self.groupbox.setCheckable(True)
		
		self.cbox_server = PyComboBox()
		# self.tab_texttospeech = QTabWidget()
		# self.tab_texttospeech.setObjectName("tabWidget")
		# self.tab_texttospeech.setProperty("class", "tabSmall")
		
		self.progess_convert = QProgressBar(self, objectName="RedProgressBar")
		
		self.lb_status_demo = QLabel()
		# self.btn_demo = QPushButton("Đọc thử")
		# self.btn_demo.setCursor(Qt.CursorShape.PointingHandCursor)
		
		
		self.lb_person_voice = QLabel("Chọn Giọng Đọc:")
		self.cb_person_voice = PyComboBox()
		self.btn_play_demo = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("play.png"),
			parent=self,
			width=25,
			height=25,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
			app_parent=self,
			tooltip_text="Nghe thử"
		
		)
		self.lb_style = QLabel("Style:")
		self.cb_style = PyComboBox()
		
		self.lb_mode_tts = QLabel("Mode:")
		self.cb_mode = PyComboBox()
		
		self.lb_api = QLabel("FILE JSON")
		self.input_api = QLineEdit()
		self.input_api.setReadOnly(True)
		
		self.btn_file_json = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		
		self.lb_language = QLabel("Chọn Ngôn Ngữ Đọc:")
		self.cb_language = PyComboBox()
		
		text = "- Bạn tích chọn vào ô vuông để lồng tiếng đọc cho video, tích bỏ chọn để chỉ hiện thị sub trong video"
		text += "\n\n- B1: Bấm vào chọn server chuyển giọng đọc"
		text += "\n\n- B2: Chọn Chế độ Đọc"
		text += "\n\n- B3: Chọn ngôn ngữ giọng đọc"
		text += "\n\n- B4: Chọn giọng đọc"
		
		text += "\n\n- B5: Chọn Mode Khi lồng giọng đọc"
		text += "\n\n- Do giọng đọc của các ngôn ngữ sẽ có độ dài khác nhau nên việc khớp vào đoạn sub sẽ bị lệch nhau. Vậy nên để khớp với nhau thì tool sẽ có 2 MODE cho bạn lựa chọn. "
		
		text += "\n\n  + Mode: KHỚP VỚI GIỌNG ĐỌC"
		text += "\n       - Tức là hình ảnh của đoạn sub phải khới với giọng đọc lồng tiếng"
		text += "\n       - Ưu điểm: Khi đọc ngôn ngữ khác nhau sẽ không bị tình trạng đoạn nói quá nhanh, đoạn nói quá chậm."
		text += "\n       - Khuyết điểm: Nhiều đoạn hình sẽ hơi giật và bị slowmotion."
		
		text += "\n\n  + Mode: KHỚP VỚI HÌNH"
		text += "\n       - Tức là giọng đọc lồng tiếng phải khới với hình ảnh của đoạn sub"
		text += "\n       - Ưu điểm: Không bị tình trạng giật lag lúc chuyển sub"
		text += "\n       - Khuyết điểm: Nhiều đoạn nói quá nhanh hoặc quá chậm, không nghe rõ tiếng, vì mỗi ngôn ngữ phát âm độ dài khác nhau"
		
		text += "\n\n- Bấm Nút START để bắt đầu quá trình render"
		text += "\n- TIP: Nếu sử dụng nhiều nên dùng proxy để không bị chặn IP"
		text += "\n\n------------------ CHỨC NĂNG ĐỘ LỆCH TIME ------------------"
		
		text += "\n\n- Độ lệch thời gian là tổng thời gian đọc đoạn sub đó so với thời lượng thực tế đoạn sub đó xuất hiện."
		text += "\n\n- Nếu độ lệch càng lớn thì đoạn sub đó sẽ bị nói quá nhanh hoặc hình ảnh bị chậm slomotion."
		text += "\n\n- Sau khi quá trình check thành công thì màu sắc của sub sẽ phân chia ra 4 cấp độ màu khác nhau: "
		text += "\n 	+Cấp độ 1 (Màu Trắng): Đoạn sub bình thường không cần chỉnh sủa gì thêm"
		text += "\n	+Cấp độ 2 (Màu Vàng): Đoạn sub có độ lệch 1 < dolech < 1,5 thời gian thực tế"
		text += "\n 	+Cấp độ 3 (Màu Cam): Đoạn sub có độ lệch 1.5 < dolech < 2 thời gian thực tế"
		text += "\n 	+Cấp độ 4 (Màu Đỏ): Đoạn sub có độ lệch dolech > 2 lần thời gian thực tế"
		text += "\n\n- Đối với các đoạn sub có cấp độ 3,4 bạn nên sử dụng chức năng rút gọn nội dung để có được thời gian đọc ngắn hơn bằng cách chuột phải vào dòng sub và chọn RÚT NGẮN NỘI DUNG "
		text += "\n\n- Lưu ý đối với chức năng RÚT GỌN NỘI DUNG bạn phải chọn ngôn ngữ đọc và CHẾ ĐỘ ĐỌC đúng"
		self.dialog_info = PyDialogShowInfo(text, 800)
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
		self.lb_blance = QLabel("")
		self.lb_link_dang_ky = QLabel("")
		self.lb_link_dang_ky.setOpenExternalLinks(True)
		
		self.lb_volume_tts = QLabel("Âm Lượng Đọc:")
		self.slider_volume_tts = QSlider()
		self.slider_volume_tts.setOrientation(Qt.Orientation.Horizontal)
		self.slider_volume_tts.setRange(0, 500)
		self.slider_volume_tts.setPageStep(1)
		self.slider_volume_tts.setValue(100)
		self.lb_number_volume_tts = QLabel(str(self.slider_volume_tts.value()))
		
		self.lb_speed = QLabel("Tốc Độ Đọc:")
		self.slider_speed = QSlider()
		self.slider_speed.setMinimum(3)
		self.slider_speed.setMaximum(35)
		self.slider_speed.setPageStep(1)
		# self.slider_speed.setValue(10)
		self.slider_speed.setOrientation(Qt.Orientation.Horizontal)
		self.lb_speed_number = QLabel(str(self.slider_speed.value() / 10) + "x")
		
		self.lb_pitch = QLabel("Chỉnh giọng:")
		self.slider_pitch = QSlider()
		self.lb_number_pitch = QLabel()
		self.slider_pitch.setOrientation(Qt.Orientation.Horizontal)
		self.slider_pitch.setRange(-50, 50)
		self.slider_pitch.setPageStep(1)
		
		self.slider_pitch.setValue(0)
		self.lb_number_pitch.setText(str(self.slider_pitch.value()) + "%")
		
		self.lb_quang_nghi = QLabel("Quãng nghỉ:")
		self.slider_quang_nghi = QSlider()
		self.lb_number_quang_nghi = QLabel()
		self.slider_quang_nghi.setOrientation(Qt.Orientation.Horizontal)
		self.slider_quang_nghi.setRange(0, 1000)
		self.slider_quang_nghi.setValue(0)
		self.lb_number_quang_nghi.setText(str(self.slider_quang_nghi.value()) + " ms")
		
		# self.cb_remove_sound = PyCheckBox(value="remove_sound", text="Xoá Âm Thanh Gốc")
		
		self.cb_thuyet_minh = PyCheckBox(value="thuyet_minh", text="Giữ Tiếng Gốc")
		self.dialog_config_thuyet_minh = PyDialogConfigThuyetMinh()
		self.btn_config_thuyet_minh = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("settings.png"),
			parent=self,
			app_parent=self.groupbox,
			width=25,
			height=25,
			tooltip_text="Cài đặt thuyết minh",
		
		)
		
		self.cb_smart_cut = PyCheckBox(value="smart_cut", text="Cắt Thông Minh")
		self.dialog_smart_cut = PyDialogConfigSmartCut()
		self.btn_config_smart_cut = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("settings.png"),
			parent=self,
			app_parent=self.groupbox,
			width=25,
			height=25,
			tooltip_text="Cài đặt",
		
		)
		
		self.cb_render_video_origin = PyCheckBox(value="use_video_origin", text="Dùng Video Gốc")

		self.lb_solan = QLabel("Kiểm tra time lệch:")
		self.combobox_solan = PyComboBox()
		self.combobox_solan.addItems([str(i) for i in range(2, 15)])
		# self.combobox_solan.setCurrentText("8")
		
		# self.btn_get_token = QPushButton("Lấy Token")
		# self.btn_get_token.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.lb_channel_audio = QLabel("Số Kênh Âm Thanh:")
		self.combo_channel_audio = PyComboBox()
		self.combo_channel_audio.addItems(['1', '2'])
		
		self.btn_demo = QPushButton("Đọc thử")
		self.btn_demo.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.btn_check_do_lech = QPushButton("Check Lệch Time")
		self.btn_check_do_lech.setCursor(Qt.CursorShape.PointingHandCursor)
		#
		# self.btn_gop_thoai = QPushButton("Gộp Thoại")
		# self.btn_gop_thoai.setCursor(Qt.CursorShape.PointingHandCursor)
		#
		self.lb_folder_voice = QLabel("Folder Voice:")
		self.btn_dialog_folder_voice = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.input_src_voice = QLineEdit()
		self.input_src_voice.setReadOnly(True)
	
	# self.dialog_info_dolech = PyDialogShowInfo(text, 820)
	
	def modify_widgets (self):
		
		self.cb_mode.addItems(self.MODE_TTS.values())
		
		self.cbox_server.addItems(SERVER_TAB_TTS.keys())
		
		self.progess_convert.hide()
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_groupbox_layout = QVBoxLayout()
		
		self.content_layout = QVBoxLayout()
		# self.content_layout.setContentsMargins(0, 0, 0, 0)
		self.content_server_layout = QHBoxLayout()
		self.content_language_layout = QHBoxLayout()
		self.content_mode_layout = QHBoxLayout()
		self.content_status = QHBoxLayout()
		self.content_thuyet_minh = QHBoxLayout()
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		self.setLayout(self.bg_layout)
		
		self.groupbox.setLayout(self.content_groupbox_layout)
		self.content_groupbox_layout.addWidget(QLabel())
		# self.content_groupbox_layout.addWidget(, 20)
		self.content_groupbox_layout.addLayout(self.content_layout)
		
		# self.content_layout.addWidget(QLabel(""), 5)
		self.content_layout.addLayout(self.content_server_layout)
		self.content_layout.addWidget(QLabel())
		self.content_layout.addLayout(self.content_language_layout)
		self.content_layout.addWidget(QLabel())
		self.content_layout.addLayout(self.content_mode_layout)
		self.content_layout.addWidget(QLabel())
		self.content_layout.addLayout(self.content_thuyet_minh)
		self.content_layout.addLayout(self.content_status)
		
		self.content_server_layout.addWidget(QLabel("Chọn Server"), 10)
		self.content_server_layout.addWidget(self.cbox_server, 35)
		self.content_server_layout.addWidget(QLabel(), 10)
		self.content_server_layout.addWidget(self.lb_language, 10)
		self.content_server_layout.addWidget(self.cb_language, 35)
		
		# self.content_language_layout.addWidget(self.lb_language, 10)
		# self.content_language_layout.addWidget(self.cb_language, 15)
		# self.content_language_layout.addWidget(QLabel(), 5)
		self.content_language_layout.addWidget(self.lb_person_voice)
		self.content_language_layout.addWidget(self.cb_person_voice, 20)
		self.content_language_layout.addWidget(self.btn_play_demo)
		self.content_language_layout.addWidget(QLabel(), 10)
		self.content_language_layout.addWidget(self.lb_style)
		self.content_language_layout.addWidget(self.cb_style)
		self.content_language_layout.addWidget(QLabel())
		self.content_language_layout.addWidget(self.lb_mode_tts, alignment=Qt.AlignmentFlag.AlignRight)
		self.content_language_layout.addWidget(self.cb_mode, alignment=Qt.AlignmentFlag.AlignLeft)
		# self.content_mode_layout.addWidget(QLabel())
		
		self.content_mode_layout.addWidget(self.lb_volume_tts)
		self.content_mode_layout.addWidget(self.slider_volume_tts)
		self.content_mode_layout.addWidget(self.lb_number_volume_tts)
		self.content_mode_layout.addWidget(QLabel())
		self.content_mode_layout.addWidget(self.lb_speed)
		self.content_mode_layout.addWidget(self.slider_speed)
		self.content_mode_layout.addWidget(self.lb_speed_number)
		self.content_mode_layout.addWidget(QLabel())
		self.content_mode_layout.addWidget(self.lb_pitch)
		self.content_mode_layout.addWidget(self.slider_pitch)
		self.content_mode_layout.addWidget(self.lb_number_pitch)
		
		self.content_thuyet_minh.addWidget(self.cb_thuyet_minh)
		self.content_thuyet_minh.addWidget(self.btn_config_thuyet_minh)
		self.content_thuyet_minh.addWidget(QLabel())
		self.content_thuyet_minh.addWidget(QLabel())
		
		self.content_thuyet_minh.addWidget(self.cb_smart_cut)
		self.content_thuyet_minh.addWidget(self.btn_config_smart_cut)
		self.content_thuyet_minh.addWidget(QLabel())
		self.content_thuyet_minh.addWidget(QLabel())
		
		self.content_thuyet_minh.addWidget(self.cb_render_video_origin)
		self.content_thuyet_minh.addWidget(QLabel())
		self.content_thuyet_minh.addWidget(QLabel())
		
		self.content_thuyet_minh.addWidget(self.lb_channel_audio)
		self.content_thuyet_minh.addWidget(self.combo_channel_audio)
		self.content_thuyet_minh.addWidget(QLabel())
		
		self.content_thuyet_minh.addWidget(self.lb_solan)
		self.content_thuyet_minh.addWidget(self.combobox_solan)
		self.content_thuyet_minh.addWidget(QLabel())
		
		self.content_thuyet_minh.addWidget(self.lb_folder_voice)
		self.content_thuyet_minh.addWidget(self.input_src_voice)
		self.content_thuyet_minh.addWidget(self.btn_dialog_folder_voice)
		
		self.content_thuyet_minh.addWidget(self.lb_api)
		self.content_thuyet_minh.addWidget(self.input_api, 10)
		self.content_thuyet_minh.addWidget(self.btn_file_json)
		# self.content_thuyet_minh.addWidget(QLabel(),2)
		
		
		self.content_status.addWidget(self.lb_link_dang_ky, 10)
		# self.content_status.addWidget(self.btn_get_token, 15)
		self.content_status.addWidget(self.btn_demo, 5)
		self.content_status.addWidget(self.btn_check_do_lech, 10)
		# self.content_status.addWidget(self.btn_gop_thoai, 5)
		# self.content_status.addWidget(self.btn_reset)
		self.content_status.addWidget(self.progess_convert, 15)
		self.content_status.addWidget(QLabel(), 15)
		self.content_status.addWidget(self.lb_blance, alignment=Qt.AlignmentFlag.AlignRight)
		self.content_status.addWidget(self.btn_info_frame, alignment=Qt.AlignmentFlag.AlignRight)
	
	def setup_connections (self):
		self.cbox_server.currentIndexChanged.connect(self._indexTabChanged)
		self.groupbox.toggled.connect(self._groupboxStatusChanged)
		self.btn_info_frame.clicked.connect(self.dialog_info.exec)
		self.btn_demo.clicked.connect(self.clickDemo)
		# self.btn_gop_thoai.clicked.connect(self.clickGopThoai)
		# self.btn_reset.clicked.connect(self.clickReset)
		self.btn_check_do_lech.clicked.connect(lambda: self.clickBtnDolech())
		# self.btn_get_token.clicked.connect(self.clickGetToken)
		self.btn_play_demo.clicked.connect(self.clickNgheThu)
		
		self.cb_mode.currentIndexChanged.connect(lambda index: self.modeTTSChanged(index))
		self.combobox_solan.currentIndexChanged.connect(lambda index: self.combobox_solanChanged(index))
		self.combo_channel_audio.currentIndexChanged.connect(lambda index: self.cb_channel_audio_Changed(index))
		self.cb_language.currentIndexChanged.connect(lambda index: self.languageChanged(index))
		self.cb_person_voice.currentIndexChanged.connect(lambda index: self.genderVoiceChanged(index))
		self.cb_style.currentIndexChanged.connect(lambda index: self.styleChanged(index))
		
		self.input_api.textChanged.connect(self.apiChanged)
		self.btn_file_json.clicked.connect(self._openDialogFileJson)
		self.btn_dialog_folder_voice.clicked.connect(self._openDialogFolderVoice)
		
		self.btn_config_thuyet_minh.clicked.connect(self.open_dialog_config_thuyet_minh)
		self.btn_config_smart_cut.clicked.connect(self.open_dialog_smart_cut)
		# self.cb_gop_thoai.stateChanged.connect(lambda: self._checkboxChanged(self.cb_gop_thoai, "gop_thoai"))
		self.cb_thuyet_minh.stateChanged.connect(lambda: self._checkboxChanged(self.cb_thuyet_minh, "thuyet_minh"))
		self.cb_smart_cut.stateChanged.connect(lambda: self._checkboxChanged(self.cb_smart_cut, "smart_cut"))
		self.cb_render_video_origin.stateChanged.connect(lambda: self._checkboxChanged(self.cb_render_video_origin, "use_video_origin"))
		# self.cb_remove_sound.stateChanged.connect(lambda: self._checkboxChanged(self.cb_remove_sound, "remove_sound"))  ## remove_sound
		
		self.slider_volume_tts.valueChanged.connect(self.sliderVolumeValueChanged)
		self.slider_speed.valueChanged.connect(self.sliderSpeedValueChanged)
		self.slider_pitch.valueChanged.connect(self.sliderValueChanged)
		# self.slider_quang_nghi.valueChanged.connect(self.sliderQuangNghiValueChanged)
		
		self.manage_thread_pool.resultChanged.connect(self._resultThreadChanged)
		self.manage_thread_pool.progressChanged.connect(self._progressChanged)
		
		self.thread_pool_limit.resultChanged.connect(self._resultThreadChanged)
	
	def _progressChanged (self, type_progress, id_thread, proge):
		
		if type_progress == UPDATE_VALUE_PROGRESS_CHECK_LECH_SUB:
			self.progess_convert.setValue(proge)
			# print(proge,self.total_sub)
			if proge == self.total_sub:
				# self.lb_status.setText("Hoàn thành!")
				self.btn_check_do_lech.setText("Check Lệch Time")
				self.progess_convert.hide()
				self.progess_convert.setValue(0)
				self.isStopCheckDoLech = False
				self.isCheckingDoLech = False
	
	def _checkboxChanged (self, checkbox: QCheckBox, text):
		self._checkEnableButton()
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh[text] = checkbox.isChecked()
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	def _checkEnableButton (self):
		
		if self.cb_thuyet_minh.isChecked():
			self.btn_config_thuyet_minh.setDisabled(False)
		else:
			self.btn_config_thuyet_minh.setDisabled(True)
	
	# if self.cb_gop_thoai.isChecked():
	# 	self.btn_config_gop_thoai.setDisabled(False)
	# else:
	# 	self.btn_config_gop_thoai.setDisabled(True)
	
	def open_dialog_config_thuyet_minh (self):
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			self.dialog_config_thuyet_minh.loadData(self.configCurrent)
			if self.dialog_config_thuyet_minh.exec():
				
				cau_hinh.update(self.dialog_config_thuyet_minh.getValue())
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
			
			else:
				print("Cancel!")
		else:
			self.dialog_config_thuyet_minh.exec()
	
	def open_dialog_smart_cut (self):
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			self.dialog_smart_cut.loadData(self.configCurrent)
			if self.dialog_smart_cut.exec():
				
				cau_hinh.update(self.dialog_smart_cut.getValue())
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
			
			else:
				print("Cancel!")
		else:
			self.dialog_smart_cut.exec()
	
	def _openDialogFolderVoice (self):
		PyMessageBox().show_info("Lưu Ý", "Lưu ý Số thứ tự của từng dòng sub phải tương ứng với tên file nếu không sẽ bị lệch")
		
		folder_name = QFileDialog.getExistingDirectory(self, caption='Chọn thư mục chứa voice',
			dir=APP_PATH)
		
		if folder_name == "":
			return
		else:
			if os.path.exists(folder_name):
				if hasattr(self, "configCurrent"):
					if self.isClearData is False:
						cau_hinh = json.loads(self.configCurrent.value)
						
						cau_hinh["folder_src_voice"] = folder_name
						self.configCurrent.value = json.dumps(cau_hinh)
						self.configCurrent.save()
						self.input_src_voice.setText(folder_name)
	
	def _openDialogFileJson (self):
		PyMessageBox().show_info("Lưu Ý", "Lấy API Key sau đó vào thư mục 'db' nhập vào file json tương ứng với server")
		path_file, _ = QFileDialog.getOpenFileName(self, caption='Chọn file json',
			dir=(APP_PATH), filter='File Sub (*.json)')
		
		if path_file == "":
			return PyMessageBox().show_error("Lỗi", "Vui lòng chọn file json")
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				api_server = SERVER_TAB_TTS.get(
					list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("name_api_db")
				
				cau_hinh["servers_tts"][api_server] = path_file
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
				self.input_api.setText(path_file)
	
	def sliderValueChanged (self, value):
		self.lb_number_pitch.setText(str(value) + "%")
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["servers_tts"]["pitch"] = value
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	def sliderQuangNghiValueChanged (self, value):
		self.lb_number_quang_nghi.setText(str(value) + " ms")
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["quang_nghi"] = value
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	def sliderVolumeValueChanged (self, value):
		self.lb_number_volume_tts.setText(str(value))
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["volume_giong_doc"] = value
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	def sliderSpeedValueChanged (self, value):
		self.lb_speed_number.setText(str(value / 10) + "x")
		
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["speed_giong_doc"] = value
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	# self.btn_demo.setDisabled(False)
	
	def clickGetToken (self):
		
		account = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("file_account")
		
		fn_get_token = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("get_token", None)
		
		if account is None:
			return PyMessageBox().show_warning("Thông Báo", "Server này không cần lấy token")
		
		file_json = self.input_api.text()
		# print(file_json)
		if not os.path.exists(file_json):
			return PyMessageBox().show_warning("Thông Báo", f"File {file_json} không tồn tại")
		
		# if self.tab_texttospeech.currentIndex() == TabIndexTTS.FPTAI.value:  # 0-fpt"
		file_account = JOIN_PATH(PATH_DB, account)
		if not os.path.exists(file_account):
			return PyMessageBox().show_warning("Thông Báo", f"File {account} không tồn tại")
		
		with open(file_account, "r") as file:
			data_acc = file.read()
		
		ds_tai_khoan = data_acc.split('\n')
		text_i = f"- B1: Nhập tài khoản vào file {account} mỗi tài khoản 1 hàng"
		text_i += f'\n\n- B2: Load File Json {account.split("-")[0]}.json tương ứng trong thư mục "db" của tool'
		text_i += "\n\n- Nếu bạn có nhiều tài khoản, mà muốn lấy token nhanh chóng thì nhập số luồng lớn hơn 1 để cho nó chạy nhanh hơn"
		text_i += "\n\n- Đối với Server nào không có CAPTCHA sẽ đăng nhập và lấy token tự động. "
		text_i += "\n\n- Đối với server VBEE các bạn phải:"
		text_i += "\n\n + Giải CAPTCHA bằng tay, sau đó bấm đăng nhập và chọn vào mục STUDIO"
		text_i += "\n\n + Nếu xuât hiện link: https://studio.vbee.vn/studio/text-to-speech thì đã lấy thành công chorme sẽ tự động đóng lại."
		dial = PyDialogGetInt(text_i, "Số Tab Chorme Chạy Cùng Lúc", 'Nhập Số Luồng (Tab Chorme Mở Cùng Lúc):', 1, 20, width=850, height=420)
		if dial.exec():
			print(dial.getValue())
		else:
			return
		self.thread_pool_limit.setMaxThread(dial.getValue())
		ds_tk_ok = []
		for tk in ds_tai_khoan:
			if tk == '' or tk is None:
				continue
			try:
				user, pas = tk.split("|")
				if user == '' or pas == '':
					return PyMessageBox().show_warning("Thông Báo", "Thiếu username hoặc mật khẩu")
				ds_tk_ok.append(tk)
			except:
				pass
		
		for index, tk in enumerate(ds_tk_ok):
			user, pas = tk.split("|")
			# print(user, pas)
			self.thread_pool_limit.start(self._func_get_token, "get_token" + uuid.uuid4().__str__(), GET_TOKEN_SERVER_TTS, limit_thread=True, index=index, user=user.strip(), pas=pas.strip(), fn_get_token=fn_get_token)
		
		self.total_acc = len(ds_tai_khoan)
	
	def _func_get_token (self, **kwargs):
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		fn_get_token = kwargs["fn_get_token"]
		user = kwargs["user"]
		pas = kwargs["pas"]
		index = kwargs["index"]
		
		data = fn_get_token(user.strip(), pas.strip())
		thread_pool.finishSingleThread(id_worker, limit_thread=True)
		# print(data)
		return index, data
	
	def save_config_json (self, file_json, data):
		# filename = JOIN_PATH(PATH_DB,"fpt.json")
		filename = file_json
		if not os.path.exists(filename):
			with open(filename, 'w') as openfile:
				openfile.write(json.dumps([]))
		
		with open(filename, 'w') as openfile:
			openfile.write(json.dumps(data))
	
	def clickBtnDolech (self, list_sub=None, type_thread=None):
		if hasattr(self, 'path_video'):
			if self.isCheckingDoLech:
				# self.manage_thread_pool.resultChanged.emit(STOP_THREAD_CHECK_DO_LECH, STOP_THREAD_CHECK_DO_LECH, "")
				self.isStopCheckDoLech = True
				self.isCheckingDoLech = False
				# self.resetStatus()
				self.progess_convert.hide()
				self.btn_check_do_lech.setText("Check Lệch Time")
			
			else:
				self.isStopCheckDoLech = False
				self.isCheckingDoLech = True
				# self.isStop = False
				
				self.btn_check_do_lech.setText("STOP")
				
				if not os.path.isfile(self.path_video):
					PyMessageBox().show_error('Cảnh Báo', "Không tìm thấy file 'Video' tương ứng!")
					return
				
				try:
					cau_hinh = json.loads(self.configCurrent.value)
					# print(list_sub)
					type_thread = CHECK_DO_LECH_VIDEO if type_thread is None else type_thread
					
					# TODO: AC,Ratio, Time,  Text
					data_sub = self.groupbox_timeline.getDataSub() if list_sub is None else list_sub
					# print(data_sub)
					translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
					
					try:
						sub_origin, row = self.groupbox_timeline.getRandomTextSub()
					except:
						return PyMessageBox().show_warning("Thông Báo", "Chưa load file srt!")
					
					# sub_random =data_sub[0]
					text_random = sub_origin
					
					lang_code = cau_hinh["servers_tts"]["language_tts"].split("-")[0]
					
					if lang_code != voice_co_san:
						language_tts = Language(lang_code).in_foreign_languages.get('en')
						if language_tts == 'Filipino':
							language_tts = 'Tagalog'
							lang_code = 'tl'
						
						lang_source = translator_server.language(text_random).result.in_foreign_languages.get('en')
						
						if not lang_source == language_tts:
							return PyMessageBox().show_warning('Cảnh Báo', "Ngôn ngữ SUB không trùng với ngôn ngữ đọc. Vui lòng chọn đúng ngôn ngữ đọc, hoặc Chế Độ Đọc khác")
					else:
						return PyMessageBox().show_warning('Cảnh Báo', "Không hỗ trợ check độ lệch SERVER này")
				except:
					return
				
				self.thread_pool_limit.setMaxThread(10)
				# self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, "Đang check độ lệch, vui lòng đợi...\nClick đúp vào bảng này để tắt")
				# self.lb_status_demo.setText("Đang check...")
				self.total_sub = len(data_sub)
				self.progess_convert.setRange(0, self.total_sub)
				self.progess_convert.setValue(0)
				self.progess_convert.show()
				self.groupbox_timeline.count_result_check_lech = 0
				# list(mmm.keys())[0]
				gender = list(self.GENDER_VOICE_FREE_TTS_ONLINE.get(lang_code).keys())[0]
				# print(gender)
				# quang_nghi = datetime.strptime(f"00:00:0{cau_hinh.get('quang_nghi', 0) / 1000}", "%H:%M:%S.%f")
				# sequences = [sub[:2] for sub in data_sub]
				duration_video_main, bit_rate = get_duaration_video(self.path_video)
				
				for index, sub in enumerate(data_sub):
					
					start, end = sub[ColumnNumber.column_time.value].split(' --> ')
					start_time = datetime.strptime(start, "%H:%M:%S,%f")
					end_time = datetime.strptime(end, "%H:%M:%S,%f")
					if index < len(data_sub) - 1:
						start_sub_next = datetime.strptime(
							data_sub[index + 1][ColumnNumber.column_time.value].split(' --> ')[0], "%H:%M:%S,%f")
					else:
						dur_main_time = datetime.strptime(seconds_to_timestamp(duration_video_main, ","), "%H:%M:%S,%f")
						if (dur_main_time - end_time).total_seconds() > 1:
							start_sub_next = dur_main_time
						else:
							start_sub_next = end_time
					if len(data_sub) < 2:
						delta = end_time - start_time
					else:
						delta = start_sub_next - start_time
					
					seconds_sub = delta.total_seconds()
					
					sub_tts = sub[ColumnNumber.column_sub_text.value]
					
					self.thread_pool_limit.start(self._funcCheckDoLech, "_funcCheckDoLech" + str(index),
						type_thread, limit_thread=True, index=index, seconds_sub=seconds_sub, pitch=self.slider_pitch.value(), speed=self.slider_speed.value(), volume=self.slider_volume_tts.value(), gender=gender, row_number=index, text=sub_tts)
	
	def _funcCheckDoLech (self, **kwargs):
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		
		index = kwargs["index"]
		row_number = kwargs["row_number"]
		seconds_sub = kwargs["seconds_sub"]
		
		gender = kwargs["gender"]
		text = kwargs["text"]
		speed = kwargs["speed"]
		volume = kwargs["volume"]
		pitch = kwargs["pitch"]
		if self.isStopCheckDoLech:
			return "STOP"
		server_trans = TTSFreeOnlineTranslator(thread_pool)
		
		text_trans = server_trans.text_to_speech(text, gender=gender)
		folder_temp = tempfile.mkdtemp(dir=PATH_TEMP)
		
		while True:
			if check_exsist_app(folder_temp):
				if os.path.exists(folder_temp):
					remove_dir(folder_temp)
				folder_temp = tempfile.mkdtemp(dir=PATH_TEMP)
			else:
				break
		file_temp = JOIN_PATH(folder_temp, str(row_number) + "_temp.wav")
		file_temp2 = JOIN_PATH(folder_temp, str(row_number) + "_temp2.wav")
		file_speed = JOIN_PATH(folder_temp, str(row_number) + "_speed.wav")
		file_pitch = JOIN_PATH(folder_temp, str(row_number) + "_pitch.wav")
		file_out = JOIN_PATH(folder_temp, str(row_number) + "out.wav")
		
		if text_trans.result is not None:
			text_trans.write_to_file(file_temp)
			
			code_ff = f'ffmpeg -i "{file_temp}" -acodec pcm_s16le -ac 1 -ar 16000 -y "{file_temp2}"'
			self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index), TRIM_AUDIO_SLICE)
			
			sp = (speed / 10)
			if not sp == 1:
				stretch_audio(file_temp2, file_speed, ratio=(1 / sp))
				shutil.move(file_speed, file_temp2)
			# code_ff = f'ffmpeg -i "{file_speed}" -af volume={volume / 100},silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse -y "{file_out}"'
			if not pitch == 0:
				pitch_shift(file_temp2, file_pitch, (pitch / 10), folder_temp, index)
				shutil.move(file_pitch, file_temp2)
			
			code_ff = f'ffmpeg -i "{file_temp2}" -af volume={volume / 100},silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse -y "{file_out}"'
			
			self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index), TRIM_AUDIO_SLICE)
			try:
				if os.path.exists(file_temp):
					os.unlink(file_temp)
				
				if os.path.exists(file_temp2):
					os.unlink(file_temp2)
				
				if os.path.exists(file_speed):
					os.unlink(file_speed)
				
				if os.path.exists(file_pitch):
					os.unlink(file_pitch)
			except:
				print(f"Không thể xóa file")
		duration_voice, bitrate = get_duaration_video(file_out)
		tempo = duration_voice / seconds_sub
		# self.groupbox_timeline.setValueItem(row_number, ColumnNumber.column_do_lech.value, str(round(tempo, 2)))
		
		return row_number, tempo, folder_temp
	
	def clickNgheThu (self):
		cau_hinh = json.loads(self.configCurrent.value)
		# gender = cau_hinh["servers_tts"]["gender"].replace("|", "")
		
		gender = cau_hinh["servers_tts"]["gender"]
		language_tts = cau_hinh["servers_tts"]["language_tts"]
		style = cau_hinh["servers_tts"].get('style')
		
		self.manage_thread_pool.start(self._funcNgheThu, "_funcNgheThu" + uuid.uuid4().__str__(), TEXT_TO_SPEECH_DEMO, gender=gender, style=style)
		self.spiner = WaitingSpinner(
			self.groupbox,
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
		self.spiner.start()
	
	def _funcNgheThu (self, **kwargs):
		
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		gender = kwargs["gender"]
		style = kwargs["style"]
		file_temp = JOIN_PATH(PATH_VOICE, gender + style + ".mp3")
		if os.path.exists(file_temp):
			play_media_preview(file_temp)
		else:
			if self.cbox_server.currentIndex() == TabIndexTTS.TTSDaNgonNgu.value:
				user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
				headers = {"Authorization": f"Bearer {user_data['token']}"}
				response = requests.get(url=URL_API_BASE + f"/tts/public/voice-demo/{gender}?style={style}", headers=headers)
				if response.status_code == 200:
					decoded_bytes = base64.b64decode(response.json().get("data"))
					with open(file_temp, 'wb') as file:
						file.write(decoded_bytes)
					if os.path.exists(file_temp):
						play_media_preview(file_temp)
				else:
					return False
			elif self.cbox_server.currentIndex() == TabIndexTTS.FreeTTS.value:
				text_s = f'Xin chào các bạn, cám ơn các bạn đã sử dụng phần mềm của N T S Tool, đây là giọng nói demo của tôi'
				lang_code = self.get_language_code()
				if not lang_code == 'vi':
					text_s = GoogleTranslateV2(self.manage_thread_pool).translate(text_s, lang_code).result
				
				lamda_server_trans = SERVER_TAB_TTS.get(
					list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("server_trans")
				
				server_trans = lamda_server_trans(manage_thread_pool=self.manage_thread_pool,
					file_json=self.input_api.text())
				text_trans = server_trans.text_to_speech(text_s, 100, gender, lang_code, style=style)
				if text_trans.result is None:
					return False
				text_trans.write_to_file(file_temp)
				if os.path.exists(file_temp):
					play_media_preview(file_temp)
			else:
				url_demo = self.LINK_DEMO_VOICE.get(gender)
				try:
					content = requests.get(url_demo).content
					# print(content)
					with open(file_temp, 'wb') as file:
						file.write(content)
					if os.path.exists(file_temp):
						play_media_preview(file_temp)
				except:
					return "chua_nghe_duoc"
	
	# os.startfile(file_temp)
	
	# def clickReset (self):
	#
	# 	self.groupbox_timeline.resetDataOrigin()
	
	def clickGopThoai (self):
		cau_hinh = json.loads(self.configCurrent.value)
		
		data_sub = self.groupbox_timeline.getDataSub()
		
		gop_thoai_max_time = cau_hinh.get('gop_thoai_max_time', 0)
		gop_thoai_max_line = cau_hinh.get('gop_thoai_max_line', 2)
		gop_thoai_ky_tu_noi = cau_hinh.get('gop_thoai_ky_tu_noi', '')
		
		list_gop = []
		data_sub_gop = []
		data_sub_new = []
		for index_sub, sub in enumerate(data_sub):
			ac, ratio, time_, text = sub
			
			end = time_.split(' --> ')[1]
			# start_time = datetime.strptime(start, "%H:%M:%S,%f")
			end_time = datetime.strptime(end, "%H:%M:%S,%f")
			# dura = (start_time - end_time_pre).total_seconds() * 1000
			# print(dura)
			if index_sub < len(data_sub) - 1:
				next_sub = data_sub[index_sub + 1]
				start_sub_next = datetime.strptime(
					next_sub[ColumnNumber.column_time.value].split(' --> ')[0], "%H:%M:%S,%f")
				
				delta = start_sub_next - end_time
				
				seconds_sub = delta.total_seconds() * 1000
				# print(seconds_sub)
				if seconds_sub <= gop_thoai_max_time:
					# print(1)
					list_gop.append(sub)
					list_gop.append(next_sub)
				else:
					# print(11)
					# print(list_gop)
					
					if len(list_gop) > 0:
						data_sub_gop.append(list_gop)
						list_gop = []
					else:
						
						data_sub_gop.append([sub])
			else:
				# print(12)
				if len(list_gop) > 0:
					data_sub_gop.append(list_gop)
					list_gop = []
				else:
					data_sub_gop.append([sub])
		
		# print(data_sub_gop)
		for list_sub_gop in data_sub_gop:
			# print(list_sub_gop)
			
			time_start = ''
			time_end = ''
			
			sub_pre_orgin = ''
			# sub_pre_trans = ''
			list_temp = []
			for index, sub in enumerate(list_sub_gop):
				ac, ratio, time_, sub_origin_ = sub
				
				if sub_pre_orgin != sub_origin_:
					list_temp.append(sub)
				sub_pre_orgin = sub_origin_
			
			chunk_skip = gop_thoai_max_line
			chunks = [list_temp[x:x + chunk_skip] for x in range(0, len(list_temp), chunk_skip)]
			
			for chunk in chunks:
				# print(chunk)
				sub_origin_concat = ''
				sub_trans_concat = ''
				kytu_noi = f"{gop_thoai_ky_tu_noi} "
				# print(kytu_noi)
				for index, sub in enumerate(chunk):
					ac, ratio, time_, sub_origin_ = sub
					start_ = time_.split(' --> ')[0]
					end_ = time_.split(' --> ')[1]
					if index == 0:
						time_start = start_
					time_end = end_
					
					# if sub_pre_orgin != sub_origin_:
					sub_origin_concat += sub_origin_.strip(",").strip(".") + kytu_noi
				
				# sub_pre_orgin = sub_origin_
				# sub_pre_trans = sub_translate_
				
				data_sub_new.append(["", '', f"{time_start} --> {time_end}", sub_origin_concat.strip(" ")])
		
		self.groupbox_timeline.model.update_data = data_sub_new
	
	# print(data_sub_new)
	
	def clickDemo (self):
		
		
		cau_hinh = json.loads(self.configCurrent.value)
		
		data_sub_timeline = self.groupbox_timeline.getDataSub()
		if len(data_sub_timeline) == 0:
			return PyMessageBox().show_warning("Thông Báo", "Chưa load file srt!")
		
		try:
			text_trans, row = self.groupbox_timeline.getRandomTextSub()
		except:
			return PyMessageBox().show_warning("Thông Báo", "Chưa load file srt!")
		
		api_server = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("name_api_db")
		
		lamda_server_trans = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("server_trans")
		
		server_trans = lamda_server_trans(manage_thread_pool=self.manage_thread_pool, file_json=cau_hinh["servers_tts"][
			api_server])
		check_ok, mes = server_trans.check_token()
		if check_ok is False:
			return PyMessageBox().show_warning("Thông báo", mes)
		
		check_ok, balance, total_token = server_trans.check_balance()
		if check_ok is False:
			return PyMessageBox().show_warning("Thông báo", balance)
		if isinstance(balance, dict):
			balance = -1 if isinstance(balance.get('characters'), str) else balance.get('characters')
		
		if not balance == -1:
			if len(text_trans) > int(balance) - 100:
				return PyMessageBox().show_warning("Thông báo", "Số ký tự còn lại trong tài khoản không đủ !")
		
		# self.btn_demo.setDisabled(True)
		self.lb_status_demo.setText("Đang get voice...")
		self.groupbox_timeline.main_table.selectRow(row)
		self.manage_thread_pool.resultChanged.emit(CLICK_DOC_THU_VOICE, CLICK_DOC_THU_VOICE, "")
	
	def _resultThreadChanged (self, id_worker, id_thread, result):
		
		if id_thread == CHECK_LECH_SUB_FINISHED:
			self.btn_check_do_lech.setText("Check Lệch Time")
			self.progess_convert.hide()
			self.progess_convert.setValue(0)
			self.isStopCheckDoLech = False
			self.isCheckingDoLech = False
			
		if id_thread == TTS_GET_VOICE_FINISHED:
			# print('thanh công')
			
			cau_hinh = json.loads(self.configCurrent.value)
			
			api_server = SERVER_TAB_TTS.get(
				list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("name_api_db")
			
			lamda_server_trans = SERVER_TAB_TTS.get(
				list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("server_trans")
			
			server_trans = lamda_server_trans(manage_thread_pool=self.manage_thread_pool, file_json=
			cau_hinh["servers_tts"][
				api_server])
			
			check_ok, balance, total_token = server_trans.check_balance()
			
			if isinstance(balance, dict):
				self.lb_blance.setText(f"Ký Tự Còn Lại: {balance.get('characters') if isinstance(balance.get('characters'), str) else '{:,}'.format(balance.get('characters'))}")
			else:
				if not balance == -1:
					self.lb_blance.setText(f"SL Account: {total_token} - Kí Tự Còn Lại: {'{:,}'.format(balance)}")
				else:
					self.lb_blance.setText(f"")
		
		if id_thread == RESET_FOLDER_VOICE:
			if hasattr(self, "configCurrent"):
				cau_hinh = json.loads(self.configCurrent.value)
				
				cau_hinh["folder_src_voice"] = ''
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
				self.input_src_voice.setText('')
		
		if id_thread == CHECK_DO_LECH_TABLE_CHANGED_PART:
			''' Dịch lại 1 phần trong bảng'''
			# self.btn_convert.setDisabled(False)
			# try:
			
			self.clickBtnDolech(list_sub=result, type_thread=CHECK_DO_LECH_PART_SUB)
		
		if id_thread == CHECK_DO_LECH_DIALOG_SUMMARY:
			''' Dịch lại 1 phần trong bảng'''
			# self.btn_convert.setDisabled(False)
			# print(result)
			try:
				self.clickBtnDolech(list_sub=result, type_thread=CHECK_DO_LECH_PART_SUMMARY)
			except Exception as e:
				print("Lỗi: ", e.__str__())
		
		if id_thread == CHECK_DO_LECH_VIDEO:
			if result != 'STOP':
				self.thread_pool_limit.finishSingleThread(id_worker, limit_thread=True)
				row_number, tempo, folder_temp = result
				remove_dir(folder_temp)
				self.manage_thread_pool.resultChanged.emit(RESULT_CHECK_DO_LECH_VIDEO, RESULT_CHECK_DO_LECH_VIDEO, (
					row_number, tempo))
		
		if id_thread == CHECK_DO_LECH_PART_SUB:
			if result != 'STOP':
				self.thread_pool_limit.finishSingleThread(id_worker, limit_thread=True)
				row_number, tempo, folder_temp = result
				remove_dir(folder_temp)
				self.manage_thread_pool.resultChanged.emit(RESULT_CHECK_DO_LECH_VIDEO_PART, RESULT_CHECK_DO_LECH_VIDEO_PART, (
					row_number, tempo))
		
		if id_thread == CHECK_DO_LECH_PART_SUMMARY:
			self.thread_pool_limit.finishSingleThread(id_worker, limit_thread=True)
			row_number, tempo, folder_temp = result
			remove_dir(folder_temp)
			self.manage_thread_pool.resultChanged.emit(RESULT_CHECK_DO_LECH_VIDEO_SUMMARY, RESULT_CHECK_DO_LECH_VIDEO_SUMMARY, (
				row_number, tempo))
		
		if id_thread == GET_TOKEN_SERVER_TTS:
			self.count_thread_get_token += 1
			# print(result)
			# print(self.count_thread_get_token)
			try:
				index, tk = result
				
				self.list_data_token[(index)] = tk
			
			except:
				pass
			
			if self.count_thread_get_token == self.total_acc:
				self.count_thread_get_token = 0
				self.total_acc = 0
				cau_hinh = json.loads(self.configCurrent.value)
				
				api_server = SERVER_TAB_TTS.get(
					list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("name_api_db")
				
				file_json = cau_hinh.get("servers_tts").get(api_server)
				# print(self.list_data_token)
				self.save_config_json(file_json, list(self.list_data_token.values()))
				self.list_data_token = {}
				# self.input_api.setText(cau_hinh["servers_tts"][api_server])
				
				if os.path.exists(file_json):
					lamda_server_trans = SERVER_TAB_TTS.get(
						list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("server_trans")
					# print(server_trans)
					server_trans = lamda_server_trans(manage_thread_pool=self.manage_thread_pool, file_json=
					cau_hinh["servers_tts"][
						api_server])
					
					check_ok, balance, total_token = server_trans.check_balance()
					if check_ok is False:
						self.lb_blance.setText(balance)
						return PyMessageBox().show_warning("Thông báo", balance)
					
					if not balance == -1:
						self.lb_blance.setText(f"SL Account: {total_token} - Kí Tự Còn Lại: {'{:,}'.format(balance)}")
					else:
						self.lb_blance.setText(f"")
				else:
					self.lb_blance.setText(f"")
		
		if id_thread == UPDATE_BALANCE_API_TTS:
			self.loadApiFromTab()
		
		if id_thread == TEXT_TO_SPEECH_DEMO:
			self.lb_status_demo.setText("Không lấy được voice")
			self.spiner.stop()
			
			if result == 'chua_nghe_duoc':
				return PyMessageBox().show_warning("Thông báo", "Voice này chưa có bản nghe thử")
			
			elif result is False:
				return PyMessageBox().show_warning("Thông báo", "Server hoặc Giọng đọc này hiện tại không lấy được voice")
	
	# self.btn_demo.setDisabled(False)
	def loadFileSRTCurrent (self, fileSRTCurrent):
		
		self.fileSRTCurrent = fileSRTCurrent
		cau_hinh_edit: dict = json.loads(fileSRTCurrent.value)
		
		# path_video = cau_hinh_edit.get('video_file')
		# if os.path.isfile(path_video):
		# 	self.path_video = path_video
	
	def loadDataConfigCurrent (self, configCurrent):
		self.configCurrent = configCurrent
		cau_hinh = json.loads(configCurrent.value)
		
		self.groupbox.setChecked(cau_hinh["text_to_speech"])
		self.cbox_server.setCurrentIndex(cau_hinh["tab_tts_active"])
		
		mode = cau_hinh["servers_tts"]["mode"]
		
		try:
			
			style = cau_hinh["servers_tts"]["style"]
			volume = cau_hinh["volume_video_goc_thuyet_minh"]
			thuyet_minh = cau_hinh["thuyet_minh"]
			volume_giong_doc = cau_hinh["volume_giong_doc"]
		except:
			cau_hinh["servers_tts"]["style"] = ''
			
			cau_hinh["volume_video_goc_thuyet_minh"] = 100
			cau_hinh["thuyet_minh"] = False
			cau_hinh["volume_giong_doc"] = 100
			
			thuyet_minh = cau_hinh["thuyet_minh"]
			volume_giong_doc = cau_hinh["volume_giong_doc"]
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
		
		self.checkActiveWidget()
		# self.checkLanguageTTS()
		# self.checkGenderVoice()
		self.loadApiFromTab()
		#
		
		try:
			so_lan_lech = cau_hinh["so_lan_lech"]
		except:
			cau_hinh["so_lan_lech"] = 8
			so_lan_lech = cau_hinh["so_lan_lech"]
			
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
		
		try:
			channel_audio = cau_hinh["channel_audio"]
		except:
			cau_hinh["channel_audio"] = 1
			channel_audio = cau_hinh["channel_audio"]
			
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
		
		self.combobox_solan.setCurrentText(str(so_lan_lech))
		self.combo_channel_audio.setCurrentText(str(channel_audio))
		self.cb_mode.setCurrentText(self.MODE_TTS.get(mode))
		
		#
		# try:
		# 	remove_sound = cau_hinh["remove_sound"]
		# except:
		# 	cau_hinh["remove_sound"] = False
		# 	self.configCurrent.value = json.dumps(cau_hinh)
		# 	self.configCurrent.save()
		self.input_src_voice.setText(cau_hinh.get("folder_src_voice", ""))
		
		try:
			speed_giong_doc = cau_hinh["speed_giong_doc"]
		except:
			cau_hinh["speed_giong_doc"] = 10
			speed_giong_doc = cau_hinh["speed_giong_doc"]
			
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
 
		
		try:
			pitch = cau_hinh["servers_tts"]["pitch"]
		except:
			cau_hinh["servers_tts"]["pitch"] = 0
			pitch = cau_hinh["servers_tts"]["pitch"]
			
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
		
		try:
			volume = cau_hinh["volume_video_goc_thuyet_minh"]
		except:
			cau_hinh["volume_video_goc_thuyet_minh"] = 100
			volume = cau_hinh["volume_video_goc_thuyet_minh"]
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
		try:
			smart_cut = cau_hinh["smart_cut"]
			smart_cut_audio = cau_hinh["smart_cut_audio"]
			smart_cut_video = cau_hinh["smart_cut_video"]
			use_video_origin = cau_hinh["use_video_origin"]
		except:
			cau_hinh["smart_cut"] = False
			cau_hinh["smart_cut_audio"] = 8
			cau_hinh["smart_cut_video"] = 0
			cau_hinh["use_video_origin"] = False
			smart_cut =False
			use_video_origin = False
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
		# self.cb_remove_sound.setChecked(cau_hinh.get("remove_sound"))
		self.cb_render_video_origin.setChecked(use_video_origin)
		self.cb_smart_cut.setChecked(smart_cut)
		self.cb_thuyet_minh.setChecked(thuyet_minh)
		self.slider_volume_tts.setValue(volume_giong_doc)
		self.slider_speed.setValue(speed_giong_doc)
		self.slider_pitch.setValue(pitch)
		# self.slider_quang_nghi.setValue(quang_nghi)
		
		self._checkEnableButton()
		if self.cbox_server.currentIndex() == 0:
			# self._indexTabChanged(1)
			self._indexTabChanged(0)
	
	def checkActiveWidget (self):
		cau_hinh = json.loads(self.configCurrent.value)
		server = cau_hinh["tab_tts_active"]
		
		if server == TabIndexTTS.CoSan.value:
			self.lb_folder_voice.show()
			self.input_src_voice.show()
			self.btn_dialog_folder_voice.show()
		else:
			self.lb_folder_voice.hide()
			self.input_src_voice.hide()
			self.btn_dialog_folder_voice.hide()
		
		if server == TabIndexTTS.FPTAI.value or server == TabIndexTTS.VIETTELAI.value or server == TabIndexTTS.VbeeAPI.value:  # fpt, vnpt
			self.input_api.show()
			self.lb_api.show()
			self.btn_file_json.show()
		
		else:  # free
			self.input_api.hide()
			self.lb_api.hide()
			self.btn_file_json.hide()
	
	def get_language_code (self):
		language_tts = self.get_language_server()
		language_code = list(language_tts.keys())[self.cb_language.currentIndex()]
		return language_code
	
	def get_language_server (self):
		server_trans = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()])
		key_lang = server_trans.get("key_lang")
		return self.list_language_support.get(key_lang)
	
	def get_gender_language (self):
		server_trans = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()])
		# print(server_trans)
		key_gender = server_trans.get("gender")
		# print(key_gender)
		list_gender = self.list_gender_voice.get(key_gender)
		# print(list_gender)
		
		gender = list_gender.get(
			list(list_gender.keys())[self.cb_language.currentIndex()])
		# print(gender)
		
		return gender
	
	def get_style_gender (self):
		gender_id = self.get_gender_id()
		return self.STYLE_LIST_TTS.get(gender_id, '')
	
	def get_gender_id (self):
		gender = self.get_gender_language()
		gender_id = list(gender.keys())[self.cb_person_voice.currentIndex()]
		return gender_id
	
	def checkLanguageTTS (self):
		# print('checkLanguageTTS')
		cau_hinh = json.loads(self.configCurrent.value)
		self.cb_language.clear()
		# language_tts = SERVER_TAB_TTS.get(
		# 	list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("language_tts")
		# self.cb_language.addItems(language_tts.values())
		#
		# # print(cau_hinh["servers_tts"]["language_tts"])
		language_tts = self.get_language_server()
		self.cb_language.addItems(language_tts.values())
		
		self.cb_language.setCurrentText(language_tts.get(cau_hinh["servers_tts"]["language_tts"]))
		self.isChanged = True
		self.languageChanged(self.cb_language.currentIndex())
	
	# print(111)
	
	
	def languageChanged (self, index):
		if hasattr(self, "configCurrent"):
			if self.isClearData is False and self.isChanged:
				# print('languageChanged')
				# print(index)
				
				cau_hinh = json.loads(self.configCurrent.value)
				
				# language_tts = SERVER_TAB_TTS.get(
				# 	list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("language_tts")
				
				language_tts = self.get_language_server()
				
				cau_hinh["servers_tts"]["language_tts"] = list(language_tts.keys())[index]
				# print(cau_hinh["servers_tts"]["language_tts"])
				
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
				self.checkGenderVoice()
	
	
	def checkGenderVoice (self):
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				self.cb_person_voice.clear()
				# print('checkGenderVoice')
				self.isChanged = False
				try:
					# gender_voice = SERVER_TAB_TTS.get(
					# 	list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("gender").get(
					# 	cau_hinh["servers_tts"]["language_tts"])
					gender_voice = self.get_gender_language()
					self.cb_person_voice.addItems(gender_voice.values())
					
					self.cb_person_voice.setCurrentText(gender_voice.get(cau_hinh["servers_tts"]["gender"]))
					self.isChanged = True
					self.genderVoiceChanged(self.cb_person_voice.currentIndex())
				except:
					self.isChanged = True
	
	
	def genderVoiceChanged (self, index):
		if hasattr(self, "configCurrent"):
			# print(self.isChanged)
			if self.isClearData is False and self.isChanged:
				cau_hinh = json.loads(self.configCurrent.value)
				self.isChanged = False
				
				self.cb_style.clear()
				
				# print('genderVoiceChanged')
				try:
					# gender_voice = SERVER_TAB_TTS.get(
					# 	list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("gender").get(
					# 	cau_hinh["servers_tts"]["language_tts"])
					# print(index,gender_voice.keys())
					gender_voice = self.get_gender_language()
					
					cau_hinh["servers_tts"]["gender"] = list(gender_voice.keys())[index]
					
					self.configCurrent.value = json.dumps(cau_hinh)
					self.configCurrent.save()
				except:
					pass
				self.isChanged = True
				self.checkStyleVoice()
	
	
	def checkStyleVoice (self):
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				# print('checkGenderVoice')
				self.isChanged = False
				self.cb_style.clear()
				try:
					# list_style = self.STYLE_LIST_TTS.get(cau_hinh["servers_tts"]["gender"])
					list_style = self.get_style_gender()
					# print(list_style)
					if list_style is not None and len(list_style) > 0:
						# print('vào')
						self.cb_style.addItems(list_style)
						self.cb_style.setCurrentText(cau_hinh["servers_tts"]["style"])
						
						self.isChanged = True
						self.styleChanged(self.cb_style.currentIndex())
					else:
						self.isChanged = True
						
						self.styleChanged(1)
				except:
					self.isChanged = True
	
	def styleChanged (self, index):
		if hasattr(self, "configCurrent"):
			if self.isClearData is False and self.isChanged:
				cau_hinh = json.loads(self.configCurrent.value)
				
				try:
					
					cau_hinh["servers_tts"]["style"] = self.cb_style.currentText()
					
					self.configCurrent.value = json.dumps(cau_hinh)
					self.configCurrent.save()
				except:
					pass
	
	def getValue (self):
		
		api_server = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("name_api_db")
		
		language_tts = self.get_language_server()
		
		language_tts = list(language_tts.keys())[self.cb_language.currentIndex()]
		gender_voice = self.get_gender_language()
		
		gender = list(gender_voice.keys())[self.cb_person_voice.currentIndex()]
		
		style = self.cb_style.currentText()
		
		tts = {"text_to_speech": self.groupbox.isChecked(),
			   "tab_tts_active": self.cbox_server.currentIndex(),
			   "thuyet_minh": self.cb_thuyet_minh.isChecked(),
			   # "gop_thoai": self.cb_gop_thoai.isChecked(),
			   "channel_audio": int(self.combo_channel_audio.currentText()),
			   "so_lan_lech": int(self.combobox_solan.currentText()),
			   }
		
		servers_tts = {
			
			"mode": list(self.MODE_TTS.keys())[self.cb_mode.currentIndex()],
			"pitch": self.slider_pitch.value(),
			"folder_src_voice": self.input_src_voice.text(),
			"gender": gender,
			"speed": 100,
			"style": style,
			"language_tts": language_tts,
			api_server: self.input_api.text(),
		}
		
		return {**tts, "servers_tts": servers_tts}
	
	def _indexTabChanged (self, indexTab):
		
		if hasattr(self, "configCurrent"):
			
			if self.isClearData is False:
				# print('_indexTabChanged')
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["tab_tts_active"] = self.cbox_server.currentIndex()
				
				api_server = SERVER_TAB_TTS.get(
					list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("name_api_db")
				
				if cau_hinh["servers_tts"].get(api_server) is None:
					cau_hinh["servers_tts"][api_server] = ""
				
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
				self.checkActiveWidget()  # phải kiem tra cái này trước
				self.checkLanguageTTS()
				# self.checkGenderVoice()
				self.loadApiFromTab()
	
	# self.btn_demo.setDisabled(False)
	
	def loadApiFromTab (self):
		cau_hinh = json.loads(self.configCurrent.value)
		
		indexServer = self.cbox_server.currentIndex()
		api_server = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[indexServer]).get("name_api_db")
		
		link_web = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[indexServer]).get("web")
		
		is_check_balance = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[indexServer]).get("check_balance")
		
		if link_web is not None:
			self.lb_link_dang_ky.setText(f'''<a style="color:#22c467" href='{link_web}'>Link Đăng Ký </a>''')
		else:
			self.lb_link_dang_ky.setText('')
		
		if cau_hinh["servers_tts"].get(api_server) is None:
			self.input_api.setText("")
			self.lb_blance.setText(f"")
		else:
			self.input_api.setText(cau_hinh["servers_tts"][api_server])
			
			if is_check_balance:
				lamda_server_trans = SERVER_TAB_TTS.get(
					list(SERVER_TAB_TTS.keys())[self.cbox_server.currentIndex()]).get("server_trans")
				# print(server_trans)
				server_trans = lamda_server_trans(manage_thread_pool=self.manage_thread_pool, file_json=
				cau_hinh["servers_tts"][
					api_server])
				
				check_ok, balance, total_token = server_trans.check_balance()
				if check_ok is False:
					self.lb_blance.setText(balance)
					return
				# return PyMessageBox().show_warning("Thông báo", "Token của bạn bị sai hoặc đã hết hạn")
				if isinstance(balance, dict):
					self.lb_blance.setText(f"Ký Tự Còn Lại: {balance.get('characters') if isinstance(balance.get('characters'), str) else '{:,}'.format(balance.get('characters'))}")
				else:
					if not balance == -1:
						
						self.lb_blance.setText(f"SL Account: {total_token} - Ký Tự Còn Lại: {'{:,}'.format(balance)}")
					else:
						self.lb_blance.setText(f"")
			else:
				self.lb_blance.setText(f"")
	
	
	def apiChanged (self):
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				api_server = SERVER_TAB_TTS.get(
					list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("name_api_db")
				
				cau_hinh["servers_tts"][api_server] = self.input_api.text()
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	
	def modeTTSChanged (self, index):
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["servers_tts"]["mode"] = list(self.MODE_TTS.keys())[index]  # vi,en
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	def combobox_solanChanged (self, index):
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["so_lan_lech"] = int(self.combobox_solan.currentText())  # vi,en
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	def cb_channel_audio_Changed (self, index):
		if hasattr(self, "configCurrent"):
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["channel_audio"] = int(self.combo_channel_audio.currentText())  # vi,en
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	
	def _groupboxStatusChanged (self, status):
		if hasattr(self, "configCurrent"):
			
			if self.isClearData is False:
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh["text_to_speech"] = status
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
	
	# self.isClearData = False
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.isClearData = True
		self.groupbox.setChecked(False)
		self.input_api.clear()
		self.slider_pitch.setValue(0)
		self._checkEnableButton()
		
		self.isClearData = False
	
	def mouseDoubleClickEvent (self, e):
		print("stop")
		if hasattr(self, "spiner"):
			if self.spiner.is_spinning:
				self.spiner.stop()
