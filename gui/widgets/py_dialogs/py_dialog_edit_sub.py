import time

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGridLayout, QDialog, \
	QPlainTextEdit

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN, SUMMARY_SUB_IN_TABLE, \
	CHECK_DO_LECH_DIALOG_SUMMARY, RESULT_CHECK_DO_LECH_VIDEO_SUMMARY, get_color_do_lech_sub, TOGGLE_SPINNER, USER_DATA
from gui.helpers.ect import mh_ae, gm_ae, cr_pc
from gui.helpers.func_helper import getValueSettings
from gui.helpers.get_data import URL_API_BASE
from gui.helpers.translatepy.translators import GoogleTranslateV2
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_spinner.spinner import WaitingSpinner
from gui.widgets.py_table_widget.model_timeline_addsub import ColumnNumber


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


class PyDialogEditSub(QDialog):
	def __init__ (self, manage_thread_pool, data_sub,model_AI, column_sub):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		self.manage_thread_pool = manage_thread_pool
		self.data_sub = data_sub
		dolech, time_, pos_ori, sub_origin, sub_translate, pos_trans = data_sub
		self.item_sub = sub_translate if column_sub == ColumnNumber.column_sub_translate.value else sub_origin
		self.column_sub = column_sub
		self.text_current = self.item_sub
		self.model_AI = model_AI
		
	 
		
		self.item_time = time_
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Rút Gọn Nội Dung Của Sub Để Căn Chỉnh Thời Gian Không Quá Lệch")
		
		# self.setMinimumHeight(height)
		self.setMinimumWidth(1000)
		self.summary_sub = {
			"trans": "",
			"origin": ""
		}
		self.spiner = WaitingSpinner(
			self,
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
		
		self.setup_ui()
		# if self.item_sub != "":
		# 	self.checkDoLech(self.item_sub)
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		
		self.buttonSave = QPushButton("Lưu")
		self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonSummary = QPushButton("Rút Gọn Nội Dung")
		self.buttonSummary.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonCheckDoLech = QPushButton("Check Độ Lệch")
		self.buttonCheckDoLech.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonReset = QPushButton("Reset")
		self.buttonReset.setCursor(Qt.CursorShape.PointingHandCursor)
		
		huong_dan = "B1: Chọn chế độ đọc từ loại SUB nào"
		huong_dan += "\n\nB2: Bấm nút RÚT GỌN để server thực hiện"
		huong_dan += "\n\nNếu chưa ưng ý câu rút gọn bạn có thể bấm lại nút RÚT GỌN đến khi nào cảm thấy ok thì bấm LƯU để cập nhật"
		huong_dan += "\n\nHoặc bạn có thể chỉnh sửa trực tiếp Nội Dung Rút Gọn sao cho phù hợp."
		huong_dan += "\n\nLưu ý các câu ngắn chỉ 1 vài từ sẽ không thể rút gọn được mà bạn phải tự sửa"
		self.text_huongdan = QPlainTextEdit()
		self.text_huongdan.setReadOnly(True)
		self.text_huongdan.setMaximumHeight(200)
		self.text_huongdan.setPlainText(huong_dan)
		self.text_huongdan.setProperty("class", "dialog_info")
		
		self.text_edit = QPlainTextEdit()
		# self.text_edit.setReadOnly(True)
		self.text_edit.setMaximumHeight(150)
		# self.text_goc.setProperty("class", "dialog_info")
		
		# self.text_rutgon = QPlainTextEdit()
		# self.text_rutgon.setMaximumHeight(100)
		# self.text_rutgon.setReadOnly(True)
		# self.text_rutgon.setProperty("class", "dialog_info")
		
		# self.groupbox_show_sub = QGroupBox("Thông Tin:")
		
		# self.rad_sub_origin = PyRadioButton(value='origin', text="Sub Gốc")
		# self.rad_sub_origin.setChecked(True)
		
		# self.text_goc.setPlainText(self.item_sub_org.text())
		
		# self.rad_sub_translate = PyRadioButton(value='translate', text="Sub Dịch")
		
		# self.label_mode_doc = QLabel()
		# texxt = f'Chế ĐỘ Đọc Từ: <p style="font-size:15px; font-weight:bold; color: #e5342b;">{" SUB DỊCH" if self.mode_doc == "trans" else " SUB GỐC"}</p>'
		# self.label_mode_doc.setText(texxt)
		#
		# texxt = f'Ngôn Ngữ Đọc: <p style="font-size:15px; font-weight:bold; color: #e5342b;">{str(self.language)}</p>'
		#
		# self.label_language = QLabel()
		# self.label_language.setText(texxt)
		
		self.label_status = QLabel()
		self.label_do_lech = QLabel()
	
	def modify_widgets (self):
		self.text_edit.setPlainText(self.text_current)
		# self.buttonReset.setFocus()

	
	
	def create_layouts (self):
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.app_layout.setSpacing(0)
		
		self.btn_layout = QHBoxLayout()
		
		self.content_frame = QWidget()
		
		self.groupbox_show_sub_layout = QGridLayout()
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
	
	# self.content_layout.setSpacing(0)
	
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		# self.content_layout.addWidget(self.text_huongdan)
		# self.content_layout.addWidget(self.groupbox_show_sub)
		self.content_layout.addWidget(QLabel("Nội Dung Gốc"))
		self.content_layout.addWidget(self.text_edit)
		# self.content_layout.addWidget(QLabel("Nội Dung Rút Gọn"))
		# self.content_layout.addWidget(self.text_rutgon)
		
		self.content_layout.addLayout(self.btn_layout)
		
		# self.groupbox_show_sub.setLayout(self.groupbox_show_sub_layout)
		
		# self.groupbox_show_sub_layout.addWidget(self.label_mode_doc, 0, 0)
		# self.groupbox_show_sub_layout.addWidget(self.label_language, 0, 1)
		
		
		self.btn_layout.addWidget(self.label_status, 30)
		self.btn_layout.addWidget(self.buttonSave, 10)
		self.btn_layout.addWidget(self.buttonSummary, 15)
		self.btn_layout.addWidget(self.buttonCheckDoLech, 15)
		self.btn_layout.addWidget(self.buttonReset)
		self.btn_layout.addWidget(self.label_do_lech, 30, alignment=Qt.AlignmentFlag.AlignRight)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.accept)
		self.buttonReset.clicked.connect(self.reset)
		self.buttonSummary.clicked.connect(self.summary_)
		self.buttonCheckDoLech.clicked.connect(lambda: self.checkDoLech(self.text_edit.toPlainText()))
		# self.buttonChangeSum.clicked.connect(self.close)
		self.manage_thread_pool.resultChanged.connect(self.resultThreadChanged)
	
	# self.rad_sub_origin.clicked.connect(lambda: self.check_radio_button(self.rad_sub_origin))
	# self.rad_sub_translate.clicked.connect(lambda: self.check_radio_button(self.rad_sub_translate))
	def reset(self):
		self.text_current = self.item_sub
		self.text_edit.setPlainText(self.text_current)
		
	def resultThreadChanged (self, id_worker, typeThread, result):
		# print(typeThread)
		
		if typeThread == SUMMARY_SUB_IN_TABLE:
			if result is False:
				return self.label_status.setText(f"Hết Token, Liên Hệ Admin Mua")
			self.text_edit.clear()
			self.text_edit.setPlainText(result)
			self.label_status.setText("Ok")
			# self.checkDoLech(result)
			if self.spiner.is_spinning:
				self.spiner.stop()
		
		if typeThread == RESULT_CHECK_DO_LECH_VIDEO_SUMMARY:
			row_number, tempo = result
			
			do_lech = "Độ lệch time: " + str(round(tempo, 2)) + " lần"
			color = get_color_do_lech_sub(tempo)
			self.label_do_lech.setText(f'<p style="font-size:15px; font-weight:bold; color: {color};">{do_lech}</p>')
			self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
			if self.spiner.is_spinning:
				self.spiner.stop()
	
	
	def checkDoLech (self, text):
		if text == "":
			return PyMessageBox().show_warning('Cảnh Báo', "Nội dung không được trống")
		# self.listRowCheckDoLechPart = []
		data = []
		dolech, time, pos_ori, sub_origin, sub_translate, pos_trans = self.data_sub
		
		if self.column_sub == ColumnNumber.column_sub_translate.value:
			data.append([dolech, time, pos_ori, sub_origin, text, pos_trans])
		else:
			data.append([dolech, time, pos_ori, text, sub_translate, pos_trans])
		
		self.manage_thread_pool.resultChanged.emit(CHECK_DO_LECH_DIALOG_SUMMARY, CHECK_DO_LECH_DIALOG_SUMMARY, data)

		self.spiner.start()
	
	def summary_ (self):
		if self.text_edit.toPlainText() == "":
			return PyMessageBox().show_warning('Cảnh Báo', "Nội dung không được trống")
		
		self.label_status.setText("Đang rút gọn nội dung...")
		
		self.manage_thread_pool.start(self._funcSummary, SUMMARY_SUB_IN_TABLE, SUMMARY_SUB_IN_TABLE, text=self.item_sub)
		
		self.spiner = WaitingSpinner(
			self,
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
	
	def _funcSummary (self, **kwargs):
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		text = kwargs["text"]
		
		translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
		lang_result = translator_server.language(text)
		
		
		dataTrans = {
			"text": text,
			"source_lang": lang_result.result.alpha2,
			"tc": TOOL_CODE_MAIN,
			"model": self.model_AI,
			"cp": cr_pc(),
			't': int(float(time.time())),
		}
		user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		
		data_encrypt = mh_ae(dataTrans, user_data['paes'])
		
		headers = {"Authorization": f"Bearer {user_data['token']}"}
		# print(headers)
		status =0
		for i in range(1):
			res = requests.post(url=URL_API_BASE + "/translate/private/summary",
				json={"data": data_encrypt}, headers=headers)
			
			if res.status_code == 200:
				text_res = gm_ae(res.json()["data"], user_data['paes'])
				return text_res

			# time.sleep(1)
		return False
	
	def getValue (self):
		return self.text_edit.toPlainText()
