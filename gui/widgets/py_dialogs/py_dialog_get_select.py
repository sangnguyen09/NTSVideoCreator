from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QComboBox

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import OUPUT_FORMAT_SUB


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


class PyDialogGetOutputFormatSub(QDialog):
	def __init__ (self, width=400, height=200):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
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
		self.setWindowTitle("Lưu File")
		
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
		
		self.lb_format = QLabel("Vui Lòng Lựa Chọn Định Dạng Lưu")
		self.combobox_format = QComboBox()
		self.combobox_format.addItems(OUPUT_FORMAT_SUB)
		
		self.lb_type_sub = QLabel("Vui Lòng Lựa Chọn Loại Sub")
		self.combobox_type = QComboBox()
		self.combobox_type.addItems([ "SUB GỐC","SUB DỊCH"])
	
	
	# self.input_int.setMaximum(2000)
	
	def modify_widgets (self):
		pass
	
	# self.textarea_info.appendPlainText(self.text)
	
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
		
		self.content_layout.addWidget(self.lb_type_sub)
		self.content_layout.addWidget(self.combobox_type)
		
		self.content_layout.addWidget(self.lb_format)
		self.content_layout.addWidget(self.combobox_format)
		
		self.content_layout.addLayout(self.btn_layout)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 10)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.accept)
	
	# self.buttonSkip.clicked.connect(self.skip)
	
	def getIndex (self):
		return self.combobox_type.currentIndex(), self.combobox_format.currentIndex()
	
	def getText (self):
		return self.combobox_type.currentText(), self.combobox_format.currentText()
