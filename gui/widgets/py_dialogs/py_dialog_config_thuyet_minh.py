import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QSlider

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


class PyDialogConfigThuyetMinh(QDialog):
	def __init__ (self):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		self.app_path = os.path.abspath(os.getcwd())
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Cấu hình thuyết minh")
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
		
		self.lb_volume = QLabel("Âm lượng video gốc:")
		self.slider_volume = QSlider()
		self.slider_volume.setOrientation(Qt.Orientation.Horizontal)
		self.slider_volume.setRange(0, 200)
		self.slider_volume.setValue(100)
		self.lb_volume_number = QLabel(str(self.slider_volume.value()))
		
		self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86", bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)
	
	
	def modify_widgets (self):
		pass
	
	def create_layouts (self):
		
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		
		# self.app_layout.setSpacing(0)
		
		self.file_music_layout = QHBoxLayout()
		self.folder_music_layout = QHBoxLayout()
		self.volume_layout = QHBoxLayout()
		
		self.btn_layout = QHBoxLayout()
		
		self.content_frame = QWidget()
		
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
	
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addLayout(self.volume_layout, 90)
		self.content_layout.addWidget(QLabel(""))

		self.content_layout.addLayout(self.btn_layout, 10)
		
		self.volume_layout.addWidget(self.lb_volume, 20)
		self.volume_layout.addWidget(self.slider_volume, 75)
		self.volume_layout.addWidget(self.lb_volume_number, 5)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	
	def setup_connections (self):
		self.slider_volume.valueChanged.connect(self.sliderValueChanged)
		# self.rad_folder_random.toggled.connect(lambda: self.radioChanged(self.rad_folder_random,"them_nhac_ngau_nhien"))
		
		self.buttonSave.clicked.connect(self.save)
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		cau_hinh = json.loads(configCurrent.value)
		# try:
		volume = cau_hinh["volume_video_goc_thuyet_minh"]
		# except:
		# 	cau_hinh["volume_video_goc_thuyet_minh"] = 100
		# 	volume = cau_hinh["volume_video_goc_thuyet_minh"]
		# 	self.configCurrent.value = json.dumps(cau_hinh)
		# 	self.configCurrent.save()
		
		self.slider_volume.setValue(volume)
	
	
	def sliderValueChanged (self):
		self.lb_volume_number.setText(str(self.slider_volume.value()))
	
	
	def save (self):
		self.accept()
	
	def getValue (self):
		return {
			"volume_video_goc_thuyet_minh": self.slider_volume.value(),
		}
	
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.slider_volume.setValue(100)
