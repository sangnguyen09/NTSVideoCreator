from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QSpinBox, QDialog, QPlainTextEdit

from gui.configs.config_theme import ConfigTheme


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


class PyDialogGetInt(QDialog):
	def __init__ (self, text, title,lb_input ,min, max, width=400, height=600, ):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		self.text = text
		self.min = min
		self.max = max
		self.lb_input = lb_input
		# st = QSettings(*SETTING_APP)
		# self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_AUTOSUB)
		self.setMinimumWidth(width)
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		self.is_skip = False
		# SET UP MAIN WINDOW
		self.setWindowTitle(title)
		
		self.setMinimumHeight(height)
		
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		self.buttonSave = QPushButton("OK")
		self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.textarea_info = QPlainTextEdit()
		self.textarea_info.setReadOnly(True)
		
		self.textarea_info.setProperty("class", "dialog_info")
		
		self.input_int = QSpinBox()
		self.input_int.setMinimum(self.min)
		self.input_int.setMaximum(self.max)
	
	# self.input_int.setMaximum(2000)
	
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
		
		self.content_layout.addWidget(self.textarea_info)
		self.content_layout.addWidget(QLabel(self.lb_input))
		self.content_layout.addWidget(self.input_int)
		self.content_layout.addLayout(self.btn_layout)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 10)
		# self.btn_layout.addWidget(self.buttonSkip, 10)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.accept)
	
	# self.buttonSkip.clicked.connect(self.skip)
	
	def getValue (self):
		return self.input_int.value()
