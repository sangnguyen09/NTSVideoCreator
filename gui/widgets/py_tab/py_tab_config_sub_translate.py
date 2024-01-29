# -*- coding: utf-8 -*-
import json

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QGroupBox, QSlider, QLineEdit, QColorDialog, \
	QComboBox, QRadioButton

from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_messagebox.py_massagebox import PyMessageBox
from ..py_radio_buttion import PyRadioButton
from ...configs.config_resource import ConfigResource
from ...db.sqlite import CauHinhTuyChonModel


class PyTabConfigSubTranslate(QWidget):
	def __init__ (self, manage_thread_pool: ManageThreadPool):
		
		super().__init__()
		# PROPERTIES
		
		self.manage_thread_pool = manage_thread_pool
		self.isLoad = True
		
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	def create_widgets (self):
		self.groupbox_position_sub = QGroupBox("Vị Trí SUB Dịch:")
 
		self.rad_position_topleft = PyRadioButton(value=9, text="Top Left")
		self.rad_position_topcenter = PyRadioButton(value=8, text="Top Center")
		self.rad_position_topright = PyRadioButton(value=7, text="Top Right")
		
		self.rad_position_middleright = PyRadioButton(value=6, text="Middle Right")
		self.rad_position_middlecenter = PyRadioButton(value=5, text="Middle Center")
		self.rad_position_middleleft = PyRadioButton(value=4, text="Middle Left")
		
		self.rad_position_bottomright = PyRadioButton(value=3, text="Bottom Right")
		self.rad_position_bottomcenter = PyRadioButton(value=2, text="Bottom Center")
		self.rad_position_bottomleft = PyRadioButton(value=1, text="Bottom Left")
		self.rad_position_dragto = PyRadioButton(value=0, text="Drag To Positon")
		
		self.groupbox_style_sub = QGroupBox("STyle")
		# self.groupbox_style_sub.setCheckable(True)
		# self.groupbox_style_sub.setChecked(False)
		# self.groupbox_split_sub = QGroupBox("Ngắt Đoạn Sub Thành Nhiều Dòng:")
		# self.groupbox_split_sub.setCheckable(True)
		# self.lb_number_charecter_in_line = QLabel("Số Từ Tối Đa Trên 1 Dòng")
		# self.max_character_inline = QSpinBox()
		# self.max_character_inline.setMinimum(5)
		# self.max_character_inline.setMaximum(50)
		# self.lb_noty = QLabel("Chỉ nên dùng khi ngôn ngữ là Tiếng Nhật hoặc Trung Quốc")
		
		
		# self.groupbox_vien_chu = QGroupBox("Thêm viền chữ cho sub:")
		# self.groupbox_vien_chu.setCheckable(True)
		# self.groupbox_vien_chu.setChecked(False)
		
		self.label_mau_vien = QLabel("Màu:")
		self.btn_dialog_mau_vien = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("color-picker.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			width=30,
			height=30,
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.input_mau_vien = QLineEdit()
		self.input_mau_vien.setReadOnly(True)
		self.color_picker_mau_vien = QColorDialog()
		
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
		self.combobox_font_size.addItems([str(i)+"px" for i in range(8,500)])
		self.combobox_font_size.setCurrentIndex(6)
		self.combobox_font_size.setCurrentIndex(6)
	
	
	def modify_widgets (self):
		# self.tab_addsub_right.setStyleSheet("background-color: #931e1e;font-size:20px; padding:10px")
		
		# self.tabWidget.setStyleSheet(tab_main_style())
		pass
	
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

		
		# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.groupbox_position_sub, 35)
		self.content_layout.addWidget(self.groupbox_style_sub, 50)
		# self.content_layout.addLayout(self.btn_layout, 15)
		
		self.groupbox_position_sub.setLayout(self.groupbox_position_sub_layout)
		
		self.groupbox_position_sub_layout.addWidget(self.rad_position_topleft, 0, 0)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_topcenter, 0, 1)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_topright, 0, 2)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_middleleft, 1, 0)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_middlecenter, 1, 1)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_middleright, 1, 2)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_bottomleft, 2, 0)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_bottomcenter, 2, 1)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_bottomright, 2, 2)
		
		self.groupbox_position_sub_layout.addWidget(QLabel(), 3, 0)
		self.groupbox_position_sub_layout.addWidget(self.rad_position_dragto, 3, 1)
		self.groupbox_position_sub_layout.addWidget(QLabel(), 3, 2)
		
		
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
		
		# self.vien_chu_layout.addWidget(self.label_mau_vien, 0, 0, 1, 2)
		# self.vien_chu_layout.addWidget(self.input_mau_vien, 0, 2, 1, 2)
		# self.vien_chu_layout.addWidget(self.btn_dialog_mau_vien, 0, 4)
		# self.vien_chu_layout.addWidget(QLabel(""), 0, 5)
		# self.vien_chu_layout.addWidget(self.lb_do_day_vien, 0, 6, 1, 2)
		# self.vien_chu_layout.addWidget(self.combobox_do_day_vien, 0, 8, 1, 4)
		# self.vien_chu_layout.addWidget(self.lb_opacity_nen_value_current,0,11)
		
		# self.ngat_doan_layout.addWidget(self.lb_number_charecter_in_line, 0, 0, 1, 2)
		# self.ngat_doan_layout.addWidget(QLabel(""), 0, 2)
		# self.ngat_doan_layout.addWidget(self.max_character_inline, 0, 3, 1, 2)
		# self.ngat_doan_layout.addWidget(self.lb_noty, 0, 5, 1, 7)
		
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
	
	
	def setup_connections (self):
		self.btn_dialog_color.clicked.connect(self._openDialogColorSub)
		self.btn_dialog_mau_vien.clicked.connect(self._openDialogMauVien)
		self.btn_dialog_mau_nen.clicked.connect(self._openDialogMauNen)
		
		self.slider_color_opacity.valueChanged.connect(
			lambda value: self.lb_opacity_color_value_current.setText(str(value)))
		self.slider_mau_nen_opacity.valueChanged.connect(self._sliderOpacityChanged)
		# self.groupBox_save_config.signalNameConfigChanged.connect(self.addConfigDB)
	
	def _sliderOpacityChanged (self, value):
		self.lb_opacity_nen_value_current.setText(str(value))
	
	def loadData (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
		cau_hinh: dict = json.loads(configCurrent.value)
		# self.groupbox_style_sub.setChecked(cau_hinh["style_sub_dich"])
		self.groupbox_color.setChecked(cau_hinh["add_mau_sub_dich"])
		self.input_color.setText(cau_hinh["mau_sub_dich"])
		self.slider_color_opacity.setValue(cau_hinh["opacity_mau_sub_dich"])
		
		# self.groupbox_vien_chu.setChecked(cau_hinh["vien_sub_dich"])
		# self.input_mau_vien.setText(cau_hinh["mau_vien_sub_dich"])
		# self.combobox_do_day_vien.setCurrentText(cau_hinh["do_day_vien_sub_dich"])
		
		self.groupbox_nen_chu.setChecked(cau_hinh["nen_sub_dich"])
		self.input_mau_nen.setText(cau_hinh["mau_nen_sub_dich"])
		self.slider_mau_nen_opacity.setValue(cau_hinh["opacity_nen_sub_dich"])
		self.groupbox_font.setChecked(cau_hinh["font_sub_dich"])
		self.combobox_font_family.setCurrentText(cau_hinh["font_family_sub_dich"])
		self.combobox_font_size.setCurrentText(cau_hinh["font_size_sub_dich"])
		
		self.color_picker.setCurrentColor(QColor(cau_hinh["mau_sub_dich"]))
		# self.color_picker_mau_vien.setCurrentColor(QColor(cau_hinh["mau_vien_sub_dich"]))
		self.color_picker_nen_chu.setCurrentColor(QColor(cau_hinh["mau_nen_sub_dich"]))
		
		# self.groupbox_split_sub.setChecked(False if cau_hinh.get("split_sub_translate") is None else cau_hinh.get("split_sub_translate"))
		# self.max_character_inline.setValue(20 if cau_hinh.get("max_character_inline_translate") is None else cau_hinh.get("max_character_inline_translate"))
		
		
		if cau_hinh['sub_hien_thi'] == 'all':
			self.checkRadioDisabled(True)
		else:
			self.checkRadioDisabled(False)
	
	def checkRadioDisabled (self, is_all):
		cau_hinh: dict = json.loads(self.configCurrent.value)
		
		for rb in self.groupbox_position_sub.findChildren(QRadioButton):
			if rb.getValue() == cau_hinh["vi_tri_sub_dich"]:
				rb.setChecked(True)
			
			if is_all is True:
				if cau_hinh['vi_tri_sub'] in [4, 6, 7]:
					if rb.getValue() in [4, 6, 7]:
						rb.setDisabled(True)
				
				elif cau_hinh['vi_tri_sub'] in [8, 10, 11]:
					if rb.getValue() in [8, 10, 11]:
						rb.setDisabled(True)
				
				elif cau_hinh['vi_tri_sub'] in [1, 2, 3]:
					if rb.getValue() in [1, 2, 3]:
						rb.setDisabled(True)
			else:
				rb.setDisabled(False)
	
	def _openDialogColorSub (self):
		done = self.color_picker.exec()
		color = self.color_picker.currentColor()
		if done and color.isValid():
			rgb_255 = [color.red(), color.green(), color.blue()]
			color_hex = '#' + ''.join(
				[hex(v)[2:].ljust(2, '0') for v in rgb_255]
			)
			self.input_color.setText(color_hex)
	
	def _openDialogMauVien (self):
		done = self.color_picker_mau_vien.exec()
		color = self.color_picker_mau_vien.currentColor()
		if done and color.isValid():
			rgb_255 = [color.red(), color.green(), color.blue()]
			color_hex = '#' + ''.join(
				[hex(v)[2:].ljust(2, '0') for v in rgb_255]
			)
			self.input_mau_vien.setText(color_hex)
	
	def _openDialogMauNen (self):
		done = self.color_picker_nen_chu.exec()
		color = self.color_picker_nen_chu.currentColor()
		if done and color.isValid():
			rgb_255 = [color.red(), color.green(), color.blue()]
			color_hex = '#' + ''.join(
				[hex(v)[2:].ljust(2, '0') for v in rgb_255]
			)
			self.input_mau_nen.setText(color_hex)
	
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
 
	
	def getValue (self):
		position_text = ""
		for rb in self.groupbox_position_sub.findChildren(QRadioButton):
			if rb.isChecked():
				position_text = rb.getValue()
		
		return {
			"vi_tri_sub_dich": position_text,
			# "style_sub_dich": self.groupbox_style_sub.isChecked(),
			# "split_sub_translate": self.groupbox_split_sub.isChecked(),
			# "max_character_inline_translate": self.max_character_inline.value(),
			
			"add_mau_sub_dich": self.groupbox_color.isChecked(),
			"mau_sub_dich": self.input_color.text(),
			"opacity_mau_sub_dich": self.slider_color_opacity.value(),
			# "vien_sub_dich": self.groupbox_vien_chu.isChecked(),
			# "mau_vien_sub_dich": self.input_mau_vien.text(),
			# "do_day_vien_sub_dich": self.combobox_do_day_vien.currentText(),
			"nen_sub_dich": self.groupbox_nen_chu.isChecked(),
			"mau_nen_sub_dich": self.input_mau_nen.text(),
			"opacity_nen_sub_dich": self.slider_mau_nen_opacity.value(),
			"font_sub_dich": self.groupbox_font.isChecked(),
			"font_family_sub_dich": self.combobox_font_family.currentText(),
			"font_size_sub_dich": self.combobox_font_size.currentText()
			
		}
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		
		# self.groupbox_style_sub.setChecked(False)
		# self.groupbox_style_sub.setChecked(False)
		# self.groupbox_split_sub.setChecked(False)

		self.groupbox_color.setChecked(False)
		self.input_color.setText("#ffffff")
		self.slider_color_opacity.setValue(100)
		# self.groupbox_vien_chu.setChecked(False)
		# self.input_mau_vien.setText("#000000")
		# self.combobox_do_day_vien.setCurrentText("1px")
		self.groupbox_nen_chu.setChecked(False)
		self.input_mau_nen.setText("#000000")
		self.slider_mau_nen_opacity.setValue(80)
		self.groupbox_font.setChecked(False)
		self.combobox_font_family.setCurrentText("Arial")
		self.combobox_font_size.setCurrentText("12px")
		
		# self.rad_position_bottomcenter.setChecked(True)
		
		for rb in self.groupbox_position_sub.findChildren(QRadioButton):
			if rb.getValue() == 2:
				rb.setChecked(True)
