from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QPlainTextEdit

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings


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


class PyDialogShowQuestion(QDialog):
	def __init__ (self, text, height, title="",font_size=12):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		self.text = text
		self.font_size = font_size
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
		
		# SET UP MAIN WINDOW
		self.setWindowTitle(title)
		
		self.setMinimumHeight(height)
		# self.setMinimumWidth(800)
		
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		
		self.buttonSave = QPushButton("Yes")
		self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttoncancel = QPushButton("No")
		self.buttoncancel.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.textarea_info = QPlainTextEdit()
		self.textarea_info.setReadOnly(True)
		
		self.textarea_info.setStyleSheet(f"font-size: {self.font_size}px")
	
	def modify_widgets (self):
		self.textarea_info.appendPlainText(self.text)
	
	def create_layouts (self):
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.app_layout.setSpacing(0)
		
		self.btn_layout = QHBoxLayout()
		
		self.content_frame = QWidget()
		
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
		# self.content_layout.setSpacing(0)
	
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.textarea_info, 90)
		self.content_layout.addLayout(self.btn_layout, 10)
		
		self.btn_layout.addWidget(QLabel(""), 30)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(self.buttoncancel, 20)
		self.btn_layout.addWidget(QLabel(""), 30)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.accept)
		self.buttoncancel.clicked.connect(self.close)
