import json
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QBrush, QPen
from PySide6.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog, \
	QColorDialog, QComboBox, \
	QSlider, QWidget

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN, CHANGE_STYLE_DIALOG_EDIT_SUB
from gui.helpers.func_helper import getValueSettings
from gui.helpers.thread import ManageThreadPool
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


class PyDialogGraphicConfigEditSub(QDialog):
	def __init__ (self, list_fonts,dataConfigChanged, manage_thread_pool ):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
		
		self.list_fonts = list_fonts
		self.manage_thread_pool =manage_thread_pool
		# self.dataConfigChanged =dataConfigChanged
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
 
		self.app_path = os.path.abspath(os.getcwd())
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Tuỳ chỉnh thông số")
		self.setStyleSheet(self.style_format)
		
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	def create_widgets (self):
		
		self.groupbox_style_sub = QGroupBox("STyle")
		
		self.lb_do_day_vien = QLabel("Độ dày:")
		self.combobox_do_day_vien = QComboBox()
		self.combobox_do_day_vien.addItems(
			["1px", "2px", "3px"])
		# self.combobox_do_day_vien.setCurrentIndex(1)
		
		self.groupbox_nen_chu = QGroupBox("thêm Nền của sub:")
		self.groupbox_nen_chu.setCheckable(True)
		self.groupbox_nen_chu.setChecked(False)
		self.label_mau_nen = QLabel("Màu:")
		self.btn_dialog_mau_nen = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("color-picker.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			width=30,
			height=30,
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.input_mau_nen = QLineEdit()
		self.input_mau_nen.setReadOnly(True)
		self.color_picker_nen_chu = QColorDialog()
		
		self.lb_opacity_nen = QLabel("Opacity:")
		self.lb_opacity_nen_value_current = QLabel("")
		self.slider_mau_nen_opacity = QSlider()
		self.slider_mau_nen_opacity.setOrientation(Qt.Orientation.Horizontal)
		self.slider_mau_nen_opacity.setRange(1, 100)
		self.slider_mau_nen_opacity.setValue(100)
		self.lb_opacity_nen_value_current.setText(self.slider_mau_nen_opacity.value().__str__())
		
		#####################################
		self.groupbox_color = QGroupBox("thay đổi Màu Chữ của Sub:")
		self.groupbox_color.setCheckable(True)
		self.groupbox_color.setChecked(False)
		self.label_color = QLabel("Màu:")
		self.btn_dialog_color = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("color-picker.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			width=30,
			height=30,
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.input_color = QLineEdit()
		self.input_color.setReadOnly(True)
		self.color_picker = QColorDialog()
		
		self.lb_opacity_color = QLabel("Opacity:")
		self.lb_opacity_color_value_current = QLabel("")
		self.slider_color_opacity = QSlider()
		self.slider_color_opacity.setOrientation(Qt.Orientation.Horizontal)
		self.slider_color_opacity.setRange(1, 100)
		self.slider_color_opacity.setValue(100)
		self.lb_opacity_color_value_current.setText(self.slider_color_opacity.value().__str__())
		
		#####################################
		self.groupbox_font = QGroupBox("Font:")
		self.groupbox_font.setCheckable(True)
		self.groupbox_font.setChecked(False)
		self.lb_font_sub = QLabel("Font Chữ:")
		self.lb_font_size_sub = QLabel("Font Size:")
		
		self.combobox_font_family = QComboBox()
		
		self.combobox_font_size = QComboBox()
		# self.combobox_font_size.addItems(
		# 	["6px", "8px", "9px", "10px", "11px", "12px", "14px", "16px", "18px", "24px", "30px", "36px", "48px",
		# 	 "60px", "72px"])
		self.combobox_font_size.addItems([str(i) + "px" for i in range(8, 500)])
		self.combobox_font_size.setCurrentIndex(32)
		# self.combobox_font_size.setCurrentIndex(6)
		
		self.buttonSave = PyPushButton(text="Save", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86",
			bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)
	
	def modify_widgets (self):
		# self.tab_addsub_right.setStyleSheet("background-color: #931e1e;font-size:20px; padding:10px")
		
		# self.tabWidget.setStyleSheet(tab_main_style())
		self.loadFont(self.list_fonts)
	
	# pass
	
	def loadFont (self, list_fonts):
		for index, font in enumerate(list_fonts):
			self.combobox_font_family.addItem(font)
			self.combobox_font_family.setItemData(index, QFont(font, 14), Qt.ItemDataRole.FontRole)
	
	def create_layouts (self):
		
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.content_frame = QWidget()
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
		
		self.groupbox_position_sub_layout = QGridLayout()
		
		self.add_style_layout = QVBoxLayout()
		self.font_layout = QGridLayout()
		self.vien_chu_layout = QGridLayout()
		self.nen_chu_layout = QGridLayout()
		self.color_layout = QGridLayout()
		self.ngat_doan_layout = QGridLayout()
	
		self.btn_layout = QHBoxLayout()
		self.btn_layout.setContentsMargins(0, 10, 0, 10)
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.groupbox_style_sub)
		self.content_layout.addLayout(self.btn_layout)
		
		
		self.groupbox_style_sub.setLayout(self.add_style_layout)
		
		# self.add_style_layout.addWidget(self.groupbox_split_sub)
		self.add_style_layout.addWidget(self.groupbox_color)
		# self.add_style_layout.addWidget(self.groupbox_vien_chu)
		self.add_style_layout.addWidget(self.groupbox_nen_chu)
		self.add_style_layout.addWidget(self.groupbox_font)
		
		# self.groupbox_split_sub.setLayout(self.ngat_doan_layout)
		# self.groupbox_vien_chu.setLayout(self.vien_chu_layout)
		self.groupbox_nen_chu.setLayout(self.nen_chu_layout)
		self.groupbox_color.setLayout(self.color_layout)
		self.groupbox_font.setLayout(self.font_layout)
		
		self.color_layout.addWidget(self.label_color, 0, 0, 1, 2)
		self.color_layout.addWidget(self.input_color, 0, 2, 1, 2)
		self.color_layout.addWidget(self.btn_dialog_color, 0, 4)
		self.color_layout.addWidget(QLabel(""), 0, 5)
		self.color_layout.addWidget(self.lb_opacity_color, 0, 6, 1, 2)
		self.color_layout.addWidget(self.slider_color_opacity, 0, 8, 1, 3)
		self.color_layout.addWidget(self.lb_opacity_color_value_current, 0, 11)
		
		self.nen_chu_layout.addWidget(self.label_mau_nen, 0, 0, 1, 2)
		self.nen_chu_layout.addWidget(self.input_mau_nen, 0, 2, 1, 2)
		self.nen_chu_layout.addWidget(self.btn_dialog_mau_nen, 0, 4)
		self.nen_chu_layout.addWidget(QLabel(""), 0, 5)
		self.nen_chu_layout.addWidget(self.lb_opacity_nen, 0, 6, 1, 2)
		self.nen_chu_layout.addWidget(self.slider_mau_nen_opacity, 0, 8, 1, 3)
		self.nen_chu_layout.addWidget(self.lb_opacity_nen_value_current, 0, 11)
		
		self.font_layout.addWidget(self.lb_font_sub, 0, 0, 1, 2)
		self.font_layout.addWidget(self.combobox_font_family, 0, 2, 1, 2)
		self.font_layout.addWidget(QLabel(""), 0, 4, 1, 2)
		self.font_layout.addWidget(self.lb_font_size_sub, 0, 6, 1, 2)
		self.font_layout.addWidget(self.combobox_font_size, 0, 8, 1, 4)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
		
	def setup_connections (self):
		self.btn_dialog_color.clicked.connect(self._openDialogColorSub)
		self.btn_dialog_mau_nen.clicked.connect(self._openDialogMauNen)
		self.buttonSave.clicked.connect(self.save)
		#
		# self.slider_color_opacity.valueChanged.connect(
		#     lambda value: self.lb_opacity_color_value_current.setText(str(value)))
		# self.slider_mau_nen_opacity.valueChanged.connect(self._sliderOpacityChanged)
		# self.input_color.textChanged.connect(self._sliderOpacityChanged)
		
		
		self.groupbox_color.toggled.connect(lambda: self.dataConfigChanged(self.groupbox_color.isChecked(), 'add_mau_sub_dich'))
		self.input_color.textChanged.connect(lambda: self.dataConfigChanged(self.input_color.text(), 'mau_sub_dich'))
		self.slider_color_opacity.valueChanged.connect(lambda: self.dataConfigChanged(self.slider_color_opacity.value(), 'opacity_mau_sub_dich'))
		
		self.groupbox_nen_chu.toggled.connect(lambda: self.dataConfigChanged(self.groupbox_nen_chu.isChecked(), 'nen_sub_dich'))
		self.input_mau_nen.textChanged.connect(lambda: self.dataConfigChanged(self.input_mau_nen.text(), 'mau_nen_sub_dich'))
		self.slider_mau_nen_opacity.valueChanged.connect(lambda: self.dataConfigChanged(self.slider_mau_nen_opacity.value(), 'opacity_nen_sub_dich'))
		
		self.groupbox_font.toggled.connect(lambda: self.dataConfigChanged(self.groupbox_font.isChecked(), 'font_sub_dich'))
		self.combobox_font_family.currentIndexChanged.connect(lambda: self.dataConfigChanged(self.combobox_font_family.currentText(), 'font_family_sub_dich'))
		self.combobox_font_size.currentIndexChanged.connect(lambda: self.dataConfigChanged(self.combobox_font_size.currentText(), 'font_size_sub_dich'))
	
	
	# self.groupBox_save_config.signalNameConfigChanged.connect(self.addConfigDB)
	
	def dataConfigChanged (self, value, key_db):
		
		if hasattr(self, 'configCurrent'):
			cau_hinh = json.loads(self.configCurrent.value)
			cau_hinh[key_db] = value
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			if key_db =='opacity_mau_sub_dich':
				self.lb_opacity_color_value_current.setText(self.slider_color_opacity.value().__str__())
			elif key_db =='opacity_nen_sub_dich':
				self.lb_opacity_nen_value_current.setText(self.slider_mau_nen_opacity.value().__str__())
			
			self.manage_thread_pool.resultChanged.emit(CHANGE_STYLE_DIALOG_EDIT_SUB, CHANGE_STYLE_DIALOG_EDIT_SUB, "")
		
	def _sliderOpacityChanged (self, value):
		self.lb_opacity_nen_value_current.setText(str(value))
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		# self.pos_text = pos_text
		cau_hinh: dict = json.loads(configCurrent.value)
		# self.groupbox_style_sub.setChecked(cau_hinh["style_sub_dich"])
		self.groupbox_color.setChecked(cau_hinh["add_mau_sub_dich"])
		self.input_color.setText(cau_hinh["mau_sub_dich"])
		self.slider_color_opacity.setValue(cau_hinh["opacity_mau_sub_dich"])
		
		self.groupbox_nen_chu.setChecked(cau_hinh["nen_sub_dich"])
		self.input_mau_nen.setText(cau_hinh["mau_nen_sub_dich"])
		self.slider_mau_nen_opacity.setValue(cau_hinh["opacity_nen_sub_dich"])
		self.groupbox_font.setChecked(cau_hinh["font_sub_dich"])
		self.combobox_font_family.setCurrentText(cau_hinh["font_family_sub_dich"])
		self.combobox_font_size.setCurrentText(cau_hinh["font_size_sub_dich"])
		
		self.color_picker.setCurrentColor(QColor(cau_hinh["mau_sub_dich"]))
		# self.color_picker_mau_vien.setCurrentColor(QColor(cau_hinh["mau_vien_sub_dich"]))
		self.color_picker_nen_chu.setCurrentColor(QColor(cau_hinh["mau_nen_sub_dich"]))
	
	def _openDialogColorSub (self):
		done = self.color_picker.exec()
		color = self.color_picker.currentColor()
		if done and color.isValid():
			rgb_255 = [color.red(), color.green(), color.blue()]
			color_hex = '#' + ''.join(
				[hex(v)[2:].ljust(2, '0') for v in rgb_255]
			)
			self.input_color.setText(color_hex)
 
	
	def _openDialogMauNen (self):
		done = self.color_picker_nen_chu.exec()
		color = self.color_picker_nen_chu.currentColor()
		if done and color.isValid():
			rgb_255 = [color.red(), color.green(), color.blue()]
			color_hex = '#' + ''.join(
				[hex(v)[2:].ljust(2, '0') for v in rgb_255]
			)
			self.input_mau_nen.setText(color_hex)
	
	
	def getValue (self):
		
		return {
			"add_mau_sub_dich": self.groupbox_color.isChecked(),
			"mau_sub_dich": self.input_color.text(),
			"opacity_mau_sub_dich": self.slider_color_opacity.value(),
			
			"nen_sub_dich": self.groupbox_nen_chu.isChecked(),
			"mau_nen_sub_dich": self.input_mau_nen.text(),
			"opacity_nen_sub_dich": self.slider_mau_nen_opacity.value(),
			
			"font_sub_dich": self.groupbox_font.isChecked(),
			"font_family_sub_dich": self.combobox_font_family.currentText(),
			"font_size_sub_dich": self.combobox_font_size.currentText()
			
		}
	
	def save (self):
		self.accept()
	def checkValid (self):
		if self.groupbox_color.isChecked() is False and self.groupbox_nen_chu.isChecked() is False and self.groupbox_font.isChecked() is False:
			PyMessageBox().show_warning("Lỗi", "Thiếu dữ liệu bên TAB SUB DỊCH Vui lòng điền đầy đủ")
			return False
		
		elif (self.groupbox_color.isChecked() and self.input_color.text() == "") or (
				self.groupbox_nen_chu.isChecked() and self.input_mau_nen.text() == ""):
			PyMessageBox().show_warning("Lỗi", "Thiếu dữ liệu bên TAB SUB DỊCH Vui lòng điền đầy đủ")
			return False
		
		else:
			return True
	
