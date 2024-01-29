import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QDialog, QSlider, QFileDialog, \
	QPlainTextEdit

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import LIST_FILE_MUSIC, SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_radio_buttion import PyRadioButton

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


class PyDialogAddMusicBackground(QDialog):
	def __init__ (self):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
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
		self.setWindowTitle("Thêm Nhạc Nền Vào Video")
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
		
		self.rad_file_fixed = PyRadioButton(value="add_music_file", text="Thêm Nhạc Cố Định")
		self.rad_folder_random = PyRadioButton(value="add_music_file", text="Thêm Ngẫu Nhiên Trong Thư Mục")
		
		self.lb_file_music = QLabel("Chọn File Nhạc:")
		self.btn_dialog_file_music = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.text_src_file_music = QLineEdit()
		self.text_src_file_music.setReadOnly(True)  # chỉ đọc
		
		self.lb_folder_music = QLabel("Chọn Folder Nhạc:")
		self.btn_dialog_folder_music = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-folder.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		
		self.text_src_folder_music = QLineEdit()
		self.text_src_folder_music.setReadOnly(True)  # chỉ đọc
		
		self.lb_volume = QLabel("Âm lượng:")
		self.slider_volume = QSlider()
		self.slider_volume.setOrientation(Qt.Orientation.Horizontal)
		self.slider_volume.setRange(0, 100)
		self.slider_volume.setValue(100)
		self.lb_volume_number = QLabel(str(self.slider_volume.value()))
		
		self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86", bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)
		
		self.textarea_proxy = QPlainTextEdit()
		self.textarea_proxy.setPlaceholderText("")
	
	
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
		
		self.content_layout.addWidget(self.rad_file_fixed, 10)
		self.content_layout.addLayout(self.file_music_layout, 20)
		
		self.content_layout.addWidget(QLabel(""))
		
		self.content_layout.addWidget(self.rad_folder_random, 10)
		self.content_layout.addLayout(self.folder_music_layout, 20)
		self.content_layout.addWidget(QLabel(""))
		
		self.content_layout.addLayout(self.volume_layout, 20)
		self.content_layout.addLayout(self.btn_layout, 10)
		self.content_layout.addWidget(QLabel(""))
		
		self.file_music_layout.addWidget(self.lb_file_music, 20)
		self.file_music_layout.addWidget(self.text_src_file_music, 75)
		self.file_music_layout.addWidget(self.btn_dialog_file_music, 5)
		
		self.folder_music_layout.addWidget(self.lb_folder_music, 20)
		self.folder_music_layout.addWidget(self.text_src_folder_music, 75)
		self.folder_music_layout.addWidget(self.btn_dialog_folder_music, 5)
		
		self.volume_layout.addWidget(self.lb_volume, 20)
		self.volume_layout.addWidget(self.slider_volume, 75)
		self.volume_layout.addWidget(self.lb_volume_number, 5)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	
	def setup_connections (self):
		self.slider_volume.valueChanged.connect(self.sliderValueChanged)
		self.btn_dialog_file_music.clicked.connect(self.openDialogFile)
		self.btn_dialog_folder_music.clicked.connect(self.openDialogFolder)
		self.rad_file_fixed.toggled.connect(lambda: self.radioChanged())
		# self.rad_folder_random.toggled.connect(lambda: self.radioChanged(self.rad_folder_random,"them_nhac_ngau_nhien"))
		
		self.buttonSave.clicked.connect(self.save)
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		cau_hinh = json.loads(configCurrent.value)
		
		self.rad_file_fixed.setChecked(cau_hinh["them_nhac_co_dinh"])
		self.rad_folder_random.setChecked(cau_hinh["them_nhac_ngau_nhien"])
		self.text_src_file_music.setText(cau_hinh["src_nhac_co_dinh"])
		self.text_src_folder_music.setText(cau_hinh["src_nhac_ngau_nhien"])
		self.slider_volume.setValue(cau_hinh["am_luong_nhac_nen"])
	
	def openDialogFile (self):
		file_name, _ = QFileDialog.getOpenFileName(self, caption='Chọn file nhạc nền',
			dir=(self.app_path), filter=f'File Nhạc ({"*" + " *".join(LIST_FILE_MUSIC)})')
		self.text_src_file_music.setText(file_name)
	
	def openDialogFolder (self):
		folder_name = QFileDialog.getExistingDirectory(self, caption='Chọn thư mục chứa nhạc',
			dir=(self.app_path))
		self.text_src_folder_music.setText(folder_name)
	
	def sliderValueChanged (self):
		self.lb_volume_number.setText(str(self.slider_volume.value()))
	
	def radioChanged (self):
		
		if self.rad_file_fixed.isChecked():
			self.btn_dialog_folder_music.setDisabled(True)
			self.btn_dialog_file_music.setDisabled(False)
		else:
			self.btn_dialog_folder_music.setDisabled(False)
			self.btn_dialog_file_music.setDisabled(True)
	
	def save (self):
		if self.rad_file_fixed.isChecked() and self.text_src_file_music.text() == "":
			return PyMessageBox().show_warning("Thiếu thông tin", "Vui lòng chọn file nhạc cố định")
		
		if self.rad_folder_random.isChecked() and self.text_src_folder_music.text() == "":
			return PyMessageBox().show_warning("Thiếu thông tin", "Vui lòng chọn folder chứa nhạc")
		else:
			self.accept()
	
	def getValue (self):
		return {
			"them_nhac_co_dinh": self.rad_file_fixed.isChecked(),
			"them_nhac_ngau_nhien": self.rad_folder_random.isChecked(),
			"src_nhac_co_dinh": self.text_src_file_music.text(),
			"src_nhac_ngau_nhien": self.text_src_folder_music.text(),
			"am_luong_nhac_nen": self.slider_volume.value(),
		}
	
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.rad_file_fixed.setChecked(True)
		# self.rad_folder_random.setChecked(False)
		self.text_src_file_music.clear()
		self.text_src_folder_music.clear()
		self.slider_volume.setValue(50)
