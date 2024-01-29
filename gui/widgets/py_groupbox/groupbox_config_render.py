import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QCheckBox, \
	QHBoxLayout, QVBoxLayout, QGroupBox

from gui.configs.config_resource import ConfigResource
from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import UPDATE_TY_LE_KHUNG_HINH_VIDEO, CHANGE_HIEN_THI_SUB, PATH_OUTPUT
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_checkbox import PyCheckBox
from gui.widgets.py_dialogs.py_dialog_add_music_bg import PyDialogAddMusicBackground
from gui.widgets.py_dialogs.py_dialog_lach_video import PyDialogLachVideo
from gui.widgets.py_dialogs.py_dialog_output import PyDialogOutput
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon

# STYLE
# ///////////////////////////////////////////////////////////////
style = '''
QRadioButton {{
    color: #c3f0ff;
}}
QRadioButton:hover {{

            color: #ff0000;

}}
QRadioButton:checked  {{
            color: #34c950;

}}

'''
# APPLY STYLESHEET
style_format = style.format()


class GroupBoxConfigRender(QWidget):
	def __init__ (self, manage_thread_pool: ManageThreadPool):
		super().__init__()
		# các biến giá trị
		self.manage_thread_pool = manage_thread_pool
		self.isClearData = False
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.modify_widgets()
		self.setup_connections()
	
	def create_widgets (self):
		self.groupbox = QGroupBox("Cấu Hình Render")
		# subtext
		# self.label_add_text = QLabel("Cài Đặt Phụ Đề")
		# self.dialog_config_sub_text = PyDialogConfigSubText(self.manage_thread_pool)
		# self.btn_add_sub_text = PyButtonIcon(
		# 	icon_path=ConfigResource.set_svg_icon("settings.png"),
		# 	parent=self,
		# 	app_parent=self.groupbox,
		# 	width=25,
		# 	height=25,
		# 	tooltip_text="Cài đặt",
		#
		# )
		self.checkbox_hien_thi_sub = PyCheckBox(value="hien_thi_sub", text="Hiển Thị Sub")

		
		self.checkbox_add_music_background = PyCheckBox(value="add_music_background", text="Thêm Nhạc Nền")
		self.dialog_add_music_background = PyDialogAddMusicBackground()
		self.btn_add_music_background = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("settings.png"),
			parent=self,
			app_parent=self.groupbox,
			width=25,
			height=25,
			tooltip_text="Cài đặt",
		
		)
		
		self.checkbox_use_gpu = PyCheckBox(value="add_music_background", text="Dùng GPU (NVIDIA)")
		
		# self.dialog_add_intro_outro = PyDialogAddIntroOutro()
		# self.btn_add_intro_outro = PyButtonIcon(
		# 	icon_path=ConfigResource.set_svg_icon("settings.png"),
		# 	parent=self,
		# 	width=25,
		# 	height=25,
		# 	app_parent=self.groupbox,
		# 	tooltip_text="Cài đặt",
		#
		# )
		
		self.lb_output_video = QLabel("Output Video")
		self.dialog_output_video = PyDialogOutput()
		self.btn_add_output_video = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("settings.png"),
			parent=self,
			width=25,
			height=25,
			app_parent=self.groupbox,
			tooltip_text="Cài đặt",
		
		)
		
		self.lb_edit_video = QLabel("Lách Video")
		self.dialog_edit_video = PyDialogLachVideo()
		self.btn_edit_video = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("settings.png"),
			parent=self,
			width=25,
			height=25,
			app_parent=self.groupbox,
			tooltip_text="Cài đặt",
		
		)
	
	def modify_widgets (self):
		self.setStyleSheet(style_format)
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		self.gbox_layout = QVBoxLayout()
		self.groupbox.setLayout(self.gbox_layout)
		
		self.content_layout = QHBoxLayout()
		
		self.content_add_sub = QHBoxLayout()
		self.content_add_music = QHBoxLayout()
		self.content_add_intro = QHBoxLayout()
		self.content_output_video = QHBoxLayout()
		self.content_cut_video = QHBoxLayout()
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		self.setLayout(self.bg_layout)
		
		self.gbox_layout.addWidget(QLabel(""))
		self.gbox_layout.addLayout(self.content_layout)
		
		self.content_layout.addWidget(self.checkbox_use_gpu)
		self.content_layout.addLayout(self.content_add_music)
		# self.content_layout.addLayout(self.content_add_intro)
		self.content_layout.addLayout(self.content_add_sub)
		self.content_layout.addLayout(self.content_cut_video)
		
		self.content_layout.addLayout(self.content_output_video)
		
		# self.content_4g_layout.addWidget(self.text_4g,10)
		self.content_add_sub.addWidget(self.checkbox_hien_thi_sub)
		# self.content_add_sub.addWidget(QLabel(), 80)
		
		self.content_add_music.addWidget(self.checkbox_add_music_background)
		self.content_add_music.addWidget(self.btn_add_music_background,alignment=Qt.AlignmentFlag.AlignLeft)
		# self.content_add_music.addWidget(QLabel(), 80)
		
		# self.content_add_intro.addWidget(self.checkbox_hien_thi_sub)
		# self.content_add_intro.addWidget(self.btn_add_intro_outro)
		# self.content_add_intro.addWidget(QLabel(), 80)
		
		self.content_cut_video.addWidget(self.lb_edit_video,alignment=Qt.AlignmentFlag.AlignRight)
		self.content_cut_video.addWidget(self.btn_edit_video)
		# self.content_cut_video.addWidget(QLabel(), 80)
		
		self.content_output_video.addWidget(self.lb_output_video,alignment=Qt.AlignmentFlag.AlignRight)
		self.content_output_video.addWidget(self.btn_add_output_video)
		# self.content_output_video.addWidget(QLabel(), 80)
	
	def setup_connections (self):
		
		
		self.checkbox_add_music_background.stateChanged.connect(
			lambda: self._checkboxChanged(self.checkbox_add_music_background, "them_nhac"))
		
		self.checkbox_hien_thi_sub.stateChanged.connect(
			lambda: self._checkboxChanged(self.checkbox_hien_thi_sub, "hien_thi_sub"))
			
		self.checkbox_use_gpu.stateChanged.connect(
			lambda: self._checkboxChanged(self.checkbox_use_gpu, "use_gpu"))
		
		# self.checkbox_edit_video.stateChanged.connect(
		#     lambda: self._checkboxChanged(self.checkbox_edit_video, "lach_video"))
		
		# self.btn_add_sub_text.clicked.connect(self.open_dialog_config_sub_text)
		self.btn_add_music_background.clicked.connect(self.open_dialog_add_music_background)
		# self.btn_add_intro_outro.clicked.connect(self.open_dialog_add_intro_outro)
		self.btn_add_output_video.clicked.connect(self.open_dialog_output_video)
		self.btn_edit_video.clicked.connect(self.open_dialog_edit_video)
	
	def loadDataConfigCurrent (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
		cau_hinh: dict = json.loads(configCurrent.value)
		# print(cau_hinh)
		self.checkbox_add_music_background.setChecked(cau_hinh.get('them_nhac'))
		self.checkbox_use_gpu.setChecked(cau_hinh["use_gpu"])
		# self.checkbox_edit_video.setChecked(cau_hinh["lach_video"])
		try:
			width_V, height_V = cau_hinh["chat_luong_video"].split("|")
		except:
			cau_hinh["chat_luong_video"] = "1920|1080"
			cau_hinh["ti_le_khung_hinh"] = "16:9"
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
		
		if cau_hinh.get('bit_rate_video') is None:
			cau_hinh["bit_rate_video"] =15000
			cau_hinh["bit_rate_audio"] =15000
			# cau_hinh["bit_rate_value_origin"] = 4800
			# cau_hinh["bit_rate_value_tuy_chinh"] = 4800
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('delete_data_output') is None:
			cau_hinh["he_so_crf"] = 19
			cau_hinh["he_so_preset"] = 'fast'
			cau_hinh["he_so_fps"] = 30
			cau_hinh["delete_data_output"] = True
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('zoom_in_out') is None:
			cau_hinh["zoom_in_out"] = False
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('render_style') is None:
			cau_hinh["render_style"] = 0
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('no_sound') is None:
			cau_hinh["no_sound"] = False
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('so_luong_render') is None:
			cau_hinh["so_luong_render"] = 1
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('concat_v2') is None:
			cau_hinh["concat_v2"] = False
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('mode_fast') is None:
			cau_hinh["mode_fast"] = True
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('folder_src_voice') is None:
			cau_hinh["folder_src_voice"] = ''
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('show_log') is None:
			cau_hinh["show_log"] = False
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		if cau_hinh.get('hien_thi_sub') is None:
			cau_hinh["hien_thi_sub"] = True
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			
		self.checkbox_hien_thi_sub.setChecked(cau_hinh["hien_thi_sub"])
		
		if cau_hinh.get('src_output') == '' or os.path.exists(cau_hinh.get('src_output')) is False:
			cau_hinh["src_output"] = PATH_OUTPUT
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
		# print(cau_hinh)

		# print(cau_hinh)
		
		self._checkEnableButton()
	
	def _checkEnableButton (self):
		
		if self.checkbox_add_music_background.isChecked():
			self.btn_add_music_background.setDisabled(False)
		else:
			self.btn_add_music_background.setDisabled(True)
		
	
		
		# if self.checkbox_edit_video.isChecked():
		#     self.btn_edit_video.setDisabled(False)
		# else:
		#     self.btn_edit_video.setDisabled(True)
	
	def _checkboxChanged (self, checkbox: QCheckBox, text):
		self._checkEnableButton()
		if hasattr(self, "configCurrent"):
 
				cau_hinh = json.loads(self.configCurrent.value)
				cau_hinh[text] = checkbox.isChecked()
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
				if text == "hien_thi_sub":
					self.manage_thread_pool.resultChanged.emit(CHANGE_HIEN_THI_SUB, CHANGE_HIEN_THI_SUB, "")
	
	# def open_dialog_config_sub_text (self):
	# 	if hasattr(self, "configCurrent"):
	# 		cau_hinh = json.loads(self.configCurrent.value)
	#
	# 		self.dialog_config_sub_text.loadData(self.configCurrent)
	# 		if self.dialog_config_sub_text.exec():
	# 			value = self.dialog_config_sub_text.getValue()
	# 			cau_hinh.update(value)
	# 			self.configCurrent.value = json.dumps(cau_hinh)
	# 			self.configCurrent.save()
	# 			self.manage_thread_pool.resultChanged.emit(CHANGE_STYLE_SUB, CHANGE_STYLE_SUB, cau_hinh)
	#
	# 		else:
	# 			print("Cancel!")
	# 	else:
	# 		self.dialog_config_sub_text.exec()
	
	def open_dialog_add_music_background (self):
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			self.dialog_add_music_background.loadData(self.configCurrent)
			if self.dialog_add_music_background.exec():
				
				cau_hinh.update(self.dialog_add_music_background.getValue())
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
			
			else:
				print("Cancel!")
		else:
			self.dialog_add_music_background.exec()
	
	def open_dialog_edit_video (self):
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			self.dialog_edit_video.loadData(self.configCurrent)
			if self.dialog_edit_video.exec():
				cau_hinh.update(self.dialog_edit_video.getValue())
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
			
			else:
				print("Cancel!")
		else:
			self.dialog_edit_video.exec()
	
	# def open_dialog_add_intro_outro (self):
	# 	if hasattr(self, "configCurrent"):
	# 		cau_hinh = json.loads(self.configCurrent.value)
	#
	# 		self.dialog_add_intro_outro.loadData(self.configCurrent)
	#
	# 		if self.dialog_add_intro_outro.exec():
	#
	# 			cau_hinh.update(self.dialog_add_intro_outro.getValue())
	# 			self.configCurrent.value = json.dumps(cau_hinh)
	# 			self.configCurrent.save()
	# 		else:
	# 			print("Cancel!")
	# 	else:
	# 		self.dialog_add_intro_outro.exec()
	#
	def open_dialog_output_video (self):
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			ti_le_khung_hinh= cau_hinh.get('ti_le_khung_hinh')
			chat_luong_video= cau_hinh.get('chat_luong_video')
			self.dialog_output_video.loadData(self.configCurrent)
			
			if self.dialog_output_video.exec():
				cau_hinh.update(self.dialog_output_video.getValue())
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
				ti_le_khung_hinh_new = cau_hinh.get("ti_le_khung_hinh")
				chat_luong_video_new = cau_hinh.get("chat_luong_video")
				if ti_le_khung_hinh != ti_le_khung_hinh_new or chat_luong_video_new != chat_luong_video:
					self.manage_thread_pool.resultChanged.emit(UPDATE_TY_LE_KHUNG_HINH_VIDEO, UPDATE_TY_LE_KHUNG_HINH_VIDEO, "")
			else:
				print("Cancel!")
		else:
			self.dialog_output_video.exec()
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.isClearData = True
		for cb in self.groupbox.findChildren(QCheckBox):
			cb.setChecked(False)
		self._checkEnableButton()
		
		# self.dialog_config_sub_text.clearData()
		self.dialog_add_music_background.clearData()
		self.dialog_edit_video.clearData()
		self.dialog_output_video.clearData()
		# self.dialog_add_intro_outro.clearData()
		
		self.isClearData = False
	
	def getValue (self):
		
		return {
			# "che_sub_cu": self.checkbox_hide_sub_old.isChecked(),
			"them_nhac": self.checkbox_add_music_background.isChecked(),
			# "them_intro_outro": self.checkbox_hien_thi_sub.isChecked(),
			"hien_thi_sub": self.checkbox_hien_thi_sub.isChecked(),
			"use_gpu": self.checkbox_use_gpu.isChecked(),
			# "lach_video": self.checkbox_edit_video.isChecked(),
			# **self.dialog_config_sub_text.getValue(),
			**self.dialog_add_music_background.getValue(),
			**self.dialog_edit_video.getValue(),
			**self.dialog_output_video.getValue(),
			# **self.dialog_add_intro_outro.getValue(),
		}
