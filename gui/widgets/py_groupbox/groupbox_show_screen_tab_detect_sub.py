# -*- coding: utf-8 -*-
import os

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QSlider, \
	QFileDialog

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import ROW_SELECTION_CHANGED_TABLE_EXTRACT, \
	LOAD_VIDEO_FROM_FILE_SRT_EXTRACT, SELECTION_AREA_SUB_CHANGED, LOAD_FILE_EXTRACT_FINISHED, LOAD_VIDEO_FROM_DROP_FILE, \
	TOOL_CODE_MAIN, SETTING_APP_DATA
from gui.helpers.custom_logger import decorator_try_except_class
from gui.helpers.func_helper import VideoCapture, getValueSettings, is_chinese_char

from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_graphics.py_graphic_view_generate_sub import GraphicViewGenerateSub
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox

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


class GroupBoxShowScreenTabDetectSub(QWidget):
	sliderChangeFrameChanged = Signal(int)
	
	def __init__ (self, manage_thread_pool: ManageThreadPool, manage_cmd, thread_pool_limit, table_process):
		super().__init__()
		self.app_path = os.path.abspath(os.getcwd())
		settings =getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')

		self.languages = settings.get("language_support").get("language_detect")
		
		self.manage_thread_pool = manage_thread_pool
		self.manage_cmd = manage_cmd
		self.thread_pool_limit = thread_pool_limit
		self.table_process = table_process
		self.blur_sub = False
		
		self.is_loaded = True
		self.is_load_file_local = True  # là load file ở dưới local để detect, false là load file tử bảng process để xem sub
		
		self.contrast = 0
		self.brightness = 0
		self.video_width = 0
		self.video_heigth = 0
		self.sub_size = 30
 
		
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
		self.viewer = GraphicViewGenerateSub(self.manage_thread_pool)
		
		self.btn_dialog_load_file = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		
		# hbox_down
		self.slider_change_frame = QSlider()
		self.slider_change_frame.setEnabled(False)
		
		# self.sliderListImg.setGeometry(QRect(90, 450, 571, 22))
		self.slider_change_frame.setOrientation(Qt.Orientation.Horizontal)
		
		self.lb_change_frame_number = QLabel("")
		self.lb_change_frame = QLabel("Change Frame")
		
		# self.groupbox_server = GroupboxDetectSub(self, self.manage_thread_pool, self.manage_cmd, self.thread_pool_limit,
		# 	self.table_process, self.viewer)
		
		self.check_active_tool = QLabel()
		
		self.btn_privious = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("privious.png"),
			parent=self,
			tooltip_text="Previous",
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
		self.setDisabledButton(True)
		
		# path_ffsub = getValueSettings(PATH_INSTALL_TOOL, TOOL_CODE_FFSUB)
		

	# self.setDisabledButton(True)
	
	
	def create_layouts (self):
		self.bg_layout = QVBoxLayout()
		self.content_up_layout = QVBoxLayout()
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
		
		self.content_layout.addWidget(QLabel(""))  # tạo khoảng cách với tiêu đề GroupBox
		self.content_layout.addLayout(self.content_up_layout, 95)
		# self.content_layout.addLayout(self.content_bottom_layout, 5)
		self.content_layout.addLayout(self.content_down_layout, 5)
		
		# self.vbox.addWidget(QLabel(""))
		# self.content_up_layout.addWidget(self.groupbox_tools)
		self.content_up_layout.addWidget(self.viewer, alignment=Qt.AlignmentFlag.AlignHCenter)
		
		# self.content_up_layout.addWidget(self.slider_pos_sub)
		# self.content_down_layout.addWidget(self.check_active_tool)
		self.content_down_layout.addWidget(self.btn_dialog_load_file)
		self.content_down_layout.addWidget(QLabel(""))
		self.content_down_layout.addWidget(self.lb_change_frame)
		self.content_down_layout.addWidget(self.slider_change_frame)
		self.content_down_layout.addWidget(self.lb_change_frame_number)
		
		# self.content_bottom_layout.addWidget(QLabel(""), 42)
		# self.content_bottom_layout.addWidget(self.btn_privious, 5)
		# self.content_bottom_layout.addWidget(self.input_skip_frame, 5)
		# self.content_bottom_layout.addWidget(self.btn_next, 5)
		# self.content_bottom_layout.addWidget(QLabel(""), 43 )
	
	
	def setup_connections (self):
		
		self.slider_change_frame.valueChanged.connect(self._sliderFrameValueChanged)
		self.btn_next.clicked.connect(self._clickNext)
		self.btn_privious.clicked.connect(self._clickPrevious)
		self.manage_thread_pool.resultChanged.connect(self._resultChanged)
		
		self.btn_dialog_load_file.clicked.connect(self._openDialogFileVideo)
	
	def setDisabledButtonOpen (self, disabled):
		self.btn_dialog_load_file.setDisabled(disabled)
		
		if disabled is True:
			self.btn_dialog_load_file.set_icon_color = "#c3ccdf"
			self.btn_dialog_load_file.icon_color = "#c3ccdf"
			self.btn_dialog_load_file.icon_color_hover = "#dce1ec"
			self.btn_dialog_load_file.icon_color_pressed = "#edf0f5"
		else:
			self.btn_dialog_load_file.set_icon_color = "#f5ca1e"
			self.btn_dialog_load_file.icon_color = "#f5ca1e"
			self.btn_dialog_load_file.icon_color_hover = "#ffe270"
			self.btn_dialog_load_file.icon_color_pressed = "#d1a807"
		
		self.btn_dialog_load_file.repaint()
	
	def setDisabledButton (self, status):
		self.btn_privious.setDisabled(status)
		self.btn_next.setDisabled(status)
		self.input_skip_frame.setDisabled(status)
		if status is True:
			self.btn_privious.set_icon_color = "#c3ccdf"
			self.btn_privious.icon_color = "#c3ccdf"
			self.btn_privious.icon_color_hover = "#dce1ec"
			self.btn_privious.icon_color_pressed = "#edf0f5"
			self.btn_next.set_icon_color = "#c3ccdf"
			self.btn_next.icon_color = "#c3ccdf"
			self.btn_next.icon_color_hover = "#dce1ec"
			self.btn_next.icon_color_pressed = "#edf0f5"
		else:
			self.btn_privious.set_icon_color = "#4aeeaa"
			self.btn_privious.icon_color = "#4aeeaa"
			self.btn_privious.icon_color_hover = "#ffe270"
			self.btn_privious.icon_color_pressed = "#d1a807"
			self.btn_next.set_icon_color = "#4aeeaa"
			self.btn_next.icon_color = "#4aeeaa"
			self.btn_next.icon_color_hover = "#ffe270"
			self.btn_next.icon_color_pressed = "#d1a807"
		
		self.btn_next.repaint()
		self.btn_privious.repaint()
	
	def _clickNext (self):
		if self.slider_change_frame.value() >= self.slider_change_frame.maximum():
			return
		self.slider_change_frame.setValue(self.slider_change_frame.value() + self.input_skip_frame.value())
	
	def _clickPrevious (self):
		if self.slider_change_frame.value() <= 0:
			return
		self.slider_change_frame.setValue(self.slider_change_frame.value() - self.input_skip_frame.value())
	
	def _openDialogFileVideo (self):
		
		# PyMessageBox().show_info("Lưu Ý", "Tên file srt phải trùng với tên file video tương ứng")
		self.path_file, _ = QFileDialog.getOpenFileName(self, caption='Chọn file video',
			dir=(self.app_path),
			filter='File Video (*.mp4 *.avi *wmv *mkv *mov)')
		if self.path_file == "":
			return PyMessageBox().show_error("Lỗi", "Vui lòng chọn file video")
		
		name = os.path.basename(self.path_file)
		if is_chinese_char(name):
			PyMessageBox().show_error('Cảnh Báo', "Tên file phải để tiếng anh không dấu")
			return
		
		if os.path.isfile(self.path_file):
			self.view_video()
	
	def view_video (self):
		with VideoCapture(self.path_file) as video_cap:
			# video_cap = cv2.VideoCapture(path_file)
			# frame_no = 1001  # set frame số mấy
			# video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
			if video_cap.isOpened():
				is_ok, frame = video_cap.read()
				if is_ok is True:
					self.is_load_file_local = True
					self.is_loaded = True
					frame_count = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
					frame_height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
					frame_width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
					fps = video_cap.get(cv2.CAP_PROP_FPS)
					# print(frame_count, frame_height, frame_width, fps)
					
					image_b = cv2.imencode('.png', frame)[1].tobytes()
					pixmap = self.convertCvImage2QtImage(image_b)
					
					self.viewer.setFrameVideo(pixmap, frame_width, frame_height)
					self.viewer.removeRectBlur()
					self.viewer.addRectBlur()
					
					self.slider_change_frame.setRange(1, frame_count)
					self.slider_change_frame.setEnabled(True)
					# self.slider_change_frame.setValue(2)
					self.slider_change_frame.setValue(1)
					self.selectionAreaSubChanged(frame)
					
					self.is_loaded = False
					self.setDisabledButton(False)
					self.viewer.removeBoxSubOriginExtract()
					self.manage_thread_pool.resultChanged.emit(LOAD_FILE_EXTRACT_FINISHED, LOAD_FILE_EXTRACT_FINISHED, self.path_file)
	
	# except Exception as e:
	#     try:
	#         customLogger().error(e)
	#     finally:
	#         e = None
	#         del e
	
	@decorator_try_except_class
	def loadFrameVideo (self, frame_number):
		# frame_no = 1001  # set frame số mấy
		if self.is_load_file_local is True:
			
			if hasattr(self, "path_file") and self.is_loaded is False:
				with VideoCapture(self.path_file) as video_cap:
					video_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
					if video_cap.isOpened():
						ret, frame = video_cap.read()
						
						if ret is True:
							frame_height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
							frame_width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
							image_b = cv2.imencode('.png', frame)[1].tobytes()
							pixmap = self.convertCvImage2QtImage(image_b)
							self.viewer.setFrameVideo(pixmap, frame_width, frame_height)
							
							self.selectionAreaSubChanged(frame)
		
		# cv2.imshow('frame', sharpened)
		# cv2.waitKey()
		else:
			if hasattr(self, "path_video"):
				
				if os.path.isfile(self.path_video):
					# if self.is_loaded is False:
					sequence = self.sequences[frame_number - 1]
					with VideoCapture(self.path_video) as video_cap:
						stt_, time_, content_ = sequence[0], sequence[1], sequence[2]
						# manage_thread.progressChanged.emit(UPDATE_VALUE_PROGRESS_GET_FRAME_IMAGE,id_worker,count + 1)
						start = time_.split(' --> ')[0]
						end = time_.split(' --> ')[1]
						start = self.strFloatTime(start)
						end = self.strFloatTime(end)
						(start, end) = map(float, (start, end))
						span = (end + start) / 2
						video_cap.set(cv2.CAP_PROP_POS_MSEC, span * 1000)
						(success, frame) = video_cap.read()
						if success:
							frame_height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
							frame_width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
							image_b = cv2.imencode('.png', frame)[1].tobytes()
							pixmap = self.convertCvImage2QtImage(image_b)
							self.viewer.setFrameVideo(pixmap, frame_width, frame_height)
							self.viewer.addSubTextOrigin(content_)
	
	# self.loadSubText()
	
	# self.is_loaded = False
	
	@decorator_try_except_class
	def selectionAreaSubChanged (self, frame):
		if self.is_load_file_local is True:
			if hasattr(self, "path_file"):
				# cv2.imshow('frame', frame)
				# cv2.waitKey()
				
				crop_x = int(self.viewer.rect_selection_sub_area.pos().x())
				crop_y = int(self.viewer.rect_selection_sub_area.pos().y())
				crop_width = int(self.viewer.rect_selection_sub_area.rect().width())
				crop_height = int(self.viewer.rect_selection_sub_area.rect().height())
				
				if (crop_x > 0 or crop_y > 0) and (crop_width > 0 and crop_height > 0):
					crop_x_end = crop_x + crop_width
					crop_y_end = crop_y + crop_height
					
					frame_crop = frame[crop_y:crop_y_end, crop_x:crop_x_end]
					
					result_brightness = cv2.convertScaleAbs(frame_crop,
						alpha=self.contrast / 100,
						beta=self.brightness)
					gray = cv2.cvtColor(result_brightness, cv2.COLOR_BGR2GRAY)
					
					# gray = cv2.cvtColor(frame_crop, cv2.COLOR_BGR2GRAY)
					# Create a sharpening kernel
					kernel = np.array([[0, -1, 0],
									   [-1, 5, -1],
									   [0, -1, 0]])
					# Apply the sharpening kernel to the grayscale image
					sharpened = cv2.filter2D(gray, -1, kernel)
					self.frame_area_current = sharpened
					image_blur = cv2.imencode('.png', sharpened)[1].tobytes()
					pixmap = self.convertCvImage2QtImage(image_blur)
					self.viewer.setFrameSelectionArea(pixmap)
	
	def unsharp_mask (self, image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
		"""Return a sharpened version of the image, using an unsharp mask."""
		blurred = cv2.GaussianBlur(image, kernel_size, sigma)
		sharpened = float(amount + 1) * image - float(amount) * blurred
		sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
		sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
		sharpened = sharpened.round().astype(np.uint8)
		if threshold > 0:
			low_contrast_mask = np.absolute(image - blurred) < threshold
			np.copyto(sharpened, image, where=low_contrast_mask)
		return sharpened
	
	# def sharpen_image (self, image, model):
	# 	sr = cv2.dnn_superres.DnnSuperResImpl_create()
	# 	path = JOIN_PATH(PATH_MODEl, f"{model}_x2.pb")
	# 	sr.readModel(path)
	# 	sr.setModel(model.lower(), 2)
	#
	# 	return sr.upsample(image)
	
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
	
	def loadData (self, configCurrent):
		
		self.configCurrent = configCurrent
		self.viewer.loadData(configCurrent, self.manage_thread_pool)
		if self.viewer.hasPhoto() is True:
			pass
	
	def _sliderFrameValueChanged (self, value):
		# push ra ngoài chô ben groupbox timeline chuyển frame
		if self.is_load_file_local is False:
			self.sliderChangeFrameChanged.emit(value)
		
		self.lb_change_frame_number.setText(str(value))
		# self.manage_thread_pool.resultChanged(SLI)
		
		self.loadFrameVideo(value)
	
	def loadDataFrameVideo (self, sequences, path_video):
		self.path_video = path_video
		self.sequences = sequences
		self.is_load_file_local = False
		# self.groupbox_server.groupbox_server.setDisabled(True)
		self.slider_change_frame.setEnabled(True)
		self.slider_change_frame.setRange(1, len(sequences))
		self.slider_change_frame.setValue(2)
		self.slider_change_frame.setValue(1)
		self.viewer.removeRectBlur()
	
	# def imageChangeFrame(self, value_slider):
	#     """ Mô tả: Cập nhập ảnh sau mỗi lần thay đổi giá trị của Slider """
	#     # try:
	#
	
	def _resultChanged (self, id_worker, typeThread, result):
		''' nhận data từ các widget khác thông qua biến manage_thread_pool'''
		
		if typeThread == LOAD_VIDEO_FROM_DROP_FILE:
			if os.path.isfile(result):
				self.path_file = result
				self.view_video()
		
		if typeThread == ROW_SELECTION_CHANGED_TABLE_EXTRACT:
			if self.is_load_file_local is False:
				self.slider_change_frame.setValue(result)

		if typeThread == SELECTION_AREA_SUB_CHANGED:
			if self.is_load_file_local is True:
				if hasattr(self, "path_file") and self.is_loaded is False:
					
					with VideoCapture(self.path_file) as video_cap:
						video_cap.set(cv2.CAP_PROP_POS_FRAMES, self.slider_change_frame.value())
						if video_cap.isOpened():
							ret, frame = video_cap.read()
							if ret is True:
								self.selectionAreaSubChanged(frame)
# print(typeThread)
