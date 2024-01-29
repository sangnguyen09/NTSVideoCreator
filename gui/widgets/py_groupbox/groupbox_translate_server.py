# -*- coding: utf-8 -*-
import json
import os
import random
import time

import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
	QFileDialog, QProgressBar

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import RESULT_TRANSLATE_SUB_EXTRACT, TRANSLATE_SUB_EXTRACT_FINISHED, APP_PATH, \
	TOGGLE_SPINNER, LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT, \
	UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, USER_DATA, TOOL_CODE_MAIN, LOAD_SUB_TRANSLATE_TXT_TABLE_EXTRACT, \
	JOIN_PATH, PATH_DB, TRANSLATE_SUB_PART_TAB_EXTRACT, RESULT_TRANSLATE_SUB_EXTRACT_PART, \
	LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT_PART, STOP_THREAD_TRANSLATE, LANGUAGE_CODE_SPLIT_NO_SPACE
from gui.helpers.ect import cr_pc, mh_ae
from gui.helpers.func_helper import filter_sequence_srt, writeFileSrt, getValueSettings
from gui.helpers.get_data import URL_API_BASE, LANGUAGES_SUPPORT_TRANSPRO1
from gui.helpers.selelium.chatgpt import translateSubChatGPTThuCong, TranslaterServer
from gui.helpers.thread import ManageThreadPool
from gui.helpers.translatepy.translators import GoogleTranslateV2
from gui.helpers.translatepy.translators.server import TranslatorsServer
from gui.helpers.translatepy.translators.tts_online_free import TTSFreeOnlineTranslator
from gui.helpers.translatepy.utils.lru_cacher import LRUDictCache
from gui.widgets.py_combobox import PyComboBox
from gui.widgets.py_dialogs.py_dialog_show_info import PyDialogShowInfo
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_table_widget.model_timeline_addsub import ColumnNumberTabEdit


class GroupboxTranslateServer(QWidget):
	def __init__ (self, manage_thread_pool, table_timeline, settings):
		self.manage_thread_pool = manage_thread_pool
		self.thread_pool_limit = ManageThreadPool()
		self.thread_pool_limit.setMaxThread(10)
		self.table_timeline_edit = table_timeline
		# self.checker = ProxyChecker(manage_thread_pool)
		self.translate_cache = LRUDictCache()
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		self.translate_server = TranslaterServer(manage_thread_pool)
		self.translator_server_free = TranslatorsServer(manage_thread_pool, self.translate_cache)
		self.translator_google = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
		
		self.isStop = False
		self.isStatusTranslate = False
		super().__init__()
		# PROPERTIES
		# settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		
		self.list_languages = settings.get("language_support").get("language_code")
		self.MODEL_AI_TRANSLATE = settings.get("model_ai_translate")
		self.SERVER_TRANSLATE_V2 = settings.get("server_translate")
		self.TabIndexTranslate = settings.get("TabIndexTranslate")
		self.GENDER_VOICE_FREE_TTS_ONLINE = settings.get("gender_voice").get("tts_free_v2")
		self.isLoad = True
		self.load_file_srt_finished = False
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		self.groupbox = QGroupBox("DỊCH PHỤ ĐỀ")
		self.lb_language_origin = QLabel("Dịch Sang:")
		self.cb_languages_destination = PyComboBox()
		
		self.lb_server_trans = QLabel("Chọn Server:")
		self.cb_server_trans = PyComboBox()
		
		self.lb_modelAI = QLabel("Model AI:")
		self.cb_modelAI = PyComboBox()
		# self.lb_notify = QLabel("Tip: Nên sử dụng proxy khi dịch để hạn chế bị block IP")
		
		# self.lb_file_srt = QLabel("Load File SRT:")
		# self.btn_dialog_file_srt = PyButtonIcon(
		# 	icon_path=ConfigResource.set_svg_icon("open-file.png"),
		# 	parent=self,
		# 	app_parent=self,
		# 	icon_color="#f5ca1e",
		# 	icon_color_hover="#ffe270",
		# 	icon_color_pressed="#d1a807",
		#
		# )
		
		text = "- Tip: Nên sử dụng proxy khi dịch để hạn chế bị block IP"
		text += "\n\n- Bấm vào nút hình thư mục để load file srt chỉnh sửa lên"
		text += "\n\n- Sau khi video và sub được load lên Bạn bấm nút xem thử của từng dòng sub để coi nó có khớp với tiếng chưa, sau đó có thể chỉnh lại thời gian hoặc nội dung cho phù hợp"
		text += "\n\n- Nếu có nhiều dòng trùng lặp hoặc ký tự lạ không chính xác thì bấm nút xóa đoạn sub đó đi."
		text += "\n\n- Sau khi sửa sub gốc cảm thấy ưng ý rồi thì có thể bấm vào nút DỊCH để chuyển qua ngôn ngữ mà bạn muốn."
		text += "\n\n- Sau cùng bạn có thể bấm nút XUẤT FILE để lưu với nhiều định dạng khác nhau"
		
		self.dialog_info = PyDialogShowInfo(text, 400)
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
		self.progess_convert = QProgressBar(self, objectName="RedProgressBar")
		self.lb_status = QLabel()
		
		self.btn_translate = QPushButton("Dịch")
		self.btn_translate.setCursor(Qt.CursorShape.PointingHandCursor)
		
		# self.btn_check_render = QPushButton("Kiểm tra lỗi Trước khi render")
		# self.btn_check_render.setCursor(Qt.CursorShape.PointingHandCursor)
		
		# self.btn_export_srt = QPushButton("Xuất File")
		# self.btn_export_srt.setCursor(Qt.CursorShape.PointingHandCursor)
		# self.btn_save_srt = QPushButton("Lưu Lại SUB GỐC")
		# self.btn_save_srt.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.lb_token_chatgpt = QLabel("")
	
	def modify_widgets (self):
		self.cb_server_trans.addItems(list(self.SERVER_TRANSLATE_V2.keys()))
		
		# try:
		languages = self.SERVER_TRANSLATE_V2.get(self.cb_server_trans.currentText()).get("language_support")
		self.cb_languages_destination.clear()
		self.cb_languages_destination.addItems(languages.values())
		
		self.cb_modelAI.addItems(list(self.MODEL_AI_TRANSLATE.values()))
		# self.cb_modelAI.setDisabled(True)
		self.server_changed()
		# self.cb_modelAI.hide()
		# self.lb_modelAI.hide()
		
		# except:
		# 	print("Không get được dữ liệu")
		self.progess_convert.hide()
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_layout = QVBoxLayout()
		# self.content_layout.setContentsMargins(0, 0, 0, 0)
		
		# self.gbox_layout = QVBoxLayout()
		self.groupbox.setLayout(self.content_layout)
		
		self.content_chat_language = QHBoxLayout()
		self.content_language_layout = QHBoxLayout()
		
		self.progess_convert_layout = QHBoxLayout()
		self.content_file_layout = QHBoxLayout()
		self.content_btn_layout = QGridLayout()
		self.content_status = QGridLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		self.setLayout(self.bg_layout)
		# self.setLayout(self.content_layout)
		
		self.content_layout.addWidget(QLabel(""))
		self.content_layout.addLayout(self.content_language_layout)
		# self.content_layout.addWidget(QLabel(""))
		
		self.content_layout.addLayout(self.content_file_layout)
		# self.content_layout.addWidget(QLabel(""))
		self.content_layout.addLayout(self.content_btn_layout)
		self.content_layout.addLayout(self.content_chat_language)
		
		self.content_layout.addLayout(self.content_status)
		
		# self.content_language_layout.addWidget(QLabel(""), 20)
		self.content_language_layout.addWidget(self.lb_server_trans, 20)
		self.content_language_layout.addWidget(self.cb_server_trans, 30)
		self.content_language_layout.addWidget(self.lb_language_origin, 20)
		self.content_language_layout.addWidget(self.cb_languages_destination, 30)
		
		self.content_chat_language.addWidget(self.lb_token_chatgpt)
		# self.content_chat_language.addWidget(self.lb_language_origin, alignment=Qt.AlignmentFlag.AlignRight)
		
		# self.content_radio.addWidget(self.rad_save_file_origin)
		# self.content_radio.addWidget(self.rad_save_file_trans)
		# self.content_radio.addWidget(self.rad_save_all_file)
		self.content_file_layout.addWidget(self.lb_modelAI)
		self.content_file_layout.addWidget(self.cb_modelAI)
		# self.content_file_layout.addWidget(self.lb_file_srt)
		# self.content_file_layout.addWidget(self.btn_dialog_file_srt)
		self.content_file_layout.addWidget(QLabel(), 20)
		
		self.content_btn_layout.addWidget(QLabel(), 0, 0, 1, 4)
		self.content_btn_layout.addWidget(self.btn_translate, 0, 4, 1, 4)
		# self.content_btn_layout.addWidget(self.btn_check_render, 0, 6, 1, 3)
		# self.content_btn_layout.addWidget(self.btn_export_srt, 0, 8, 1, 2)
		self.content_btn_layout.addWidget(QLabel(), 0, 8, 1, 4)
		
		# self.content_btn_layout.addWidget(self.btn_info_frame, 0, 11)
		
		self.content_status.addWidget(self.lb_status, 0, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignLeft)
		self.content_status.addWidget(QLabel(), 0, 4, 1, 3)
		self.content_status.addWidget(self.progess_convert, 0, 7, 1, 3)
		self.content_status.addWidget(self.btn_info_frame, 0, 10, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)
	
	def setup_connections (self):
		self.manage_thread_pool.progressChanged.connect(self._progressChanged)
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		# self.btn_dialog_file_srt.clicked.connect(self._openDialogFileSrt)
		# self.cb_modelAI.currentIndexChanged.connect(self.modelAIChanged)
		# self.checker.finishedCheckLiveProxySignal.connect(self._finishedCheckLiveProxySignal)
		
		self.cb_server_trans.currentIndexChanged.connect(self.server_changed)
		self.cb_languages_destination.currentIndexChanged.connect(lambda index: self.comboxChanged(index))
		
		self.btn_info_frame.clicked.connect(self._click_info)
		# self.btn_save_srt.clicked.connect(self.save_srt)
		
		self.btn_translate.clicked.connect(self.clickStart)
		# self.btn_check_render.clicked.connect(self.clickCheckPreRender)
	
	# def modelAIChanged (self, indexTab):
	# 	if hasattr(self, "configCurrent"):
	# 		if self.isClearData is False:
	# 			model = list(MODEL_AI_TRANSLATE.keys())[self.cb_modelAI.currentIndex()]
	#
	def server_changed (self):
		languages = self.SERVER_TRANSLATE_V2.get(self.cb_server_trans.currentText()).get("language_support")
		self.cb_languages_destination.clear()
		self.cb_languages_destination.addItems(languages.values())
		self.cb_languages_destination.setCurrentIndex(0)
		# self.btn_translate.setDisabled(False)
		# self.cb_modelAI.setDisabled(True)
		
		if self.cb_server_trans.currentIndex() in [
			self.TabIndexTranslate.get('Translate_Pro1'),
			self.TabIndexTranslate.get('Translate_Pro2'),
			self.TabIndexTranslate.get('ChatGPT_Pro')
		]:
			server_trans = self.SERVER_TRANSLATE_V2.get(
				list(self.SERVER_TRANSLATE_V2.keys())[self.cb_server_trans.currentIndex()]).get('server')
			self.check_balance_chatgptPro(server_trans)
		
		else:
			self.lb_token_chatgpt.setText("")
		# print(self.cb_server_trans.currentIndex() )
		if self.cb_server_trans.currentIndex() in [self.TabIndexTranslate.get('ChatGPT_Pro'),
												   self.TabIndexTranslate.get('ChatGPT_API')]:
			# self.cb_modelAI.setDisabled(False)
			self.cb_modelAI.show()
			self.lb_modelAI.show()
		else:
			# print('111')
			self.cb_modelAI.hide()
			self.lb_modelAI.hide()
	
	def _openDialogFileSrt (self):
		
		path_file, _ = QFileDialog.getOpenFileName(self, caption='Chọn file sub srt',
			dir=(APP_PATH), filter='File Sub (*.srt)')
		
		if os.path.exists(path_file):
			video_temporary_mp4 = path_file[:-4] + '.mp4'
			video_temporary_avi = path_file[:-4] + '.avi'
			video_temporary_mkv = path_file[:-4] + '.mkv'
			video_temporary_wmv = path_file[:-4] + '.wmv'
			video_temporary_flv = path_file[:-4] + '.flv'
			video_temporary_mov = path_file[:-4] + '.mov'
			# *wmv * flv * mkv * mov
			# print(video_temporary_mp4)
			
			if os.path.isfile(f'{video_temporary_mp4}'):
				path_video = video_temporary_mp4
			elif os.path.isfile(video_temporary_avi):
				path_video = video_temporary_avi
			
			elif os.path.isfile(video_temporary_mkv):
				path_video = video_temporary_mkv
			
			elif os.path.isfile(video_temporary_wmv):
				path_video = video_temporary_wmv
			
			elif os.path.isfile(video_temporary_flv):
				path_video = video_temporary_flv
			
			elif os.path.isfile(video_temporary_mov):
				path_video = video_temporary_mov
			
			else:
				PyMessageBox().show_error('Cảnh Báo', "Không tìm thấy file 'Video' tương ứng!")
				return
			
			sequences = filter_sequence_srt(path_file, path_video)
			data_table = []
			for (count, item) in enumerate(sequences):
				stt_, time_, content_ = item[0], item[1], item[2]
				data_table.append([time_, content_, ""])
			
			self.table_timeline_edit.displayTable(data_table, path_video, sequences)
			
			self.path_srt = path_file
	
	
	def comboxChanged (self, index):
		pass
	
	# self.btn_translate.setDisabled(False)
	
	def _click_info (self):
		self.dialog_info.exec()
	
	def loadData (self, configCurrent):
		
		self.configCurrent = configCurrent
		
		self.isLoad = False
	
	# def writeFileSrt (self, filename_srt, data_sub, type_srt="origin"):
	# 	""" Mô tả: Lưu file srt dịch vào thư mục temp"""
	#
	# 	if os.path.isfile(filename_srt):
	# 		os.remove(filename_srt)
	#
	# 	with open(filename_srt, "w", encoding='utf-8') as file_data:
	# 		for index, item in enumerate(data_sub):
	# 			time_, sub_origin, trans_ = item[0], item[1], item[2]
	# 			file_data.write(str(index + 1) + '\n')
	# 			file_data.write(str(time_) + '\n')
	# 			if type_srt == "origin":
	# 				file_data.write(str(sub_origin) + '\n\n')
	# 			else:
	# 				file_data.write(str(trans_) + '\n\n')
	#
	# 	PyMessageBox().show_info("Thông Báo", "Lưu File Thành Công!")
	#
	# @decorator_try_except_class
	def loadFileSRTCurrent (self, fileSRTCurrent):
		
		self.fileSRTCurrent = fileSRTCurrent
	
	# cau_hinh_edit: dict = json.loads(fileSRTCurrent.value)
	def clickCheckPreRender (self):
		data_sub = self.table_timeline_edit.getDataSub()
		detect_lang = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
		cau_hinh_edit: dict = json.loads(self.fileSRTCurrent.value)
		
		sub_random = random.choice(data_sub)
		text_random = sub_random[ColumnNumberTabEdit.column_original.value]
		if cau_hinh_edit.get('sub_hien_thi') == "trans":
			if data_sub[0][ColumnNumberTabEdit.column_translated.value] == "":
				return PyMessageBox().show_warning("Cảnh báo", "Sub chưa được dịch")
			text_random = sub_random[ColumnNumberTabEdit.column_translated.value]
		lang =detect_lang.language(text_random).result
		lang_source = lang.in_foreign_languages.get('en')
		lang_code = lang.alpha2
		is_ok = PyMessageBox().show_question("Thông báo", f"Ngôn ngữ SUB là {lang_source}, Bạn có muốn tiếp tục Kiểm Tra Lỗi Không ?")
		if is_ok:
			pass
		else:
			return
		if lang_source == 'Filipino':
			# language_tts = 'Tagalog'
			lang_code = 'tl'
		
		server_trans = TTSFreeOnlineTranslator(self.manage_thread_pool)
		# gender = list(GENDER_VOICE_FREE_TTS_ONLINE.get(self.LANGUAGES_CHANGE_CODE.get(lang_code)).keys())[0]
		gender = list(self.GENDER_VOICE_FREE_TTS_ONLINE.get(lang_code).keys())[0]
		self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
		
	
	
	# @decorator_try_except_class
	def clickStart (self):
		self.table_timeline_edit.isTranslating = False
		self.table_timeline_edit.count_result_trans = 0
		self.table_timeline_edit.list_row_trans_chunk = []
		# print(self.isStatusTranslate)
		# print(self.isStop)
		if self.table_timeline_edit.isHasSub is True:
			if self.isStatusTranslate:
				self.manage_thread_pool.resultChanged.emit(STOP_THREAD_TRANSLATE, STOP_THREAD_TRANSLATE, "")
				self.isStop = True
				self.isStatusTranslate = False
				self.resetStatus()
			else:
				self.isStatusTranslate = True
				self.isStop = False
				
				self.btn_translate.setText("STOP")
				
				self._translateStartThread()
		else:
			PyMessageBox().show_warning('Cảnh Báo', "Chưa có phụ đề nào được load !")
	
	def _progressChanged (self, type_progress, id_thread, proge):
		if type_progress == UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT:
			if self.isStop:
				self.progess_convert.setValue(0)
				return
			self.progess_convert.setValue(proge)
			if proge == self.total_sub:
				self.lb_status.setText("Hoàn thành!")
				self.progess_convert.hide()
				self.progess_convert.setValue(0)
	
	def _resultThread (self, id_worker, id_thread, result):
		if id_thread == TRANSLATE_SUB_PART_TAB_EXTRACT:
			''' Dịch lại 1 phần trong bảng'''
			# self.btn_convert.setDisabled(False)
			self.isStop = False
			
			self.resetStatus()
			# print("again")
			self._translateStartThread(list_sequences=result)
		
		# if id_thread == ITEM_TABLE_TIMELINE_EXTRACT_CHANGED:
		# 	self.btn_export_srt.setDisabled(False)
		# self.rad_save_file_origin.setDisabled(False)
		
		if id_thread == TRANSLATE_SUB_EXTRACT_FINISHED:
			# self.btn_export_srt.setDisabled(False)
			# print("OK")
			if self.cb_server_trans.currentIndex() in [self.TabIndexTranslate.get('Translate_Pro1'),
													   self.TabIndexTranslate.get('Translate_Pro2'),
													   self.TabIndexTranslate.get('ChatGPT_Pro')]:
				server_trans = self.SERVER_TRANSLATE_V2.get(
					list(self.SERVER_TRANSLATE_V2.keys())[self.cb_server_trans.currentIndex()]).get('server')
				self.check_balance_chatgptPro(server_trans)
			else:
				self.lb_token_chatgpt.setText("")
			self.resetStatus()
	
	def resetStatus (self):
		self.lb_status.setText("")
		self.btn_translate.setText("DỊCH")
		self.progess_convert.hide()
		self.progess_convert.setValue(0)
		self.isStatusTranslate = False
		self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
	
	def _translateStartThread (self, list_sequences=None):
		
		type_thread_server = RESULT_TRANSLATE_SUB_EXTRACT if list_sequences is None else RESULT_TRANSLATE_SUB_EXTRACT_PART
		type_thread_chatgpt = LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT if list_sequences is None else LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT_PART
		
		sequences = self.table_timeline_edit.getDataSub() if list_sequences is None else list_sequences
		# self.table_timeline_extract.resetDataColumn(ColumnNumberTabEdit.column_translated.value)
		# print(111111)
		self.lb_status.setText("Đang dịch sub....")
		server_trans = self.SERVER_TRANSLATE_V2.get(
			list(self.SERVER_TRANSLATE_V2.keys())[self.cb_server_trans.currentIndex()]).get('server')
		languages = self.SERVER_TRANSLATE_V2.get(self.cb_server_trans.currentText()).get("language_support")
		
		des_lang = list(languages.keys())[self.cb_languages_destination.currentIndex()]
		
		list_sub_origin = [item[ColumnNumberTabEdit.column_original.value] for item in
						   sequences]  # lấy ra mảng sub gốc
		# self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
		self.progess_convert.setRange(0, len(list_sub_origin))
		self.progess_convert.setValue(0)
		self.progess_convert.show()
		
		self.total_sub = len(list_sub_origin)
		translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
		lang_result = translator_server.language(random.choice(list_sub_origin))
		# print(lang_result.result)
		lang_source = lang_result.result.alpha2
		
		if 'zh' in lang_source:
			lang_source = 'zh'
		
		lang = self.list_languages.get(lang_source)
		lang_des = self.cb_languages_destination.currentText()
		if lang == lang_des:
			self.lb_status.setText("Lỗi ngôn ngữ dịch")
			self.progess_convert.hide()
			self.progess_convert.setValue(0)
			return PyMessageBox().show_warning('Cảnh Báo', "Ngôn ngữ dịch không được trùng với ngôn ngữ nguồn")
		
		if server_trans == 'baidu':
			lang_source = 'auto'
		
		data_sub = []
		for sub in sequences:
			time, sub_origin, sub_translate = sub
			data_sub.append(["dolech", time, 'pos_ori', sub_origin, sub_translate, 'pos_trans'])
		
		if server_trans == 'chatgpt_thu_cong':
			translateSubChatGPTThuCong(self.manage_thread_pool, type_thread_chatgpt, data_sub, lang_source, des_lang, lang_result, self.resetStatus)
		
		elif server_trans == 'chatgpt_pro' or 'translate_pro' in server_trans:
			self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
			model = list(self.MODEL_AI_TRANSLATE.keys())[self.cb_modelAI.currentIndex()]
			# print(model)
			if 'translate_pro2' in server_trans:
				model = server_trans
			if 'translate_pro1' in server_trans:
				lang_support = LANGUAGES_SUPPORT_TRANSPRO1.get(lang_source)
				if lang_support is None:
					self.resetStatus()
					return PyMessageBox().show_warning('Cảnh Báo', f"{lang_result.result.as_dict().get('in_foreign_languages')['vi']} Không Hỗ Trợ Dịch Sang Ngôn Ngữ Này")
				elif not des_lang in lang_support:
					self.resetStatus()
					
					return PyMessageBox().show_warning('Cảnh Báo', f"{lang_result.result.as_dict().get('in_foreign_languages')['vi']} Không Hỗ Trợ Dịch Sang Ngôn Ngữ Này")
				
				model = server_trans
			
			self.translate_server.translateSubServerPro(server_trans, type_thread_chatgpt, data_sub, lang_source, des_lang, lang_result, model, self.resetStatus, self.translate_cache)
		
		elif server_trans == 'chatgpt_api_key':
			self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
			model = list(self.MODEL_AI_TRANSLATE.keys())[self.cb_modelAI.currentIndex()]
			if 'claude' in model.lower():
				return PyMessageBox().show_warning('WARNING',
					f"Không hỗ trợ")
			
			file_api = JOIN_PATH(PATH_DB, "open_api.json")
			if not os.path.exists(file_api):
				return PyMessageBox().show_warning('WARNING',
					f"File open_api.json not found")
			with open(file_api, "r", encoding="utf-8") as file:
				data_token = json.load(file)
				if data_token.get("list_api") is None or data_token.get("prompt_custom") is None:
					return PyMessageBox().show_warning('WARNING',
						f"Vui lòng nhập đầy đủ thông tin trong file open_api.json")
			
			self.translate_server.translateGPTApiKey(type_thread_chatgpt, data_sub, lang_source,
				des_lang, lang_result, model, data_token.get("list_api"), data_token.get("prompt_custom"), data_token.get("line_break"), self.resetStatus,
				self.translate_cache)
		# print(chunk)
		elif server_trans == 'txt_file':
			file_name, _ = QFileDialog.getOpenFileName(self, caption='Load file txt chứa văn bản DỊCH',
				dir=(APP_PATH),
				filter='File txt (*.txt)')
			if file_name == "":
				self.resetStatus()
				return PyMessageBox().show_warning('Cảnh Báo', f"File không tồn tại")
			
			with open(file_name, "r", encoding='utf-8') as file_data:
				content = file_data.read()
				if content == "":
					self.resetStatus()
					return PyMessageBox().show_warning('Cảnh Báo', f"File rỗng")
				so_dong_sub_goc = len(list_sub_origin)
				
				so_dong_sub_dich = len(content.split("\n"))
			# print(so_dong_sub_dich)
			if not so_dong_sub_dich == so_dong_sub_goc:
				self.resetStatus()
				return PyMessageBox().show_warning('Cảnh Báo', f"Số dòng sub gốc là {so_dong_sub_goc}, nhưng số dòng sub dịch là {so_dong_sub_dich}. Không đều nhau")
			
			self.manage_thread_pool.resultChanged.emit(LOAD_SUB_TRANSLATE_TXT_TABLE_EXTRACT, LOAD_SUB_TRANSLATE_TXT_TABLE_EXTRACT, content.split("\n"))
		
		else:
			self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
			self.translator_server_free.is_error = False
			# print('ooooo')
			for index, sub in enumerate(list_sub_origin):
				if str(lang_result.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
					content = sub.strip().replace("\n", "")
				else:
					content = sub.strip().replace("\n", " ")
				
				self.thread_pool_limit.start(self._funcConvertLanguage, "translate_sub_" + str(index), type_thread_server,
					is_stop=self.get_is_stop, type_thread_server=type_thread_server,
					server_trans=server_trans, sub=content, row_number=index, source_lang=lang_source,
					des_lang=des_lang)
	
	def get_is_stop (self):
		# print(self.isStop)
		return self.isStop
	
	def _funcConvertLanguage (self, **kwargs):
		# try:
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		row_number = kwargs["row_number"]
		des_lang = kwargs["des_lang"]
		text = kwargs["sub"]
		
		server_trans = kwargs["server_trans"]
		source_lang = kwargs["source_lang"]
		type_thread_server = kwargs["type_thread_server"]
		get_is_stop = kwargs["is_stop"]
		# print(get_is_stop())
		if get_is_stop():
			return
		
		text_trans = ''
		
		if server_trans == 'baidu':
			for i in range(5):
				if get_is_stop():
					return
				try:
					text_res = self.translator_server_free.translate_text(query_text=text, translator='baidu_v1', from_language='auto', to_language=des_lang, timeout=10000)
					if 'lời bài hát' in text_res.lower() or 'lyrics' in text_res.lower():
						time.sleep(1)
						continue
					
					else:
						text_trans = text_res
						break
				except:
					continue
			
			if text_trans == '':
				# print('google')
				text_trans = self.translator_google.translate(text, destination_language=des_lang, source_language=source_lang).result
		
		elif server_trans == 'google':
			for i in range(5):
				text_res = self.translator_google.translate(text, destination_language=des_lang, source_language=source_lang).result
				if text_res != '':
					text_trans = text_res
					# print('ok')
					break
			if text_trans == '':
				text_trans = self.translator_server_free.translate_text(query_text=text, translator=server_trans, from_language=source_lang, to_language=des_lang, timeout=10000)
		
		else:
			text_trans = self.translator_server_free.translate_text(query_text=text, translator=server_trans, from_language=source_lang, to_language=des_lang, timeout=10000)
		
		thread_pool.finishSingleThread(id_worker)
		self.manage_thread_pool.resultChanged.emit(type_thread_server, type_thread_server,
			{"row": row_number, "text_trans": text_trans})
	
	def save_srt (self):
		data_sub_timeline = self.table_timeline_edit.getDataSub()
		# print(data_sub_timeline)
		if len(data_sub_timeline) == 0:
			return PyMessageBox().show_warning("Thông Báo", "Chưa load file sub")
		
		data_sub = []
		for sub in data_sub_timeline:
			time, sub_origin, sub_translate = sub
			data_sub.append(["dolech", time, 'pos_ori', sub_origin, sub_translate, 'pos_trans'])
		
		if hasattr(self, 'path_srt'):
			writeFileSrt(self.path_srt, data_sub, 0)
		else:
			return PyMessageBox().show_warning("Thông Báo", "Chưa load file srt!")
		
		PyMessageBox().show_info("Thông Báo", "Lưu File Thành Công!")
	
	def check_balance_chatgptPro (self, type_):
		headers = {"Authorization": f"Bearer {self.user_data['token']}"}
		payload = {
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		response = requests.post(url=URL_API_BASE + f"/translate/private/check-balance/{type_}", headers=headers,
			json={
				"data": mh_ae(payload, p_k=self.user_data['paes'])}
		)
		# print(response.json())
		if response.status_code == 200:
			self.lb_token_chatgpt.setText(f"Token Còn Lại: {response.json().get('data') if isinstance(response.json().get('data'), str) else '{:,}'.format(response.json().get('data'))}")
		
		# self.lb_token_chatgpt.setText(f"Token Còn Lại: {response.json().get('data')}")
		else:
			self.lb_token_chatgpt.setText(f"Hết Token, Liên Hệ Admin Mua")
