# -*- coding: utf-8 -*-
import json
import os

import cv2
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPixmap, QPainter
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QFrame, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
	QFileDialog

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import STATUS_BUTTON_SAVE_CONFIG_CHANGED, \
	ROW_SELECTION_CHANGED_TABLE_ADD_SUB, SELECTION_AREA_BLUR_CHANGED, \
	SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, LOAD_SUB_IN_TABLE_FINISHED, UPDATE_TY_LE_KHUNG_HINH_VIDEO, \
	CHANGE_HIEN_THI_SUB, CHANGE_STYLE_DIALOG_ADD_SUB, POSITION_ADD_SUB_CHANGED, \
	CENTER_POSITION_ADD_SUB, DELIMITER_CENTER_POS_SUB, ITEM_TABLE_TIMELINE_EDIT_SUB_CHANGED, \
	ITEM_TABLE_TIMELINE_ADD_SUB_CHANGED, CHANGE_BACKGROUND_MAIN_VIDEO, TypeBackgroundMainVideo
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
	
	def __init__ (self, manage_thread_pool: ManageThreadPool, groupbox_timeline):
		super().__init__()
		self.app_path = os.path.abspath(os.getcwd())
		self.frames_storage = os.path.join(self.app_path, 'frames/')
		
		# self.settings = QSettings(*SETTING_CONFIG)
		# self.settings = st.value(SETTING_APP_DATA)
		
		self.manage_thread_pool = manage_thread_pool
		self.groupbox_timeline = groupbox_timeline
		self.blur_sub = False
		self.video_new = False
		
		self.is_loaded = False
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
		self.groupbox = QGroupBox("VIDEO SCREEN")
		
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
		
		self.btn_save = QPushButton("Save ConFig")
		self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_save.setDisabled(True)
		# hbox_down
		# self.slider_change_frame = QSlider()
		# self.slider_change_frame.setEnabled(False)
		# self.slider_change_frame.setMinimum(1)
		
		# self.sliderListImg.setGeometry(QRect(90, 450, 571, 22))
		# self.slider_change_frame.setOrientation(Qt.Orientation.Horizontal)
		
		self.lb_change_frame_number = QLabel("")
	
	# self.lb_change_frame = QLabel("Dòng Sub")
	
	def modify_widgets (self):
		self.setStyleSheet(style_format)
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()

		self.content_up_layout = QVBoxLayout()
		self.content_down_layout = QHBoxLayout()
		
		self.content_layout = QVBoxLayout()
		# self.content_layout.setContentsMargins(0, 0, 0, 0)

		self.groupbox.setLayout(self.content_layout)
		
		self.content_tools_layout = QGridLayout()
		self.groupbox_tools.setLayout(self.content_tools_layout)
	
	def add_widgets_to_layouts (self):
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.bg_layout)
		
		self.bg_layout.addWidget(self.groupbox)

		self.content_layout.addWidget(QLabel(""))  # tạo khoảng cách với tiêu đề GroupBox
		self.content_layout.addLayout(self.content_up_layout)
		# self.content_layout.addLayout(self.content_down_layout)
		# self.vbox.addWidget(QLabel(""))
		self.content_up_layout.addWidget(self.groupbox_tools)
		self.content_up_layout.addWidget(self.viewer, 0, Qt.AlignmentFlag.AlignHCenter)
		
		# self.content_up_layout.addWidget(self.slider_pos_sub)
		
		# self.content_down_layout.addWidget(self.lb_change_frame)
		# self.content_down_layout.addWidget(self.slider_change_frame)
		# self.content_down_layout.addWidget(self.lb_change_frame_number)
		
		# self.content_tools_layout.addWidget(QLabel(""),0,0,1,11)
		self.content_tools_layout.addWidget(QLabel(""), 0, 0, 1, 2)
		self.content_tools_layout.addWidget(self.btn_add_text, 0, 2, 1, 2)
		self.content_tools_layout.addWidget(self.btn_add_rectangle, 0, 4, 1, 2)
		self.content_tools_layout.addWidget(self.btn_add_media, 0, 6, 1, 2)
		self.content_tools_layout.addWidget(self.btn_add_rect_blur, 0, 8, 1, 2)
		self.content_tools_layout.addWidget(self.btn_save, 0, 10, 1, 2)
	
	# self.content_tools_layout.addWidget(self.lb_change_frame_number, 0, 12, 1, 2)
	
	def setup_connections (self):
		
		# self.slider_change_frame.valueChanged.connect(self._sliderFrameValueChanged)
		# self.slider_pos_sub.valueChanged.connect(self._sliderPosSubValueChanged)
		self.manage_thread_pool.resultChanged.connect(self._resultChanged)
		
		self.btn_add_text.clicked.connect(self._addText)
		self.btn_add_rectangle.clicked.connect(self._addRectangle)
		self.btn_add_media.clicked.connect(self._addMedia)
		self.btn_add_rect_blur.clicked.connect(self._addRectBlur)
		
		self.btn_save.clicked.connect(self._saveDB)
	
	
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
			"font_size": 60,
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
		file_name, _ = QFileDialog.getOpenFileName(self, caption='Chọn file hình',
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
	
	
	# @decorator_try_except_class
	def selectionAreaBlurChanged (self):
		# try:
		if hasattr(self,'folder_name') and os.path.isdir(self.folder_name) and len(self.viewer.list_blur) > 0:
			
			# self.viewer._scene.removeItem(self.viewer._frame_blur)
			
			# pixmap = self.viewer._frame_video_main_sub.pixmap().copy()

			pixmap = QPixmap(self.viewer._scene.sceneRect().size().toSize())
			pixmap.fill(Qt.transparent)
			painter = QPainter(pixmap)
			self.viewer._scene.render(painter, pixmap.rect(), self.viewer._scene.sceneRect())
			painter.end()
			# print(pixmap.size())
			# print(self.viewer._frame_video_main_sub.x())
			# print(self.viewer._frame_video_main_sub.y())
			frame = self.pixmapToCV2(pixmap)

			for index_blur, blur in enumerate(self.viewer.list_blur):
				# print(blur)
				crop_x = int(blur.pos().x() - pixmap.rect().x())
				crop_y = int(blur.pos().y() - pixmap.rect().y())
				crop_width = int(blur.rect().width())
				crop_height = int(blur.rect().height())
				
				if (crop_width > 0 and crop_height > 0):
					# print(3)
					crop_x_end = crop_x + crop_width
					crop_y_end = crop_y + crop_height
					
					stroke_blur = 3  # viền màu xanh
					frame_crop = frame[crop_y + stroke_blur:crop_y_end - stroke_blur,
								 crop_x + stroke_blur:crop_x_end - stroke_blur]
					# cv2.imshow("Gaussian Smoothing", frame_crop)
					# cv2.waitKey(0)
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
	
	def loadFrameVideo (self, line_number):
		if hasattr(self,'folder_name') and os.path.isdir(self.folder_name):
				# self.sequence_current = self.groupbox_timeline.getDataRow(line_number - 1)
				cau_hinh_edit: dict = json.loads(self.fileSRTCurrent.value)
				cau_hinh: dict = json.loads(self.configCurrent.value)
				# item_current = cau_hinh_edit.get('data_table',[])[line_number-1]
				self.sequence_current = self.groupbox_timeline.getDataRow(line_number - 1)
				# print(self.sequence_current)
				image_curr =self.sequence_current[ColumnNumber.column_image.value]
				if os.path.exists(image_curr):
					pixmap = QPixmap(image_curr)
					frame_width = pixmap.width()
					frame_height = pixmap.height()

					if cau_hinh.get('bg_video_main') ==TypeBackgroundMainVideo.BG_IMAGE_ORIGIN.value:
						frame = cv2.imread(image_curr)

						frame_blur = cv2.GaussianBlur(frame, (0, 0), cau_hinh.get('sigma_bg_image_ori',15) * 1, cv2.BORDER_DEFAULT)

						image_blur = cv2.imencode('.png', frame_blur)[1].tobytes()
						# cv2.imshow("Gaussian Smoothing", frame_blur)
						# cv2.waitKey(0)
						pixmap_bur = self.convertCvImage2QtImage(image_blur)
					elif cau_hinh.get('bg_video_main') ==TypeBackgroundMainVideo.BG_IMAGE_NEW.value:
						image_new = cau_hinh.get('src_bg_co_dinh')
						if image_new == ''or  os.path.exists(image_new) is False:
							return PyMessageBox().show_warning("Lỗi", "File ảnh nền không tìm thấy")

						frame = cv2.imread(image_new)
						# print(cau_hinh.get('sigma_bg_image_new',15))
						frame_blur = cv2.GaussianBlur(frame, (0, 0), cau_hinh.get('sigma_bg_image_new',15) * 1, cv2.BORDER_DEFAULT)
						image_blur = cv2.imencode('.png', frame_blur)[1].tobytes()
						# cv2.imshow("Gaussian Smoothing", frame_blur)
						# cv2.waitKey(0)
						pixmap_bur = self.convertCvImage2QtImage(image_blur)
					else:
						pixmap_bur = QPixmap(frame_width, frame_height)
						pixmap_bur.fill(QColor(cau_hinh.get('bg_color_main','#000000')))

					self.viewer.setVideoMain(pixmap,pixmap_bur, frame_width, frame_height, self.video_new)
					self.loadSubText(self.sequence_current[ColumnNumber.column_sub_text.value], cau_hinh_edit.get('pos_add_sub'))
					self.selectionAreaBlurChanged()
		# AC, content_ = self.sequence_current

		# print(AC, Ratio, time_, content_)
		# print(AC, Ratio, time_, content_)
		# if hasattr(self, 'fileSRTCurrent') and hasattr(self,'video_cap') and self.video_cap and os.path.isfile(self.path_video) and time_ != '':
		# 	# if self.is_loaded is False: AC,Ratio, Time,  Text
		# 	# sequence = self.sequences[line_number - 1]
		# 	# with VideoCapture(self.path_video) as video_cap:
		# 		# print(time_)
		# 		# manage_thread.progressChanged.emit(UPDATE_VALUE_PROGRESS_GET_FRAME_IMAGE,id_worker,count + 1)
		# 	start = time_.split(' --> ')[0]
		# 	end = time_.split(' --> ')[1]
		# 	start = self.strFloatTime(start)
		# 	end = self.strFloatTime(end)
		# 	(start, end) = map(float, (start, end))
		# 	span = (end + start) / 2
		# 	self.video_cap.set(cv2.CAP_PROP_POS_MSEC, span * 1000)
		# 	frame_height = self.video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
		# 	frame_width = self.video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
		# 	(success, frame) = self.video_cap.read()
		# 	# frame_count = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
		# 	# print(success)
		# 	if success:
		# 		image_b = cv2.imencode('.png', frame)[1].tobytes()
		# 		pixmap = self.convertCvImage2QtImage(image_b)
		# 		self.frame_current = frame
		# 		# print(pixmap)
		# 		# self.lb_change_frame_number.setPixmap(pixmap)
		# 		# cv2.imshow("WindowNameHere", frame)
		# 		# cv2.waitKey(0)
		# 		cau_hinh_edit: dict = json.loads(self.fileSRTCurrent.value)
		#
		# 		self.viewer.setVideoMain(pixmap, frame_width, frame_height, self.video_new)
		# 		self.loadSubText(content_, cau_hinh_edit.get('pos_add_sub'))
		# 		self.selectionAreaBlurChanged()
		# 		# print(111)
		#
		# 	self.video_new = False
		#
		#
	
	# @decorator_try_except_class
	def loadSubText (self, content, position):
		""" Mô tả: Lựa chọn vị trí hiển thị sub """
		if hasattr(self, 'configCurrent') and content != '':
			data_conf: dict = json.loads(self.configCurrent.value)
			self.viewer.removeTextSubCurrent()
			# print('removeTextSubCurrent')
			
			if data_conf['hien_thi_sub']:
				self.viewer.addSubTextOrigin(content, position)
 
	def loadDataConfigCurrent (self, configCurrent):
		
		self.configCurrent = configCurrent
		self.viewer.loadDataConfigCurrent(configCurrent, self.manage_thread_pool)
	
	def loadFileSRTCurrent (self, fileSRTCurrent):
		
		self.fileSRTCurrent = fileSRTCurrent
		cau_hinh_edit: dict = json.loads(fileSRTCurrent.value)
		
		# path_video = cau_hinh_edit.get('video_file')
		self.folder_name = cau_hinh_edit.get('folder_name')

		if self.folder_name and os.path.isdir(self.folder_name):
			self.loadFrameVideo(1)
			self.viewer.isLoaded = False
		# if os.path.isfile(path_video):
		# 	self.path_video = path_video
		# 	if hasattr(self, 'video_cap'):
		# 		self.video_cap.release()
		# 		del self.video_cap
		#
		# 	self.video_cap = cv2.VideoCapture(path_video)
		#
		# 	self.loadFrameVideo(1)
		# 	self.is_loaded = True

	def _resultChanged (self, id_worker, typeThread, result):
		''' nhận data từ các widget khác thông qua biến manage_thread_pool'''
		# print(typeThread)
		# if typeThread == STATUS_BUTTON_SAVE_CONFIG_CHANGED:
		
		
		if typeThread == STATUS_BUTTON_SAVE_CONFIG_CHANGED:
			self.btn_save.setDisabled(result)
		
		if typeThread == LOAD_SUB_IN_TABLE_FINISHED:
			self.video_new = True
 
		
		if typeThread == CHANGE_BACKGROUND_MAIN_VIDEO:
			if hasattr(self, 'fileSRTCurrent'):
				self.loadFrameVideo(self.groupbox_timeline.main_table.currentIndex().row()+1)


		if typeThread == ROW_SELECTION_CHANGED_TABLE_ADD_SUB:
				self.loadFrameVideo(result)

		if typeThread == ITEM_TABLE_TIMELINE_ADD_SUB_CHANGED or typeThread == ITEM_TABLE_TIMELINE_EDIT_SUB_CHANGED or typeThread == CHANGE_HIEN_THI_SUB or typeThread == CHANGE_STYLE_DIALOG_ADD_SUB:
			if hasattr(self, 'fileSRTCurrent'):
				sequence_current = self.groupbox_timeline.getDataRowCurrent()
				AC, content_ = sequence_current
				cau_hinh_edit: dict = json.loads(self.fileSRTCurrent.value)
				self.loadSubText(content_, cau_hinh_edit.get('pos_add_sub'))
			# # self.data_conf = result
			# if hasattr(self,'sequence_current') and self.is_loaded:
			# 	AC, Ratio, time_, content_ = self.sequence_current
			# 	cau_hinh_edit: dict = json.loads(self.fileSRTCurrent.value)
			# 	self.loadSubText(content_, cau_hinh_edit.get('pos_add_sub'))
		
		if typeThread == UPDATE_TY_LE_KHUNG_HINH_VIDEO:
			if self.viewer.hasPhoto() is True:
				self.loadFrameVideo(1)

		if typeThread == SELECTION_AREA_BLUR_CHANGED:
			if hasattr(self,'folder_name') and os.path.isdir(self.folder_name) :
				self.selectionAreaBlurChanged()
	
		if typeThread == CENTER_POSITION_ADD_SUB:
			if hasattr(self, 'fileSRTCurrent'):
				x, y = result
				cau_hinh_edit = json.loads(self.fileSRTCurrent.value)
				pos_add_sub = f"{round(x, 2)}{DELIMITER_CENTER_POS_SUB}{round(y, 2)}"
				
				cau_hinh_edit['pos_add_sub'] = pos_add_sub
				self.fileSRTCurrent.value = json.dumps(cau_hinh_edit)
				self.fileSRTCurrent.save()
				
				AC, Ratio, time_, content_ = self.sequence_current
				
				self.loadSubText(content_, cau_hinh_edit.get('pos_add_sub'))
				
		if typeThread == POSITION_ADD_SUB_CHANGED:
			if hasattr(self, 'fileSRTCurrent'):
				x, y = result
				cau_hinh = json.loads(self.fileSRTCurrent.value)
				cau_hinh['pos_add_sub'] = f"{x}:{y}"
				self.fileSRTCurrent.value = json.dumps(cau_hinh)
				self.fileSRTCurrent.save()
				
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
		return image_np
	
	
	def convertCvImage2QtImage (self, cv_img):
		pixmap = QPixmap()
		pixmap.loadFromData(cv_img)
		return pixmap
	
	def strFloatTime (self, tempStr):
		""" Mô tả: Đưa về định dạng thời gian"""
		xx = tempStr.split(':')
		hour = int(xx[0])
		minute = int(xx[1])
		second = int(xx[2].split(',')[0])
		minsecond = int(xx[2].split(',')[1])
		allTime = hour * 60 * 60 + minute * 60 + second + minsecond / 1000
		return allTime
