import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog, \
	QSlider

from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_checkbox import PyCheckBox
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


class PyDialogLachVideo(QDialog):
	def __init__ (self):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
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
		self.setWindowTitle("Lách Video Đầu Vào")
		self.setStyleSheet(self.style_format)
		
		self.setup_ui()
		
		self.list_proxy = None
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		self.groupbox_edit = QGroupBox("EDIT Video")
		self.cb_cut_end = PyCheckBox(value="cut_end", text="Cắt đuôi:")
		self.cb_cut_start = PyCheckBox(value="cut_start", text="Cắt đầu:")
		self.text_number_start = QSpinBox()
		self.text_number_end = QSpinBox()
		
		self.cb_flip_video = PyCheckBox(value="flip_video", text="Lật ngược video")
		self.cb_change_md5 = PyCheckBox(value="change_md5", text="Change MD5")
		# self.cb_fix_concat_video = PyCheckBox(value="fix_concat", text="No Sound")
		self.cb_video_no_sound = PyCheckBox(value="no_sound", text="Render Video No Sound")
		self.cb_zoom_inout = PyCheckBox(value="zoom_in_out", text="Zoom In Out")
		# self.cb_no_audio = PyCheckBox(value="no_audio", text="No Sound")
		
		self.cb_speed_video = PyCheckBox(value="speed_video", text="Tăng Speed:")
		self.slider_speed = QSlider()
		self.slider_speed.setMinimum(5)
		self.slider_speed.setMaximum(40)
		self.slider_speed.setPageStep(1)
		self.slider_speed.setValue(10)
		self.slider_speed.setOrientation(Qt.Orientation.Horizontal)
		
		self.lb_speed_number = QLabel(str(self.slider_speed.value() / 10) + "x")
		
		self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86",
			bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)
	
	def modify_widgets (self):
		pass
	
	def create_layouts (self):
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.content_frame = QWidget()
		self.content_layout = QVBoxLayout(self.content_frame)
		
		self.gbox_edit_layout = QGridLayout()
		self.gbox_edit_layout.setContentsMargins(0, 0, 0, 0)
		
		self.btn_layout = QHBoxLayout()
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.groupbox_edit, 80)
		self.content_layout.addLayout(self.btn_layout, 20)
		
		self.groupbox_edit.setLayout(self.gbox_edit_layout)
		
		# self.gbox_edit_layout.addWidget(self.cb_cut_start, 0, 0, 1,
		#                                 2)  # (widget, row, column, rowSpan số dòng muốn gộp, columnSpan số cột muốn gộp tình từ 2 thông số đầu, alignment)
		# self.gbox_edit_layout.addWidget(self.text_number_start, 0, 2, 1, 3)
		# self.gbox_edit_layout.addWidget(QLabel(""), 0, 5, 1, 2)
		# self.gbox_edit_layout.addWidget(self.cb_cut_end, 0, 7, 1, 2)
		# self.gbox_edit_layout.addWidget(self.text_number_end, 0, 9, 1, 3)
		
		self.gbox_edit_layout.addWidget(self.cb_flip_video, 1, 0, 1,3)
		# self.gbox_edit_layout.addWidget(QLabel(""), 1, 4, 1, 2)
		self.gbox_edit_layout.addWidget(self.cb_change_md5, 1, 3, 1, 3)
		self.gbox_edit_layout.addWidget(self.cb_zoom_inout, 1, 6, 1, 3)
		self.gbox_edit_layout.addWidget(self.cb_video_no_sound, 1, 9, 1, 3)
		
		self.gbox_edit_layout.addWidget(self.cb_speed_video, 2, 0, 1, 2)
		self.gbox_edit_layout.addWidget(self.slider_speed, 2, 2, 1, 9)
		self.gbox_edit_layout.addWidget(self.lb_speed_number, 2, 11)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.slider_speed.valueChanged.connect(self.sliderValueChanged)
		self.buttonSave.clicked.connect(self.save)
	
	def loadData (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
		cau_hinh: dict = json.loads(configCurrent.value)
		
		self.cb_cut_start.setChecked(cau_hinh["cat_dau"])
		self.text_number_start.setValue(cau_hinh["so_giay_cat_dau"])
		self.text_number_end.setValue(cau_hinh["so_giay_cat_duoi"])
		self.cb_cut_end.setChecked(cau_hinh["cat_duoi"])
		self.cb_flip_video.setChecked(cau_hinh["lat_video"])
		self.cb_change_md5.setChecked(cau_hinh["change_md5"])
		# self.cb_remove_sound.setChecked(cau_hinh["remove_sound"])
		try:
			bmm =cau_hinh['fix_concat']
		except:
			cau_hinh['fix_concat'] = True
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		self.cb_zoom_inout.setChecked(cau_hinh["zoom_in_out"])
		self.cb_video_no_sound.setChecked(cau_hinh["no_sound"])
		self.cb_speed_video.setChecked(cau_hinh["tang_speed"])
		self.slider_speed.setValue(int(cau_hinh["toc_do_tang_speed"] * 10))
	
	def save (self):
		if self.cb_cut_start.isChecked() and self.text_number_start.value() <= 0:
			return PyMessageBox().show_warning("Thiếu thông tin", "Số giây cắt phải lớn hơn 0")
		
		if self.cb_cut_end.isChecked() and self.text_number_end.value() <= 0:
			return PyMessageBox().show_warning("Thiếu thông tin", "Số giây cắt phải lớn hơn 0")
		else:
			self.accept()
	
	def sliderValueChanged (self):
		self.lb_speed_number.setText(str(self.slider_speed.value() / 10) + "x")
	
	def getValue (self):
		return {
			# "cat_dau": self.cb_cut_start.isChecked(),
			# "so_giay_cat_dau": self.text_number_start.value(),
			# "so_giay_cat_duoi": self.text_number_end.value(),
			# "cat_duoi": self.cb_cut_end.isChecked(),
			"lat_video": self.cb_flip_video.isChecked(),
			"change_md5": self.cb_change_md5.isChecked(),
			"zoom_in_out": self.cb_zoom_inout.isChecked(),
			# "fix_concat": self.cb_no_audio.isChecked(),
			"no_sound": self.cb_video_no_sound.isChecked(),
			"tang_speed": self.cb_speed_video.isChecked(),
			"toc_do_tang_speed": self.slider_speed.value() / 10,
		}
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.cb_cut_start.setChecked(False)
		self.text_number_start.clear()
		self.text_number_end.clear()
		self.cb_cut_end.setChecked(False)
		self.cb_flip_video.setChecked(False)
		self.cb_change_md5.setChecked(False)
		self.cb_zoom_inout.setChecked(False)
		self.cb_video_no_sound.setChecked(False)
		self.cb_speed_video.setChecked(False)
		self.slider_speed.setValue(10)
