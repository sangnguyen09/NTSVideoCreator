import json
import math
import os
import random
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import budoux
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Signal, QPoint, Slot, QItemSelectionModel, QItemSelection, QEvent, QModelIndex, \
	QCoreApplication, QPersistentModelIndex
from PySide6.QtGui import QIcon, QColor, QKeyEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu, QTableWidgetItem, QAbstractItemView, QHeaderView, QTableView, \
	QHBoxLayout, QPushButton

from gui.db.sqlite import ConfigAppModel
from gui.helpers.constants import UPDATE_VALUE_PROGRESS_TRANSLATE_SUB, RESULT_TRANSLATE_SUB, \
	TRANSLATE_SUB_FINISHED, ROW_SELECTION_CHANGED_TABLE_ADD_SUB, CHANGE_STYLE_SUB, \
	SPLIT_SUB_TRANSLATE_IN_TABLE, TOGGLE_SPINNER, \
	UPDATE_TEXT_TABLE_ADD_SUB, LOAD_SUB_TRANSLATE_CHATGPT, LANGUAGE_CODE_SPLIT_NO_SPACE, TRANSLATE_SUB_PART, \
	RESULT_TRANSLATE_SUB_PART, LOAD_SUB_TRANSLATE_CHATGPT_PART, UPDATE_VALUE_PROGRESS_CHECK_LECH_SUB, \
	CHECK_LECH_SUB_FINISHED, RESULT_CHECK_DO_LECH_VIDEO, RESULT_CHECK_DO_LECH_VIDEO_PART, \
	CHECK_DO_LECH_TABLE_CHANGED_PART, LOAD_SUB_IN_TABLE_FINISHED, \
	SETTING_APP_DATA, TOOL_CODE_MAIN, POSITION_SUB_ORIGINAL_CHANGED, \
	 DELIMITER_POS_SUB, POSITION_SUB_CHANGED, CENTER_POSITION_SUB, LIST_COLOR_NAME_DO_LECH, \
	get_index_name_do_lech_sub, XOA_SUB_DONG_SO, THEM_KY_TU_NEU_SUB_CO_HAI_KYTU, LOAD_SUB_TRANSLATE_TXT, \
	PREVIEW_PRE_RENDER, UPDATE_TY_LE_KHUNG_HINH_VIDEO, DELIMITER_CENTER_POS_SUB, GET_VOICE_PREVIEW, \
	TTS_GET_VOICE_FINISHED, STOP_THREAD_TRANSLATE, GOP_SUB_DONG_TREN, GOP_SUB_DONG_DUOI, \
	THAY_THE_SUB_NEU_SUB_CO_DO_LECH_LON, CLICK_DOC_THU_VOICE, FILE_SRT_CURRENT, SET_AUTO_SAVE_SUB
from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from .model_timeline_addsub import TableAddModel, ColumnNumber
from ..py_dialogs.py_dialog_edit_sub import PyDialogEditSub
from ..py_dialogs.py_dialog_find_replace import PyDialogFindReplace
from ..py_dialogs.py_dialog_get_int import PyDialogGetInt
from ..py_dialogs.py_dialog_select_option import PyDialogSelectOption
from ..py_dialogs.py_dialog_summary import PyDialogSummary
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_messagebox.py_massagebox import PyMessageBox
from ...configs.config_resource import ConfigResource
from ...helpers.custom_logger import decorator_try_except_class
from ...helpers.func_helper import getValueSettings, seconds_to_timestamp, string_time_to_seconds, play_media_preview, \
	writeFileSrt
from ...helpers.server import SERVER_TAB_TTS
from ...helpers.translatepy import Language
from ...helpers.translatepy.translators import GoogleTranslateV2


class TableView(QTableView):
	def __init__ (self, *args, **kwargs):
		QTableView.__init__(self, *args, **kwargs)
		self.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
	
	def keyPressEvent (self, event):
		if event.key() == Qt.Key_Up:
			# self.selectRow(self.currentIndex().row() - 1)
			index = self.moveCursor(
				QtWidgets.QAbstractItemView.MoveUp, QtCore.Qt.NoModifier
			)
			command = self.selectionCommand(self.currentIndex(), event)
			self.selectionModel().setCurrentIndex(index, command)
		
		# elif event.key() == Qt.S:
		# 	self.selectRow(self.currentIndex().row() + 1)
		
		elif event.key() == Qt.Key_Down:
			index = self.moveCursor(
				QtWidgets.QAbstractItemView.MoveDown, QtCore.Qt.NoModifier
			)
			command = self.selectionCommand(self.currentIndex(), event)
			self.selectionModel().setCurrentIndex(index, command)
		
		elif event.key() == Qt.Key_Delete:
			index = self.currentIndex()
			print('delete line: ', index.row())
			self.model().removeRow(index.row())
		
		
		elif event.type() == QEvent.KeyPress and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
			if self.state() != QAbstractItemView.EditingState:
				self.edit(self.currentIndex())
		else:
			super().keyPressEvent(event)


class TableTimeline(QWidget):
	getConfigChanged = Signal()
	statusButtonChanged = Signal(str)
	rowSelectionChanged = Signal(int)
	
	def __init__ (self, manage_thread_pool: ManageThreadPool):
		super().__init__()
		# SET STYLESHEET
		
		self.manage_thread_pool = manage_thread_pool  # tạo trước ui
		self.thread_limit_update = ThreadPoolExecutor(max_workers=1)
		self.thread_limit = ManageThreadPool()
		self.thread_limit.setMaxThread(10)
		self.listRowTransPart = []
		self.listRowCheckDoLechPart = []
		self.data_sub_origin = []
		self.count_result_trans = 0
		self.count_result_pos = 0
		self.total_pos_update = 0
		self.count_split_sub = 0
		self.count_result_check_lech = 0
		self.list_row_do_lech_chunk = []
		self.list_row_trans_chunk = []
		self.resultThread = {}
		self.isLoadSrtFinish = True
		self.isCheckingDoLech = True
		self.isCheckFinish = False
		self.isTranslating = False
		self.getXCenterSub = None
		self.setMinimumHeight(200)
		settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
		self.chunk_split = settings.get('chunk_split', 5)
		self.list_language_support = settings.get("language_support")
		
		self.is_check_all = False  # trạng thái checkbok ban đầu là chưa check
		self.icon_checked = QIcon(ConfigResource.set_svg_icon("checked.png"))
		self.icon_unchecked = QIcon(ConfigResource.set_svg_icon("uncheck.png"))
		self.icon_check_all = QIcon(ConfigResource.set_svg_icon("uncheck.png"))
		
		self.init_ui()
	
	def init_ui (self):
		self.create_widgets()
		
		self.create_layouts()
		self.add_widgets_to_layouts()
		
		self.setup_table()
		# show dư liệu
		# self.displayTable()
		
		self.setup_connections()
	
	def create_widgets (self):
		self.main_table = TableView()  # QTableWidget()
		self.main_table.setObjectName(u"tableWidget2")
		# tạo Nút CheckBox trên tiêu đề
		
		# menu ngữ cảnh
		self.menu = QMenu()
		
		# setting_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DriveDVDIcon)
		# newAct = self.menu.addAction("New", self.triggered, shortcut='A')
		self.act_select_all = self.menu.addAction("Preview", self.signal_privew)  # (QAction('test'))
		self.act_select_all = self.menu.addAction("Get Voice", self.signal_get_voice)  # (QAction('test'))
		self.act_select_all = self.menu.addAction("Select All", lambda: self.main_table.selectAll())  # (QAction('test'))
		self.act_select_all = self.menu.addAction("Select Option", self.signal_option)  # (QAction('test'))
		self.act_select_all = self.menu.addAction("Find And Replace", self.signal_find_replace)  # (QAction('test'))
		self.act_concat_sub = self.menu.addAction("Gộp Lại Sub", self.signal_concat_sub)  # (QAction('test'))
		self.act_split_sub = self.menu.addAction("Tách Sub Thành Nhiều Dòng", self.signal_split_sub)  # (QAction('test'))
		# self.act_concat_sub.setShortcut("Ctrl+G")
		
		# play_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
		self.menu.addAction("Rút Gọn Nội Dung", lambda: self.signal_summary())
		# self.menu.addAction("Rút Gọn Nội Dung SUB DỊCH", lambda: self.signal_summary("trans"))
		# self.act_summary.setShortcut("Alt+P")
		
		# stop_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
		self.menu.addAction("Dịch Lại", self.signal_translate_again)
		self.menu.addAction("Xóa", self.signal_remove)
	
	# self.main_table.installEventFilter(self)
	# self.main_table.keyPressEvent = self.tableKeyPressEvent
	
	# self.act_translate_again.setShortcut("Ctrl+S")
	
	# self.timer = QTimer()  # thực hiện việc gi đó sau khoảng thời gian
	# sự kiện cho context menu
	
	
	def signal_get_voice (self):
		items_selected = self.main_table.selectionModel().selectedRows()
		cau_hinh = json.loads(self.configCurrent.value)
		type_tts_sub = cau_hinh["servers_tts"]["type_tts_sub"]
		
		if len(items_selected) < 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn GET VOICE")
		if type_tts_sub == "trans":
			item_sub_trans = self.getValueItem(
				items_selected[0].row(), ColumnNumber.column_sub_translate.value)
			if item_sub_trans == "":
				return PyMessageBox().show_warning("Thông Báo", "Sub chưa được dịch")
		
		data = []
		list_rows = []
		row_pre = 0
		for index, item in enumerate(items_selected):
			if not index == 0:
				if not (item.row() - row_pre) == 1:
					return PyMessageBox().show_warning('Cảnh Báo', "Chỉ được GET VOICE các hàng liền nhau")
			row_pre = item.row()
			
			dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = self.getDataRow(item.row())
			data.append([dolech, time, pos_ori, sub_origin, sub_translate, pos_trans])
			list_rows.append(item.row())
		self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
		
		self.manage_thread_pool.resultChanged.emit(GET_VOICE_PREVIEW, GET_VOICE_PREVIEW, (data, cau_hinh, list_rows))
	
	def signal_privew (self):
		items_selected = self.main_table.selectionModel().selectedRows()
		if len(items_selected) < 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn XEM TRƯỚC")
		
		data = []
		row_pre = 0
		for index, item in enumerate(items_selected):
			if not index == 0:
				if not (item.row() - row_pre) == 1:
					return PyMessageBox().show_warning('Cảnh Báo', "Chỉ được XEM TRƯỚC các hàng liền nhau")
			row_pre = item.row()
			
			dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = self.getDataRow(item.row())
			data.append([dolech, time, pos_ori, sub_origin, sub_translate, pos_trans])
		
		self.manage_thread_pool.resultChanged.emit(PREVIEW_PRE_RENDER, PREVIEW_PRE_RENDER, data)
	
	def signal_option (self):
		# print(self.getDataSub())
		dialog = PyDialogSelectOption("Select Dòng Sub Theo Độ Lệch", "Chọn Màu Của Sub Muốn Select", LIST_COLOR_NAME_DO_LECH, height=120)
		
		if dialog.exec():
			list_row_select = []
			for row, sub in enumerate(self.getDataSub()):
				dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = sub
				try:
					dl = float(dolech.replace(" lần", ""))
					if get_index_name_do_lech_sub(dl) == dialog.getIndex():
						list_row_select.append(row)
				except:
					return PyMessageBox().show_warning("Thông báo", "Bạn chưa Bấm nút CHECK ĐỘ LỆCH")
			if len(list_row_select) > 0:
				self.selectListRow(list_row_select)
			else:
				return PyMessageBox().show_warning("Thông báo", "Không có dòng nào có màu bạn đã chọn")
	
	def signal_find_replace (self):
		# print(self.getDataSub())
		dialog = PyDialogFindReplace(self.manage_thread_pool, self.getDataSub())
		
		if dialog.exec():
			self.model.update_data = dialog.getValue()
	
	# print(dialog.getValue())
	
	def signal_split_sub (self):
		items_selected = self.main_table.selectionModel().selectedRows()
		if len(items_selected) < 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn tách")
		elif len(items_selected) > 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Chỉ có thể tách từng dòng")
		row_number = items_selected[0].row()
		
		time_line = self.getValueItem(row_number, ColumnNumber.column_time.value)
		
		start = time_line.split(' --> ')[0]
		end = time_line.split(' --> ')[1]
		sub_origin = self.getValueItem(row_number, ColumnNumber.column_sub_text.value)
		translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
		lang_source = translator_server.language(sub_origin)
		count_chars = 0
		if 'jpn' in str(lang_source.result):
			parser = budoux.load_default_japanese_parser()
			content = sub_origin.strip().replace("\n", "")
			count_chars = len(content)
			list_content = parser.parse(content)
		
		elif 'zho' in str(lang_source.result):  # tieng trun gian the
			parser = budoux.load_default_simplified_chinese_parser()
			content = sub_origin.strip().replace("\n", "")
			count_chars = len(content)
			list_content = parser.parse(content)
		
		elif 'och' in str(lang_source.result):  # tieng trung quoc te
			parser = budoux.load_default_traditional_chinese_parser()
			content = sub_origin.strip().replace("\n", "")
			count_chars = len(content)
			list_content = parser.parse(content)
		else:
			list_content = sub_origin.strip().replace("\n", " ").split(" ")
			count_chars = len(list_content)
		
		content = "- Bạn muốn tách tối đa bao nhiêu từ trên 1 dòng ?"
		# content += "\n + Đối với ngôn ngữ không có dấu khoảng cách như Trung Quốc, Nhật Bản,... thì lên để số từ lớn."
		# content += "\n + Đối với ngôn ngữ có dấu khoảng cách thì lên để số từ bé."
		# content += f"\n\n- Đoạn Sub này là ngôn ngữ {lang_source.result.in_foreign_languages.get('vi')}"
		content += f"\n\n- Đoạn Sub này có tổng cộng {count_chars} từ "
		
		dialog = PyDialogGetInt(content, "Tách Sub Thành Nhiều Dòng", "Số từ/dòng: ", 2, 50, height=150)
		
		if dialog.exec():
			
			
			list_text = []
			text_c = ''
			for index, text_ in enumerate(list_content):
				max_length = dialog.getValue()
				
				if str(lang_source.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
					if len(text_c) + len(text_) > max_length:
						list_text.append(text_c.strip())
						text_c = ''
					text_c += text_
				else:
					if len(text_c.strip().split()) + 1 > max_length:
						list_text.append(text_c.strip())
						text_c = ''
					elif not text_c == '':
						if len(text_c.strip().split()) > max_length / 2 and text_c.strip()[
							-1] in '''.,!;?'"]:)>/\\}''':
							list_text.append(text_c.strip())
							text_c = ''
					text_c += text_ + " "
				if index == len(list_content) - 1:
					list_text.append(text_c.strip())
			
			start_time = datetime.strptime(start, "%H:%M:%S,%f")
			end_time = datetime.strptime(end, "%H:%M:%S,%f")
			
			time_split = (end_time - start_time).total_seconds() / len(list_text)
			
			self.model.removeRows(row_number)
			# print(list_text)
			for ind, text in enumerate(list_text):
				# for index, item in enumerate(items_selected):
				# 	print()
				start_pre = seconds_to_timestamp((
						string_time_to_seconds(start) + time_split * ind))
				end_pre = seconds_to_timestamp((
						string_time_to_seconds(start_pre) + time_split))
				# print(start_pre)
				# print(end_pre)
				row_cur = row_number + ind
				
				self.model.insertRows(row_cur)
				# print(row_start, [None, None, f"{time_start} --> {time_end}", sub_origin_concat.strip("\n"),
				# 				  sub_trans_concat.strip("\n")])
				# ['1', None, '00:00:00,390 --> 00:00:01,160', 'All righty, guys.']
				# ["Ratio", "Time", "Pos Ori", "Original", "Translation", "Pos Trans"]
				self.addDataRow(row_cur, ["", f"{start_pre} --> {end_pre}", '', text, '', ''])
			
			# self.main_table.selectRow(row_number)
			self.selectRowDown()
		else:
			return
	
	def signal_remove (self):
		items_selected = self.main_table.selectionModel().selectedRows()
		if len(items_selected) < 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn xóa")
		
		cau_hinh = json.loads(self.configCurrent.value)
		if cau_hinh.get("chinh_sua_thuong"):
			req = True
		else:
			req = PyMessageBox().show_question("Xách Nhận", "Bạn có chắc chắn muốn xóa !")
		row_start = items_selected[0].row()
		
		if req is True:
			row_pre = 0
			for index, item in enumerate(items_selected):
				if not index == 0:
					if not (item.row() - row_pre) == 1:
						return PyMessageBox().show_warning('Cảnh Báo', "Chỉ được xóa các hàng liền nhau")
				row_pre = item.row()
			
			for index, item in enumerate(items_selected):
				self.model.removeRows(item.row())
		# data = []
		# for row in range(self.model.rowCount()):
		# 	dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = self.getDataRow(row)
		# 	# print(time, sub_origin, sub_translate, dolech, pos_ori, pos_trans)
		# 	# data.append([time, sub_origin, sub_translate, pos_ori, pos_trans])
		# 	data.append(["", time, "", sub_origin, sub_translate, ''])
		
		# self.model.update_data = data
		else:
			return
		# self.main_table.selectRow(row_start)
		self.selectRowDown()
	
	def signal_concat_sub (self):
		time_start = ''
		time_end = ''
		sub_origin_concat = ''
		sub_trans_concat = ''
		
		items_selected = self.main_table.selectionModel().selectedRows()
		if len(items_selected) < 2:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn gộp")
		
		row_start = items_selected[0].row()
		# pos_ori = self.getValueItem(row_start, ColumnNumber.column_position_origin.value)
		# pos_trans = self.getValueItem(row_start, ColumnNumber.column_position_trans.value)
		# print(items_selected)
		row_pre = 0
		for index, item in enumerate(items_selected):
			if not index == 0:
				if not (item.row() - row_pre) == 1:
					return PyMessageBox().show_warning('Cảnh Báo', "Chỉ được gộp các hàng liền nhau")
			row_pre = item.row()
		
		for index, item in enumerate(items_selected):
			
			time_line = self.getValueItem(row_start, ColumnNumber.column_time.value)
			start = time_line.split(' --> ')[0]
			end = time_line.split(' --> ')[1]
			
			if index == 0:
				time_start = start
			
			time_end = end
			sub_org = self.getValueItem(row_start, ColumnNumber.column_sub_text.value)
			sub_trans = self.getValueItem(row_start, ColumnNumber.column_sub_translate.value)
			# print(sub_org)
			sub_origin_concat += sub_org + " "
			sub_trans_concat += sub_trans + " "
			
			self.model.removeRow(row_start)
		
		self.model.insertRow(row_start)
		
		self.addDataRow(row_start, ["", f"{time_start} --> {time_end}", '', sub_origin_concat.strip("\n"),
									sub_trans_concat.strip("\n"), ''])
		
		self.selectRowDown()
	
	def selectRowDown (self):
		# index = self.main_table.moveCursor(
		# 	QtWidgets.QAbstractItemView.MoveDown, QtCore.Qt.NoModifier
		# )
		# command = self.main_table.selectionCommand(self.main_table.currentIndex(), event)
		# self.selectionModel().setCurrentIndex(index, command)
		# Tạo một sự kiện phím giả
		key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
		#
		# # Gửi sự kiện đến table_view
		QCoreApplication.postEvent(self.main_table, key_event)
	
	def signal_summary (self):
		cau_hinh = json.loads(self.configCurrent.value)
		type_tts_sub = cau_hinh["servers_tts"]["type_tts_sub"]
		
		# list_language_tts = SERVER_TAB_TTS.get(
		# 	list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("language_tts")
		#
		# language_tts = list_language_tts.get(cau_hinh["servers_tts"]["language_tts"])
		server_trans = SERVER_TAB_TTS.get(
			list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]])
		key_lang = server_trans.get("key_lang")
		language_tts = self.list_language_support.get(key_lang).get(cau_hinh["servers_tts"]["language_tts"])
		
		items_selected = self.main_table.selectionModel().selectedRows()
		if len(items_selected) < 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn rút gọn")
		
		translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
		
		if type_tts_sub == "trans":
			item_sub_trans = self.getValueItem(
				items_selected[0].row(), ColumnNumber.column_sub_translate.value)
			if item_sub_trans == "":
				return PyMessageBox().show_warning("Thông Báo", "Sub chưa được dịch")
			
			lang_result = translator_server.language(item_sub_trans)
		
		else:
			item_sub_org = self.getValueItem(
				items_selected[0].row(), ColumnNumber.column_sub_text.value)
			
			lang_result = translator_server.language(item_sub_org)
		
		# lang_source = lang_result.result.alpha3
		lang_tts = Language(cau_hinh["servers_tts"]["language_tts"].split("-")[0]).alpha3
		
		if not lang_result.result.alpha3 == lang_tts:
			return PyMessageBox().show_warning('Cảnh Báo', "Ngôn ngữ SUB không trùng với ngôn ngữ đọc. Vui lòng chọn đúng ngôn ngữ đọc, hoặc Chế Độ Đọc khác")
		if hasattr(self, 'model_AI'):
			for index, item in enumerate(items_selected):
				# item_sub_trans = self.getValueItem(item.row(), ColumnNumber.column_sub_translate.value)
				# item_sub_org = self.getValueItem(item.row(), ColumnNumber.column_sub_original.value)
				# item_time = self.getValueItem(item.row(), ColumnNumber.column_time.value)
				data_sub = self.getDataRow(item.row())
				# print(data_sub)
				
				dialog = PyDialogSummary(self.manage_thread_pool, data_sub, self.model_AI, mode_doc=type_tts_sub, language=language_tts, source_lang=lang_result.result.alpha2)
				if dialog.exec():
					if type_tts_sub == "trans":
						self.setValueItem(item.row(), ColumnNumber.column_sub_translate.value, dialog.getValue())
					# item_sub_trans.setText(dialog.getValue())
					else:
						self.setValueItem(item.row(), ColumnNumber.column_sub_text.value, dialog.getValue())
				
				else:
					continue
	
	
	def signal_translate_again (self):
		self.listRowTransPart = []
		
		items_selected = self.main_table.selectionModel().selectedRows()
		if len(items_selected) < 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn dịch")
		
		data = []
		
		for index, item in enumerate(items_selected):
			self.listRowTransPart.append(item.row())
			# ("Ratio", "Time", "Pos Ori", "Original", "Translation", "Pos Trans")
			dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = self.getDataRow(item.row())
			
			data.append([dolech, time, pos_ori, sub_origin, sub_translate, pos_trans])
		self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_PART, TRANSLATE_SUB_PART, data)
	
	
	def setup_table (self):
		# ========== Cài đặt cho table============
		# self.main_table.setColumnCount(6)  # số lượng cột
		data = [["","", "", "", ""]]
		name_column = ["Action","Ratio", "Time", "Duration", "Text"]
		self.model = TableAddModel(data, name_column)
		
		self.main_table.setModel(self.model)

		# self.main_table.verticalHeader().setVisible(False)  # ko hiện số thứ tự ở các dòng
		# self.main_table.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # cái này là khi focus vào thì ko hiện cái viền
		# self.main_table.horizontalHeader().setHighlightSections(False)  # không Highlight khi chọn vào tiêu đề
		# .horizontalHeader().setSectionsClickable(True)
		self.main_table.setAlternatingRowColors(True)  # hiện màu dòng xen kẽ
		
		self.main_table.horizontalHeader().setStretchLastSection(True)  # cái này cho kéo dãn full table
		# self.main_table.horizontalHeader().setDefaultSectionSize(126)
		self.main_table.horizontalHeader().setMinimumSectionSize(40)
		self.main_table.verticalHeader().setDefaultSectionSize(60)
		self.main_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # làm cho content xuống dòng
		# self.main_table.resizeRowsToContents()
		# self.main_table.resizeColumnsToContents()
		
		# self.main_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
		# QHeaderView.setSectionsClickable()
		
		self.main_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # cho phép chọn thành dòng
		# self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)  # cho phép chọn 1 dòng
		# self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)  # cái này là ko cho bấm vào chọn
		
		# self.main_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)  # không cho edit
		# self.main_table.setEditTriggers(QAbstractItemView.EditTrigger.EditKeyPressed)  # không cho edit
		
		# ------------------------ Set FIxed tiêu đề ko cho di chuyển
		
		self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumber.column_do_lech.value,
			QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
		self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumber.column_time.value,
			QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
		
		self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumber.column_duaration.value,
			QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
		
		self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumber.column_sub_text.value,
			QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
		
		# self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumber.column_sub_translate.value,
		# 	QHeaderView.ResizeMode.ResizeToContents)
		#
		# self.main_table.horizontalHeader().setResizeContentsPrecision(ColumnNumber.column_sub_translate.value) # gian cách vừa với content
		#
		# self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumber.column_position_trans.value,
		# 	QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
		#
		# tao menucontext
		# self.main_table.viewport().installEventFilter(self)
		self.main_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.main_table.customContextMenuRequested.connect(self.generateMenu)
	
	# self.model.se
	
	def setup_connections (self):
		##==================Các sự kiện của table ========
		self.main_table.doubleClicked.connect(self.cellDoubleClicked)  # nhận đc row và colum
		# self.main_table.itemDoubleClicked.connect(self.itemDoubleClicked)  # nhận đc item
		# self.main_table.itemChanged.connect(self.itemDataChanged)  # nh# nhận đc item
		self.model.dataChanged.connect(self.itemDataChanged)
		self.main_table.selectionModel().selectionChanged.connect(self._rowSelectionChanged)  # nhận đc item
		# self.main_table.itemSelectionChanged.connect(self.removeAllCheckedItem)  # nhận đc item
		# self.main_table.horizontalHeader().sectionPressed.connect(self.onHeaderClicked)  # bắt sự kiện ng dùng nhấn vào tiêu đề
		# ========== Các sự kiện cho thread ============
		# self.manage_thread.statusChanged.connect(self.status_thread_changed)
		self.manage_thread_pool.resultChanged.connect(self.resultThreadChanged)
		self.thread_limit.resultChanged.connect(self.resultThreadChanged)
	
	# # ========== Các sự kiện cho menu contentext ============
	# self.act_concat_sub.triggered.connect(self.signal_concat_sub)
	# self.act_summary.triggered.connect(self.signal_summary)
	# self.act_translate_again.triggered.connect(self.signal_translate_again)
	
	#
	
	def selectListRow (self, list_row):
		
		selection = QItemSelection()
		for row in list_row:
			self.main_table.selectRow(row)
			model_index = self.model.index(row, 0)
			# Select single row.
			selection.select(model_index, model_index)  # top left, bottom right identical
		mode = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
		# Apply the selection, using the row-wise mode.
		resultselection = self.main_table.selectionModel()
		resultselection.select(selection, mode)
	
	def onHeaderClicked (self, logicalIndex):
		if logicalIndex == 0:
			self.is_check_all = not self.is_check_all
			if self.is_check_all:
				# self.main_table.horizontalHeaderItem(0).setIcon(self.icon_checked)
				# self.main_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.icon_checked,""))
				self.main_table.selectAll()
			else:
				# self.main_table.horizontalHeaderItem(0).setIcon(self.icon_unchecked)
				# self.main_table.setHorizontalHeaderItem(0,QTableWidgetItem(self.icon_unchecked,""))
				self.main_table.clearSelection()
	
	def itemCheckboxTable (self, isCheck):
		icon = ""
		if isCheck:
			icon = self.icon_checked
		else:
			icon = self.icon_unchecked
		
		item = QTableWidgetItem(icon, "")
		item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
		# if row_number % 2 == 0:
		# 	item.setBackground(QColor(91, 91, 91))
		# else:
		# 	item.setBackground(QColor(135, 135, 135))
		return item
	
	@Slot(QItemSelection, QItemSelection)
	def _rowSelectionChanged (self, selected, deselected):  # emit bên widget kia kết nối với resultChanged  để nhận thông tin qua các widget khác nhau
		# print(selected)
		# for ix in selected.indexes():
		# 	print(ix.data())
		self.manage_thread_pool.resultChanged.emit(ROW_SELECTION_CHANGED_TABLE_ADD_SUB, ROW_SELECTION_CHANGED_TABLE_ADD_SUB, self.main_table.currentIndex().row() + 1)
	
	def create_layouts (self):
		self.widget_layout = QVBoxLayout()
		self.widget_layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.widget_layout)
	
	def add_widgets_to_layouts (self):
		self.widget_layout.addWidget(self.main_table)
	
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
	
	@decorator_try_except_class
	def displayTable (self, data, db_app: ConfigAppModel):
		""" Mô tả: Hiển thị dữ liệu vừa lấy được trong video """
		self.db_app = db_app
		self.isLoadSrtFinish = True
		if data == []:
			return
		self.show_data(data=data)
	
	def show_data (self, **kwargs):
		# print("Show")
		data = kwargs["data"]
		
		list_data = []
		list_data_origin = []
		# ["Ratio", "Time", "Duration", "Text"]
		for item in data:
			# [ time_, content_]
			button = self.itemButtonAction(0, ["", "", "", "", ""])
			index = self.model.index(0, 0)  # Chọn cell ở hàng đầu tiên và cột đầu tiên
			self.main_table.setIndexWidget(index, button)
			
			list_data.append(["", item[0], "", item[1]])
			list_data_origin.append(["", item[0], "", item[1]])
		# print(list_data)
		
		# self.model = TableModel(list_data)
		self.data_sub_origin = list_data_origin
		self.model.update_data = list_data
		
		self.main_table.selectRow(0)
		self.manage_thread_pool.resultChanged.emit(LOAD_SUB_IN_TABLE_FINISHED, LOAD_SUB_IN_TABLE_FINISHED, 1)
		self.isLoadSrtFinish = False
	
	def itemButtonAction (self, row_number, data):
		
		widget = QWidget()
		
		layout_action = QHBoxLayout()
		
		widget.btn_open_folder_file = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-folder1.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
			app_parent=self,
			tooltip_text="Mở thư mục lưu"
		
		)
		
		# widget.btn_open_folder_file.setDisabled(True)
		index2 = QPersistentModelIndex(self.main_table.model().index(row_number, ColumnNumber.column_chuc_nang.value))
		widget.btn_open_folder_file.clicked.connect(lambda: self.clickButtonAction(data, index2, "btn_open_folder_file"))
		
		widget.btn_play = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("play.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#03b803",
			icon_color_hover="#1be21b",
			icon_color_pressed="#4fc65e",
			app_parent=self,
			tooltip_text="Play"
		
		)
		
		# widget.btn_play.setObjectName("btn_pause")
		index3 = QPersistentModelIndex(self.main_table.model().index(row_number,  ColumnNumber.column_chuc_nang.value))
		widget.btn_play.clicked.connect(lambda: self.clickButtonAction(data, index3, "btn_play"))
		
		widget.btn_stop = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("stop.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#f24646",
			icon_color_hover="#f24646",
			icon_color_pressed="#790a1a",
			app_parent=self,
			tooltip_text="Stop"
		
		)
		
		index4 = QPersistentModelIndex(self.main_table.model().index(row_number,  ColumnNumber.column_chuc_nang.value))
		widget.btn_stop.clicked.connect(lambda: self.clickButtonAction(data, index4, "btn_stop", btn=widget.btn_stop))
		
		layout_action.addWidget(widget.btn_play)
		layout_action.addWidget(widget.btn_open_folder_file)
		layout_action.addWidget(widget.btn_stop)
		# layout_action.setAlignment(Qt.AlignmentFlag.AlignHCenter)
		layout_action.setAlignment(Qt.AlignmentFlag.AlignVCenter)
		layout_action.setContentsMargins(0, 0, 10, 0)
		
		widget.setLayout(layout_action)
		self.setDisabledButton(widget, True)
		# self.listIItemAction[(row_number)] = widget
		return widget
	
	# @decorator_try_except_class
	def clickButtonAction (self, data: str, index: QPersistentModelIndex, type, **kwargs):
		path_output = data[0]  # co 1 phần tu, cái này được cấu hình sẵn
		# print(file_ouput)
		
		if type == "btn_stop":
			print("Stop")
			kwargs.get("btn").set_icon_color = "#c3ccdf"
			kwargs.get("btn").icon_color = "#c3ccdf"
			kwargs.get("btn").icon_color_hover = "#c3ccdf"
			kwargs.get("btn").icon_color_pressed = "#c3ccdf"
			# self.manage_thread_pool.resultChanged.emit(STOP_GET_VOICE, STOP_GET_VOICE, index.row())
		
		# if type == "btn_open_folder_file":
		# 	file_ouput = self.main_table.item(index.row(), self.column_name_video_ouput).text()
		#
		# 	open_and_select_file(file_ouput)
		# # webbrowser.open(path_output)
		
		elif type == "btn_play":
			file_ouput = self.main_table.item(index.row(), self.column_name_video_ouput).text()
			
			# file_output = JOIN_PATH(path_output,name_video)
			
			if os.path.isfile(file_ouput):
				os.startfile(file_ouput)
			else:
				return PyMessageBox().show_warning("Thông báo", "File Không Tồn Tại")
	
	def setDisabledButton (self, widget: QWidget, status):
		
		widget.btn_open_folder_file.setDisabled(status)
		widget.btn_play.setDisabled(status)
		
		if status is True:  # disabled
			
			widget.btn_open_folder_file.set_icon_color = "#c3ccdf"
			widget.btn_open_folder_file.icon_color = "#c3ccdf"
			widget.btn_open_folder_file.icon_color_hover = "#c3ccdf"
			widget.btn_open_folder_file.icon_color_pressed = "#c3ccdf"
			
			widget.btn_play.set_icon_color = "#c3ccdf"
			widget.btn_play.icon_color = "#c3ccdf"
			widget.btn_play.icon_color_hover = "#c3ccdf"
			widget.btn_play.icon_color_pressed = "#c3ccdf"
		else:
			
			widget.btn_open_folder_file.set_icon_color = "#f5ca1e"
			widget.btn_open_folder_file.icon_color = "#f5ca1e"
			widget.btn_open_folder_file.icon_color_hover = "#ffe270"
			widget.btn_open_folder_file.icon_color_pressed = "#d1a807"
			
			widget.btn_play.set_icon_color = "#03b803"
			widget.btn_play.icon_color = "#03b803"
			widget.btn_play.icon_color_hover = "#1be21b"
			widget.btn_play.icon_color_pressed = "#4fc65e"
		
		widget.btn_open_folder_file.repaint()
		widget.btn_play.repaint()
	
	# thread_pool.finishSingleThread(id_worker)
 
	def generateMenu (self, pos):
		x = pos.x() + 10
		y = pos.y() + 30
		self.menu.exec(self.main_table.mapToGlobal(QPoint(x, y)))
	
	def cellDoubleClicked (self, indexModel: QModelIndex):
		# print("cellDoubleClicked " + str(indexModel.row()))
		# print("column " + str(indexModel.column()))
		cau_hinh = json.loads(self.configCurrent.value)
		if cau_hinh.get("chinh_sua_thuong"):
			return
		data_sub = self.getDataRow(indexModel.row())
		# print(data_sub)
		if hasattr(self, 'model_AI'):
			if indexModel.column() == ColumnNumber.column_sub_text.value or indexModel.column() == ColumnNumber.column_sub_translate.value:
				dialog = PyDialogEditSub(self.manage_thread_pool, data_sub, self.model_AI, column_sub=indexModel.column())
				if dialog.exec():
					
					self.setValueItem(indexModel.row(), indexModel.column(), dialog.getValue())
				
				else:
					pass
	
	
	def itemDoubleClicked (self, item):
		print()
	
	# print(item)
	def split_sub_origin (self, **kwargs):
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		cau_hinh = kwargs["cau_hinh"]
		
		if self.model.rowCount() > 0:
			translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
			item = self.getValueItem(0, ColumnNumber.column_sub_text.value)
			
			lang_source = translator_server.language(item)
			for row in range(self.model.rowCount()):
				dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = self.getDataRow(row)
				
				if cau_hinh.get("split_sub_origin") is True:
					if 'jpn' in str(lang_source.result):
						parser = budoux.load_default_japanese_parser()
						content = sub_origin.strip().replace("\n", "")
						list_content = parser.parse(content)
					
					elif 'zho' in str(lang_source.result):  # tieng trun gian the
						parser = budoux.load_default_simplified_chinese_parser()
						content = sub_origin.strip().replace("\n", "")
						list_content = parser.parse(content)
					
					elif 'och' in str(lang_source.result):  # tieng trung quoc te
						parser = budoux.load_default_traditional_chinese_parser()
						content = sub_origin.strip().replace("\n", "")
						list_content = parser.parse(content)
					else:
						list_content = sub_origin.strip().replace("\n", " ").split(" ")
					
					list_text = []
					text_c = ''
					for index, text_ in enumerate(list_content):
						max_length = 20 if cau_hinh.get("max_character_inline_origin") is None else cau_hinh.get("max_character_inline_origin")
						
						if str(lang_source.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
							if len(text_c) + len(text_) > max_length:
								list_text.append(text_c.strip())
								text_c = ''
							text_c += text_
						else:
							if len(text_c.strip().split()) + 1 > max_length:
								list_text.append(text_c.strip())
								text_c = ''
							elif not text_c == '':
								if len(text_c.strip().split()) > max_length / 2 and text_c.strip()[
									-1] in '''.,!;?'"]:)>/\\}''':
									list_text.append(text_c.strip())
									text_c = ''
							text_c += text_ + " "
						if index == len(list_content) - 1:
							list_text.append(text_c.strip())
					self.manage_thread_pool.resultChanged.emit(UPDATE_TEXT_TABLE_ADD_SUB, UPDATE_TEXT_TABLE_ADD_SUB, (
						row, "\n".join(list_text), 'origin'))
				
				else:
					# continue
					if len(sub_origin.split("\n")) > 1:
						if str(lang_source.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
							content = sub_origin.strip().replace("\n", "")
						else:
							content = sub_origin.strip().replace("\n", " ")
						
						self.manage_thread_pool.resultChanged.emit(UPDATE_TEXT_TABLE_ADD_SUB, UPDATE_TEXT_TABLE_ADD_SUB, (
							row, content, 'origin'))
		thread_pool.finishSingleThread(id_worker)
		return cau_hinh
	
	def split_sub_translate (self, **kwargs):
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		cau_hinh = kwargs["cau_hinh"]
		item = self.getValueItem(0, ColumnNumber.column_sub_text.value)
		
		if self.model.rowCount() > 0 and not item == '':
			translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
			lang_source = translator_server.language(item)
			for row in range(self.model.rowCount()):
				dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = self.getDataRow(row)
				
				if cau_hinh.get("split_sub_translate") is True:
					if 'jpn' in str(lang_source.result):
						parser = budoux.load_default_japanese_parser()
						content = sub_translate.strip().replace("\n", "")
						list_content = parser.parse(content)
					
					elif 'zho' in str(lang_source.result):  # tieng trun gian the
						parser = budoux.load_default_simplified_chinese_parser()
						content = sub_translate.strip().replace("\n", "")
						list_content = parser.parse(content)
					
					elif 'och' in str(lang_source.result):  # tieng trung quoc te
						parser = budoux.load_default_traditional_chinese_parser()
						content = sub_translate.strip().replace("\n", "")
						list_content = parser.parse(content)
					else:
						list_content = sub_translate.strip().replace("\n", " ").split(" ")
					
					list_text = []
					text_c = ''
					for index, text_ in enumerate(list_content):
						max_length = 20 if cau_hinh.get("max_character_inline_translate") is None else cau_hinh.get("max_character_inline_translate")
						
						if str(lang_source.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
							if len(text_c) + len(text_) > max_length:
								list_text.append(text_c.strip())
								text_c = ''
							text_c += text_
						else:
							if len(text_c.strip().split()) + 1 > max_length:
								list_text.append(text_c.strip())
								text_c = ''
							elif not text_c == '':
								if len(text_c.strip().split()) > max_length / 2 and text_c.strip()[
									-1] in '''.,!;?'"]:)>/\\}''':
									list_text.append(text_c.strip())
									text_c = ''
							text_c += text_ + " "
						if index == len(list_content) - 1:
							list_text.append(text_c.strip())
					self.manage_thread_pool.resultChanged.emit(UPDATE_TEXT_TABLE_ADD_SUB, UPDATE_TEXT_TABLE_ADD_SUB, (
						row, "\n".join(list_text), 'trans'))
				
				else:
					# continue
					if len(sub_translate.split("\n")) > 1:
						
						if str(lang_source.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
							content = sub_translate.strip().replace("\n", "")
						else:
							content = sub_translate.strip().replace("\n", " ")
						
						self.manage_thread_pool.resultChanged.emit(UPDATE_TEXT_TABLE_ADD_SUB, UPDATE_TEXT_TABLE_ADD_SUB, (
							row, content, 'trans'))
		
		thread_pool.finishSingleThread(id_worker)
		return cau_hinh
	
	def gop_sub_tren_duoi (self):
		time_start = ''
		time_end = ''
		sub_origin_concat = ''
		sub_trans_concat = ''
		items_selected = self.main_table.selectionModel().selectedRows()
		row_start = items_selected[0].row()
		
		for index, item in enumerate(items_selected):
			
			time_line = self.getValueItem(row_start, ColumnNumber.column_time.value)
			start = time_line.split(' --> ')[0]
			end = time_line.split(' --> ')[1]
			
			if index == 0:
				time_start = start
			
			time_end = end
			sub_org = self.getValueItem(row_start, ColumnNumber.column_sub_text.value)
			sub_trans = self.getValueItem(row_start, ColumnNumber.column_sub_translate.value)
			# print(sub_org)
			sub_origin_concat += sub_org + " "
			sub_trans_concat += sub_trans + " "
			
			self.model.removeRow(row_start)
		
		self.model.insertRow(row_start)
		
		self.addDataRow(row_start, ["", f"{time_start} --> {time_end}", '', sub_origin_concat.strip("\n"),
									sub_trans_concat.strip("\n"), ''])
	
	def resultThreadChanged (self, id_worker, typeThread, result):
		
		if typeThread == SET_AUTO_SAVE_SUB:
			self.isTranslating = False
			self.isCheckingDoLech = False
		
		if typeThread == FILE_SRT_CURRENT:
			self.path_srt = result
		
		if typeThread == CLICK_DOC_THU_VOICE:
			self.signal_get_voice()
		
		# if typeThread == STOP_THREAD_TRANSLATE:
		# 	self.count_result_trans = 0
		# 	self.isTranslating = False
		# 	self.isCheckingDoLech = False
		
		if typeThread == TTS_GET_VOICE_FINISHED:
			# PyMessageBox().show_info("Thành Công","Đã Get Voice Thành Công")
			# print('thanh công')
			self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
			play_media_preview(result)
		
		if typeThread == XOA_SUB_DONG_SO:
			self.model.removeRow(result)
		
		if typeThread == GOP_SUB_DONG_TREN:
			ind_row = result
			ind_pre = (ind_row - 1)
			if ind_pre < 0:
				return PyMessageBox().show_warning("Cảnh báo", "Chỉ được gộp dòng bên dưới")
			
			self.selectListRow([ind_pre, ind_row])
			self.gop_sub_tren_duoi()
		if typeThread == GOP_SUB_DONG_DUOI:
			ind_row = result
			ind_next = (ind_row + 1)
			if ind_next > self.model.rowCount():
				return PyMessageBox().show_warning("Cảnh báo", "Chỉ được gộp dòng bên Trên")
			
			self.selectListRow([ind_row, ind_next])
			self.gop_sub_tren_duoi()
		
		if typeThread == THAY_THE_SUB_NEU_SUB_CO_DO_LECH_LON:
			ind_row, data, type_tts_sub = result
			time_line, text_sub = data
			column = ColumnNumber.column_sub_translate.value
			if type_tts_sub == 'origin':
				column = ColumnNumber.column_sub_text.value
			
			self.setValueItem(ind_row, column, text_sub)
			self.setValueItem(ind_row, ColumnNumber.column_time.value, time_line)
		
		if typeThread == THEM_KY_TU_NEU_SUB_CO_HAI_KYTU:
			ind_row, char, type_tts_sub = result
			column = ColumnNumber.column_sub_translate.value
			if type_tts_sub == 'origin':
				column = ColumnNumber.column_sub_text.value
			value = self.getValueItem(ind_row, column)
			
			self.setValueItem(ind_row, column, value + char)
		
		if id_worker == CENTER_POSITION_SUB:  # cái này phải dùng ID
			items_selected = self.main_table.selectionModel().selectedRows()
			if len(items_selected) < 1:
				return
 
			data_list =[]
			for item in items_selected:
				# if typeThread == POSITION_SUB_TRANS_CHANGED:
				# 	# sub_column = ColumnNumber.column_sub_translate.value
				# 	pos_column = ColumnNumber.column_position_trans.value
				# # type_sub = "trans"
				#
				# else:
					# sub_column = ColumnNumber.column_sub_original.value
				pos_column = ColumnNumber.column_duaration.value
				# type_sub = "origin"
				
				row_cur = item.row()
 
				x_sub_, y_sub_ = result
				if (x_sub_ or y_sub_) == '':
					text_pos = ''
				else:
					# text = f"{x_sub_center}{DELIMITER_POS_SUB}{y_sub_}"
					text_pos = f"{round(x_sub_, 2)}{DELIMITER_CENTER_POS_SUB}{round(y_sub_, 2)}"
					
				data_list.append((row_cur, pos_column, text_pos))
				
			self.thread_limit_update.submit(self.model.update_list_item, data_list)

				# self.setValueItem(row_cur, pos_column, text_pos)
			
			if items_selected[0].row() == 0:
				self.main_table.selectRow(1)
				self.main_table.selectRow(0)
			
			else:
				self.main_table.selectRow(items_selected[0].row() - 1)
				self.main_table.selectRow(items_selected[0].row())
		if typeThread == UPDATE_TY_LE_KHUNG_HINH_VIDEO:
			data = []
			for row in range(self.model.rowCount()):
				dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = self.getDataRow(row)
				# print(time, sub_origin, sub_translate, dolech, pos_ori, pos_trans)
				# data.append([time, sub_origin, sub_translate, pos_ori, pos_trans])
				data.append(["", time, "", sub_origin, sub_translate, ''])
			
			self.model.update_data = data
		
		if id_worker == POSITION_SUB_CHANGED:  # cái này phải dùng ID
			items_selected = self.main_table.selectionModel().selectedRows()
			if len(items_selected) < 1:
				return
			try:
				x, y = result
			except:
				x, y = "", ""
			data_list = []
			for item in items_selected:
				if (x or y) == '':
					text = ''
				else:
					text = f"{round(x, 2)}{DELIMITER_POS_SUB}{round(y, 2)}"
				row_current = item.row()
				if typeThread == POSITION_SUB_ORIGINAL_CHANGED:
					pos_column = ColumnNumber.column_duaration.value
					# self.setValueItem(row_current, ColumnNumber.column_position_origin.value, text)
				else :
					pos_column = ColumnNumber.column_position_trans.value

					# self.setValueItem(row_current, ColumnNumber.column_position_trans.value, text)
				data_list.append((row_current, pos_column, text))
			
			self.thread_limit_update.submit(self.model.update_list_item, data_list)
			
			# self.model.layoutChanged.emit()
		
		if typeThread == RESULT_CHECK_DO_LECH_VIDEO:
			
			self.isCheckingDoLech = True
			self.count_result_check_lech += 1
			self.list_row_do_lech_chunk.append(result)
			if len(self.list_row_do_lech_chunk) == int(30*(self.model.rowCount()/1000)):
				data = [item for item in self.list_row_do_lech_chunk]
				self.list_row_do_lech_chunk = []
				data_list = []
				for index, item_ in enumerate(data):
					row_number, type_tts_sub, tempo = item_
					data_list.append((row_number,ColumnNumber.column_do_lech.value, str(round(tempo, 2))))
				
				self.thread_limit_update.submit(self.model.update_list_item,data_list)
				# print('1111')
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_CHECK_LECH_SUB, "", self.count_result_check_lech)
			
			# self.setValueItem(int(row_number), ColumnNumber.column_do_lech.value, str(round(tempo, 2)))
			#
			if self.count_result_check_lech == self.model.rowCount():
				if len(self.list_row_do_lech_chunk) > 0:
					data_list = []
					for index, item_ in enumerate(self.list_row_do_lech_chunk):
						row_number, type_tts_sub, tempo = item_
						data_list.append((row_number, ColumnNumber.column_do_lech.value, str(round(tempo, 2))))
					
					self.thread_limit_update.submit(self.model.update_list_item, data_list)
					
				self.list_row_do_lech_chunk = []
				self.model.layoutChanged.emit()
				self.count_result_check_lech = 0
				
				self.isCheckingDoLech = False
				self.isCheckFinish = True
				
				# print(self.isCheckingDoLech)
				self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
				self.manage_thread_pool.resultChanged.emit(CHECK_LECH_SUB_FINISHED, CHECK_LECH_SUB_FINISHED, None)
		
		if typeThread == RESULT_CHECK_DO_LECH_VIDEO_PART:
			row_number, type_tts_sub, tempo = result
			# print(row_number, type_tts_sub, tempo)
			self.isCheckingDoLech = True
			row = self.listRowCheckDoLechPart[row_number]
			
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_CHECK_LECH_SUB, "", self.count_result_check_lech)
			
			self.setValueItem(row, ColumnNumber.column_do_lech.value, str(round(tempo, 2)))
			
			self.count_result_check_lech += 1
			
			if self.count_result_check_lech == len(self.listRowCheckDoLechPart):
				self.count_result_check_lech = 0
				self.isCheckingDoLech = False
				self.isCheckFinish = True
				self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
				self.manage_thread_pool.resultChanged.emit(CHECK_LECH_SUB_FINISHED, CHECK_LECH_SUB_FINISHED, None)
		
		if typeThread == SPLIT_SUB_TRANSLATE_IN_TABLE:
			
			if self.isCheckFinish:
				self.isCheckingDoLech = False
			
			self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
		
		if typeThread == CHANGE_STYLE_SUB:  # emit ở lúc lôad giao diện config
			cau_hinh = result
		
		if typeThread == UPDATE_TEXT_TABLE_ADD_SUB:
			row, content, type_sub = result
			
			if type_sub == 'origin':
				self.setValueItem(row, ColumnNumber.column_sub_text.value, content)
			
			elif type_sub == 'trans':
				self.setValueItem(row, ColumnNumber.column_sub_translate.value, content)
		#
		# if typeThread == RESULT_TRANSLATE_SUB and not result is None:
		#
		# 	if "row" in result.keys() and "text_trans" in result.keys():
		# 		self.isTranslating = True
		# 		if self.isCheckFinish:
		# 			self.isCheckingDoLech = True
		# 		self.count_result_trans = self.count_result_trans + 1
		# 		# self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB, "", self.count_result_trans)
		# 		#
		# 		# self.setValueItem(int(result["row"]), ColumnNumber.column_sub_translate.value,
		# 		# 	result["text_trans"])
		# 		self.list_row_trans_chunk.append(result)
		# 		if len(self.list_row_trans_chunk) == int(30 * (self.model.rowCount() / 1000)):
		# 			data = [item for item in self.list_row_trans_chunk]
		# 			self.list_row_trans_chunk = []
		# 			data_list = []
		# 			for index, item_ in enumerate(data):
		#
		# 				data_list.append((int(item_["row"]), ColumnNumber.column_sub_translate.value, item_["text_trans"]))
		#
		# 			self.thread_limit_update.submit(self.model.update_list_item, data_list)
		# 			# print('1111')
		# 		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB, "", self.count_result_trans)
		#
		# 	if self.count_result_trans == self.model.rowCount():
		# 		if len(self.list_row_trans_chunk) > 0:
		# 			data_list = []
		# 			for index, item_ in enumerate(self.list_row_trans_chunk):
		# 				data_list.append((
		# 				int(item_["row"]), ColumnNumber.column_sub_translate.value, item_["text_trans"]))
		#
		# 			self.thread_limit_update.submit(self.model.update_list_item, data_list)
		#
		# 		self.isTranslating = False
		# 		self.count_result_trans = 0
		# 		if self.isCheckFinish:
		# 			self.isCheckingDoLech = False
		# 		self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
		# 		self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_FINISHED, TRANSLATE_SUB_FINISHED, None)
		# 		self.refresh()
		#
		# if typeThread == RESULT_TRANSLATE_SUB_PART and not result is None:
		#
		# 	if "row" in result.keys() and "text_trans" in result.keys():
		# 		self.isTranslating = True
		# 		if self.isCheckFinish:
		# 			self.isCheckingDoLech = True
		#
		# 		self.count_result_trans = self.count_result_trans + 1
		# 		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB, "", self.count_result_trans)
		# 		row = self.listRowTransPart[int(result["row"])]
		# 		self.setValueItem(row, ColumnNumber.column_sub_translate.value,
		# 			result["text_trans"])
		#
		# 	if self.count_result_trans == len(self.listRowTransPart):
		# 		self.isTranslating = False
		# 		self.count_result_trans = 0
		# 		if self.isCheckFinish:
		# 			self.isCheckingDoLech = False
		# 		self.refresh()
		# 		self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
		# 		self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_FINISHED, TRANSLATE_SUB_FINISHED, None)
		#
		# if typeThread == LOAD_SUB_TRANSLATE_TXT:
		# 	self.isTranslating = True
		# 	data_list =[]
		# 	for index, sub in enumerate(result):
		# 		# self.setValueItem(index, ColumnNumber.column_sub_translate.value, sub)
		# 		data_list.append((index, ColumnNumber.column_sub_translate.value, sub))
		# 		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB, "", index + 1)
		#
		# 	self.thread_limit_update.submit(self.model.update_list_item, data_list)
		#
		# 	if self.isCheckFinish:
		# 		self.isCheckingDoLech = False
		# 	self.isTranslating = False
		# 	self.refresh()
		# 	self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
		# 	self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_FINISHED, TRANSLATE_SUB_FINISHED, None)
		#
		# if typeThread == LOAD_SUB_TRANSLATE_CHATGPT:
		# 	self.isTranslating = True
		# 	if self.isCheckFinish:
		# 		self.isCheckingDoLech = True
		# 	ind_chunk, data_res, chunk_split = result
		# 	# print(ind_chunk, data_res )
		# 	data_list = []
		# 	for index, item_ in enumerate(self.list_row_trans_chunk):
		# 		data_list.append((
		# 			int(item_["row"]), ColumnNumber.column_sub_translate.value, item_["text_trans"]))
		#
		# 	for index, sub in enumerate(data_res):
		# 		if ind_chunk == -1:
		# 			data_list.append((self.count_result_trans, ColumnNumber.column_sub_translate.value, sub))
		# 			# self.setValueItem(self.count_result_trans, ColumnNumber.column_sub_translate.value, sub)
		#
		# 		else:
		# 			data_list.append((index + (chunk_split * ind_chunk), ColumnNumber.column_sub_translate.value, sub))
		# 			# self.setValueItem(index + (chunk_split * ind_chunk), ColumnNumber.column_sub_translate.value, sub)
		#
		# 		self.count_result_trans = self.count_result_trans + 1
		#
		# 	self.thread_limit_update.submit(self.model.update_list_item, data_list)
		#
		# 	self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB, "", self.count_result_trans)
		# 	# print(self.count_result_trans,self.model.rowCount())
		# 	if self.count_result_trans == self.model.rowCount():
		# 		self.isTranslating = False
		# 		self.count_result_trans = 0
		# 		if self.isCheckFinish:
		# 			self.isCheckingDoLech = False
		# 		self.refresh()
		# 		self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
		# 		self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_FINISHED, TRANSLATE_SUB_FINISHED, None)
		#
		# if typeThread == LOAD_SUB_TRANSLATE_CHATGPT_PART:
		# 	self.isTranslating = True
		# 	if self.isCheckFinish:
		# 		self.isCheckingDoLech = True
		#
		# 	ind_chunk, data_res, chunk_split = result
		# 	for index, sub in enumerate(data_res):
		# 		if ind_chunk == -1:
		# 			row = self.listRowTransPart[self.count_result_trans]
		#
		# 		else:
		# 			row = self.listRowTransPart[index + (chunk_split * ind_chunk)]
		#
		# 		self.setValueItem(row, ColumnNumber.column_sub_translate.value, sub)
		#
		# 		self.count_result_trans = self.count_result_trans + 1
		# 		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB, "", self.count_result_trans)
		#
		# 	if self.count_result_trans == len(self.listRowTransPart):
		# 		self.isTranslating = False
		# 		self.count_result_trans = 0
		# 		if self.isCheckFinish:
		# 			self.isCheckingDoLech = False
		#
		# 		self.refresh()
		# 		self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
		# 		self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_FINISHED, TRANSLATE_SUB_FINISHED, None)
		#
	
	def itemDataChanged (self, item: QModelIndex, item2: QModelIndex):
		data_sub_timeline = self.getDataSub()
		# self.isTranslating = False
		if len(data_sub_timeline) > 0 and self.isTranslating is False and self.isCheckingDoLech is False:
			cau_hinh = json.loads(self.configCurrent.value)
			auto_save_sub = cau_hinh.get("auto_save_sub", False)
			
			if hasattr(self, 'path_srt') and auto_save_sub:
				writeFileSrt(self.path_srt, data_sub_timeline, 0)
				print("Đã save sub gốc")
	
	# if self.isLoadSrtFinish is False and self.isCheckingDoLech is False:
	# 	# print(item)
	# 	self.checkDoLechPart([item.row()])
	
	def checkDoLechPart (self, list_items_selected: list):
		self.listRowCheckDoLechPart = []
		self.count_result_check_lech = 0
		
		if len(list_items_selected) < 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn kiểm tra độ lệch")
		
		data = []
		
		for index, row in enumerate(list_items_selected):
			self.listRowCheckDoLechPart.append(row)
			# ["Ratio", "Time", "Duration", "Text"]
			
			AC,Ratio, Time, Duration, Text  = self.getDataRow(row)
			
			data.append([AC,Ratio, Time, Duration, Text])
		# print(data)
		self.manage_thread_pool.resultChanged.emit(CHECK_DO_LECH_TABLE_CHANGED_PART, CHECK_DO_LECH_TABLE_CHANGED_PART, data)
	
	
	def getDataSub (self):
		"""[dolech, time, pos_ori, sub_origin, sub_translate, pos_trans]"""
		
		data = []
		for row in range(self.model.rowCount()):
			# data.append([])
			# for column in range(self.model.columnCount()):
			
			AC,Ratio, Time, Duration, Text = self.getDataRow(row)
			# print(time, sub_origin, sub_translate, dolech, pos_ori, pos_trans)
			# data.append([time, sub_origin, sub_translate, pos_ori, pos_trans])
			data.append([AC,Ratio, Time, Duration, Text])
		return data
	
	# def deleteRow (self, row):
	# 	return self.model.removeRow(row)
	# def insertDataRow (self, row, data):
	# 	return self.model.insertRow()
	#
	def getValueItem (self, row, column):
		return self.model.data(self.model.index(row, column))
	
	def setValueItem (self, row, column, value):
		return self.model.update_item(row, column, value)
	
	def refresh (self):
		# print("Refreshing")
		self.model.layoutChanged.emit()
	
	def getDataRow (self, row):
		""":return (AC,Ratio, Time, Duration, Text)"""
		
		# """:return [time, sub_origin, sub_translate,do_lech, pos_ori, pos_trans]"""
		data = list(self.getValueItem(row, i) for i in range(self.model.columnCount()))
		return data
	
	
	def addDataRow (self, row, data):
		"""data: AC,Ratio, Time, Duration, Text"""
		
		for i in range(self.model.columnCount()):
			self.setValueItem(row, i, data[i])
	
	def getRandomTextSub (self):
		
		rad = random.randrange(0, self.model.rowCount() - 1)
		AC,Ratio, Time, Duration, Text = self.getDataRow(rad)
		return Text, rad
	
	def resetDataOrigin (self):
		# print(self.data_sub_origin)
		if len(self.data_sub_origin) > 0:
			self.model.update_data = [item.copy() for item in self.data_sub_origin]
