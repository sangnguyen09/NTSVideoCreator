# -*- coding: utf-8 -*-
import json
import os

import cv2
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QSlider

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import TOOL_CODE_MAIN, SETTING_APP_DATA, LOAD_CONFIG_TAB_EDIT_SUB_CHANGED, \
	ITEM_TABLE_TIMELINE_EDIT_SUB_CHANGED, \
	ROW_SELECTION_CHANGED_TABLE_EDIT_SUB, LOAD_CONFIG_CHANGED, CHANGE_STYLE_DIALOG_EDIT_SUB, POSITION_EDIT_SUB_CHANGED, \
	LOAD_FONT_FAMILY, CHANGE_HIEN_THI_TAB_EDIT_SUB, PLAY_VIDEO_AGAIN
from gui.helpers.func_helper import VideoCapture, getValueSettings
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_graphics.py_graphic_view_edit_sub import GraphicViewEditSub
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon

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


class GroupBoxShowScreenTabEditSub(QWidget):
	sliderChangeFrameChanged = Signal(int)
	
	def __init__ (self, manage_thread_pool: ManageThreadPool, groupbox_timeline):
		super().__init__()
		settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		
		self.languages = settings.get("language_support").get("language_detect")
		
		self.manage_thread_pool = manage_thread_pool
		
		self.groupbox_timeline = groupbox_timeline
		self.blur_sub = False
		
		self.is_loaded = False
		self.is_load_file_local = True  # là load file ở dưới local để detect, false là load file tử bảng process để xem sub
		
		self.contrast = 0
		self.brightness = 0
		self.video_width = 0
		self.video_heigth = 0
		self.sub_size = 30
		self.sequence_current = None
		
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		
		self.modify_widgets()
		
		self.create_layouts()
		
		self.add_widgets_to_layouts()
		
		self.setup_connections()
	
	
	def create_widgets (self):
		self.groupbox = QGroupBox("Preview")
		
		# hbox_up
		
		self.bg_up_frame = QFrame()
		self.bg_up_frame.setStyleSheet('background-color:#0a0808')
		self.viewer = GraphicViewEditSub(self.manage_thread_pool)
		# self.viewer.setMinimumHeight(600)
		# hbox_down
		self.slider_change_frame = QSlider()
		self.slider_change_frame.setEnabled(False)
		
		# self.sliderListImg.setGeometry(QRect(90, 450, 571, 22))
		self.slider_change_frame.setOrientation(Qt.Orientation.Horizontal)
		
		self.lb_change_frame_number = QLabel("")
		self.lb_change_frame = QLabel("Dòng Sub")
		
		self.check_active_tool = QLabel()
		
		self.btn_play = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("play.png"),
			parent=self,
			tooltip_text="Play",
			app_parent=self.groupbox,
			icon_color="#4aeeaa",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.input_skip_frame = QSpinBox()
		self.input_skip_frame.setValue(1)
		
		self.btn_next = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("next.png"),
			parent=self,
			app_parent=self.groupbox,
			tooltip_text="Next",
			icon_color="#4aeeaa",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
	
	# self.groupbox.setCheckable(True)
	
	def modify_widgets (self):
		self.setStyleSheet(style_format)
	
	# self.setDisabledButton(True)
	
	# path_ffsub = getValueSettings(PATH_INSTALL_TOOL, TOOL_CODE_FFSUB)
	
	
	# self.setDisabledButton(True)
	
	
	def create_layouts (self):
		self.bg_layout = QVBoxLayout()
		self.content_up_layout = QHBoxLayout()
		self.content_up_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_down_layout = QHBoxLayout()
		self.content_bottom_layout = QHBoxLayout()
		
		self.content_layout = QVBoxLayout()
		# self.content_server_layout = QVBoxLayout()
		
		self.groupbox.setLayout(self.content_layout)
	
	# self.groupbox_server.setLayout(self.content_server_layout)
	
	# self.content_tools_layout = QGridLayout()
	# self.groupbox_tools.setLayout(self.content_tools_layout)
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		# self.bg_layout.addWidget(self.groupbox_server,20)
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.bg_layout)
		
		# self.content_layout.addWidget(QLabel(""))  # tạo khoảng cách với tiêu đề GroupBox
		self.content_layout.addLayout(self.content_up_layout)
		# self.content_layout.addLayout(self.content_bottom_layout, 5)
		# self.content_layout.addLayout(self.content_down_layout, 5)
		
		# self.vbox.addWidget(QLabel(""))
		# self.content_up_layout.addWidget(self.groupbox_tools)
		self.content_up_layout.addWidget(self.viewer, alignment=Qt.AlignmentFlag.AlignHCenter)
		
		# self.content_up_layout.addWidget(self.slider_pos_sub)
		# self.content_down_layout.addWidget(self.check_active_tool)
		# self.content_down_layout.addWidget(QLabel(""))
		self.content_down_layout.addWidget(self.lb_change_frame)
		self.content_down_layout.addWidget(self.slider_change_frame)
		self.content_down_layout.addWidget(self.lb_change_frame_number)
		
		# self.content_bottom_layout.addWidget(QLabel(""), 42)
		# self.content_bottom_layout.addWidget(self.btn_play, 5)
	
	# self.content_bottom_layout.addWidget(self.input_skip_frame, 5)
	# self.content_bottom_layout.addWidget(self.btn_next, 5)
	# self.content_bottom_layout.addWidget(QLabel(""), 43 )
	#
	
	def setup_connections (self):
		
		self.slider_change_frame.valueChanged.connect(self._sliderFrameValueChanged)
		self.btn_next.clicked.connect(self._clickNext)
		self.btn_play.clicked.connect(self._clickPlay)
		self.manage_thread_pool.resultChanged.connect(self._resultChanged)
	
	
	def setDisabledButton (self, status):
		self.btn_play.setDisabled(status)
		self.btn_next.setDisabled(status)
		self.input_skip_frame.setDisabled(status)
		if status is True:
			self.btn_play.set_icon_color = "#c3ccdf"
			self.btn_play.icon_color = "#c3ccdf"
			self.btn_play.icon_color_hover = "#dce1ec"
			self.btn_play.icon_color_pressed = "#edf0f5"
			self.btn_next.set_icon_color = "#c3ccdf"
			self.btn_next.icon_color = "#c3ccdf"
			self.btn_next.icon_color_hover = "#dce1ec"
			self.btn_next.icon_color_pressed = "#edf0f5"
		else:
			self.btn_play.set_icon_color = "#4aeeaa"
			self.btn_play.icon_color = "#4aeeaa"
			self.btn_play.icon_color_hover = "#ffe270"
			self.btn_play.icon_color_pressed = "#d1a807"
			self.btn_next.set_icon_color = "#4aeeaa"
			self.btn_next.icon_color = "#4aeeaa"
			self.btn_next.icon_color_hover = "#ffe270"
			self.btn_next.icon_color_pressed = "#d1a807"
		
		self.btn_next.repaint()
		self.btn_play.repaint()
	
	def _clickNext (self):
		if self.slider_change_frame.value() >= self.slider_change_frame.maximum():
			return
		self.slider_change_frame.setValue(self.slider_change_frame.value() + self.input_skip_frame.value())
	
	def _clickPlay (self):
		# sequence =self.groupbox_timeline.getDataRow(line_number-1)
		if self.sequence_current:
			time_, content_, translate = self.sequence_current
			if hasattr(self, 'path_video') and os.path.isfile(self.path_video) and time_ != '' and content_ != '':
				start = time_.split(' --> ')[0]
				end = time_.split(' --> ')[1]
				start = self.strFloatTime(start)
				end = self.strFloatTime(end)
				(start, end) = map(float, (start * 1000, end * 1000))
				
				self.viewer.player.play()
	
	# Sử dụng QTimer để chờ đến khi đạt end_pos và sau đó dừng lại
	
	
	# print(111)
	# with VideoCapture(self.path_video) as video_cap:
	# 	# print(time_)
	# 	# manage_thread.progressChanged.emit(UPDATE_VALUE_PROGRESS_GET_FRAME_IMAGE,id_worker,count + 1)
	# 	start = time_.split(' --> ')[0]
	# 	end = time_.split(' --> ')[1]
	# 	start = self.strFloatTime(start)
	# 	end = self.strFloatTime(end)
	# 	(start, end) = map(float, (start* 1000, end* 1000))
	# 	# span = (end + start) / 2
	# 	for i in range(int(start),int(end)):
	# 		video_cap.set(cv2.CAP_PROP_POS_MSEC, i)
	# 		(success, frame) = video_cap.read()
	# 		if success:
	# 			frame_height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
	# 			frame_width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
	#
	# 			image_b = cv2.imencode('.png', frame)[1].tobytes()
	# 			pixmap = self.convertCvImage2QtImage(image_b)
	# 			self.viewer.setFrameVideo(pixmap, frame_width, frame_height)
	#
	# 			self.viewer.addSubTextOrigin(content_)
	#
	
	def loadFrameVideo (self, line_number):

		if hasattr(self,'folder_name') and os.path.isdir(self.folder_name):
				# self.sequence_current = self.groupbox_timeline.getDataRow(line_number - 1)
				cau_hinh_edit: dict = json.loads(self.fileSRTCurrent.value)
				item_current = cau_hinh_edit.get('data_table',[])[line_number-1]
				file_image = item_current[0]
				# print(file_image)
				if file_image != '' and os.path.exists(file_image):
					pixmap = QPixmap(file_image)
					frame_width = pixmap.width()
					frame_height = pixmap.height()
					# print(frame_height)
					# print(frame_width)
					self.viewer.setFrameVideo(pixmap,frame_width, frame_height)

					self.is_loaded =True
	# self.loadSubText()
	
	# self.is_loaded = False
	
	# @decorator_try_except_class
	def selectionAreaSubChanged (self, frame):
		print(111)
	
	def strFloatTime (self, tempStr):
		""" Mô tả: Đưa về định dạng thời gian"""
		xx = tempStr.split(':')
		hour = int(xx[0])
		minute = int(xx[1])
		second = int(xx[2].split(',')[0])
		minsecond = int(xx[2].split(',')[1])
		allTime = hour * 60 * 60 + minute * 60 + second + minsecond / 1000
		return allTime
	
	def convertCvImage2QtImage (self, cv_img):
		pixmap = QPixmap()
		pixmap.loadFromData(cv_img)
		return pixmap
	
	
	def _sliderFrameValueChanged (self, value):
		# push ra ngoài chô ben groupbox timeline chuyển frame
		if self.is_load_file_local is False:
			self.sliderChangeFrameChanged.emit(value)
		
		self.lb_change_frame_number.setText(str(value))
	
	def loadDataConfigCurrent (self, configCurrent):
		self.configCurrent = configCurrent
		
		self.viewer.loadDataConfigCurrent(configCurrent)
	
	def loadFileSRTCurrent (self, fileSRTCurrent):
		
		self.fileSRTCurrent = fileSRTCurrent
		cau_hinh_edit: dict = json.loads(fileSRTCurrent.value)
		# print(cau_hinh_edit)
		self.folder_name = cau_hinh_edit.get('folder_name')

		if self.folder_name and os.path.isdir(self.folder_name):
			self.loadFrameVideo(1)
			self.viewer.isLoaded = False

	
	# self.manage_thread_pool.resultChanged.emit(SHOW_DATA_TABLE_TIMELINE, SHOW_DATA_TABLE_TIMELINE, result)
	
	
	def _resultChanged (self, id_worker, typeThread, result):
		''' nhận data từ các widget khác thông qua biến manage_thread_pool'''
		
		if typeThread == POSITION_EDIT_SUB_CHANGED:
			if hasattr(self, 'fileSRTCurrent'):
				x, y = result
				cau_hinh = json.loads(self.fileSRTCurrent.value)
				cau_hinh['pos_edit_sub'] = f"{x}:{y}"
				self.fileSRTCurrent.value = json.dumps(cau_hinh)
				self.fileSRTCurrent.save()
		
		if typeThread == ITEM_TABLE_TIMELINE_EDIT_SUB_CHANGED or typeThread == CHANGE_STYLE_DIALOG_EDIT_SUB or typeThread == LOAD_FONT_FAMILY or typeThread == CHANGE_HIEN_THI_TAB_EDIT_SUB:
			
			if hasattr(self, 'fileSRTCurrent'):
				sequence_current = self.groupbox_timeline.getDataRowCurrent()
				time_, content_, translate = sequence_current
				cau_hinh_edit: dict = json.loads(self.fileSRTCurrent.value)
				# print(cau_hinh_edit)
				
				# text = translate
				# if cau_hinh_edit.get('sub_hien_thi', 'origin') == 'origin':
				# 	text = content_
				#
				# if content_:
				# 	self.viewer.addSubTextTranslate(text, cau_hinh_edit.get('pos_edit_sub'))
		
		if typeThread == ROW_SELECTION_CHANGED_TABLE_EDIT_SUB:
			if self.is_loaded:
		# 		# print('ssssssssy')
				self.loadFrameVideo(result)
		# self.slider_change_frame.setValue(result)
		
		# if  typeThread == PLAY_VIDEO_AGAIN:
		# 	self.loadFrameVideo(result)
	# self.slider_change_frame.setValue(result)


# if typeThread == LOAD_CONFIG_CHANGED:
# 	self.configCurrent =result
