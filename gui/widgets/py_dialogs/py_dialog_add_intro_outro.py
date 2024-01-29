import json
import os

from PySide6.QtWidgets import QWidget, QLabel, QCheckBox, \
	QLineEdit, QHBoxLayout, QVBoxLayout, QDialog, QFileDialog

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import LIST_FILE_VIDEO, SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_checkbox import PyCheckBox
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
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


class PyDialogAddIntroOutro(QDialog):
	def __init__ (self):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
		# print(self.settings)
		self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
		
		self.app_path = os.path.abspath(os.getcwd())
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Thêm Intro Outro Vào Video")
		self.setStyleSheet(self.style_format)
		
		# self.setMinimumHeight(self.settings.dialog_size[1])
		
		
		self.setup_ui()
		
		self.list_proxy = None
	
	def loadData (self, data):
		pass
		# self.textarea_proxy.clear()
		# self.textarea_proxy.appendPlainText(data)
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		
		self.cb_intro = PyCheckBox(value="add_intro", text="Thêm Intro")
		self.cb_outro = PyCheckBox(value="add_outro", text="Thêm Outro")
		
		self.lb_file_intro = QLabel("Chọn File:")
		self.btn_dialog_file_intro = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.text_src_file_intro = QLineEdit()
		self.text_src_file_intro.setReadOnly(True)  # chỉ đọc
		
		self.btn_dialog_file_outro = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		# self.btn_dialog_file_outro.setObjectName(u"pushButton_file_dialog")
		# self.btn_dialog_file_outro.setProperty("class", "small_button")
		self.lb_file_outro = QLabel("Chọn File:")
		self.text_src_file_outro = QLineEdit()
		self.text_src_file_outro.setReadOnly(True)  # chỉ đọc
		
		self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86", bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)
	
	
	def modify_widgets (self):
		pass
	
	def create_layouts (self):
		
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		
		# self.app_layout.setSpacing(0)
		
		self.file_intro_layout = QHBoxLayout()
		self.file_outro_layout = QHBoxLayout()
		
		self.btn_layout = QHBoxLayout()
		
		self.content_frame = QWidget()
		
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
	
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.cb_intro, 10)
		self.content_layout.addLayout(self.file_intro_layout, 20)
		
		self.content_layout.addWidget(QLabel(""))
		
		self.content_layout.addWidget(self.cb_outro, 10)
		self.content_layout.addLayout(self.file_outro_layout, 20)
		self.content_layout.addWidget(QLabel(""))
		self.content_layout.addLayout(self.btn_layout)
		
		self.file_intro_layout.addWidget(self.lb_file_intro, 10)
		self.file_intro_layout.addWidget(self.text_src_file_intro, 70)
		self.file_intro_layout.addWidget(self.btn_dialog_file_intro, 30)
		
		self.file_outro_layout.addWidget(self.lb_file_outro, 10)
		self.file_outro_layout.addWidget(self.text_src_file_outro, 70)
		self.file_outro_layout.addWidget(self.btn_dialog_file_outro, 30)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.save)
		self.btn_dialog_file_intro.clicked.connect(lambda: self.openDialogFile("intro"))
		self.btn_dialog_file_outro.clicked.connect(lambda: self.openDialogFile("outro"))
		
		self.cb_intro.stateChanged.connect(lambda: self.checkboxChanged(self.cb_intro, "intro"))
		self.cb_outro.stateChanged.connect(lambda: self.checkboxChanged(self.cb_outro, "outro"))
	
	
	def loadData (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
		self.cau_hinh: dict = json.loads(configCurrent.value)
		
		self.cb_intro.setChecked(self.cau_hinh["them_intro"])
		self.cb_outro.setChecked(self.cau_hinh["them_outro"])
		self.text_src_file_intro.setText(self.cau_hinh["src_intro"])
		self.text_src_file_outro.setText(self.cau_hinh["src_outro"])
		
		# kiem tra nut de disabled
		self.btn_dialog_file_intro.setDisabled(not self.cau_hinh["them_intro"])
		self.btn_dialog_file_outro.setDisabled(not self.cau_hinh["them_outro"])
	
	def checkboxChanged (self, cbox: QCheckBox, type):
		if type == "intro":
			self.btn_dialog_file_intro.setDisabled(not cbox.isChecked())
			if not cbox.isChecked():
				self.text_src_file_intro.clear()
		
		if type == "outro":
			self.btn_dialog_file_outro.setDisabled(not cbox.isChecked())
			if not cbox.isChecked():
				self.text_src_file_outro.clear()
	
	
	def openDialogFile (self, type):
		file_name, _ = QFileDialog.getOpenFileName(self, caption='Chọn file video',
			dir=(self.app_path), filter=f'File Video ({"*" + " *".join(LIST_FILE_VIDEO)})')
		if type == "intro":
			self.text_src_file_intro.setText(file_name)
		else:
			self.text_src_file_outro.setText(file_name)
	
	def save (self):
		if self.cb_intro.isChecked() and self.text_src_file_intro.text() == "":
			return PyMessageBox().show_warning("Thiếu thông tin", "Vui lòng chọn file nhạc intro")
		
		if self.cb_outro.isChecked() and self.text_src_file_outro.text() == "":
			return PyMessageBox().show_warning("Thiếu thông tin", "Vui lòng chọn file nhạc outro")
		else:
			self.accept()
	
	def getValue (self):
		
		return {
			"them_intro": self.cb_intro.isChecked(),
			"them_outro": self.cb_outro.isChecked(),
			"src_intro": self.text_src_file_intro.text(),
			"src_outro": self.text_src_file_outro.text()
		}
	
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.cb_intro.setChecked(False)
		self.cb_outro.setChecked(False)
		self.text_src_file_intro.clear()
		self.text_src_file_outro.clear()
