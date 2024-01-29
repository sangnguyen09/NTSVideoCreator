import json

from PySide6.QtWidgets import QLabel, QFrame, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, QDialog, QRadioButton, \
	QTabWidget

from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import SETTING_APP_DATA, LOAD_FONT_FAMILY, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_radio_buttion import PyRadioButton
from gui.widgets.py_tab.py_tab_config_sub_origin import PyTabConfigSubOrigin
from gui.widgets.py_tab.py_tab_config_sub_translate import PyTabConfigSubTranslate


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


class PyDialogConfigSubText(QDialog):
	def __init__ (self, manage_thread_pool):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
		self.manage_thread_pool = manage_thread_pool
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		# self.app_path = os.path.abspath(os.getcwd())
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Thêm Sub Vào Video")
		self.setStyleSheet(self.style_format)
		
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		# BG FRAME
		self.bg_frame = QFrame()
		self.bg_frame.setObjectName("bg_frame")
		
		self.groupbox_show_sub = QGroupBox("Chọn sub Muốn Hiển thị:")
		self.rad_sub_origin = PyRadioButton(value='origin', text="Sub Gốc")
		self.rad_sub_translate = PyRadioButton(value='translate', text="Sub Dịch")
		self.rad_all_sub = PyRadioButton(value='all', text="Cả Hai")
		self.rad_no_sub = PyRadioButton(value='nosub', text="Không Hiển Thị")
		
		# Tạo Tab
		self.tabWidget = QTabWidget()
		self.tabWidget.setObjectName("tabWidget")
		self.tab_sub_origin = PyTabConfigSubOrigin(self.manage_thread_pool)
		self.tab_sub_translate = PyTabConfigSubTranslate(self.manage_thread_pool)
		
		self.tabWidget.addTab(self.tab_sub_origin, "Cấu hình SUB gốc")
		self.tabWidget.addTab(self.tab_sub_translate, "cấu hình SUB dịch")
		
		self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86",
			bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)
	
	def modify_widgets (self):
		pass
	
	def create_layouts (self):
		self.widget_layout = QHBoxLayout()
		self.widget_layout.setContentsMargins(0, 0, 0, 0)
		
		self.groupbox_show_sub_layout = QGridLayout()
		
		self.bg_layout = QVBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		self.btn_layout = QHBoxLayout()
		self.btn_layout.setContentsMargins(0, 10, 0, 10)
	
	def add_widgets_to_layouts (self):
		# self.bg_layout.addWidget(self.groupbox_split_sub)
		self.bg_layout.addWidget(self.groupbox_show_sub)
		self.bg_layout.addWidget(self.tabWidget)
		self.bg_layout.addLayout(self.btn_layout)
		self.setLayout(self.bg_layout)
		
		# self.groupbox_split_sub.setLayout(self.ngat_doan_layout)
		self.groupbox_show_sub.setLayout(self.groupbox_show_sub_layout)
		
		# self.ngat_doan_layout.addWidget(self.lb_number_charecter_in_line, 0, 0, 1, 2)
		# self.ngat_doan_layout.addWidget(QLabel(""), 0, 2)
		# self.ngat_doan_layout.addWidget(self.max_character_inline, 0, 3, 1, 2)
		# self.ngat_doan_layout.addWidget(QLabel(""), 0, 5, 1, 7)
		
		self.groupbox_show_sub_layout.addWidget(self.rad_sub_origin, 0, 0)
		self.groupbox_show_sub_layout.addWidget(self.rad_sub_translate, 0, 1)
		self.groupbox_show_sub_layout.addWidget(self.rad_all_sub, 0, 2)
		self.groupbox_show_sub_layout.addWidget(self.rad_no_sub, 0, 3)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.save)
		self.rad_sub_origin.clicked.connect(lambda: self.check_radio_button(self.rad_sub_origin))
		self.rad_sub_translate.clicked.connect(lambda: self.check_radio_button(self.rad_sub_translate))
		self.rad_all_sub.clicked.connect(lambda: self.check_radio_button(self.rad_all_sub))
		self.rad_no_sub.clicked.connect(lambda: self.check_radio_button(self.rad_no_sub))
		self.manage_thread_pool.resultChanged.connect(self._loadFont)
	
	def _loadFont (self, id_worker, typeThread, result):
		if typeThread == LOAD_FONT_FAMILY:
			self.tab_sub_origin.loadFont(result)
			self.tab_sub_translate.loadFont(result)
	
	def check_radio_button (self, rad):
		
		
		if rad == self.rad_sub_origin and self.rad_sub_origin.isChecked():
			self.tab_sub_origin.setDisabled(False)
			self.tab_sub_translate.setDisabled(True)
			self.tab_sub_origin.checkRadioDisabled(False)
			self.tab_sub_translate.checkRadioDisabled(False)
		
		elif rad == self.rad_sub_translate and self.rad_sub_translate.isChecked():
			self.tab_sub_origin.setDisabled(True)
			self.tab_sub_translate.setDisabled(False)
			self.tab_sub_origin.checkRadioDisabled(False)
			self.tab_sub_translate.checkRadioDisabled(False)
		
		elif rad == self.rad_no_sub and self.rad_no_sub.isChecked():
			self.tab_sub_origin.setDisabled(True)
			self.tab_sub_translate.setDisabled(True)
		# self.tab_sub_origin.checkRadioDisabled(True)
		# self.tab_sub_translate.checkRadioDisabled(True)
		
		else:
			self.tab_sub_origin.checkRadioDisabled(True)
			self.tab_sub_translate.checkRadioDisabled(True)
			self.tab_sub_origin.setDisabled(False)
			self.tab_sub_translate.setDisabled(False)
	
	
	def save (self):
		if self.rad_sub_origin.isChecked():
			
			if self.tab_sub_origin.checkValid() is False:
				return
			self.accept()
		elif self.rad_sub_translate.isChecked():
			if self.tab_sub_translate.checkValid() is False:
				return
			self.accept()
		elif self.rad_all_sub.isChecked():
			if self.tab_sub_origin.checkValid() is False:
				return
			if self.tab_sub_translate.checkValid() is False:
				return
			self.accept()
		else:
			self.accept()
	
	def loadData (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
		cau_hinh: dict = json.loads(configCurrent.value)
		if cau_hinh["sub_hien_thi"] == 'translate':
			self.tab_sub_origin.setDisabled(True)
			self.rad_sub_translate.setChecked(True)
		
		# self.tab_2.show()
		elif cau_hinh["sub_hien_thi"] == 'origin':
			self.rad_sub_origin.setChecked(True)
			self.tab_sub_translate.setDisabled(True)
		
		elif cau_hinh["sub_hien_thi"] == 'nosub':
			self.rad_no_sub.setChecked(True)
			self.tab_sub_translate.setDisabled(True)
			self.tab_sub_origin.setDisabled(True)
		
		# self.tab_2.show()
		else:
			self.rad_all_sub.setChecked(True)
		
		self.tab_sub_origin.loadData(configCurrent)
		self.tab_sub_translate.loadData(configCurrent)
	
	def getValue (self):
		sub_hien_thi = ""
		for rb in self.groupbox_show_sub.findChildren(QRadioButton):
			if rb.isChecked():
				sub_hien_thi = rb.getValue()
		return {
			**self.tab_sub_origin.getValue(),
			**self.tab_sub_translate.getValue(),
			
			"sub_hien_thi": sub_hien_thi
		}
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		
		self.tab_sub_origin.clearData()
		self.tab_sub_translate.clearData()
