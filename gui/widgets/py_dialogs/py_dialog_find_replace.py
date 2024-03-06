import os.path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QCheckBox, \
	QLineEdit, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, QPlainTextEdit, QFileDialog

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN, APP_PATH
from gui.helpers.func_helper import getValueSettings
from gui.helpers.server import TYPE_TTS_SUB, TypeSubEnum
from gui.widgets.py_combobox import PyComboBox
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_table_widget.model_timeline_addsub import ColumnNumberTabEdit

style = '''
QDialog {{
	background-color: {_bg_color};
	font-size:15px;
	font-weight:bold;
    
}}
QLabel{{
 color: {_color}
}}

'''


class PyDialogFindReplace(QDialog):
	def __init__ (self, groupbox_timeline, manage_thread_pool, data_sub):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		self.groupbox_timeline = groupbox_timeline
		self.manage_thread_pool = manage_thread_pool
		self.data_sub = data_sub
		
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		# self.setMinimumWidth(900)
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Find & Replace")
		
		# self.setMinimumHeight(height)
		self.setMinimumWidth(800)
		
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		
		self.buttonSave = QPushButton("Close")
		self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonFindCount = QPushButton("Tìm Kiếm")
		

		
		self.buttonFindCount.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonReplace = QPushButton("Thay Nội Dung Dòng Này")
		self.buttonReplace.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonRemove = QPushButton("Xóa Dòng Này")
		self.buttonRemove.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonReplaceALL = QPushButton("Thay Thế Tất Cả")
		self.buttonReplaceALL.setCursor(Qt.CursorShape.PointingHandCursor)
		
		huong_dan = "B1: Chọn loại tìm kiếm từ SUB GỐC hay SUB DỊCH"
		huong_dan += "\n\nB2: Nhập từ vào ô Tìm kiếm, bấm nút TÌM TIẾP để tìm dòng sub chứa nội dung"
		huong_dan += "\n\nB3: Nếu có dòng nào kiếm thấy nó sẽ hiện ở ô Nội Dung"
		huong_dan += "\n\nB4: Chỉnh sửa lại rồi bấm THAY THẾ hoặc XÓA DÒNG đó đi"
		huong_dan += "\n\nLƯU Ý:"
		huong_dan += "\n - Thay thế 1 dòng sẽ thay thế lại nội dung của dòng đó bằng nội dung khác"
		huong_dan += "\n - Thay thế Tất Cả sẽ thay thế lại nội dung trùng bằng nội dung được thay trên tất cả dòng sub"
		# huong_dan += "\n\nNếu chưa ưng ý câu rút gọn bạn có thể bấm lại nút RÚT GỌN đến khi nào cảm thấy ok thì bấm LƯU để cập nhật"
		# huong_dan += "\n\nHoặc bạn có thể chỉnh sửa trực tiếp Nội Dung Rút Gọn sao cho phù hợp."
		# huong_dan += "\n\nLưu ý các câu ngắn chỉ 1 vài từ sẽ không thể rút gọn được mà bạn phải tự sửa"
		self.text_huongdan = QPlainTextEdit()
		self.text_huongdan.setReadOnly(True)
		self.text_huongdan.setFixedHeight(250)
		self.text_huongdan.setPlainText(huong_dan)
		self.text_huongdan.setProperty("class", "dialog_info")
		
		self.lb_type_tts_sub = QLabel("Loại Sub:")
		self.cb_type_tts_sub = PyComboBox()
		self.cb_type_tts_sub.addItems(TYPE_TTS_SUB.values())
		
		self.label_status = QLabel()
		self.lb_find = QLabel("Nhập nội dung cần tìm kiếm:")
		self.input_find = QLineEdit()
		
		self.lb_replace = QLabel("Nhập Nội dung thay thế:")
		self.input_replace = QPlainTextEdit()
		self.input_replace.setMaximumHeight(100)
		
		self.lb_file_loc = QLabel("File Lọc Từ:")
		self.btn_dialog_file_loc = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.input_file_loc = QLineEdit()
		self.input_file_loc.setReadOnly(True)
		
		# self.lb_inhoa = QLabel("")
		self.cb_inhoa = QCheckBox("Phân biệt chữ hoa thường")
		self.cb_tu_giong_nhau = QCheckBox("Chỉ thay thế từ giống nhau")
		self.cb_tu_giong_nhau.setChecked(True)
	
	def modify_widgets (self):
		# self.text_goc.setPlainText(self.item_sub)
		pass
	
	
	def create_layouts (self):
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.app_layout.setSpacing(0)
		
		self.btn_layout = QHBoxLayout()
		
		self.content_frame = QWidget()
		
		self.groupbox_show_sub_layout = QGridLayout()
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
		self.btn_file_layout = QHBoxLayout()
	
	# self.content_layout.setSpacing(0)
	
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.text_huongdan)
		self.content_layout.addWidget(self.lb_type_tts_sub)
		self.content_layout.addWidget(self.cb_type_tts_sub)
		self.content_layout.addWidget(QLabel())
		
		self.content_layout.addWidget(self.lb_find)
		self.content_layout.addWidget(self.input_find)
		self.content_layout.addWidget(QLabel())
		self.content_layout.addWidget(self.lb_replace)
		self.content_layout.addWidget(self.input_replace)
		
		self.content_layout.addWidget(QLabel())
		
		self.content_layout.addWidget(self.lb_file_loc)
		self.content_layout.addWidget(self.btn_dialog_file_loc)
		self.content_layout.addLayout(self.btn_file_layout)
		self.content_layout.addWidget(self.cb_inhoa)
		self.content_layout.addWidget(self.cb_tu_giong_nhau)
		
		self.btn_file_layout.addWidget(self.btn_dialog_file_loc)
		self.btn_file_layout.addWidget(self.input_file_loc)
		
		self.content_layout.addLayout(self.btn_layout)
		
		self.btn_layout.addWidget(self.label_status, 30)
		self.btn_layout.addWidget(self.buttonFindCount, 15)
		self.btn_layout.addWidget(self.buttonRemove, 15)
		self.btn_layout.addWidget(self.buttonReplace, 15)
		self.btn_layout.addWidget(self.buttonReplaceALL, 15)
		self.btn_layout.addWidget(self.buttonSave, 10)
		self.btn_layout.addWidget(QLabel(), 30)
	
	# self.btn_layout.addWidget(self.buttonCancel)
	# self.btn_layout.addWidget(self.label_do_lech, 30, alignment=Qt.AlignmentFlag.AlignRight)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.accept)
		self.buttonFindCount.clicked.connect(self.fn_find)
		self.buttonReplace.clicked.connect(self.fn_replace)
		self.buttonReplaceALL.clicked.connect(self.fn_replaceall)
		self.buttonRemove.clicked.connect(self.fn_remove)
		self.btn_dialog_file_loc.clicked.connect(self.openDialogFile)
		self.input_find.returnPressed.connect(self.fn_find)

		self.manage_thread_pool.resultChanged.connect(self.resultThreadChanged)
	
	def openDialogFile (self):
		path_file, _ = QFileDialog.getOpenFileName(self, caption='Chọn file txt',
			dir=(APP_PATH), filter='File Txt (*.txt)')
		
		self.input_file_loc.setText(path_file)
	
	def resultThreadChanged (self, id_worker, typeThread, result):
		# print(typeThread)
		pass
	
	# if typeThread == SUMMARY_SUB_IN_TABLE:
	# 	if result is False:
	# 		return self.label_status.setText("Server Đang Bận Vui lòng Thử Lại Sau")
	# 	self.text_rutgon.clear()
	# 	self.text_rutgon.setPlainText(result)
	# 	self.label_status.setText("Ok")
	# 	if self.spiner.is_spinning:
	# 		self.spiner.stop()
	
	
	def fn_replace (self):
		if hasattr(self, 'row_curr'):
			time, sub_origin, sub_translate = self.data_sub[self.row_curr]
			text_replace = self.input_replace.toPlainText()
			
			if self.cb_type_tts_sub.currentIndex() == TypeSubEnum.origin.value:
				column = ColumnNumberTabEdit.column_original.value
				self.data_sub[self.row_curr] = [time, text_replace, sub_translate]
			else:
				column = ColumnNumberTabEdit.column_translated.value
				self.data_sub[self.row_curr] = [time, sub_origin, text_replace]
				
			self.groupbox_timeline.setValueItem(self.row_curr, column, text_replace)
			self.groupbox_timeline.refresh()

	def fn_replaceall (self):
		
		list_filter = []
		
		if self.input_file_loc.text() == "":
			if self.input_replace.toPlainText() == "":
				return PyMessageBox().show_warning('Cảnh Báo', "Nội dung Thay Thế không được trống")
			if self.input_find.text() == "":
				return PyMessageBox().show_warning('Cảnh Báo', "Nội dung Tìm Kiếm không được trống")
			text_find = self.input_find.text()
			text_replace = self.input_replace.toPlainText()
			list_filter.append([text_find, text_replace])
		else:
			file_loc = self.input_file_loc.text()
			name, ext = os.path.splitext(file_loc)
			
			if not os.path.exists(file_loc):
				return PyMessageBox().show_warning('Cảnh Báo', "Không tìm thấy file")
			if not ext.lower() in ['.txt']:
				return PyMessageBox().show_warning("Thông báo", f"Chỉ hỗ trợ file txt theo cấu trúc từng hàng text_find|text_replace")
			with open(file_loc, 'r', encoding='utf-8') as file:
				content = file.read()
			ds_tu_loc = content.split('\n')
			for tk in ds_tu_loc:
				if tk == '' or tk is None:
					continue
				try:
					text_find, text_replace = tk.split("|")
					list_filter.append([text_find, text_replace])
				except:
					return PyMessageBox().show_warning("Thông Báo", "Sai cấu trúc từng hàng text_find|text_replace")
		
		list_sub = []
		
		for sub in self.data_sub:
		 
			time, sub_origin, sub_translate = sub
			
			if self.cb_type_tts_sub.currentIndex() == TypeSubEnum.origin.value:
				
				sub_o = sub_origin
				for filter in list_filter:
					text_find, text_replace = filter
					if self.cb_inhoa.isChecked():
						text_ = sub_origin
					else:
						text_ = sub_origin.lower()
						# text_ = sub_origin.lower().replace(text_find, text_replace)

						# sub_o = re.sub(text_find, text_replace, sub_origin, flags=re.IGNORECASE)
					sub_o = ''
					if self.cb_tu_giong_nhau.isChecked():
						for txt in text_.split(' '):
							if txt == text_find:
								sub_o += text_replace + " "
							else:
								sub_o += txt + " "
					else:
						sub_o = text_.replace(text_find, text_replace)
						
				list_sub.append([time, sub_o.strip(), sub_translate])
			else:
				sub_tran = sub_translate
				for filter in list_filter:
					text_find, text_replace = filter
					# print(filter)
					if self.cb_inhoa.isChecked():
						text_ = sub_translate
					else:
						text_ = sub_translate.lower()
					sub_tran = ''
					if self.cb_tu_giong_nhau.isChecked():
						for txt in text_.split(' '):
							# print(txt)
							# print(text_find)
							# print(text_replace)
							if txt == text_find:
								sub_tran += text_replace + " "
							else:
								sub_tran += txt + " "
					else:
						sub_tran = text_.replace(text_find, text_replace)
						
					# if self.cb_inhoa.isChecked():
					# 	sub_tran = sub_translate.replace(text_find, text_replace)
					#
					# 	# sub_tran = re.sub(text_find, text_replace, sub_translate)
					# else:
					# 	sub_tran = sub_translate.lower().replace(text_find, text_replace)

						# sub_tran = re.sub(text_find, text_replace, sub_translate, flags=re.IGNORECASE)
						# print(sub_tran)
				list_sub.append([time, sub_origin, sub_tran.strip()])
		
		self.data_sub = list_sub
		# self.fn_find()
		# print(list_sub)
		row_current = self.groupbox_timeline.main_table.currentIndex().row()
		self.groupbox_timeline.displayTable(list_sub,self.groupbox_timeline.path_video)
		self.groupbox_timeline.main_table.selectRow(row_current)
		self.groupbox_timeline.refresh()
		# self.manage_thread_pool.resultChanged.emit(UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, "")

		return PyMessageBox().show_info('Thông báo', "Nội dung Tìm Kiếm đã được thay thế")
	
	def fn_remove (self):
		if hasattr(self, 'row_curr'):
			self.groupbox_timeline.model.removeRow(self.row_curr)
			del self.data_sub[self.row_curr]
			self.groupbox_timeline.refresh()

	
	def fn_find (self):
		list_filter = []
		count = 0
		self.label_status.setText(f"")
		self.input_replace.clear()

		if self.input_file_loc.text() == "":
			if self.input_find.text() == "":
				return PyMessageBox().show_warning('Cảnh Báo', "Nội dung Tìm Kiếm không được trống")
			text_find_ = self.input_find.text()

			list_filter.append(text_find_)
		else:
			file_loc = self.input_file_loc.text()
			name, ext = os.path.splitext(file_loc)
			
			if not os.path.exists(file_loc):
				return PyMessageBox().show_warning('Cảnh Báo', "Không tìm thấy file")
			if not ext.lower() in ['.txt']:
				return PyMessageBox().show_warning("Thông báo", f"Chỉ hỗ trợ file txt theo cấu trúc từng hàng text_find|text_replace")
			with open(file_loc, 'r', encoding='utf-8') as file:
				content = file.read()
			ds_tu_loc = content.split('\n')
			for tk in ds_tu_loc:
				if tk == '' or tk is None:
					continue
				try:
					text_find_, text_replace = tk.split("|")
					list_filter.append(text_find_)
				except:
					return PyMessageBox().show_warning("Thông Báo", "Sai cấu trúc từng hàng text_find|text_replace")
		
		list_finded = []
		
		for row_curr, sub in enumerate(self.data_sub):
			# TODO:[time, sub_origin, sub_translate]
			time, sub_origin, sub_translate = sub
			sub = sub_translate
			if self.cb_type_tts_sub.currentIndex() == TypeSubEnum.origin.value:
				sub = sub_origin
			sub_old = sub
			
			if self.cb_inhoa.isChecked():
				text_ = sub
			else:
				text_ = sub.lower()

			for text_find in list_filter:
				# sub_tran = ''
				if self.cb_tu_giong_nhau.isChecked():
					for txt in text_.split(' '):
						if txt == text_find:
							count += 1
							list_finded.append((row_curr, sub_old))
				else:
				
				# if self.cb_inhoa.isChecked() is False:
				# 	text_find = text_find.lower()
				# 	sub = sub.lower()
					find = text_.count(text_find)
					if find:
						count +=1
						list_finded.append((row_curr,sub_old))

					# print(count)
				# if count:
				# 	list_finded.append((row_curr,sub_old))

				# self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_PART_TAB_EXTRACT, TRANSLATE_SUB_PART_TAB_EXTRACT, data)
		if len(list_finded) >0:
			row_curr , sub_old = list_finded[0]
			self.row_curr = row_curr
			self.groupbox_timeline.main_table.selectRow(row_curr)
			self.input_replace.setPlainText(sub_old)
			self.label_status.setText(f"Có {len(list_finded)} dòng được tìm thấy")
			return
		else:
			self.label_status.setText(f"Không có dòng nào tìm thấy")
	
	def getValue (self):
		return self.data_sub


if __name__ == "__main__":
	test = "Nội Dung Tìm Kiếm không Dung được khdung"
	
	# text = re.sub('dung', 'August', test, flags=re.IGNORECASE)
	# text2 = re.sub(r'ung', 'August', test)
	texy=test.lower().replace("dung","hay")
	# print(text)
	
	print(texy)
# print(test.replace("H", "b"))
