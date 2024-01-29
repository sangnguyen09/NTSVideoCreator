import re
import time
from datetime import datetime

import requests
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QFrame, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, QDialog, QComboBox, \
	QPushButton, QSpinBox, QWidget

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN, PAE_LG, CHECKOUT_DEPOSIT, \
	CHECK_TRANG_THAI_NAP_TIEN, CHECK_SO_DU_TAI_KHOAN, MUA_HANG_ONLINE
from gui.helpers.ect import cr_pc, mh_ae, gm_ae
from gui.helpers.func_helper import getValueSettings, get_expired
from gui.helpers.get_data import URL_API_BASE
from gui.widgets.py_dialogs.py_dialog_show_chuyen_khoan import PyDialogShowChuyenKhoan
from gui.widgets.py_dialogs.py_dialog_show_question import PyDialogShowQuestion
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_spinner.spinner import WaitingSpinner


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


class PyTabShop(QWidget):
	def __init__ (self, manage_thread_pool, token):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		# self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		# self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
		self.manage_thread_pool = manage_thread_pool
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		# self.app_path = os.path.abspath(os.getcwd())
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("NTS SHOP")
		self.setStyleSheet(self.style_format)
		self.data_info = None
		self.token = token
		self.setup_ui()
		self.is_stop = False
		self.da_ck = False
		self.openShop()
		# print('open')
	
	def openShop (self):
		dataReq = {
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		headers = {
			"Authorization": f"Bearer {self.token}"}
		data_encrypt = mh_ae(dataReq, PAE_LG)
		res = requests.post(url=URL_API_BASE + "/check-out/private/get-info",
			json={"data": data_encrypt}, headers=headers)
		
		if res.status_code == 200:
			data_info = gm_ae(res.json()["data"], PAE_LG)
			# print(data_info)
			
			# self.dialog_config_sub_text.loadData(self.configCurrent)
			self.loadData(data_info)

	
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		# BG FRAME
		self.bg_frame = QFrame()
		self.bg_frame.setObjectName("bg_frame")
		
		self.groupbox_thong_tin_tk = QGroupBox("Thông Tin Tài Khoản:")
		self.lb_token_translate_pro1 = QLabel('')
		self.lb_so_du = QLabel('')
		self.lb_han_su_dung = QLabel('')
		self.lb_han_so_luong_may = QLabel('')
		self.lb_han_chuc_nang = QLabel('')
		self.lb_char_tieng_viet = QLabel('')
		self.lb_char_da_ngon_ngu = QLabel('')
		self.lb_token_chatgpt = QLabel('')
		# self.buttonNapTien.setObjectName("btns")
		
		self.groupbox_nap_tien = QGroupBox("Nạp Xu:")
		
		self.lb_so_xu_nap = QLabel("Số Xu Nạp:")
		self.input_so_tien_nap = QSpinBox()
		self.input_so_tien_nap.setMinimum(100000)
		self.input_so_tien_nap.setMaximum(5000000)
		self.lb_so_tien_toi_thieu = QLabel("(1 Xu = 1 VNĐ): Số tiền nạp tối thiểu 100K")
		self.buttonNapTien = QPushButton(text="Nạp Tiền")
		self.buttonNapTien.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.groupbox_gia_han = QGroupBox("Gia Hạn:")
		
		self.lb_chuc_nang = QLabel("Chọn Chức Năng:")
		self.combobox_chuc_nang = QComboBox()
		
		self.lb_thoi_han = QLabel("Chọn Thời Hạn:")
		self.combobox_thoi_han = QComboBox()
		
		self.lb_slm = QLabel("Số Lượng Máy Sử Dụng:")
		self.input_slm = QSpinBox()
		self.input_slm.setMinimum(1)
		self.input_slm.setMaximum(10)
		
		self.lb_gia_tien_gia_han = QLabel(f"")
		
		self.buttonGiaHan = QPushButton(text="GIA Hạn Ngay")
		self.buttonGiaHan.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.groupbox_text_to_speech = QGroupBox("Mua Ký Tự Voice:")
		
		self.lb_server_tts = QLabel("Chọn Server:")
		self.combobox_server_tts = QComboBox()
		self.lb_sl_voice = QLabel("SL:")
		self.input_sl_voice = QSpinBox()
		self.input_sl_voice.setMinimum(1)
		self.input_sl_voice.setMaximum(100)
		
		self.lb_goi_tts = QLabel("Chọn Gói:")
		self.combobox_goi_tts = QComboBox()
		# self.COMBO_GOI_TTS = self.data_info.get('tts').get('plan')
		# self.combobox_goi_tts.addItems(list(self.COMBO_GOI_TTS.keys()))
		
		# key_price = f'{self.COMBO_SERVER_TTS.get(self.combobox_server_tts.currentText())}_{self.COMBO_GOI_TTS.get(self.combobox_goi_tts.currentText())}'
		self.lb_gia_tien_tts = QLabel(f"")
		
		self.buttonMuaKyTu = QPushButton(text="Mua Ngay")
		self.buttonMuaKyTu.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.groupbox_translate = QGroupBox("Mua Ký Tự Dịch:")
		self.lb_server_translate = QLabel("Chọn Server:")
		self.combobox_server_translate = QComboBox()
		
		self.lb_goi_translate = QLabel("Chọn Gói:")
		self.combobox_goi_translate = QComboBox()
		
		self.lb_sl_trans = QLabel("SL:")
		self.input_sl_trans = QSpinBox()
		self.input_sl_trans.setMinimum(1)
		self.input_sl_trans.setMaximum(100)
		
		self.lb_gia_tien_translate = QLabel(f"")
		
		self.buttonMuaToken = QPushButton(text="Mua Ngay")
		self.buttonMuaToken.setCursor(Qt.CursorShape.PointingHandCursor)
	
	# self.spiner.start()
	
	def modify_widgets (self):
		pass
	
	def create_layouts (self):
		self.widget_layout = QHBoxLayout()
		self.widget_layout.setContentsMargins(0, 0, 0, 0)
		
		self.groupbox_gia_han_layout = QGridLayout()
		self.groupbox_nap_tien_layout = QGridLayout()
		self.groupbox_thong_tin_tk_layout = QGridLayout()
		self.groupbox_text_to_speech_layout = QGridLayout()
		self.groupbox_translate_layout = QGridLayout()
		
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(20, 20, 20, 20)
		
		self.btn_layout = QHBoxLayout()
		self.btn_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_layout = QVBoxLayout()
		self.content_layout.setContentsMargins(0, 0, 0, 0)
	
		self.content_info_layout = QHBoxLayout()
		self.content_info_layout.setContentsMargins(0, 0, 0, 0)
	def add_widgets_to_layouts (self):
		# self.bg_layout.addWidget(self.groupbox_split_sub)
		self.bg_layout.addWidget(QLabel(),10)
		self.bg_layout.addLayout(self.content_layout,80)
		self.bg_layout.addWidget(QLabel(),10)
		self.content_layout.addLayout(self.content_info_layout,40)
		self.content_info_layout.addWidget(self.groupbox_thong_tin_tk)
		self.content_layout.addWidget(self.groupbox_nap_tien,15)
		self.content_layout.addWidget(self.groupbox_gia_han,15)
		self.content_layout.addWidget(self.groupbox_text_to_speech,15)
		self.content_layout.addWidget(self.groupbox_translate,15)
		# self.bg_layout.addWidget(self.tabWidget)
		# self.content_layout.addLayout(self.btn_layout)
		
		self.setLayout(self.bg_layout)
		
		# self.groupbox_split_sub.setLayout(self.ngat_doan_layout)
		self.groupbox_gia_han.setLayout(self.groupbox_gia_han_layout)
		self.groupbox_thong_tin_tk.setLayout(self.groupbox_thong_tin_tk_layout)
		self.groupbox_nap_tien.setLayout(self.groupbox_nap_tien_layout)
		self.groupbox_text_to_speech.setLayout(self.groupbox_text_to_speech_layout)
		self.groupbox_translate.setLayout(self.groupbox_translate_layout)
		
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_so_du, 0, 0)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_han_so_luong_may, 0, 2)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_han_chuc_nang, 0, 4)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_han_su_dung, 0, 6)
		self.groupbox_thong_tin_tk_layout.addWidget(QLabel(), 1, 0)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_char_da_ngon_ngu, 2, 0)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_char_tieng_viet, 2, 2)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_token_chatgpt, 2, 4)
		self.groupbox_thong_tin_tk_layout.addWidget(self.lb_token_translate_pro1, 2, 6)
		
		self.groupbox_gia_han_layout.addWidget(self.lb_chuc_nang, 0, 0)
		self.groupbox_gia_han_layout.addWidget(self.combobox_chuc_nang, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_gia_han_layout.addWidget(QLabel(""), 0, 2)
		self.groupbox_gia_han_layout.addWidget(self.lb_thoi_han, 0, 3, alignment=Qt.AlignmentFlag.AlignRight)
		self.groupbox_gia_han_layout.addWidget(self.combobox_thoi_han, 0, 4, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_gia_han_layout.addWidget(QLabel(""), 0, 5)
		self.groupbox_gia_han_layout.addWidget(self.lb_slm, 0, 6, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_gia_han_layout.addWidget(self.input_slm, 0, 7, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_gia_han_layout.addWidget(self.lb_gia_tien_gia_han, 0, 8, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_gia_han_layout.addWidget(QLabel(""), 0, 9)
		self.groupbox_gia_han_layout.addWidget(self.buttonGiaHan, 0, 10)
		
		self.groupbox_nap_tien_layout.addWidget(self.lb_so_xu_nap, 0, 0)
		self.groupbox_nap_tien_layout.addWidget(self.input_so_tien_nap, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_nap_tien_layout.addWidget(QLabel(""), 0, 2)
		
		self.groupbox_nap_tien_layout.addWidget(self.lb_so_tien_toi_thieu, 0, 3)
		self.groupbox_nap_tien_layout.addWidget(QLabel(""), 0, 4)
		
		self.groupbox_nap_tien_layout.addWidget(self.buttonNapTien, 0, 5)
		
		self.groupbox_text_to_speech_layout.addWidget(self.lb_server_tts, 0, 0)
		self.groupbox_text_to_speech_layout.addWidget(self.combobox_server_tts, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_text_to_speech_layout.addWidget(QLabel(""), 0, 2)
		self.groupbox_text_to_speech_layout.addWidget(self.lb_goi_tts, 0, 3, alignment=Qt.AlignmentFlag.AlignRight)
		self.groupbox_text_to_speech_layout.addWidget(self.combobox_goi_tts, 0, 4, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_text_to_speech_layout.addWidget(self.lb_sl_voice, 0, 5, alignment=Qt.AlignmentFlag.AlignRight)
		self.groupbox_text_to_speech_layout.addWidget(self.input_sl_voice, 0, 6, alignment=Qt.AlignmentFlag.AlignRight)
		self.groupbox_text_to_speech_layout.addWidget(self.lb_gia_tien_tts, 0, 7, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_text_to_speech_layout.addWidget(QLabel(""), 0, 8)
		
		self.groupbox_text_to_speech_layout.addWidget(self.buttonMuaKyTu, 0, 9)
		
		self.groupbox_translate_layout.addWidget(self.lb_server_translate, 0, 0)
		self.groupbox_translate_layout.addWidget(self.combobox_server_translate, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_translate_layout.addWidget(QLabel(""), 0, 2)
		self.groupbox_translate_layout.addWidget(self.lb_goi_translate, 0, 3, alignment=Qt.AlignmentFlag.AlignRight)
		self.groupbox_translate_layout.addWidget(self.combobox_goi_translate, 0, 4, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_translate_layout.addWidget(self.lb_sl_trans, 0, 5, alignment=Qt.AlignmentFlag.AlignRight)
		self.groupbox_translate_layout.addWidget(self.input_sl_trans, 0, 6, alignment=Qt.AlignmentFlag.AlignRight)
		self.groupbox_translate_layout.addWidget(self.lb_gia_tien_translate, 0, 7, alignment=Qt.AlignmentFlag.AlignLeft)
		self.groupbox_translate_layout.addWidget(QLabel(""), 0, 8)
		
		self.groupbox_translate_layout.addWidget(self.buttonMuaToken, 0, 9)
	
	
	def setup_connections (self):
		self.buttonNapTien.clicked.connect(self.openDialogNapTien)
		self.buttonGiaHan.clicked.connect(lambda: self.buyNow("gia_han"))
		self.buttonMuaKyTu.clicked.connect(lambda: self.buyNow("mua_ky_tu"))
		self.buttonMuaToken.clicked.connect(lambda: self.buyNow("mua_token"))
		# self.buttonGiaHan.clicked.connect(self.save)
		self.input_slm.valueChanged.connect(self.changePrice)
		self.input_sl_trans.valueChanged.connect(self.changePrice)
		self.input_sl_voice.valueChanged.connect(self.changePrice)
		self.combobox_chuc_nang.currentIndexChanged.connect(self.changePrice)
		self.combobox_thoi_han.currentIndexChanged.connect(self.changePrice)
		self.combobox_server_tts.currentIndexChanged.connect(self.changePrice)
		self.combobox_goi_tts.currentIndexChanged.connect(self.changePrice)
		self.combobox_server_translate.currentIndexChanged.connect(self.changePrice)
		self.combobox_goi_translate.currentIndexChanged.connect(self.changePrice)
		
		self.manage_thread_pool.resultChanged.connect(self.resultChanged)
	
	def resultChanged (self, id_worker, id_thread, result):
		#
		
		
		if id_thread == CHECKOUT_DEPOSIT:
			if hasattr(self, 'spiner'):
				self.spiner.stop()
			is_ok, data = result
			if is_ok:
				self.manage_thread_pool.start(self._check_status_nap_tien, CHECK_TRANG_THAI_NAP_TIEN, CHECK_TRANG_THAI_NAP_TIEN, money=data.get("money"), bill_code=data.get("bill_code"))
				
				data.update({
					"time": self.data_info.get("info_chuyen_khoan").get("time"),
					"info_chuyen_khoan": self.data_info.get("info_chuyen_khoan"),
				})
				self.dialogNapTien = PyDialogShowChuyenKhoan(data, 400, title="Yêu Cầu Nạp Tiền")
				if self.dialogNapTien.exec():
					# print("OK")
					self.da_ck = True
				
				else:
					self.is_stop = True
			# print("cancel")
			else:
				return PyMessageBox().show_warning('Cảnh Báo', str(data))
		
		if id_thread == MUA_HANG_ONLINE:
			is_ok, name_product = result
			if hasattr(self, 'spiner'):
				self.spiner.stop()
			if is_ok:
				
				self.manage_thread_pool.start(self._check_blance, CHECK_SO_DU_TAI_KHOAN, CHECK_SO_DU_TAI_KHOAN)
				PyMessageBox().show_info('Thông Báo', f"Bạn Đã Mua Thành Công Gói: {name_product}")
			else:
				return PyMessageBox().show_warning('Cảnh Báo', name_product)
		
		if id_thread == CHECK_TRANG_THAI_NAP_TIEN:
			is_ok, money = result
			if is_ok:
				self.manage_thread_pool.start(self._check_blance, CHECK_SO_DU_TAI_KHOAN, CHECK_SO_DU_TAI_KHOAN)
				PyMessageBox().show_info('Thông Báo', f"Bạn Đã Nạp Thành Công {'{:,}'.format(money)} Xu")
				if hasattr(self, "dialogNapTien"):
					self.dialogNapTien.close()
		# else:
		# 	return PyMessageBox().show_warning('Cảnh Báo', str(data))
		
		if id_thread == CHECK_SO_DU_TAI_KHOAN:
			is_ok, data = result
			if is_ok:
				self.lb_so_du.setText(f"""Số Xu dư: <p style="font-size:15px; font-weight:bold; color: #f81919;">{'{:,}'.format(data.get('amount'))} Xu</p>""")
				self.lb_han_su_dung.setText(f"""Hạn Dùng: <p style="font-size:15px; font-weight:bold; color: #f81919;">{get_expired(data.get('expire_date'))}</p>""")
				self.lb_han_so_luong_may.setText(f"""Số Lượng PC: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data.get('num_pc')} PC Online</p>""")
				self.lb_han_chuc_nang.setText(f"""Chức Năng: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data.get('chuc_nang')}</p>""")
				self.lb_char_tieng_viet.setText(f"""Ký Tự Tiếng Việt: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data.get('char_tieng_viet') if isinstance(data.get('char_tieng_viet'), str) else '{:,}'.format(data.get('char_tieng_viet'))}</p>""")
				self.lb_char_da_ngon_ngu.setText(f"""Ký Tự Đa Ngôn Ngữ: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data.get('char_da_ngon_ngu') if isinstance(data.get('char_da_ngon_ngu'), str) else '{:,}'.format(data.get('char_da_ngon_ngu'))}</p>""")
				self.lb_token_chatgpt.setText(f"""Token ChatGPT: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data.get('token_chatgpt') if isinstance(data.get('token_chatgpt'), str) else '{:,}'.format(data.get('token_chatgpt'))}</p>""")
				self.lb_token_translate_pro1.setText(f"""Token Translate Pro: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data.get('token_translate_pro1') if isinstance(data.get('token_translate_pro1'), str) else '{:,}'.format(data.get('token_translate_pro1'))}</p>""")
				
				self.data_info.get('info_user').update(data)
				self.changePrice()
			else:
				return PyMessageBox().show_warning('Cảnh Báo', str(data))
	
	
	def buyNow (self, type_buy):
		key_price = ''
		name_product = ''
		dataReq = {
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		balance = self.data_info.get('info_user').get('amount')
		if type_buy == 'gia_han':
			
			name_product = self.combobox_chuc_nang.currentText() + " - " + self.combobox_thoi_han.currentText() + " - " + str(self.input_slm.value()) + " PC"
			dataReq.update({
				'num_pc': self.input_slm.value()
			})
			key_price = f'{self.COMBO_CHUC_NANG.get(self.combobox_chuc_nang.currentText())}_{self.COMBO_THOI_HAN.get(self.combobox_thoi_han.currentText())}'
			
			price_buy = self.price_gia_han(self.data_info.get('price').get(key_price) * self.input_slm.value())
		
		elif type_buy == 'mua_ky_tu':
			dataReq.update({
				'sl': self.input_sl_voice.value()
			})
			name_product = self.combobox_server_tts.currentText() + ": " + self.combobox_goi_tts.currentText() + f" - Số lượng: {self.input_sl_voice.value()} - " + str(self.data_info.get('info_user').get('num_pc')) + " PC"
			
			key_price = f'{self.COMBO_SERVER_TTS.get(self.combobox_server_tts.currentText())}_{self.COMBO_GOI_TTS.get(self.combobox_goi_tts.currentText())}'
			
			if 'unlimited' in key_price.lower():
				price_buy = self.data_info.get('price').get(key_price) * self.data_info.get('info_user').get('num_pc')
			else:
				price_buy = self.data_info.get('price').get(key_price) * self.input_sl_voice.value()
		
		elif type_buy == 'mua_token':
			dataReq.update({
				'sl': self.input_sl_trans.value()
			})
			name_product = self.combobox_server_translate.currentText() + ": " + self.combobox_goi_translate.currentText() + f" - Số lượng: {self.input_sl_trans.value()} - " + str(self.data_info.get('info_user').get('num_pc')) + " PC"
			key_price = f'{self.COMBO_SERVER_TRANSLATE.get(self.combobox_server_translate.currentText())}_{self.COMBO_GOI_TRANSLATE.get(self.combobox_goi_translate.currentText())}'
			
			if 'unlimited' in key_price.lower():
				price_buy = self.data_info.get('price').get(key_price) * self.data_info.get('info_user').get('num_pc')
			else:
				price_buy = self.data_info.get('price').get(key_price) * self.input_sl_trans.value()
		
		else:
			return PyMessageBox().show_warning('Cảnh Báo', "Lỗi Dữ Liệu")
		
		if price_buy > balance:
			text = f"\nERROR: Không Đủ SỐ DƯ, số tiền cần là: {'{:,}'.format(price_buy)} Xu"
			return PyMessageBox().show_warning('Cảnh Báo', text)
		
		# text = "THÔNG TIN ĐƠN HÀNG:\n\n"
		text = "Hãy Kiểm Tra Lại Đơn Hàng Của Bạn, Nếu Đúng Hãy Bấm Yes Để Tiến Hành Mua:\n\n"
		text += f"GÓI: {name_product}\n\n"
		text += f"GIÁ TIỀN: {'{:,}'.format(price_buy)} Xu\n"
		
		dialog = PyDialogShowQuestion(text, 80, "THÔNG TIN ĐƠN HÀNG", font_size=18)
		
		if dialog.exec():
			pass
		else:
			return
		
		dataReq.update({
			"id_price": key_price,
			
		})
		# print("buyNow")
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
		self.manage_thread_pool.start(self._funMuaHang, MUA_HANG_ONLINE, MUA_HANG_ONLINE, dataReq=dataReq, name_product=name_product)
	
	def _funMuaHang (self, **kwargs):
		# print("_funMuaHang")
		
		headers = {
			"Authorization": f"Bearer {self.token}"}
		data_encrypt = mh_ae(kwargs.get('dataReq'), PAE_LG)
		res = requests.post(url=URL_API_BASE + "/check-out/private/mua-hang",
			json={"data": data_encrypt}, headers=headers)
		
		if res.status_code == 200:
			# data_info = gm_ae(res.json()["data"], PAE_LG)
			
			# data_info.update({"money": kwargs.get('money')})
			return True, kwargs.get('name_product')
		return False, res.text
	
	def _funDeposit (self, **kwargs):
		dataReq = {
			"money": kwargs.get('money'),
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		headers = {
			"Authorization": f"Bearer {self.token}"}
		data_encrypt = mh_ae(dataReq, PAE_LG)
		res = requests.post(url=URL_API_BASE + "/check-out/private/deposit",
			json={"data": data_encrypt}, headers=headers)
		
		if res.status_code == 200:
			data_info = gm_ae(res.json()["data"], PAE_LG)
			data_info.update({"money": kwargs.get('money')})
			return True, data_info
		return False, res.text
	
	def _check_blance (self, **kwargs):
		# print('_check_blance')
		dataReq = {
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		headers = {
			"Authorization": f"Bearer {self.token}"}
		data_encrypt = mh_ae(dataReq, PAE_LG)
		res = requests.post(url=URL_API_BASE + "/users/private/check-amount",
			json={"data": data_encrypt}, headers=headers)
		# print(data_encrypt)
		# print(res.text)
		if res.status_code == 200:
			data_info = gm_ae(res.json()["data"], PAE_LG)
			# print(data_info)
			return True, data_info
		
		return False, res.text
	
	def _check_status_nap_tien (self, **kwargs):
		dataReq = {
			"bill_code": kwargs.get('bill_code'),
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		headers = {
			"Authorization": f"Bearer {self.token}"}
		data_encrypt = mh_ae(dataReq, PAE_LG)
		
		for i in range(50):
			time.sleep(3)
			n = 0
			while True:
				if self.da_ck:
					break
				if n == 6:
					break
				n += 1
				time.sleep(1)
			# print('_check_status_nap_tien')
			# if self.is_stop:
			# 	return False, 0
			res = requests.post(url=URL_API_BASE + "/check-out/private/check-bill",
				json={"data": data_encrypt}, headers=headers)
			# print(res.text)
			if res.status_code == 200:
				data_info = res.json()
				if data_info.get("data").get("status"):
					return True, kwargs.get('money')
		
		if self.da_ck:
			time.sleep(6)
		
		return False, 0
	
	
	def openDialogNapTien (self):
		self.is_stop = False
		self.da_ck = False
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
		self.manage_thread_pool.start(self._funDeposit, CHECKOUT_DEPOSIT, CHECKOUT_DEPOSIT, money=self.input_so_tien_nap.value())
	
	def price_gia_han (self, price):
		if self.data_info:
			# print(self.data_info)
			expire_date_current = datetime.fromtimestamp(self.data_info.get('info_user').get('expire_date'))
			today = datetime.now()
			so_ngay_con_lai = (expire_date_current - today).days
			so_may_lech = self.input_slm.value() - self.data_info.get('info_user').get('num_pc')
			
			if so_ngay_con_lai < 0:
				expire_date_current = today
			elif so_ngay_con_lai > 3:
				# print(len(list_tool.get(data_code.tc).get("tab")))
				# print(len(info_product.get('chuc_nang').get("tab")))
				chuc_nang = self.COMBO_CHUC_NANG.get(self.combobox_chuc_nang.currentText())
				# print(chuc_nang)
				if len(self.data_info.get('info_user').get('chuc_nang').split("+")) == 1 and chuc_nang == 'all':
					# print(price)
					# print(so_ngay_con_lai)
					if so_may_lech > 0:
						# print(1)
						price = price + so_ngay_con_lai * 1500 * self.data_info.get('info_user').get('num_pc')  # 1500 1 ngày
						
						price = price + so_ngay_con_lai * 5000 * so_may_lech  # 5000 1 ngày
					else:
						# print(2)
						
						price = price + so_ngay_con_lai * 1500 * self.input_slm.value()  # 5000 1 ngày
				
				# print(price)
				# if price > self.data_info.get('info_user').get('amount'):
				# 	text = f"\nERROR: Không Đủ SỐ DƯ, số tiền cần là: {'{:,}'.format(price)}"
				#
				# 	raise ResponseErr(status_code=status.HTTP_403_FORBIDDEN, err_msg=text)
				else:
					if so_may_lech > 0:
						hs = 3000
						if self.COMBO_CHUC_NANG.get(self.combobox_chuc_nang.currentText()) == 'all':
							hs = 5000
						price = price + so_ngay_con_lai * hs * so_may_lech  # 5000 1 ngày
			# print(price)++
			
			try:
				l_ch = re.findall(r"\d+", self.data_info.get('info_user').get('token_chatgpt'))
				if len(l_ch) == 1:
					so_ngay_con_han = int(l_ch[0])
					if so_ngay_con_han > 1:
						if so_may_lech > 0:
							price = price + so_ngay_con_han * 1600000 * so_may_lech
			# print(1,so_ngay_con_han,price,so_may_lech)
			except:
				pass
			
			try:
				
				l_ch = re.findall(r"\d+", self.data_info.get('info_user').get('token_translate_pro1'))
				if len(l_ch) == 1:
					so_ngay_con_han = int(l_ch[0])
					
					if so_ngay_con_han > 1:
						if so_may_lech > 0:
							price = price + so_ngay_con_han * 16000 * so_may_lech
			# print(1,so_ngay_con_han,price,so_may_lech)
			except:
				pass
			
			try:
				l_ch = re.findall(r"\d+", self.data_info.get('info_user').get('char_da_ngon_ngu'))
				if len(l_ch) == 1:
					so_ngay_con_han = int(l_ch[0])
					
					if so_ngay_con_han > 1:
						if so_may_lech > 0:
							price = price + so_ngay_con_han * 30000 * so_may_lech
			# print(1,so_ngay_con_han,price,so_may_lech)
			except:
				pass
			
			try:
				l_ch = re.findall(r"\d+", self.data_info.get('info_user').get('char_tieng_viet'))
				if len(l_ch) == 1:
					so_ngay_con_han = int(l_ch[0])
					if so_ngay_con_han > 1:
						if so_may_lech > 0:
							price = price + so_ngay_con_han * 10000 * so_may_lech
			# print(1,so_ngay_con_han,price,so_may_lech)
			except:
				pass
			
			return price
	
	def changePrice (self):
		# print('changePrice')
		if self.data_info:
			try:
				key_price = f'{self.COMBO_CHUC_NANG.get(self.combobox_chuc_nang.currentText())}_{self.COMBO_THOI_HAN.get(self.combobox_thoi_han.currentText())}'
				price = self.price_gia_han(self.data_info.get('price').get(key_price) * self.input_slm.value())
				
				self.lb_gia_tien_gia_han.setText(f"""<p style="font-size:14px; font-weight:bold; color: #f81919;">{'{:,}'.format(price)} Xu</p> """)
				
				key_price = f'{self.COMBO_SERVER_TTS.get(self.combobox_server_tts.currentText())}_{self.COMBO_GOI_TTS.get(self.combobox_goi_tts.currentText())}'
				
				if 'unlimited' in key_price.lower():
					price = self.data_info.get('price').get(key_price) * self.data_info.get('info_user').get('num_pc')
				else:
					price = self.data_info.get('price').get(key_price) * self.input_sl_voice.value()
				
				self.lb_gia_tien_tts.setText(f"""<p style="font-size:14px; font-weight:bold; color: #f81919;">{'{:,}'.format(price)} Xu</p>""")
				
				key_price = f'{self.COMBO_SERVER_TRANSLATE.get(self.combobox_server_translate.currentText())}_{self.COMBO_GOI_TRANSLATE.get(self.combobox_goi_translate.currentText())}'
				if 'unlimited' in key_price.lower():
					price = self.data_info.get('price').get(key_price) * self.data_info.get('info_user').get('num_pc')
				else:
					price = self.data_info.get('price').get(key_price) * self.input_sl_trans.value()
				self.lb_gia_tien_translate.setText(f"""<p style="font-size:14px; font-weight:bold; color: #f81919;">{'{:,}'.format(price)} Xu</p>""")
			except:
				pass
	
	def loadData (self, data_info):
		if hasattr(self, 'spiner'):
			self.spiner.stop()
		# self.lb_username.setText(f"""Token Translate Pro: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data_info.get('info_user').get('token_translate_pro1')}</p>""")
		self.lb_so_du.setText(f"""Số Xu Dư: <p style="font-size:15px; font-weight:bold; color: #f81919;">{'{:,}'.format(data_info.get('info_user').get('amount'))} Xu</p>""")
		self.lb_han_su_dung.setText(f"""Hạn Dùng: <p style="font-size:15px; font-weight:bold; color: #f81919;">{get_expired(data_info.get('info_user').get('expire_date'))}</p>""")
		self.lb_han_so_luong_may.setText(f"""Số Lượng PC: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data_info.get('info_user').get('num_pc')} PC Online</p>""")
		self.lb_han_chuc_nang.setText(f"""Chức Năng: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data_info.get('info_user').get('chuc_nang')}</p>""")
		self.lb_char_tieng_viet.setText(f"""Ký Tự Tiếng Việt: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data_info.get('info_user').get('char_tieng_viet') if isinstance(data_info.get('info_user').get('char_tieng_viet'), str) else '{:,}'.format(data_info.get('info_user').get('char_tieng_viet'))}</p>""")
		self.lb_char_da_ngon_ngu.setText(f"""Ký Tự Đa Ngôn Ngữ: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data_info.get('info_user').get('char_da_ngon_ngu') if isinstance(data_info.get('info_user').get('char_da_ngon_ngu'), str) else '{:,}'.format(data_info.get('info_user').get('char_da_ngon_ngu'))}</p>""")
		self.lb_token_chatgpt.setText(f"""Token ChatGPT: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data_info.get('info_user').get('token_chatgpt') if isinstance(data_info.get('info_user').get('token_chatgpt'), str) else '{:,}'.format(data_info.get('info_user').get('token_chatgpt'))}</p>""")
		self.lb_token_translate_pro1.setText(f"""Token Translate Pro: <p style="font-size:15px; font-weight:bold; color: #f81919;">{data_info.get('info_user').get('token_translate_pro1') if isinstance(data_info.get('info_user').get('token_translate_pro1'), str) else '{:,}'.format(data_info.get('info_user').get('token_translate_pro1'))}</p>""")
		
		self.COMBO_CHUC_NANG = data_info.get('gia_han').get('chuc_nang')
		self.combobox_chuc_nang.clear()
		self.combobox_chuc_nang.addItems(list(self.COMBO_CHUC_NANG.keys()))
		
		self.COMBO_THOI_HAN = data_info.get('gia_han').get('thoi_han')
		self.combobox_thoi_han.clear()
		self.combobox_thoi_han.addItems(list(self.COMBO_THOI_HAN.keys()))
		
		key_price = f'{self.COMBO_CHUC_NANG.get(self.combobox_chuc_nang.currentText())}_{self.COMBO_THOI_HAN.get(self.combobox_thoi_han.currentText())}'
		self.lb_gia_tien_gia_han.setText(f"""<p style="font-size:14px; font-weight:bold; color: #f81919;">{'{:,}'.format(data_info.get('price').get(key_price))} Xu</p> """)
		
		self.COMBO_SERVER_TTS = data_info.get('tts').get('server')
		self.combobox_server_tts.clear()
		
		self.combobox_server_tts.addItems(list(self.COMBO_SERVER_TTS.keys()))
		
		self.COMBO_GOI_TTS = data_info.get('tts').get('plan')
		self.combobox_goi_tts.clear()
		
		self.combobox_goi_tts.addItems(list(self.COMBO_GOI_TTS.keys()))
		
		key_price = f'{self.COMBO_SERVER_TTS.get(self.combobox_server_tts.currentText())}_{self.COMBO_GOI_TTS.get(self.combobox_goi_tts.currentText())}'
		self.lb_gia_tien_tts.setText(f"""<p style="font-size:14px; font-weight:bold; color: #f81919;">{'{:,}'.format(data_info.get('price').get(key_price))} Xu</p>""")
		
		self.COMBO_SERVER_TRANSLATE = data_info.get('translate').get('server')
		self.combobox_server_translate.clear()
		
		self.combobox_server_translate.addItems(list(self.COMBO_SERVER_TRANSLATE.keys()))
		
		self.COMBO_GOI_TRANSLATE = data_info.get('translate').get('plan')
		self.combobox_goi_translate.clear()
		
		self.combobox_goi_translate.addItems(list(self.COMBO_GOI_TRANSLATE.keys()))
		
		key_price = f'{self.COMBO_SERVER_TRANSLATE.get(self.combobox_server_translate.currentText())}_{self.COMBO_GOI_TRANSLATE.get(self.combobox_goi_translate.currentText())}'
		self.lb_gia_tien_translate.setText(f"""<p style="font-size:14px; font-weight:bold; color: #f81919;">{'{:,}'.format(data_info.get('price').get(key_price))} Xu</p>""")
		
		self.data_info = data_info
