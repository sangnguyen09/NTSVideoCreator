import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QSlider, QSpinBox, QLineEdit, \
	QPlainTextEdit, QGroupBox

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton

style = '''
QDialog {{
	background-color: {_bg_color};
	font-size:15px;
	font-weight:bold;
    
}}
QLabel{{
 color: {_color}
}}

'''


class PyDialogConfigSmartCut(QDialog):
	def __init__ (self):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.setMinimumWidth(850)
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		self.app_path = os.path.abspath(os.getcwd())
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Cấu hình Cắt Thông Minh")
		self.setStyleSheet(self.style_format)
		
		self.setup_ui()
		
		self.list_proxy = None
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		
		# self.lb_input_seconds = QLabel("Gộp Dòng Khi Khoảng Lặng Lớn Hơn Bao Nhiêu Mili Giây (ms): ")
		# self.input_max_time = QSpinBox()
		# self.input_max_time.setMinimum(0)
		# self.input_max_time.setMaximum(1000)
		self.groupbox = QGroupBox("Chỉnh Thông Số")
		
		huong_dan = "TH1: Đối với những video dạng đọc truyện hoặc hoạt hình dạng 2D thì chỉ cần xóa những đoạn âm thanh im lặng"
		huong_dan += "\nThông số tối ưu: Xóa Âm Thanh 8%, Xóa Video 0%"
		
		huong_dan += "\n\nTH2: Đối với những video review Phim thì cần kết hợp XÓA cả âm thanh im lặng và video có chuyển động chậm"
		huong_dan += "\nThông số tối ưu: Xóa Âm Thanh 8%, Xóa Video 8%"
		huong_dan += "\n\n- LƯU Ý: "
		huong_dan += "\n - Chỉnh về 0% sẽ không dụng áp dụng tính năng đó"
		huong_dan += "\n - Số phần trăm càng nhỏ thì video sẽ bị cắt đi càng nhiều"
		# huong_dan += "\n\nB4: Chỉnh sửa lại rồi bấm THAY THẾ hoặc XÓA DÒNG đó đi"
		self.text_huongdan = QPlainTextEdit()
		self.text_huongdan.setReadOnly(True)
		self.text_huongdan.setMinimumHeight(200)
		self.text_huongdan.setPlainText(huong_dan)
		self.text_huongdan.setProperty("class", "dialog_info")
		
		self.lb_smart_cut_audio = QLabel("Xóa bỏ những đoạn có ÂM THANH im lặng NHỎ HƠN bao nhiêu (%):")
		self.slider_smart_cut_audio = QSlider()
		self.slider_smart_cut_audio.setOrientation(Qt.Orientation.Horizontal)
		self.slider_smart_cut_audio.setRange(0, 50)
		self.slider_smart_cut_audio.setPageStep(1)
		# self.slider_smart_cut_audio.setValue(5)
		self.lb_number_cut_audio = QLabel(str(self.slider_smart_cut_audio.value())+"%")
		
		self.lb_smart_cut_video = QLabel("Xóa bỏ những đoạn VIDEO có chuyển động chậm NHỎ HƠN bao nhiêu (%):")
		self.slider_smart_cut_video = QSlider()
		self.slider_smart_cut_video.setOrientation(Qt.Orientation.Horizontal)
		self.slider_smart_cut_video.setRange(0, 50)
		self.slider_smart_cut_video.setPageStep(1)
		# self.slider_smart_cut_video.setValue(5)
		self.lb_number_cut_video = QLabel(str(self.slider_smart_cut_video.value())+"%")
		
		
		# self.lb_input_max_line = QLabel("Gộp Tối Đa Bao Nhiêu Dòng: ")
		# self.input_max_line = QSpinBox()
		# self.input_max_line.setMinimum(2)
		# self.input_max_line.setMaximum(10)
		#
		# self.lb_input_ky_tu_noi = QLabel("Ký Tự Nối Giữa Các Đoạn: ")
		# self.input_ky_tu_noi = QLineEdit()
		#
		
		self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86", bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)
	
	
	def modify_widgets (self):
		pass
	
	def create_layouts (self):
		
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		
		# self.app_layout.setSpacing(0)
		
		self.audio_slider_layout = QHBoxLayout()
		self.video_slider_layout = QHBoxLayout()
		self.input_layout = QVBoxLayout()
		
		self.btn_layout = QHBoxLayout()
		
		self.content_frame = QWidget()
		
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
	
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		# self.content_layout.addWidget(QLabel(""))
		self.content_layout.addWidget(self.text_huongdan, 30)
		self.content_layout.addWidget(self.groupbox, 60)
		self.groupbox.setLayout(self.input_layout)
		self.content_layout.addWidget(QLabel(""))

		self.content_layout.addLayout(self.btn_layout, 10)
		
		self.input_layout.addWidget(self.lb_smart_cut_audio)
		self.input_layout.addLayout(self.audio_slider_layout)
		self.audio_slider_layout.addWidget(self.slider_smart_cut_audio)
		self.audio_slider_layout.addWidget(self.lb_number_cut_audio)
		
		self.input_layout.addWidget(QLabel(""))
		self.input_layout.addWidget(self.lb_smart_cut_video)
		self.input_layout.addLayout(self.video_slider_layout)

		self.video_slider_layout.addWidget(self.slider_smart_cut_video)
		self.video_slider_layout.addWidget(self.lb_number_cut_video)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	
	def setup_connections (self):
		# self.slider_volume.valueChanged.connect(self.sliderValueChanged)
		# self.rad_folder_random.toggled.connect(lambda: self.radioChanged(self.rad_folder_random,"them_nhac_ngau_nhien"))
		self.slider_smart_cut_video.valueChanged.connect(self.sliderVideoValueChanged)
		self.slider_smart_cut_audio.valueChanged.connect(self.sliderAudioValueChanged)

		self.buttonSave.clicked.connect(self.save)
		
	def sliderAudioValueChanged (self, value):
		self.lb_number_cut_audio.setText(str(value)+"%")
	def sliderVideoValueChanged (self, value):
		self.lb_number_cut_video.setText(str(value)+"%")
		# if hasattr(self, "configCurrent"):
		# 		cau_hinh = json.loads(self.configCurrent.value)
		# 		cau_hinh["smart_cut_audio"] = value
		# 		self.configCurrent.value = json.dumps(cau_hinh)
		# 		self.configCurrent.save()
		
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		cau_hinh = json.loads(configCurrent.value)
		smart_cut_audio = cau_hinh["smart_cut_audio"]
		smart_cut_video = cau_hinh["smart_cut_video"]
		# gop_thoai_ky_tu_noi = cau_hinh["gop_thoai_ky_tu_noi"]
		self.slider_smart_cut_audio.setValue(smart_cut_audio)
		self.slider_smart_cut_video.setValue(smart_cut_video)
		# self.input_max_time.setValue(gop_thoai_max_time)
		# self.input_max_line.setValue(gop_thoai_max_line)
		# self.input_ky_tu_noi.setText(gop_thoai_ky_tu_noi)
	
 
	def save (self):
		self.accept()
	
	def getValue (self):
		return {
			"smart_cut_video": self.slider_smart_cut_video.value(),
			"smart_cut_audio": self.slider_smart_cut_audio.value(),
		}
	
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
