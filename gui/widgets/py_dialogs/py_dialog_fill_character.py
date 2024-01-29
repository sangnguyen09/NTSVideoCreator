from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QDialog, QPlainTextEdit

from gui.configs.config_theme import ConfigTheme
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox

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


class PyDialogFillCharacter(QDialog):
	def __init__ (self, text, title, lb_input, show_text=True,  show_btn_delete=False, width=400, height=600, ):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		self.text = text
		self.show_btn_delete = show_btn_delete
		self.show_text = show_text
		
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
		self.is_delete = False
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
		
		self.buttonDelete = QPushButton("Delete")
		self.buttonDelete.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonSave = QPushButton("Save")
		self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.textarea_info = QPlainTextEdit()
		self.textarea_info.setReadOnly(True)
		self.textarea_info.setMaximumHeight(120)
		
		self.textarea_info.setProperty("class", "dialog_info")
		
		self.input_time = QLineEdit()
		self.input_time.setText('..')
		
		self.input_text = QLineEdit()
		self.input_text.setText('..')

	
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
		
		if self.show_text:
			self.content_layout.addWidget(QLabel(self.lb_input))
			self.content_layout.addWidget(self.input_text)
			self.btn_layout.addWidget(QLabel(""), 40)
			self.btn_layout.addWidget(self.buttonSave, 10)
			
		self.content_layout.addLayout(self.btn_layout)

		if self.show_btn_delete:
			self.btn_layout.addWidget(self.buttonDelete, 10)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.clickSave)
		self.buttonDelete.clicked.connect(self.clickDelete)
	
	# self.buttonSkip.clicked.connect(self.skip)
	def clickSave (self):
		if self.input_text.text() == '':
			return PyMessageBox().show_warning('Cảnh Báo', "Nội dung không được trống")
		self.accept()
	
	def clickDelete (self):
		self.is_delete = True
		self.accept()
	
	def getValue (self):
		return self.input_text.text()
