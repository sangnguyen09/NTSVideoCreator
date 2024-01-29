import base64

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QPlainTextEdit, QGroupBox

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_count_down import TimeCountDown


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


class PyDialogShowChuyenKhoan(QDialog):
	def __init__ (self, data, height, title="", font_size=12):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		self.data = data
		self.font_size = font_size
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
		self.setWindowTitle("Hướng dẫn" if title == "" else title)
		
		self.setMinimumHeight(height)
		# self.setMinimumWidth(800)
		
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		# self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		# self.buttonSave = QPushButton("Close")
		# self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		self.groupbox_thong_tin_tk = QGroupBox("Thông Tin Chuyển Khoản:")
		self.lb_bank_name = QLabel(f"""Ngân Hàng:<p style="font-size:15px; font-weight:bold; color: #f81919;">{self.data.get("info_chuyen_khoan").get("ngan_hang")}</p>""")
		self.lb_account_name = QLabel(f"""Tên TK:<p style="font-size:15px; font-weight:bold; color: #f81919;">{self.data.get("info_chuyen_khoan").get("name_account")}</p>""")
		self.lb_account_number = QLabel(f"""Số TK:<p style="font-size:15px; font-weight:bold; color: #f81919;">{self.data.get("info_chuyen_khoan").get("number_account")}</p>""")
		self.lb_so_tien_nap = QLabel(f"""Số Tiền Nạp:<p style="font-size:15px; font-weight:bold; color: #f81919;">{self.data.get("money")}</p>""")
		self.lb_noi_dung_ck = QLabel(f"""Nội Dung Chuyển Khoản:<p style="font-size:15px; font-weight:bold; color: #f81919;">{self.data.get("bill_code")}</p>""")
		self.lb_luu_y = QLabel("")
		
		self.lb_luu_y.setText(f'<p style="font-size:15px; font-weight:bold; color: #f81919;">Các Bạn Vui Lòng Ghi Đúng Nội Dung Chuyển Khoản.</p><p style="font-size:15px; font-weight:bold; color: #f81919;">CK Xong Vui Lòng Bấm Nút Xác Nhận Để Hệ Thống Sẽ Tự Động Cập Nhật Số Dư Tài Khoản</p><p style="font-size:15px; font-weight:bold; color: #f81919;">Sau 10 Phút Nếu Không Thấy Cập Nhật Vui Lòng Chụp Bill Chuyển Khoản Và Gửi Cho ADMIN</p>')
		
		self.groupbox_maQR = QGroupBox("QUÉT Nhanh Mã QR")
		self.lb_image_QR = QLabel()
		image = base64.b64decode(self.data.get('qr'))
		
		pipmap = QPixmap()
		pipmap.loadFromData(image)
		pipmap = pipmap.scaled(200, 300, Qt.KeepAspectRatio)
		self.lb_image_QR.setPixmap(pipmap)
		
		self.time_countdown = TimeCountDown(self.data.get('time'))
		
		self.buttonXacNhanThanhToan = QPushButton(text="Xác Nhận Đã CK")
		self.buttonXacNhanThanhToan.setCursor(Qt.CursorShape.PointingHandCursor)
	# def modify_widgets (self):
	# 	self.textarea_info.appendPlainText(self.text)
	
	def create_layouts (self):
		self.app_layout = QVBoxLayout()
		# self.app_layout.setSpacing(0)
		
		
		self.content_frame = QWidget()
		
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QHBoxLayout(self.content_frame)
		self.content_layout.setContentsMargins(0, 0, 0, 0)
		
		self.groupbox_thong_tin_tk_layout = QVBoxLayout()
		self.groupbox_QR_layout = QHBoxLayout()
		self.groupbox_Timedown_layout = QVBoxLayout()
	
	# self.content_layout.setSpacing(0)
	
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.app_layout.addWidget(self.lb_luu_y)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.groupbox_thong_tin_tk, 50)
		self.content_layout.addWidget(self.groupbox_maQR, 50)
		# self.content_layout.addLayout(self.btn_layout, 10)
		self.groupbox_thong_tin_tk.setLayout(self.groupbox_thong_tin_tk_layout)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_bank_name)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_account_name)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_account_number)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_so_tien_nap)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_noi_dung_ck)
		
		self.groupbox_maQR.setLayout(self.groupbox_QR_layout)
		self.groupbox_QR_layout.addWidget(self.lb_image_QR)
		self.groupbox_QR_layout.addLayout(self.groupbox_Timedown_layout)
		
		self.groupbox_Timedown_layout.addWidget(self.time_countdown)
		self.groupbox_Timedown_layout.addWidget(self.buttonXacNhanThanhToan)
	
	# self.groupbox_thong_tin_tk_layout.addWidget(self.lb_luu_y)
	# self.btn_layout.addWidget(QLabel(""), 40)
	# self.btn_layout.addWidget(self.buttonSave, 20)
	# self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.buttonXacNhanThanhToan.clicked.connect(self.accept)
		
		self.time_countdown.finishedSignal.connect(self.close)
		

