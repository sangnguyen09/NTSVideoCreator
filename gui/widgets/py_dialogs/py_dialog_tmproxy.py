import json

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


class PyDialogTMProxy(QDialog):
	def __init__ (self):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# self.setMinimumHeight(self.settings.dialog_size[1])
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
		self.setWindowTitle("Danh dách API TMProxy")
		
		self.setup_ui()
		
		self.list_proxy = None
	
	# self.title_bar.set_title(self.settings.app_name)
	
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		self.buttonSave = QPushButton("Lưu")
		self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		self.textarea_proxy = QPlainTextEdit()
		self.textarea_proxy.setPlaceholderText("Nhập list API Key")
	
	def modify_widgets (self):
		pass
	
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
		
		self.content_layout.addWidget(self.textarea_proxy, 90)
		self.content_layout.addLayout(self.btn_layout, 10)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.accept)
	
	# self.textarea_proxy.textChanged.connect(self.updatePoxy)
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		self.cau_hinh = json.loads(configCurrent.value)
		
		# self.textarea_proxy.clear()
		# self.textarea_proxy.appendPlainText(self.cau_hinh["tmproxy"])
	
	
	def getValue (self):
		return self.textarea_proxy.toPlainText()
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.textarea_proxy.clear()
