# -*- coding: utf-8 -*-
import asyncio
import json
import os
import time
import uuid

import aiohttp
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel, QGridLayout, QGroupBox, QCheckBox, \
	QSlider

# from flv_con.paddle_ocr.api import ocr_api
from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import ADD_TO_TABLE_EXTRACT_PROCESS, \
	UPDATE_STATUS_TABLE_EXTRACT_PROCESS, RESULT_EXTRACT_SUB, DETECT_SUB_DEMO, SELECTION_AREA_SUB_CHANGED, \
	RUN_CMD_DETECT_SUB_DEMO, LANGUAGES_FORMAT, MODE_DETECT, LOAD_FILE_EXTRACT_FINISHED, TOOL_CODE_MAIN, USER_DATA, \
	UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, \
	START_SERVER_FFSUB_FINISHED, APP_PATH, EXTRACT_SUB_FINISHED, STOP_EXTRACT_SUB_TABLE, SETTING_APP_DATA
from gui.helpers.custom_logger import decorator_try_except_class
from gui.helpers.ect import cr_pc, mh_ae, mh_ae_w
from gui.helpers.func_helper import getValueSettings, reformat
from gui.helpers.get_data import    URL_API_BASE
from gui.helpers.handle_speech.detect_sub_voice import DetectSubImage
from gui.widgets.py_combobox import PyComboBox
from gui.widgets.py_dialogs.py_dialog_show_info import PyDialogShowInfo
from gui.widgets.py_groupbox.groupbox_start_server_ffsub import check_cuda_version
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_spinner.spinner import WaitingSpinner
from gui.widgets.py_table_widget.table_process_extract import TableProcessExtractSUB


class TabConTachSubTuHinhAnh(QWidget):
	def __init__ (self, gbox_preview, manage_thread_pool, thread_pool_limit, manage_cmd,
				  table_process: TableProcessExtractSUB,
				  groupBox_start_server, settings):
		super().__init__()

		
		# st = QSettings(*SETTING_APP)
		# self.user_data = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		
		self.manage_thread_pool = manage_thread_pool
		self.thread_pool_limit = thread_pool_limit
		self.manage_cmd = manage_cmd
		self.gbox_preview = gbox_preview
		self.groupBox_start_server = groupBox_start_server
		# self.manage_cmd.resultSignal.connect(self._resultCMDSignal)
		
		self.detect = DetectSubImage(self.manage_thread_pool, self.manage_cmd)
		
		self.table_process = table_process
		self.viewer = gbox_preview.viewer
		# self.db_app = db_appself.table_process
		
		# PROPERTIES
		# settings =getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')

		self.languages = settings.get("language_support").get("language_detect")
		PORT_FFSUB = settings.get("port_ffsub")
		self.URL_WS_LOCAL =  f"ws://localhost:{PORT_FFSUB}"
		self.list_frame_skip = [str(i) for i in range(1, 31)]
		
		self.isLoad = True
		self.list_row_number_stop = []
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	def create_widgets (self):
		self.groupbox_server = QGroupBox("Tách Sub Chữ Trong Video")
		
		self.lb_language_origin = QLabel("Ngôn Ngữ Sub:")
		self.cb_languages_origin = PyComboBox()
		
		self.lb_mode = QLabel("Chế Độ:")
		self.cb_mode = PyComboBox()
		
		# self.lb_frame_skip = QLabel("Frame Skip:")
		self.checkbox_use_sharpen = QCheckBox("Làm Nét Mẫu:")
		
		self.btn_info_frame = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("info.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#2678ff",
			icon_color_hover="#4d8df6",
			icon_color_pressed="#6f9deb",
			app_parent=self.groupbox_server,
			tooltip_text="Hướng dẫn"
		
		)
		
		self.lb_brightness = QLabel("Chỉnh sáng:")
		self.slider_brightness = QSlider()
		self.slider_brightness.setOrientation(Qt.Orientation.Horizontal)
		self.slider_brightness.setRange(0, 255)
		self.lb_brightness_number = QLabel(str(self.slider_brightness.value()))
		
		self.lb_contrast = QLabel("Chỉnh tương phản:")
		self.slider_contrast = QSlider()
		self.slider_contrast.setOrientation(Qt.Orientation.Horizontal)
		self.slider_contrast.setRange(0, 300)
		self.lb_contrast_number = QLabel(str(self.slider_contrast.value()))
		
		self.lb_confidence = QLabel("Lọc từ chính xác:")
		self.slider_confidence = QSlider()
		self.slider_confidence.setOrientation(Qt.Orientation.Horizontal)
		self.slider_confidence.setRange(30, 100)
		self.slider_confidence.setValue(65)
		
		self.lb_confidence_number = QLabel(str(self.slider_confidence.value()) + "%")
		
		text = "Bước 1. Load video lên bằng cách kéo video vào hoặc  bấm vào nút có hình thư mục màu vàng"
		text += "\n\n"
		
		text += "Bước 2. Căn chỉnh khung viền màu xanh sao cho nằm trong vùng chứa phụ và kéo thanh trượt để chuyển qua các frame khác xem có bị che mất phần phụ đề không"
		text += "\n\n"
		
		text += "Bước 3. Chọn Ngôn Ngữ của sub xuất hiện trong video"
		text += "\n\n"
		#
		text += "Bước 4. Chọn chế độ NHANH hoặc CHÍNH XÁC. Nếu có GPU thì nên chọn CHÍNH XÁC để cho kết quả tốt nhất. Nếu dùng CPU thì nên chọn chế độ NHANH để cải thiện tốc độ"
		text += "\n\n"
		
		# text += "Bước 5. Nếu chất lượng hình ảnh video thấp hoặc hình ảnh sub mờ hoặc không có độ tương phản cao thì bạn CLICK chọn vào 'Làm Nét Mẫu', điều này sẽ làm cho quá trình tách sub sẽ lâu hơn"
		# text += "\n\n"
		
		text += "Bước 5. Kéo thanh trượt để chỉnh sáng và độ tương phản sao cho vùng chứa phụ đề rõ nét và nổi bật để giúp cho AI phát hiện chữ chính xác hơn"
		text += "\n\n"
		
		text += "Bước 6. 'Lọc từ chính xác' đối với các ngôn ngữ Tiếng Trung, Hàn Quốc, Nhật Bản thì để 50-70 . Các ngôn ngữ có dấu khoảng trắng thì đặt giá trị cao trên 80. Nếu thấy nhiều từ dư thừa thì tăng tỷ lệ lên, hoặc ít từ quá thì giảm tỷ lệ xuống"
		text += "\n\n"
		
		text += "Bước 7. Bấm START rồi ngồi uống ly cà phê đợi kết quả"
		text += "\n\n"
		text += "TIP: Nếu máy tính của bạn có card màn hình NVIDIA thì cần cài thêm CUDA để tăng tốc quá trình trích xuất và độ chính xác cao hơn"
		
		self.dialog_info = PyDialogShowInfo(text, 700)
		
		self.btn_start = QPushButton("Start")
		self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_get_demo = QPushButton("Tách Thử")
		self.btn_get_demo.setCursor(Qt.CursorShape.PointingHandCursor)
		self.lb_status = QLabel()
		
		self.btn_restart = QPushButton("ReStart")
		self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.dialog_demo = PyDialogShowInfo("", 100, "Chữ được trích xuất")
	
	
	def modify_widgets (self):
		self.cb_languages_origin.addItems(self.languages.values())
		self.cb_languages_origin.setCurrentIndex(0)
		
		self.cb_mode.addItems(MODE_DETECT.values())
		
		self.groupbox_server.setDisabled(True)
		self.slider_contrast.setValue(100)
		self.slider_brightness.setValue(0)
	
	def create_layouts (self):
		self.bg_layout = QVBoxLayout()
		
		self.content_layout = QVBoxLayout()
		
		self.content_language_layout = QGridLayout()
		
		self.content_btn_layout = QGridLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox_server)
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.bg_layout)
		self.groupbox_server.setLayout(self.content_layout)
		
		self.content_layout.addWidget(QLabel(""))
		self.content_layout.addLayout(self.content_language_layout)
		self.content_layout.addWidget(QLabel(""))
		
		self.content_layout.addLayout(self.content_btn_layout)
		
		self.content_language_layout.addWidget(self.lb_language_origin, 0, 0, 1, 1)
		self.content_language_layout.addWidget(self.cb_languages_origin, 0, 2, 1, 3)
		self.content_language_layout.addWidget(QLabel(""), 0, 5)
		
		self.content_language_layout.addWidget(self.lb_mode, 0, 6)
		self.content_language_layout.addWidget(self.cb_mode, 0, 7, 1, 2)
		self.content_language_layout.addWidget(QLabel(""), 0, 9, 1, 3)
		# self.content_language_layout.addWidget(self.checkbox_use_sharpen, 0, 10, 1, 3)
		# self.content_language_layout.addWidget(self.btn_info_frame, 0, 11)
		
		self.content_language_layout.addWidget(QLabel(""), 1, 0, 1, 11)
		
		self.content_language_layout.addWidget(self.lb_brightness, 2, 0)
		self.content_language_layout.addWidget(self.slider_brightness, 2, 1, 1, 2)
		self.content_language_layout.addWidget(self.lb_brightness_number, 2, 3)
		
		self.content_language_layout.addWidget(self.lb_contrast, 2, 4)
		self.content_language_layout.addWidget(self.slider_contrast, 2, 5, 1, 2)
		self.content_language_layout.addWidget(self.lb_contrast_number, 2, 7)
		
		self.content_language_layout.addWidget(self.lb_confidence, 2, 8)
		self.content_language_layout.addWidget(self.slider_confidence, 2, 9, 1, 2)
		self.content_language_layout.addWidget(self.lb_confidence_number, 2, 11)
		
		self.content_btn_layout.addWidget(self.lb_status, 0, 0, 1, 3)
		self.content_btn_layout.addWidget(self.btn_start, 0, 3, 1, 2)
		self.content_btn_layout.addWidget(self.btn_get_demo, 0, 5, 1, 2)
		self.content_btn_layout.addWidget(self.btn_restart, 0, 7, 1, 2)
		self.content_btn_layout.addWidget(self.btn_info_frame, 0, 9, 1, 3, alignment=Qt.AlignmentFlag.AlignRight)
	
	def loadPathVideo (self, path):
		self.path_input = path
	
	def setup_connections (self):
		self.btn_info_frame.clicked.connect(self._click_info)
		self.slider_brightness.valueChanged.connect(self._sliderBrightnessChanged)
		self.slider_contrast.valueChanged.connect(self._sliderContrastChanged)
		self.slider_confidence.valueChanged.connect(self._sliderConfidenceChanged)
		self.cb_languages_origin.currentIndexChanged.connect(self.language_changed)
		self.btn_start.clicked.connect(self.clickStart)
		self.btn_get_demo.clicked.connect(self.clickDemo)
		self.btn_restart.clicked.connect(self.clickReStart)
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.thread_pool_limit.resultChanged.connect(self._resultThread)
	
	def clickReStart (self):
		self.btn_start.setDisabled(False)
		self.btn_get_demo.setDisabled(False)
	
	@decorator_try_except_class
	def clickDemo (self):
		if hasattr(self, 'path_input'):
			if self.groupBox_start_server.isRuning is False:
				return PyMessageBox().show_warning("Cảnh báo", "Bạn chưa START SERVER !")
			
			self.lb_status.setText("Đang Trích Xuất Chữ... ")
			self.btn_get_demo.setDisabled(True)
			
			video_path = self.path_input
			frame_number = self.gbox_preview.slider_change_frame.value()
			use_sharpen = self.checkbox_use_sharpen.isChecked()  # làm combox de tuy chọn
			
			brightness_value = self.slider_brightness.value()
			contrast_value = self.slider_contrast.value()
			conf_threshold = self.slider_confidence.value()
			language_origin = list(self.languages.keys())[self.cb_languages_origin.currentIndex()]
			crop_x = int(self.viewer.rect_selection_sub_area.pos().x())
			crop_y = int(self.viewer.rect_selection_sub_area.pos().y())
			crop_width = int(self.viewer.rect_selection_sub_area.rect().width())
			crop_height = int(self.viewer.rect_selection_sub_area.rect().height())
			row_number = self.table_process.main_table.rowCount()
			mode = self.cb_mode.currentIndex()
			self.manage_thread_pool.start(self._funcDetectThread, "_detectDemo" + uuid.uuid4().__str__(),
				DETECT_SUB_DEMO, detect=self.detect, row_number=row_number,
				video_path=video_path, mode=mode, frame_number=frame_number, language_origin=language_origin,
				brightness_value=brightness_value, contrast_value=contrast_value,
				conf_threshold=conf_threshold, use_sharpen=use_sharpen,
				crop_x=crop_x, crop_y=crop_y, crop_width=crop_width, crop_height=crop_height, pc=cr_pc(), token=
				self.user_data[
					'token'])
			self.spiner = WaitingSpinner(
				self.groupbox_server,
				roundness=100.0,
				# opacity=24.36,
				fade=15.719999999999999,
				radius=20,
				lines=12,
				line_length=22,
				line_width=12,
				speed=1.1,
				color=QColor(85, 255, 127),
				modality=Qt.ApplicationModal,
				disable_parent_when_spinning=True
			)
			self.spiner.start()
		
		else:
			return PyMessageBox().show_warning("Cảnh báo", "Bạn chưa load video lên !")
	
	# else:
	# 	PyMessageBox().show_error("Lỗi", "Tool Tách Sub Chưa Được Cài Đặt, Vui Lòng Liên Hệ Admin")
	
	def clickStart (self):
		if hasattr(self, 'path_input'):
			if self.groupBox_start_server.isRuning is False:
				return PyMessageBox().show_warning("Cảnh báo", "Bạn chưa START SERVER !")
			cuda_ok, version_card = check_cuda_version()
			if cuda_ok and not self.groupBox_start_server.checkbox_use_gpu.isChecked():
				is_ok = PyMessageBox().show_question("Thông báo", "Bạn chưa bật GPU, bạn có muốn tiếp tục tách sub bằng CPU")
				if not is_ok:
					return
			
			self.btn_start.setDisabled(True)
			self.btn_get_demo.setDisabled(True)
			row_number = self.table_process.main_table.rowCount()
			
			video_path = self.path_input
			use_sharpen = self.checkbox_use_sharpen.isChecked()
			mode = self.cb_mode.currentIndex()
			
			brightness_value = self.slider_brightness.value()
			contrast_value = self.slider_contrast.value()
			conf_threshold = self.slider_confidence.value()
			language_origin = list(self.languages.keys())[self.cb_languages_origin.currentIndex()]
			crop_x = int(self.viewer.rect_selection_sub_area.pos().x())
			crop_y = int(self.viewer.rect_selection_sub_area.pos().y())
			crop_width = int(self.viewer.rect_selection_sub_area.rect().width())
			crop_height = int(self.viewer.rect_selection_sub_area.rect().height())
			#
			# base, ext = os.path.splitext(video_path)
			# srt_path = "{base}.{format}".format(base=base, format='srt')
			data_item_table = []
			data_item_table.append(video_path)
			data_item_table.append(language_origin)
			data_item_table.append("Trích xuất từ hình ảnh")
			self.manage_thread_pool.resultChanged.emit(str(row_number), ADD_TO_TABLE_EXTRACT_PROCESS,
				data_item_table)
			
			base, ext = os.path.splitext(video_path)
			subtitle_file = "{base}.{format}".format(base=base, format='srt')
			if os.path.isfile(subtitle_file):
				os.remove(subtitle_file)
			
			self._detectStartThread(row_number, video_path, language_origin, brightness_value,
				contrast_value, conf_threshold, use_sharpen, mode,
				crop_x, crop_y, crop_width, crop_height)
		else:
			return PyMessageBox().show_warning("Cảnh báo", "Bạn chưa load video lên !")
	
	# else:
	# 	return PyMessageBox().show_error("Lỗi", "Tool Tách Sub Chưa Được Cài Đặt, Vui Lòng Liên Hệ Admin")
	
	def _detectStartThread (self, row_number, video_path, language_origin, brightness_value, contrast_value,
							conf_threshold, use_sharpen, mode,
							crop_x, crop_y, crop_width, crop_height):
		# try:
		
		# detect = DetectSubImage(self.manage_thread_pool)
		
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Đang đợi ...")
		self.thread_pool_limit.start(self._funcDetectThread, "_detectStartThread" + uuid.uuid4().__str__(),
			RESULT_EXTRACT_SUB, limit_thread=True, row_number=row_number, detect=self.detect,
			
			video_path=video_path, language_origin=language_origin,
			brightness_value=brightness_value, contrast_value=contrast_value,
			conf_threshold=conf_threshold, use_sharpen=use_sharpen, mode=mode,
			crop_x=crop_x, crop_y=crop_y, crop_width=crop_width, crop_height=crop_height, pc=cr_pc(), token=
			self.user_data[
				'token'])
	
	def _funcDetectThread (self, **kwargs):
		# try:
		
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		
		row_number = kwargs["row_number"]
		mode = kwargs.get("mode")
		source_path = kwargs["video_path"]
		language_origin = kwargs["language_origin"]
		brightness_value = kwargs["brightness_value"]
		contrast_value = kwargs["contrast_value"]
		conf_threshold = kwargs["conf_threshold"]
		# use_sharpen = kwargs["use_sharpen"]
		crop_x = kwargs["crop_x"]
		crop_y = kwargs["crop_y"]
		crop_width = kwargs["crop_width"]
		crop_height = kwargs["crop_height"]
		p = kwargs["pc"]
		token = kwargs["token"]
		frame_number = kwargs.get("frame_number")
		data_pl = {
			"id": row_number,
			"a": URL_API_BASE,
			"p": p,
			"t": token,
			"l": language_origin,
			"v": source_path,
			"b": brightness_value,
			"m": mode,
			# "dm": 1005,
			"cuda": self.groupBox_start_server.checkbox_use_gpu.isChecked(),
			"cp": mh_ae_w({"cp": cr_pc("tool_khac"), "tc": TOOL_CODE_MAIN, 't': int(float(time.time()))}),
			"c": contrast_value,
			"cf": conf_threshold,
			"s": [
				crop_x,
				crop_y,
				crop_width,
				crop_height
			],
			
			
		}
		if frame_number:
			data_pl.update({"dm": frame_number})
		
		payload = json.dumps(data_pl)
		
		if row_number in self.list_row_number_stop:
			thread_pool.finishSingleThread(id_worker, limit_thread=True)
			return
			# raise ValueError("Stop")
		# ocr_api(data_pl, APP_PATH,self.manage_thread_pool)
		print("Start")
		
		async def ws ():
			async with aiohttp.ClientSession(
					raise_for_status=True
			) as session, session.ws_connect(
				f"{self.URL_WS_LOCAL}/ws/ocr",
				compress=15,
				autoclose=True,
			
			) as websocket:
				await websocket.send_json(mh_ae_w(payload))
				async for received in websocket:
					if row_number in self.list_row_number_stop:
						await websocket.close()
						thread_pool.finishSingleThread(id_worker, limit_thread=True)
						return
						# raise ValueError("Stop")
					
					if received.type == aiohttp.WSMsgType.TEXT:
						data = json.loads(received.data)
						# print(data)
						
						if data.get("type") == "update_status":
							self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
								data.get("message"))
						
						if data.get("type") == "start":
							self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS,
								str(row_number), data.get("message"))
						
						if data.get("type") == "update_progress":
							self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS,
								str(row_number), data.get("message"))
						
						if data.get("type") == "success" and data.get("id") == "demo_ocr":
							self.manage_thread_pool.resultChanged.emit(str(row_number), RUN_CMD_DETECT_SUB_DEMO, (
								language_origin, data.get("message")))
						
						if data.get("type") == "error":
							print(data.get("message"))
							self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
								data.get("message"))
							return False
					# print(data)
					
					
					elif received.type == aiohttp.WSMsgType.ERROR:
						print(
							"WSMsgType.ERROR", received.data if received.data else "Unknown error"
						)
						await websocket.close()
						return False
			return True
		
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
		# loop = asyncio.get_event_loop()
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		done = loop.run_until_complete(ws())
		loop.close()
		if done and frame_number is None:
			base, ext = os.path.splitext(source_path)
			subtitle_file = "{base}.{format}".format(base=base, format='srt')
			if os.path.isfile(subtitle_file):
				if language_origin in LANGUAGES_FORMAT:
					reformat(subtitle_file)
				
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
					"Hoàn Thành")
				
				self.manage_thread_pool.resultChanged.emit(str(row_number), EXTRACT_SUB_FINISHED, subtitle_file)
			else:
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
					"Lỗi trích xuất")
		
		thread_pool.finishSingleThread(id_worker, limit_thread=True)
	
	# return row_number if done is True else None
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == STOP_EXTRACT_SUB_TABLE:
			self.list_row_number_stop.append(result)
		
		if id_thread == START_SERVER_FFSUB_FINISHED:  # start server finish
			self.groupbox_server.setDisabled(False)
		
		if id_thread == LOAD_FILE_EXTRACT_FINISHED:  # khi load file xong truyền biến file vào các tab
			self.btn_get_demo.setDisabled(False)
			self.btn_start.setDisabled(False)
			self.loadPathVideo(result)
		
		if id_thread == RUN_CMD_DETECT_SUB_DEMO:
			lang, text = result
			# print(lang, text)
			if lang in LANGUAGES_FORMAT:
				text = self.reformat_text(text)
			self.spiner.stop()
			self.btn_get_demo.setDisabled(False)
			
			self.lb_status.setText("Ok")
			self.dialog_demo.textarea_info.clear()
			self.dialog_demo.textarea_info.appendPlainText(text)
			self.dialog_demo.exec()
			self.lb_status.setText("")
	
	def reformat_text (self, text):
		return text
	
	def _sliderBrightnessChanged (self, value):
		self.lb_brightness_number.setText(str(value))
		self.gbox_preview.brightness = value
		self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_SUB_CHANGED,
			SELECTION_AREA_SUB_CHANGED,
			"")
	
	def _sliderConfidenceChanged (self, value):
		self.lb_confidence_number.setText(str(value) + "%")
	
	def language_changed (self):
		
		language_origin = list(self.languages.keys())[self.cb_languages_origin.currentIndex()]
		if language_origin in ['ch', 'chinese_cht', 'japan']:
			self.slider_confidence.setValue(65)
		else:
			self.slider_confidence.setValue(85)
	
	def _sliderContrastChanged (self, value):
		self.lb_contrast_number.setText(str(value))
		self.gbox_preview.contrast = value
		
		self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_SUB_CHANGED,
			SELECTION_AREA_SUB_CHANGED,
			"")
	
	def _click_info (self):
		self.dialog_info.exec()
	
	def loadData (self, configCurrent):
		# self.manage_thread_pool = manage_thread_pool
		
		self.configCurrent = configCurrent
		cau_hinh = json.loads(configCurrent.value)
		
		self.isLoad = False
	
	def mouseDoubleClickEvent (self, e):
		
		if hasattr(self, "spiner") and self.spiner.is_spinning:
			self.spiner.stop()
			print("stop")
