import os

from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Signal, QPersistentModelIndex, QEvent, QPoint, QItemSelection, QItemSelectionModel, Slot, \
	QCoreApplication
from PySide6.QtGui import QColor, QBrush, QKeyEvent
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QMenu, QTableWidgetItem, QAbstractItemView, \
	QAbstractScrollArea, QTableWidget, QHeaderView, QTableView

from gui.helpers.constants import ROW_SELECTION_CHANGED_TABLE_EXTRACT, RESULT_TRANSLATE_SUB_EXTRACT, \
	TRANSLATE_SUB_EXTRACT_FINISHED, LOAD_FILE_EXTRACT_FINISHED, LOAD_VIDEO_FROM_FILE_SRT_EXTRACT, \
	ITEM_TABLE_TIMELINE_EXTRACT_CHANGED, RESULT_RUN_DEMO_TIMELINE_EDIT_SUB, JOIN_PATH, APP_PATH, \
	SHOW_DATA_TABLE_TIMELINE_EXTRACT, TOGGLE_SPINNER, LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT, \
	UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, TOOL_CODE_MAIN, SETTING_APP_DATA, \
	LOAD_SUB_TRANSLATE_TXT_TABLE_EXTRACT, RESULT_TRANSLATE_SUB_EXTRACT_PART, \
	LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT_PART, TRANSLATE_SUB_PART_TAB_EXTRACT
from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from .model_timeline_addsub import TableAddModel, ColumnNumberTabEdit
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_messagebox.py_massagebox import PyMessageBox
from ...configs.config_resource import ConfigResource
from ...helpers.custom_logger import decorator_try_except_class
from ...helpers.func_helper import convertPathImportFFmpeg, getValueSettings, play_media_preview


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
			# self.selectRow(self.currentIndex().row() + 1)
			index = self.moveCursor(
				QtWidgets.QAbstractItemView.MoveDown, QtCore.Qt.NoModifier
			)
			command = self.selectionCommand(self.currentIndex(), event)
			self.selectionModel().setCurrentIndex(index, command)
		
		elif event.type() == QEvent.KeyPress and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
			if self.state() != QAbstractItemView.EditingState:
				self.edit(self.currentIndex())
		else:
			super().keyPressEvent(event)


class TableTimelineExtract(QWidget):
	rowSelectionChanged = Signal(int)
	
	def __init__ (self, manage_thread_pool: ManageThreadPool, manage_cmd):
		super().__init__()
		# SET STYLESHEET
		
		self.manage_thread_pool = manage_thread_pool  # tạo trước ui
		self.manage_cmd = manage_cmd
		self.listRowPause = {}
		self.listIItemAction = {}
		self.count_result_trans = 0
		self.resultThread = {}
		self.isHasSub = False
		self.isLoadSrtFinish = True
		self.listRowTransPart = []
		self.setMinimumHeight(200)
		self.listRowCheckDoLechPart = []
		self.data_sub_origin = []
		self.count_result_trans = 0
		self.count_result_pos = 0
		self.total_pos_update = 0
		self.count_split_sub = 0
		self.count_result_check_lech = 0
		self.resultThread = {}
		self.isLoadSrtFinish = True
		self.isCheckingDoLech = True
		self.isCheckFinish = False
		self.getXCenterSub = None
		self.chunk_split = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting').get('chunk_split', 5)
		
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
		self.main_table = TableView()
		self.main_table.setObjectName(u"tableWidget")
		# self.main_table.setAlternatingRowColors(True)
		# tạo Nút CheckBox trên tiêu đề
		
		# menu ngữ cảnh
		self.menu = QMenu()
		
		self.menu.addAction("Dịch Lại", self.signal_translate_again)
		self.menu.addAction("Xóa", self.signal_remove)
	
	# self.timer = QTimer()  # thực hiện việc gi đó sau khoảng thời gian
	def signal_remove (self):
		items_selected = self.main_table.selectionModel().selectedRows()
		if len(items_selected) < 1:
			return PyMessageBox().show_warning('WARNING', "Please select the line you want to delete")
		
		req = PyMessageBox().show_question("CONFIRM", "Are you sure you want to delete ?")
		row_start = items_selected[0].row()
		
		if req is True:
			row_pre = 0
			for index, item in enumerate(items_selected):
				if not index == 0:
					if not (item.row() - row_pre) == 1:
						return PyMessageBox().show_warning('WARNING', "Chỉ được xóa các hàng liền nhau")
				row_pre = item.row()
			
			for index, item in enumerate(items_selected):
				self.model.removeRows(item.row())
		else:
			return
		self.selectRowDown()
		self.main_table.selectRow(row_start)
	
	def signal_translate_again (self):
		self.listRowTransPart = []
		
		items_selected = self.main_table.selectionModel().selectedRows()
		if len(items_selected) < 1:
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn dịch")
		
		data = []
		
		for index, item in enumerate(items_selected):
			self.listRowTransPart.append(item.row())
			# ("Ratio", "Time", "Pos Ori", "Original", "Translation", "Pos Trans")
			time, origin, translate = self.getDataRow(item.row())
			
			data.append([time, origin, translate])
		self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_PART_TAB_EXTRACT, TRANSLATE_SUB_PART_TAB_EXTRACT, data)
	
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
	
	def setup_table (self):
		# ========== Cài đặt cho table============
		data = [["", "", ""]]
		name_column = ["Time", "Original", "Translation"]
		self.model = TableAddModel(data, name_column)
		self.main_table.setModel(self.model)
		
		self.main_table.setAlternatingRowColors(True)  # hiện màu dòng xen kẽ
		
		self.main_table.horizontalHeader().setStretchLastSection(True)  # cái này cho kéo dãn full table
		# self.main_table.horizontalHeader().setDefaultSectionSize(126)
		self.main_table.horizontalHeader().setMinimumSectionSize(37)
		self.main_table.verticalHeader().setDefaultSectionSize(35)
		self.main_table.verticalHeader().setSectionResizeMode(
			QHeaderView.ResizeMode.ResizeToContents)  # làm cho content xuống dòng
		# QHeaderView.setSectionsClickable()
		
		self.main_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # cho phép chọn thành dòng
		self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # cho phép chọn 1 dòng
		# self.main_table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # không cho edit
		
		self.main_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # cho phép chọn thành dòng
		self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # cho phép chọn 1 dòng
		# self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)  # cái này là ko cho bấm vào chọn
		
		# self.main_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)  # không cho edit
		
		# ------------------------ Set FIxed tiêu đề ko cho di chuyển
		
		self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumberTabEdit.column_avatar.value,
                                                                QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
		
		# self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumber.column_original.value,
		#                                                         QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
		
		# tao menucontext
		self.main_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.main_table.customContextMenuRequested.connect(self.generateMenu)
	
	def generateMenu (self, pos):
		x = pos.x() + 10
		y = pos.y() + 30
		self.menu.exec(self.main_table.mapToGlobal(QPoint(x, y)))
	def setup_connections (self):
		##==================Các sự kiện của table ========
		
		# self.main_table.doubleClicked.connect(self.cellDoubleClicked)  # nhận đc row và colum
		# self.main_table.itemDoubleClicked.connect(self.itemDoubleClicked)  # nhận đc item
		# self.main_table.itemChanged.connect(self.itemDataChanged)  # nh# nhận đc item
		self.model.dataChanged.connect(self.itemDataChanged)
		self.main_table.selectionModel().selectionChanged.connect(self._rowSelectionChanged)  # nhận đc item
		
		self.manage_thread_pool.resultChanged.connect(self.resultThreadChanged)
	
	def selectListRow (self, list_row):
		
		selection = QItemSelection()
		for row in list_row:
			self.main_table.selectRow(row)
			model_index = self.model.index(row, 0)
			# Select single row.
			selection.select(model_index, model_index)  # top left, bottom right identical
		mode = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
		# Apply the selection, using the row-wise mode.
		self.resultselection = self.main_table.selectionModel()
		self.resultselection.select(selection, mode)
	
	@Slot(QItemSelection, QItemSelection)
	def _rowSelectionChanged (self, selected, deselected): # emit bên widget kia kết nối với resultChanged  để nhận thông tin qua các widget khác nhau
		self.manage_thread_pool.resultChanged.emit(ROW_SELECTION_CHANGED_TABLE_EXTRACT,
			ROW_SELECTION_CHANGED_TABLE_EXTRACT,
			self.main_table.currentIndex().row() + 1)
	
	def create_layouts (self):
		self.widget_layout = QVBoxLayout(self)
		self.widget_layout.setContentsMargins(0, 0, 0, 0)
	
	def add_widgets_to_layouts (self):
		self.widget_layout.addWidget(self.main_table)
 
	@decorator_try_except_class
	def displayTable (self, data, path_video, sequences):
		""" Mô tả: Hiển thị dữ liệu vừa lấy được trong video """
		self.isLoadSrtFinish = True
		if data == []:
			return
		self._show_data(data,path_video, sequences)
		# self.manage_thread_pool.start(self._show_data, SHOW_DATA_TABLE_TIMELINE_EXTRACT, SHOW_DATA_TABLE_TIMELINE_EXTRACT, data=data, path_video=path_video, sequences=sequences)
	
	def _show_data (self,data,path_video, sequences):
		
		self.model.update_data = data
		
		self.main_table.selectRow(0)
		self.isHasSub = True
		self.path_video = path_video
		self.isLoadSrtFinish = False
		
		self.manage_thread_pool.resultChanged.emit(LOAD_VIDEO_FROM_FILE_SRT_EXTRACT, LOAD_VIDEO_FROM_FILE_SRT_EXTRACT, {
			'sequences': sequences, 'path_video': path_video})
		
	
	def itemDataChanged (self, item):
		if self.isLoadSrtFinish == False:
			# print(1111111)
			self.manage_thread_pool.resultChanged.emit(ITEM_TABLE_TIMELINE_EXTRACT_CHANGED, ITEM_TABLE_TIMELINE_EXTRACT_CHANGED, "")
	
	def item_table (self, row_number, data):
		
		item = QTableWidgetItem(str(data))
		item.setForeground(QColor("#ffffff"))
		return item
	
	def resultThreadChanged (self, id_worker, typeThread, result):
		
		# if typeThread == SHOW_DATA_TABLE_TIMELINE_EXTRACT:
		# 	# ============== thêm nút chức năng=======
		# 	for row_number in reversed(range(self.main_table.rowCount())):
		# 		item_widget_action = self.itemButtonAction(row_number)
		# 		self.main_table.setCellWidget(row_number, self.column_action, item_widget_action)
		#
		# 	self.isHasSub = True
		# 	path_video, sequences = result
		# 	self.path_video = path_video
		# 	self.isLoadSrtFinish = False
		#
		# 	self.manage_thread_pool.resultChanged.emit(LOAD_VIDEO_FROM_FILE_SRT_EXTRACT, LOAD_VIDEO_FROM_FILE_SRT_EXTRACT, {
		# 		'sequences': sequences, 'path_video': path_video})
		
		# if typeThread == LOAD_FILE_EXTRACT_FINISHED:
		# 	# ============== xóa dữ liệu cũ =======
		# 	for i in reversed(range(self.main_table.rowCount())):
		# 		self.main_table.removeRow(i)
		#
		if typeThread == RESULT_TRANSLATE_SUB_EXTRACT and not result is None:
			if "row" in result.keys() and "text_trans" in result.keys():
				self.count_result_trans = self.count_result_trans + 1
				self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "", self.count_result_trans)
				
				# item = self.item_table(int(result["row"]), result["text_trans"])
				# self.main_table.setItem(int(result["row"]), self.column_sub_translate, item)
				self.setValueItem(int(result["row"]), ColumnNumberTabEdit.column_translated.value,
					result["text_trans"])
			
			if self.count_result_trans == self.model.rowCount():
				self.count_result_trans = 0
				self.refresh()

				self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED, TRANSLATE_SUB_EXTRACT_FINISHED, None)
				self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
				
				# PyMessageBox().show_info("Thông báo", "Dịch sub hoàn thành!")
				
		if typeThread == RESULT_TRANSLATE_SUB_EXTRACT_PART and not result is None:
			
			if "row" in result.keys() and "text_trans" in result.keys():
				# print(result)
				# print(self.listRowTransPart)
				self.count_result_trans = self.count_result_trans + 1
				self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "", self.count_result_trans)
				row = self.listRowTransPart[int(result["row"])]
				self.setValueItem(row, ColumnNumberTabEdit.column_translated.value,
					result["text_trans"])
			
			if self.count_result_trans == len(self.listRowTransPart):
				self.count_result_trans = 0
				if self.isCheckFinish:
					self.isCheckingDoLech = False
				self.refresh()
				self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
				self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED, TRANSLATE_SUB_EXTRACT_FINISHED, None)
				
		if typeThread == LOAD_SUB_TRANSLATE_TXT_TABLE_EXTRACT:
			for index, sub in enumerate(result):
				self.setValueItem(index, ColumnNumberTabEdit.column_translated.value, sub)
				
				self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "", index + 1)
			self.refresh()

			self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
			self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED, TRANSLATE_SUB_EXTRACT_FINISHED, None)
			
			# PyMessageBox().show_info("Thông báo", "Dịch sub hoàn thành!")
		
		
		if typeThread == LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT:
			
			ind_chunk, data_res, chunk_split = result
			for index, sub in enumerate(data_res):
				if ind_chunk == -1:
 
					self.setValueItem(self.count_result_trans, ColumnNumberTabEdit.column_translated.value, sub)
				else:
					self.setValueItem(index + (chunk_split * ind_chunk), ColumnNumberTabEdit.column_translated.value, sub)

					# item = self.main_table.item(index + (chunk_split * ind_chunk), self.column_sub_translate)
					# item.setText(sub)
				# self.main_table.setItem(self.count_result_trans, self.column_sub_translate, self.item_table(self.count_result_trans, sub))  # sub dịch
				
				self.count_result_trans = self.count_result_trans + 1
				self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "", self.count_result_trans)
			
			if self.count_result_trans == self.model.rowCount():
				self.count_result_trans = 0
				self.refresh()

				self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
				self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED, TRANSLATE_SUB_EXTRACT_FINISHED, None)
				
				PyMessageBox().show_info("Thông báo", "Dịch sub hoàn thành!")
	
		if typeThread == LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT_PART:
			if self.isCheckFinish:
				self.isCheckingDoLech = True
			
			ind_chunk, data_res, chunk_split = result
			for index, sub in enumerate(data_res):
				if ind_chunk == -1:
					row = self.listRowTransPart[self.count_result_trans]
				
				else:
					row = self.listRowTransPart[index + (chunk_split * ind_chunk)]
				
				self.setValueItem(row, ColumnNumberTabEdit.column_translated.value, sub)
				
				self.count_result_trans = self.count_result_trans + 1
				self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "", self.count_result_trans)
			
			if self.count_result_trans == len(self.listRowTransPart):
				self.count_result_trans = 0
				if self.isCheckFinish:
					self.isCheckingDoLech = False
				
				self.refresh()
				self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
				self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED, TRANSLATE_SUB_EXTRACT_FINISHED, None)
	def getValueItem (self, row, column):
		return self.model.data(self.model.index(row, column))
	
	def setValueItem (self, row, column, value):
		return self.model.update_item(row, column, value)
	
	def refresh (self):
		# print("Refreshing")
		self.model.layoutChanged.emit()
	
	def getDataRow (self, row):
		"""["Time", Origin", "Trans"]"""
		
		# """:return [time, sub_origin, sub_translate,do_lech, pos_ori, pos_trans]"""
		data = list(self.getValueItem(row, i) for i in range(self.model.columnCount()))
		return data
	
	
	def addDataRow (self, row, data):
		"""["Time", Origin", "Trans"]"""
		
		for i in range(self.model.columnCount()):
			self.setValueItem(row, i, data[i])
	
	def getDataSub (self):
		"""["Time", Origin", "Trans"]"""
		
		data = []
		for row in range(self.model.rowCount()):
			time, origin, translate = self.getDataRow(row)
			if origin != '':
				data.append([time, origin, translate])
		return data
