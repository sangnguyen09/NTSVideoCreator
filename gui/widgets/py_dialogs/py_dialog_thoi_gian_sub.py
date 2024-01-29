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


class PyDialogThoiGianSub(QDialog):
	def __init__ (self, text, title, time_line, text_sub, width=400, height=600, ):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		self.message = text
		self.time_line = time_line
		self.text_sub = text_sub
		
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
		self.is_auto_add = False
		self.is_top = False
		self.is_bottom = False
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
		
		self.buttonAddTop = QPushButton("Gộp Với Dòng Trên")
		self.buttonAddTop.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonAddBottom = QPushButton("Gộp Với Dòng Dưới")
		self.buttonAddBottom.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonAutoAdd = QPushButton("Tự Động Thêm Ký Tự")
		self.buttonAutoAdd.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonReplace = QPushButton("Thay Nội Dung")
		self.buttonReplace.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.messagearea_info = QPlainTextEdit()
		self.messagearea_info.setReadOnly(True)
		
		self.messagearea_info.setProperty("class", "dialog_info")
		
		self.input_text = QLineEdit()
		self.input_text.setText(self.text_sub)
		
		self.input_time = QLineEdit()
		self.input_time.setText(self.time_line)
	
	def modify_widgets (self):
		self.messagearea_info.appendPlainText(self.message)
	
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
		
		self.content_layout.addWidget(QLabel("ERROR:"))
		self.content_layout.addWidget(self.messagearea_info)
		self.content_layout.addWidget(QLabel())

		self.content_layout.addWidget(QLabel("Timeline:"))
		self.content_layout.addWidget(self.input_time)
		
		self.content_layout.addWidget(QLabel())
		self.content_layout.addWidget(QLabel("Content:"))
		self.content_layout.addWidget(self.input_text)
		self.content_layout.addWidget(QLabel())

		self.content_layout.addLayout(self.btn_layout)
		
		self.btn_layout.addWidget(QLabel(""), 25)
		self.btn_layout.addWidget(self.buttonReplace, 10)
		self.btn_layout.addWidget(self.buttonAutoAdd, 10)
		self.btn_layout.addWidget(self.buttonAddTop, 10)
		self.btn_layout.addWidget(self.buttonAddBottom, 10)
		self.btn_layout.addWidget(self.buttonDelete, 10)
		
		self.btn_layout.addWidget(QLabel(""), 25)
	
	def setup_connections (self):
		self.buttonAddTop.clicked.connect(self.clickAddTop)
		self.buttonAddBottom.clicked.connect(self.clickAddBottom)
		self.buttonDelete.clicked.connect(self.clickDelete)
		self.buttonReplace.clicked.connect(self.clickReplace)
		self.buttonAutoAdd.clicked.connect(self.clickAutoAdd)
	
	# self.buttonSkip.clicked.connect(self.skip)
	def clickReplace (self):
		if self.input_text.text() == '':
			return PyMessageBox().show_warning('Cảnh Báo', "Nội dung không được trống")
		self.accept()
	
	def clickAddBottom (self):
		self.is_bottom = True
		self.accept()
	
	def clickAddTop (self):
		self.is_top = True
		self.accept()
	
	def clickDelete (self):
		self.is_delete = True
		self.accept()
		
	def clickAutoAdd (self):
		self.is_auto_add = True
		self.accept()
	
	def getValue (self):
		return (self.input_time.text(), self.input_text.text())
