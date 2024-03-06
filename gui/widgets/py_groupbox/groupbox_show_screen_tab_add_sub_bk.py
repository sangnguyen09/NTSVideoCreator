# -*- coding: utf-8 -*-
import json
import os

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPixmap
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
	QSlider, QFileDialog

from gui.configs.config_resource import ConfigResource
from gui.db.sqlite import ConfigApp_DB
from gui.helpers.constants import CHANGE_STYLE_SUB, STATUS_BUTTON_SAVE_CONFIG_CHANGED, \
	TRANSLATE_SUB_FINISHED, ROW_SELECTION_CHANGED_TABLE_ADD_SUB, SELECTION_AREA_BLUR_CHANGED, \
	SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, SHOW_DATA_TABLE_TIMELINE, SPLIT_SUB_IN_TABLE_FINISHED, \
	LOAD_SUB_IN_TABLE_FINISHED, UPDATE_TY_LE_KHUNG_HINH_VIDEO
from gui.helpers.func_helper import getValueSettings, setValueSettings
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_dialogs import PyDialogGraphicText
from gui.widgets.py_graphics import GraphicView
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_table_widget.model_timeline_addsub import ColumnNumber

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


class GroupBoxShowScreenTabAddSub(QWidget):
	sliderChangeFrameChanged = Signal(int)
	
	def __init__ (self, manage_thread_pool: ManageThreadPool, db_app: ConfigApp_DB, groupbox_timeline):
		super().__init__()
		self.app_path = os.path.abspath(os.getcwd())
		self.frames_storage = os.path.join(self.app_path, 'frames/')
		
		# self.settings = QSettings(*SETTING_CONFIG)
		# self.settings = st.value(SETTING_APP_DATA)
		
		self.manage_thread_pool = manage_thread_pool
		self.groupbox_timeline = groupbox_timeline
		self.db_app = db_app
		self.blur_sub = False
		self.video_new = False
		
		self.is_loaded = True
		(self.x_s, self.y_s) = (None, None)
		(self.x_e, self.y_e) = (None, None)
		(self.xs_blur, self.ys_blur) = (None, None)
		(self.xe_blur, self.ye_blur) = (None, None)
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
		self.groupbox = QGroupBox("Frame")
		
		# hbox_up
		self.bg_up_frame = QFrame()
		self.bg_up_frame.setStyleSheet('background-color:#0a0808')
		self.viewer = GraphicView(self, self.manage_thread_pool)
		
		self.groupbox_tools = QGroupBox("Công cụ")
		
		self.btn_add_text = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("add-text.png"),
			parent=self,
			width=30,
			height=30,
			app_parent=self.groupbox_tools,
			tooltip_text="Thêm Chữ",
		
		)
		
		self.btn_add_rectangle = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("add-rectangle.png"),
			parent=self,
			width=30,
			height=30,
			app_parent=self.groupbox_tools,
			tooltip_text="Thêm khối chữ nhật",
		
		)
		self.btn_add_media = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("add-image.png"),
			parent=self,
			width=30,
			height=30,
			app_parent=self.groupbox_tools,
			tooltip_text="Thêm hình/video",
		
		)
		
		self.btn_add_rect_blur = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("blur.png"),
			parent=self,
			width=30,
			height=30,
			app_parent=self.groupbox_tools,
			tooltip_text="Làm Mờ 1 Vùng",
		
		)
		self.btn_add_rect_blur.setCheckable(True)
		
		self.btn_save = QPushButton("Lưu Vào Cấu Hình")
		self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_save.setDisabled(True)
		# hbox_down
		self.slider_change_frame = QSlider()
		self.slider_change_frame.setEnabled(False)
		self.slider_change_frame.setMinimum(1)
		
		# self.sliderListImg.setGeometry(QRect(90, 450, 571, 22))
		self.slider_change_frame.setOrientation(Qt.Orientation.Horizontal)
		
		self.lb_change_frame_number = QLabel("")
		self.lb_change_frame = QLabel("Dòng Sub")
	
	def modify_widgets (self):
		self.setStyleSheet(style_format)
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.content_up_layout = QVBoxLayout()
		self.content_down_layout = QHBoxLayout()
		
		self.content_layout = QVBoxLayout()
		
		self.groupbox.setLayout(self.content_layout)
		
		self.content_tools_layout = QGridLayout()
		self.groupbox_tools.setLayout(self.content_tools_layout)
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.bg_layout)
		
		self.content_layout.addWidget(QLabel(""))  # tạo khoảng cách với tiêu đề GroupBox
		self.content_layout.addLayout(self.content_up_layout)
		# self.content_layout.addLayout(self.content_down_layout)
		# self.vbox.addWidget(QLabel(""))
		self.content_up_layout.addWidget(self.groupbox_tools)
		self.content_up_layout.addWidget(self.viewer, 0, Qt.AlignmentFlag.AlignHCenter)
		
		# self.content_up_layout.addWidget(self.slider_pos_sub)
		
		self.content_down_layout.addWidget(self.lb_change_frame)
		self.content_down_layout.addWidget(self.slider_change_frame)
		self.content_down_layout.addWidget(self.lb_change_frame_number)
		
		# self.content_tools_layout.addWidget(QLabel(""),0,0,1,11)
		self.content_tools_layout.addWidget(QLabel(""), 0, 0, 1, 2)
		self.content_tools_layout.addWidget(self.btn_add_text, 0, 2, 1, 2)
		self.content_tools_layout.addWidget(self.btn_add_rectangle, 0, 4, 1, 2)
		self.content_tools_layout.addWidget(self.btn_add_media, 0, 6, 1, 2)
		self.content_tools_layout.addWidget(self.btn_add_rect_blur, 0, 8, 1, 2)
		self.content_tools_layout.addWidget(self.btn_save, 0, 10, 1, 2)
	
	def setup_connections (self):
		
		self.slider_change_frame.valueChanged.connect(self._sliderFrameValueChanged)
		# self.slider_pos_sub.valueChanged.connect(self._sliderPosSubValueChanged)
		self.manage_thread_pool.resultChanged.connect(self._resultChanged)
		
		self.btn_add_text.clicked.connect(self._addText)
		self.btn_add_rectangle.clicked.connect(self._addRectangle)
		self.btn_add_media.clicked.connect(self._addMedia)
		self.btn_add_rect_blur.clicked.connect(self._addRectBlur)
		
		self.btn_save.clicked.connect(self._saveDB)
	
	def loadData (self, configCurrent):
		
		self.configCurrent = configCurrent
		self.viewer.loadDataConfigCurrent(configCurrent, self.manage_thread_pool)
		if self.viewer.hasPhoto() is True:
			self.loadSubText()
	
	# try:
	# 	self.btn_add_rect_blur.set_active(False)
	# except:
	# 	pass
	# @decorator_try_except_class
	def _saveDB (self):
		
		if len(self.viewer.layers) > 0:
			list_items = {"layers": [list(layer.values())[0].itemToVariant() for layer in self.viewer.layers]}
			# if self.viewer._rectblur_area is not None:
			# list_items.insert(len(list_items), self.viewer._rectblur_area.itemToVariant())
			list_items['rect_scene'] = {'height': self.viewer._scene.height(), 'width': self.viewer._scene.width()}
			# ghi cấu hình vào setting app
			# self.settings.setValue((str(self.configCurrent.id)), list_items)
			# self.btn_save.setDisabled(True)
			# print(self.viewer._scene.height())
			# print(self.viewer._scene.width())
			# print(list_items)
			list_cofig = getValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN)
			if list_cofig is None:
				list_cof = {str(self.configCurrent.id): list_items}
				setValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, list_cof)
				self.btn_save.setDisabled(True)
			else:
				list_cofig[str(self.configCurrent.id)] = list_items
				
				setValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, list_cofig)
				
				self.btn_save.setDisabled(True)
		else:
			list_cofig = getValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN)
			if list_cofig is None:
				list_cof = {str(self.configCurrent.id): {}}
				setValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, list_cof)
				self.btn_save.setDisabled(True)
			else:
				list_cofig[str(self.configCurrent.id)] = {}
				
				setValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, list_cofig)
				
				self.btn_save.setDisabled(True)
	
	# @decorator_try_except_class
	def _addText (self):
		value = {
			"x": 100,
			"y": 100,
			"color_text": '#ff0000',
			"opacity_text": 100,
			"them_stroke": False,
			"color_stroke": '',
			"do_day_stroke": 1,
			"opacity_stroke": 100,
			"font_size": 68,
			"font_family": '',
			"text": '',
			"text_run": False,
			"speed_text": 15,
		}
		dialog_settings = PyDialogGraphicText(self.viewer.list_fonts)
		
		dialog_settings.loadData(value)
		if dialog_settings.exec():
			new_value = dialog_settings.getValue()
			self.viewer.addText(new_value)
	
	# print(new_value)
	
	# @decorator_try_except_class
	def _addRectangle (self):
		
		self.viewer.addRectangle()
	
	# @decorator_try_except_class
	def _addMedia (self):
		file_name, _ = QFileDialog.getOpenFileName(self, caption='Chọn file hìnhdạ',
			dir=(self.app_path), filter='File Ảnh (*.png *.jpg *jpeg)')
		self.viewer.addImage(QPixmap(file_name))
	
	# @decorator_try_except_class
	def _addRectBlur (self):
		# self.btn_add_rect_blur.set_active(not self.btn_add_rect_blur.is_active())
		if self.viewer.hasPhoto():
			self.viewer.addRectBlur()
			self.selectionAreaBlurChanged()
		else:
			PyMessageBox().show_warning("Cảnh báo", "Bạn chưa load video")
	
	def _sliderFrameValueChanged (self, value):
		# push ra ngoài chô ben groupbox timeline chuyển frame
		# print("_sliderFrameValueChanged", value)
		# print(value)
		self.sliderChangeFrameChanged.emit(value)
		
		self.lb_change_frame_number.setText(str(value))
		
		self.imageChangeFrame(value)
	
	def _resultChanged (self, id_worker, typeThread, result):
		''' nhận data từ các widget khác thông qua biến manage_thread_pool'''
		# print(typeThread)
		if typeThread == STATUS_BUTTON_SAVE_CONFIG_CHANGED:
			self.btn_save.setDisabled(result)
		
		if typeThread == LOAD_SUB_IN_TABLE_FINISHED:
			self.slider_change_frame.setValue(result + 1)
			self.slider_change_frame.setValue(1)
		
		if typeThread == ROW_SELECTION_CHANGED_TABLE_ADD_SUB:
			self.slider_change_frame.setValue(result)
		
		if typeThread == CHANGE_STYLE_SUB or typeThread == SPLIT_SUB_IN_TABLE_FINISHED or typeThread == TRANSLATE_SUB_FINISHED :  # emit ở lúc lôad giao diện config
			# self.data_conf = result
			if self.viewer.hasPhoto() is True:
				self.loadSubText()
		
		# if typeThread == TRANSLATE_SUB_FINISHED or SHOW_DATA_TABLE_TIMELINE:  # emit ở lúc tiến trình dịch thành công
		# 	if self.viewer.hasPhoto() is True:
		# 		self.loadSubText()
		
		if typeThread == UPDATE_TY_LE_KHUNG_HINH_VIDEO:
			if self.viewer.hasPhoto() is True:
				self.imageChangeFrame(self.slider_change_frame.value())
				self.loadSubText()
		
		if typeThread == SELECTION_AREA_BLUR_CHANGED:
			if hasattr(self, "path_video") and hasattr(self, "frame_current") and self.is_loaded is False:
				self.selectionAreaBlurChanged()
	
	
	# @decorator_try_except_class
	def selectionAreaBlurChanged (self):
		# try:
		if hasattr(self, "path_video") and hasattr(self, "frame_current") and self.is_loaded is False and len(self.viewer.list_blur) > 0:
			
			# self.viewer._scene.removeItem(self.viewer._frame_blur)
			
			pixmap = self.viewer._frame_video_main_sub.pixmap().copy()
			# print(pixmap.size())
			# print(self.viewer._frame_video_main_sub.x())
			# print(self.viewer._frame_video_main_sub.y())
			frame = self.pixmapToCV2(pixmap)
			for index_blur, blur in enumerate(self.viewer.list_blur):
				# print(blur)
				crop_x = int(blur.pos().x() - self.viewer._frame_video_main_sub.x())
				crop_y = int(blur.pos().y() - self.viewer._frame_video_main_sub.y())
				crop_width = int(blur.rect().width())
				crop_height = int(blur.rect().height())
				
				if (crop_width > 0 and crop_height > 0):
					# print(3)
					crop_x_end = crop_x + crop_width
					crop_y_end = crop_y + crop_height
					
					stroke_blur = 3  # viền màu xanh
					frame_crop = frame[crop_y + stroke_blur:crop_y_end - stroke_blur,
								 crop_x + stroke_blur:crop_x_end - stroke_blur]
					if len(frame_crop) == 0:  # mảng rỗng
						rect = self.viewer._scene.sceneRect()
						pixmap_ = QPixmap(int(crop_width), int(crop_height))
						#
						# painter = QPainter(pixmap_)
						# # Render the graphicsview onto the pixmap and save it out.
						# self.viewer._scene.render(painter, pixmap_.rect(), rect)
						# painter.end()
						pixmap_.fill(QColor(0, 0, 0, 0))
						self.viewer.setFrameBlur(pixmap_, stroke_blur, blur, index_blur)
					# frame_ = self.pixmapToCV2(pixmap_)
					# # cv2.imshow("Gaussian Smoothing", frame_)
					# # cv2.waitKey(0)
					# frame_crop_ = frame_[crop_y + stroke_blur:crop_y_end - stroke_blur,
					#              crop_x + stroke_blur:crop_x_end - stroke_blur]
					# image_blur = cv2.imencode('.png', frame_crop_)[1].tobytes()
					
					
					else:
						
						sigma = blur.sigma
						steps = blur.steps
						try:
							frame_blur = cv2.GaussianBlur(frame_crop, (0, 0), sigma * steps, cv2.BORDER_DEFAULT)
							
							image_blur = cv2.imencode('.png', frame_blur)[1].tobytes()
							# cv2.imshow("Gaussian Smoothing", frame_blur)
							# cv2.waitKey(0)
							pixmap_ = self.convertCvImage2QtImage(image_blur)
							self.viewer.setFrameBlur(pixmap_, stroke_blur, blur, index_blur)
						except Exception as e:
							return

	# except:
	# 	print("Không crop frame blur")
	
	def loadDataFrameVideo (self, file, sequences):
		# if hasattr(self,"path_video"):
		#     delattr(self,"path_video")
		#     delattr(self,"sequences")
		
		self.path_video = file
		self.sequences = sequences
		# print(6)
		if hasattr(self, "video_cap"):
			self.video_cap.release()
			delattr(self, "video_cap")
		
		self.video_cap = cv2.VideoCapture(file)
		if not self.video_cap.isOpened():
			raise IOError('Can not open video {}.'.format(file))
		# print(self.video_cap)
		
		self.video_new = True
		self.slider_change_frame.setMaximum(len(sequences))
		self.slider_change_frame.setEnabled(True)
	
	# if self.slider_change_frame.value() == 1:
	# 	self.slider_change_frame.setValue(2)
	# 	# self.slider_change_frame.setValue(1)
	# 	print(1)
	# else:
	# 	self.slider_change_frame.setValue(1)
	# 	self.slider_change_frame.setValue(2)
	# 	# self.slider_change_frame.setValue(1)
	# 	print(2)
	
	
	def pixmapToCV2 (self, pixmap):
		## Get the size of the current pixmap
		size = pixmap.size()
		h = size.width()
		w = size.height()
		
		## Get the QImage Item and convert it to a byte string
		qimg = pixmap.toImage()
		byte_str = qimg.bits().tobytes()
		
		## Using the np.frombuffer function to convert the byte string into an np array
		image_np = np.frombuffer(byte_str, dtype=np.uint8).reshape((w, h, 4))
		
		# im_path = JOIN_PATH(PATH_TEMP_MEDIA,"blur.png")
		#
		# cv2.imwrite(im_path, image_np)
		#
		# im_cv = cv2.imread(im_path)
		#
		# cv2.imshow("WindowNameHere", im_cv)
		# cv2.waitKey(0)
		return image_np
	
	def convertCvImage2QtImage (self, cv_img):
		pixmap = QPixmap()
		pixmap.loadFromData(cv_img)
		return pixmap
	
	# @decorator_try_except_class
	def imageChangeFrame (self, value_slider):
		""" Mô tả: Cập nhập ảnh sau mỗi lần thay đổi giá trị của Slider """
		# try:
		
		if hasattr(self, "path_video") is True:
			if os.path.isfile(self.path_video):
				# print("imageChangeFrame")
				# if self.is_loaded is False:
				data_sub = self.groupbox_timeline.getDataSub()
				# TODO: dolech, time, pos_ori, sub_origin, sub_translate, pos_trans
				
				# if len(data_sub) > 0:
				sub_current = data_sub[self.slider_change_frame.value() - 1]
				# sequence = self.sequences[value_slider - 1]
				# with VideoCapture(self.path_video) as video_cap:
				time_ = sub_current[ColumnNumber.column_image.value]
				# manage_thread.progressChanged.emit(UPDATE_VALUE_PROGRESS_GET_FRAME_IMAGE,id_worker,count + 1)
				start = time_.split(' --> ')[0]
				end = time_.split(' --> ')[1]
				start = self.strFloatTime(start)
				end = self.strFloatTime(end)
				(start, end) = map(float, (start, end))
				span = (end + start) / 2
				self.video_cap.set(cv2.CAP_PROP_POS_MSEC, span * 1000)
				(success, frame) = self.video_cap.read()
				# print(success)
				if success:
					frame_height = self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
					frame_width = self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
					self.frame_current = frame
					image_b = cv2.imencode('.png', frame)[1].tobytes()
					pixmap = self.convertCvImage2QtImage(image_b)
					
					self.viewer.setVideoMain(pixmap, frame_width, frame_height, self.video_new)
					self.loadSubText()
					# print(4444)
					self.selectionAreaBlurChanged()
				self.video_new = False
				self.is_loaded = False
	
	def strFloatTime (self, tempStr):
		""" Mô tả: Đưa về định dạng thời gian"""
		xx = tempStr.split(':')
		hour = int(xx[0])
		minute = int(xx[1])
		second = int(xx[2].split(',')[0])
		minsecond = int(xx[2].split(',')[1])
		allTime = hour * 60 * 60 + minute * 60 + second + minsecond / 1000
		return allTime
	
	# @decorator_try_except_class
	def loadSubText (self):
		""" Mô tả: Lựa chọn vị trí hiển thị sub """
		# try:
		
		if self.slider_change_frame.value() > 0:
			
			# data_sub_timeline = self.db_app.select_one_name(
			# 	"dataSubTimeline")
			
			data_sub = self.groupbox_timeline.getDataSub()
			# TODO: dolech, time, pos_ori, sub_origin, sub_translate, pos_trans
			
			if len(data_sub) > 0:
				sub_current = data_sub[self.slider_change_frame.value() - 1]
				# print(sub_current)
				data_conf: dict = json.loads(self.configCurrent.value)
				self.viewer.removeTextSubCurrent()
				# print('removeTextSubCurrent')
				
				if not data_conf['sub_hien_thi'] == "nosub":
					
					if data_conf['sub_hien_thi'] == "origin":
						self.viewer.addSubTextOrigin(
							sub_current[ColumnNumber.column_sub_text.value],
							sub_current[ColumnNumber.column_duaration.value])
					
					elif data_conf['sub_hien_thi'] == "translate":
						if not sub_current[ColumnNumber.column_sub_translate.value] == "":
							self.viewer.addSubTextTranslate(
								sub_current[ColumnNumber.column_sub_translate.value],
								sub_current[ColumnNumber.column_position_trans.value])
					
					else:
						self.viewer.addSubTextOrigin(
							sub_current[ColumnNumber.column_sub_text.value],
							sub_current[ColumnNumber.column_duaration.value])
						
						if not sub_current[ColumnNumber.column_sub_translate.value] == "":
							self.viewer.addSubTextTranslate(
								sub_current[ColumnNumber.column_sub_translate.value],
								sub_current[ColumnNumber.column_position_trans.value])

# except Exception as e:
#     try:
#         self.manage_thread_pool.errorChanged.emit(str(self.__class__), sys._getframe().f_back.f_code.co_name,
#                                                   str(e))
#     finally:
#         e = None
#         del e
