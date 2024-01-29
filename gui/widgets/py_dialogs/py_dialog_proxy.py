import json

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QDialog, QPlainTextEdit

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import CHECK_LIVE_PROXY_ON_NETWORK, SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.helpers.http_request.check_proxy import ProxyChecker
from gui.helpers.thread import ManageThreadPool
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


class PyDialogProxy(QDialog):
	checkLiveProxySignal = Signal(list)
	
	def __init__ (self, manage_thread_pool: ManageThreadPool):
		super().__init__()
		
		self.manage_thread_pool = manage_thread_pool
		self.checker = ProxyChecker(manage_thread_pool)
		
		self.list_proxy_live = []
		self.list_proxy_die = []
		self.count_proxy = 0
		self.total_proxy = 0
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Danh dách Proxy")
		self.setStyleSheet(self.style_format)
		
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		
		self.buttonSave = QPushButton("Lưu")
		self.buttonSave.setCursor(Qt.CursorShape.PointingHandCursor)
		self.buttonCheckLive = QPushButton("Check Live")
		self.buttonCheckLive.setCursor(Qt.CursorShape.PointingHandCursor)
		self.lb_check_live = QLabel("")
		self.lb_check_live_status = QLabel("")
		self.lb_check_live_status.setAlignment(Qt.AlignmentFlag.AlignRight)
		self.lb_check_live_status.setAlignment(Qt.AlignmentFlag.AlignHCenter)
		self.textarea_proxy = QPlainTextEdit()
		self.textarea_proxy.setPlaceholderText("Nhập list proxy")
	
	def modify_widgets (self):
		self.buttonSave.setDisabled(True)
		self.buttonCheckLive.setDisabled(True)
	
	def create_layouts (self):
		
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.app_layout.setSpacing(0)
		
		self.btn_layout = QHBoxLayout()
		
		self.content_frame = QWidget()
		
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.textarea_proxy, 90)
		self.content_layout.addLayout(self.btn_layout, 10)
		
		self.btn_layout.addWidget(self.lb_check_live, 30)
		self.btn_layout.addWidget(self.buttonCheckLive, 20)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(self.lb_check_live_status, 30)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.save)
		self.buttonCheckLive.clicked.connect(self._clickCheckLive)
		self.textarea_proxy.textChanged.connect(self._textareaValueChanged)
		self.checker.finishedCheckLiveProxySignal.connect(self._finishedCheckLiveProxySignal)
	
	def loadData (self, configCurrent):
		self.configCurrent = configCurrent
		cau_hinh = json.loads(configCurrent.value)
		
		if not cau_hinh["proxy_raw"] == '':
			self.buttonCheckLive.setDisabled(False)
		self.count_proxy = 0
		self.total_proxy = len(cau_hinh["proxy_raw"].split("\n"))
		self.lb_check_live_status.clear()
		self.textarea_proxy.clear()
		self.textarea_proxy.appendPlainText(cau_hinh["proxy_raw"])
	
	def _textareaValueChanged (self):
		
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			if not self.textarea_proxy.toPlainText() == cau_hinh["proxy_raw"]:
				self.buttonSave.setDisabled(True)
				self.buttonCheckLive.setDisabled(False)
				self.lb_check_live.clear()
				self.count_proxy = 0
				self.total_proxy = 0
				self.lb_check_live_status.clear()
				self.lb_check_live_status.setStyleSheet("color:white")
				self.list_proxy_live = []
				self.list_proxy_die = []
		else:
			self.buttonCheckLive.setDisabled(True)
	
	def _finishedCheckLiveProxySignal (self, id_thread, result):
		
		if id_thread == CHECK_LIVE_PROXY_ON_NETWORK:
			''' kết quả kiểm tra live proxy'''
			self.textarea_proxy.clear()
			self.textarea_proxy.appendPlainText('\n'.join(map(str, result['proxy_live'])))
			
			self.lb_check_live.setText(f"Live: {len(result['proxy_live'])}\nDie: {len(result['proxy_die'])}")
			self.lb_check_live_status.setText("Hoàn Thành")
			self.lb_check_live_status.setStyleSheet("color:green")
			self.buttonSave.setDisabled(False)
			
			PyMessageBox().show_info("Thông tin", "Check Live Hoàn Thành!")
	
	
	def _clickCheckLive (self):
		
		list_proxy = self.textarea_proxy.toPlainText().split("\n")
		try:
			if not list_proxy == ['']:
				self.lb_check_live.setText(f"Live: 0\nDie: 0")
				self.lb_check_live_status.setText("Đang check live...")
				self.buttonCheckLive.setDisabled(True)
				
				self.checker.checkLiveProxyOnThread(self.manage_thread_pool, list_proxy,
					CHECK_LIVE_PROXY_ON_NETWORK,
				)
			else:
				self.manage_thread_pool.messageBoxChanged.emit("Lỗi", "Vui lòng cung cấp thêm proxy", "error")
		except Exception as e:
			try:
				PyMessageBox().show_warning('Cảnh Báo', str(e))
			finally:
				e = None
				del e
	
	def save (self):
		PyMessageBox().show_warning("Thông Báo", "Các proxy die sẽ được xoá và các proxy live sẽ lưu vào cơ sở dữ liệu")
		self.accept()
	
	def getValue (self):
		
		return self.textarea_proxy.toPlainText()
	
	# return '\n'.join(map(str, self.list_proxy_live))
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.textarea_proxy.clear()
