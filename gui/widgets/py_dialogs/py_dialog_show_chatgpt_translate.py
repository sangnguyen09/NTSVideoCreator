import re

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QPlainTextEdit, \
	QApplication

from gui.configs.config_theme import ConfigTheme
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox

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


class PyDialogShowGPTTranslate(QDialog):
	def __init__ (self, origin_lag, des_lang, text_cur, title):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		self.text = text_cur
		self.origin_lag = origin_lag
		self.des_lang = des_lang
		# st = QSettings(*SETTING_APP)
		# self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_AUTOSUB)
		# self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		
		# SET UP MAIN WINDOW
		self.setWindowTitle(title)
		
		# self.setMinimumHeight(height)
		self.setMinimumWidth(1280)
		
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		
		self.buttonCopy = QPushButton("Copy")
		self.buttonCopy.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.buttonSave = QPushButton("Lưu")
		self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.lb_info = QLabel("Cách Dịch dùng ChatGPT")
		
		self.textarea_info = QPlainTextEdit()
		self.textarea_info.setReadOnly(True)
		self.textarea_info.setMinimumHeight(300)
		
		# self.lb_text = QLabel("Copy văn bản sau và dán vào phần ChatGPT để lấy bản dịch:")
		self.textarea_info.setProperty("class", "dialog_info")
		
		self.lb_input = QLabel("VĂN BẢN GỐC:")
		
		self.textarea_input = QPlainTextEdit()
		self.textarea_input.setStyleSheet("font-size:10px")
		
		self.textarea_input.setReadOnly(True)
		
		self.lb_output = QLabel("VĂN BẢN ĐÃ DỊCH:")
		
		self.textarea_output = QPlainTextEdit()
	
	
	def modify_widgets (self):
		text = "- B1: Truy cập vào web có ChatGPT mà bạn muốn hoặc BingChat"
		text += "\n\n- B2: Copy dòng sau vào phần chat."
		text += f"\n\n You are the translator. can you help me translate the following text from {self.origin_lag} to {self.des_lang}, newline after each paragraph"
		text += "\n\n- B3: Sau khi chatbot trả lời thì bạn copy VĂN BẢN GỐC bên dưới và dán vào phần chat"
		text += "\n\n- B4: Sau khi dịch xong thì copy bản dịch dán vào phần VĂN BẢN ĐÃ DỊCH. Lưu ý số dòng phải bằng với số dòng ở phần VĂN BẢN GỐC"
		text += "\n\n- B5: Bấm SAVE để chuyển tiếp qua các đoạn văn bản tiếp theo nếu còn"
		text += "\n\n- LƯU Ý: Nếu Chatbot không trả lời theo từng dòng thì có thể yêu cầu nó dịch theo từng dòng, hoặc bạn có thể tự tách bằng tay miễn sao đủ số dòng ở phần VĂN BẢN GỐC"
		self.textarea_info.appendPlainText(text)
		self.textarea_input.appendPlainText(self.text)
	
	def create_layouts (self):
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.app_layout.setSpacing(0)
		
		self.btn_layout = QHBoxLayout()
		self.btn_copy_layout = QHBoxLayout()
		
		self.content_frame = QWidget()
		
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
	
	# self.content_layout.setSpacing(0)
	
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.lb_info)
		self.content_layout.addWidget(self.textarea_info)
		self.content_layout.addWidget(self.lb_input)
		self.content_layout.addWidget(self.textarea_input)
		self.content_layout.addLayout(self.btn_copy_layout)
		self.content_layout.addWidget(self.lb_output)
		self.content_layout.addWidget(self.textarea_output)
		self.content_layout.addLayout(self.btn_layout)
		
		self.btn_copy_layout.addWidget(QLabel(""), 40)
		self.btn_copy_layout.addWidget(self.buttonCopy, 20)
		self.btn_copy_layout.addWidget(QLabel(""), 40)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.save)
		self.buttonCopy.clicked.connect(self.copy)
	
	def copy (self):
		clipboard = QApplication.clipboard()
		clipboard.setText(self.textarea_input.toPlainText())
	
	# print(clipboard.text(mode=QClipboard.Mode.Clipboard))
	def save (self):
		#
		# if self.textarea_input.toPlainText() =="":
		# 	return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng nhập vào VĂN ")
		#
		if self.textarea_output.toPlainText() == "":
			return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng nhập vào VĂN BẢN ĐÃ DỊCH")
		
		so_dong_sub_goc = len(self.textarea_input.toPlainText().split('\n'))
		so_dong_sub_dich = len(self.textarea_output.toPlainText().split('\n'))
		# print(self.textarea_output.toPlainText())
		# print(self._read_sequence(self.textarea_input.toPlainText()))
		# print(self._read_sequence(self.textarea_output.toPlainText()))
		if not so_dong_sub_goc == so_dong_sub_dich:
			return PyMessageBox().show_warning('Cảnh Báo', f"Số dòng sub gốc là {so_dong_sub_goc}, nhưng số dòng sub dịch là {so_dong_sub_dich}. Không đều nhau")
		self.accept()
	
	def _read_sequence (self, content):
		sequences = list(map(list, re.findall(r"(\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+)\n+(.+(?:\n.+)?)\n?", content)))
		# print(len(sequences))
		return [list(filter(None, sequence)) for sequence in sequences]
	
	def getTextTranslate (self):
		return [self.textarea_output.toPlainText().split('\n')]


if __name__ == '__main__':
	pass
	# print(len(pppp))
	# print(len(qqq))
