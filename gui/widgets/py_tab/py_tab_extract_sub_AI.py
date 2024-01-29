# -*- coding: utf-8 -*-
import asyncio
import json
import os
import time
import uuid

import aiohttp
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout

# from flv_con.vopen import extract_sub_api python -m pip install -U --force-reinstall https://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@github.com/Nuitka/Nuitka-commercial/archive/main.zip
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	RESULT_EXTRACT_SUB, \
	ADD_TO_TABLE_EXTRACT_PROCESS, MODEL_WHISPER, MODE_WHISPER, TOOL_CODE_MAIN, USER_DATA, \
	EXTRACT_SUB_FINISHED, UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, STOP_EXTRACT_SUB_TABLE, SETTING_APP_DATA
from gui.helpers.get_data import  URL_API_BASE
from gui.helpers.handle_speech.extract_sub_voice import ExtractSubVoice
from ..py_checkbox import PyCheckBox
from ..py_combobox import PyComboBox
from ..py_dialogs.py_dialog_show_info import PyDialogShowInfo
from ..py_groupbox.groupbox_start_server_ffsub import check_cuda_version
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_messagebox.py_massagebox import PyMessageBox
from ..py_table_widget.table_process_extract import TableProcessExtractSUB
from ...configs.config_resource import ConfigResource
from ...helpers.ect import cr_pc, mh_ae, mh_ae_w
from ...helpers.func_helper import getValueSettings
from ...helpers.http_request.check_proxy import ProxyChecker


class PyTabExtractSubAI(QWidget):
	def __init__ (self, group_parent, manage_thread_pool, thread_pool_limit, manage_cmd, table_process: TableProcessExtractSUB, groupBox_start_server,settings):
		# st = QSettings(*SETTING_APP)
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		# self.group_parent = group_parent
		self.manage_thread_pool = manage_thread_pool
		self.thread_pool_limit = thread_pool_limit
		self.manage_cmd = manage_cmd
		self.table_process = table_process
		self.checker = ProxyChecker(manage_thread_pool)
		self.extract = ExtractSubVoice(self.manage_thread_pool, self.manage_cmd)
		
		self.groupBox_start_server = groupBox_start_server
		# settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		
		self.languages = settings.get("language_support").get("language_code")
		PORT_FFSUB = settings.get("port_ffsub")
		self.URL_WS_LOCAL =  f"ws://localhost:{PORT_FFSUB}"
		
		super().__init__()
		# PROPERTIES
		
		self.model_whisper = MODEL_WHISPER
		self.isLoad = True
		self.load_file_srt_finished = False
		self.list_row_number_stop = []
		
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		self.lb_language_origin = QLabel("Ngôn Ngữ Giọng Nói:")
		self.cb_languages_origin = PyComboBox()
		self.checkbox_use_gpu = PyCheckBox(value="use_gpu", text="Use GPU")
		
		self.lb_model = QLabel("Chọn Tệp Mẫu:")
		self.cb_model_whisper = PyComboBox()
		
		self.lb_mode = QLabel("Chế Độ:")
		self.cb_mode = PyComboBox()
		
		self.lb_notify = QLabel("Tip: Sử dụng tệp mẫu lớn sẽ có tốc độ chậm hơn nhưng độ chính xác cao hơn")
		self.btn_info_frame = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("info.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#2678ff",
			icon_color_hover="#4d8df6",
			icon_color_pressed="#6f9deb",
			app_parent=self,
			tooltip_text="Hướng dẫn"
		
		)
		
		self.btn_start = QPushButton("Start")
		self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.btn_restart = QPushButton("ReStart")
		self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
		
		text = "Bước 1. Chọn Mode: Nhanh hoặc chính xác"
		text += "\n\n"
		
		text += "Bước 2. Chọn Mô Hình Mẫu: "
		text += "\n\n"
		
		text += "    - Đây là dữ liệu để AI phân tích, mô hình càng lớn thì độ chính xác sẽ cao hơn nhưng tốc độ sẽ bị chậm đi và yêu cầu RAM cao hơn."
		text += "\n\n"
		
		text += "    - Lần chạy đầu tiên của từng mô hình sẽ tự động tải mô hình về ổ C yêu cầu dung lượng còn trống, lần sau sẽ không tải."
		text += "\n\n"
		text += "    - Mô hình Cực Lớn sẽ yêu cầu cấu hình máy tính rất cao và card màn hình xịn. Khuyên dùng mô hình Lớn mặc định"
		text += "\n\n"
		
		text += "Bước 3. Bấm START rồi ngồi uống ly cà phê đợi kết quả"
		text += "\n\n"
		text += "TIP: Nếu máy tính của bạn có card màn hình NVIDIA thì cần cài thêm CUDA để tăng tốc quá trình trích xuất và độ chính xác cao hơn"
		
		self.dialog_info = PyDialogShowInfo(text, 500)
	
	def modify_widgets (self):
		self.setDisabled(True)
		self.cb_languages_origin.addItems(self.languages.values())
		self.cb_languages_origin.setCurrentIndex(1)
		#
		self.cb_mode.addItems(list(MODE_WHISPER.values()))
		self.cb_model_whisper.addItems(list(self.model_whisper.values()))
		self.cb_model_whisper.setCurrentIndex(2)
	
	def create_layouts (self):
		self.content_layout = QVBoxLayout()
		self.content_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_status = QVBoxLayout()
		self.content_language_layout = QHBoxLayout()
		self.content_mode_layout = QHBoxLayout()
		
		self.progess_convert_layout = QHBoxLayout()
		self.content_btn_layout = QGridLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.setLayout(self.content_layout)
		
		self.content_layout.addWidget(QLabel(""), 5)
		self.content_layout.addLayout(self.content_language_layout, 55)
		self.content_layout.addLayout(self.content_status, 20)
		self.content_layout.addLayout(self.content_btn_layout, 20)
		
		self.content_language_layout.addWidget(self.lb_language_origin)
		self.content_language_layout.addWidget(self.cb_languages_origin)
		self.content_language_layout.addWidget(QLabel())
		self.content_language_layout.addWidget(self.lb_mode)
		self.content_language_layout.addWidget(self.cb_mode)
		self.content_language_layout.addWidget(QLabel())
		self.content_language_layout.addWidget(self.lb_model)
		self.content_language_layout.addWidget(self.cb_model_whisper)
		
		# self.content_mode_layout.addWidget(self.lb_mode, 20)
		# self.content_mode_layout.addWidget(self.cb_mode, 30)
		# self.content_mode_layout.addWidget(QLabel(), 50)
		# self.content_status.addLayout(self.content_mode_layout)
		self.content_status.addWidget(self.lb_notify)
		
		self.content_btn_layout.addWidget(QLabel(), 0, 0, 1, 3)
		self.content_btn_layout.addWidget(self.btn_start, 0, 3, 1, 3)
		self.content_btn_layout.addWidget(self.btn_restart, 0, 6, 1, 3)
		
		self.content_btn_layout.addWidget(self.btn_info_frame, 0, 9, 1, 3, alignment=Qt.AlignmentFlag.AlignRight)
	
	def setup_connections (self):
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.btn_info_frame.clicked.connect(self._click_info)
		
		# self.manage_thread_pool.progressChanged.connect(self._progressChanged)
		# self.checker.finishedCheckLiveProxySignal.connect(self._finishedCheckLiveProxySignal)
		
		self.btn_start.clicked.connect(self.clickStart)
		self.btn_restart.clicked.connect(self.clickReStart)
	
	def clickReStart (self):
		self.btn_start.setDisabled(False)
	
	def _click_info (self):
		self.dialog_info.exec()
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		
		self.isLoad = False
	
	def loadFileInput (self, path):
		self.path_input = path
		self.btn_start.setDisabled(False)

	# @decorator_try_except_class
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
			row_number = self.table_process.main_table.rowCount()
			
			source_path = self.path_input
			mode_whisper = list(MODE_WHISPER.keys())[self.cb_mode.currentIndex()]
			model_whisper = list(MODEL_WHISPER.keys())[self.cb_model_whisper.currentIndex()]
			language_origin = list(self.languages.keys())[self.cb_languages_origin.currentIndex()]
			language_origin = language_origin[:2]
			
			data_item_table = []
			data_item_table.append(source_path)
			data_item_table.append(language_origin)
			data_item_table.append("Trích xuất từ voice AI")
			
			self.manage_thread_pool.resultChanged.emit(str(row_number), ADD_TO_TABLE_EXTRACT_PROCESS, data_item_table)
	 
			self._extractStartThread(source_path, mode_whisper, model_whisper, row_number, language_origin)
		else:
			return PyMessageBox().show_warning("Cảnh báo", "Bạn chưa load video lên !")
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == STOP_EXTRACT_SUB_TABLE:
			self.list_row_number_stop.append(result)
 
	
	def _extractStartThread (self, source_path, mode_whisper, model_whisper, row_number, language_origin):
		# try:
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Đang đợi...")
		user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		
		self.thread_pool_limit.start(self._funcExtractThreadAI, "_extractStartThreadAI" + uuid.uuid4().__str__(), RESULT_EXTRACT_SUB, limit_thread=True, pc=cr_pc(), token=
		user_data[
			'token'], row_number=row_number, source_path=source_path, model_whisper=model_whisper, mode_whisper=mode_whisper, language_origin=language_origin)
	
	def _funcExtractThreadAI (self, **kwargs):
		# try:
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		row_number = kwargs["row_number"]
		language_origin = kwargs["language_origin"]
		source_path = kwargs["source_path"]
		model_whisper = kwargs["model_whisper"]
		mode_whisper = kwargs["mode_whisper"]
		token = kwargs["token"]
		p = kwargs["pc"]
		
		if row_number in self.list_row_number_stop:
			thread_pool.finishSingleThread(id_worker, limit_thread=True)
			return
			# raise ValueError("Stop")
		# if "extract" in kwargs.keys():
		
		# self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
		# 	"Bắt đầu extract sub...")
		payload = json.dumps({
			"id": row_number,
			"a": URL_API_BASE,
			"p": p,
			"t": token,
			"l": language_origin,
			"v": source_path,
			"m": model_whisper,
			"cuda": self.groupBox_start_server.checkbox_use_gpu.isChecked(),
			# "md": 'f',
			"cp": mh_ae_w({"cp": cr_pc("tool_khac"), "tc": TOOL_CODE_MAIN, 't': int(float(time.time()))}),
			"md": mode_whisper,
			
		})
		
		# extract_sub_api(payload, self.manage_thread_pool)
		
		async def ws ():
			async with aiohttp.ClientSession(
					raise_for_status=True
			) as session, session.ws_connect(
				# f"ws://localhost:8686/ws/ocr",
				f"{self.URL_WS_LOCAL}/ws/ai",
				compress=15,
				autoclose=True,

			) as websocket:
				# print(encrypt(payload))
				await websocket.send_json(mh_ae_w(payload))
				async for received in websocket:
					
					if row_number in self.list_row_number_stop:
						await websocket.close()
						thread_pool.finishSingleThread(id_worker, limit_thread=True)
						return
					
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

						if data.get("type") == "error":
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
		
		if done:
			base, ext = os.path.splitext(source_path)
			subtitle_file = "{base}.{format}".format(base=base, format='srt')
			if os.path.isfile(subtitle_file):
				# if language_origin in LANGUAGES_FORMAT:
				# 	reformat(subtitle_file)
				
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
					"Hoàn Thành")
				
				self.manage_thread_pool.resultChanged.emit(str(row_number), EXTRACT_SUB_FINISHED, subtitle_file)
			else:
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
					"Lỗi trích xuất")
			
			thread_pool.finishSingleThread(id_worker, limit_thread=True)
			
		return row_number if done is True else None
