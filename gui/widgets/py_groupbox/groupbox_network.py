import json

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QRadioButton

from gui.configs.config_resource import ConfigResource
from gui.db.sqlite import CauHinhTuyChonModel
from gui.widgets.py_dialogs.py_dialog_proxy import PyDialogProxy
from gui.widgets.py_dialogs.py_dialog_tmproxy import PyDialogTMProxy
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_radio_buttion import PyRadioButton


class GroupBoxNetwork(QWidget):
	def __init__ (self, manage_thread_pool, is_save_db=False):
		super().__init__()
		# các biến giá trị
		self.manage_thread_pool = manage_thread_pool
		self.is_save_db = is_save_db
		
		self.radio_selected = None  # biến lưu trữ radio nào được chọn
		self.isAutoUpdate = True
		self.data_proxy = None
		self.data_tmproxy = None
		self.data_hma = None
		# self.data_network = None # biến lưu trữ các dữ liệu của danh sách proxy
		
		self.setup_ui()
	
	def setup_ui (self):
		self.create_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.modify_widgets()
		self.setup_connections()
	
	def create_widgets (self):
		self.groupbox = QGroupBox("Network")
		# self.groupbox.setCheckable(True)
		
		# Proxy
		self.rad_wifi = PyRadioButton(value="wifi", text="Wifi")
		
		# Proxy
		self.rad_proxy = PyRadioButton(value="proxy", text="Proxy")
		self.dialog_proxy = PyDialogProxy(self.manage_thread_pool)
		# self.dialog_proxy.textarea_proxy.toPlainText()
		self.btn_proxy = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("settings.png"),
			parent=self,
			app_parent=self.groupbox,
			width=25,
			height=25,
			tooltip_text="Cài đặt",
		
		)
		self.btn_proxy.setDisabled(True)
		# TM Proxy
		self.rad_tmproxy = PyRadioButton(value="tmproxy", text="TMProxy")
		self.dialog_tmproxy = PyDialogTMProxy()
		self.btn_tmproxy = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("settings.png"),
			parent=self,
			app_parent=self.groupbox,
			width=25,
			height=25,
			tooltip_text="Cài đặt",
		
		)
		self.btn_tmproxy.setDisabled(True)
		# HMA
		self.rad_hma = PyRadioButton(value="hma", text="HMA")
		# self.dialog_hma= PyDialogHMA()
		# self.btn_hma = PyButtonIcon(
		#     icon_path=ConfigResource.set_svg_icon("settings.png"),
		#     parent=self,
		#     width=20,
		#     height=20,
		#
		#     app_parent=self.groupbox,
		#     tooltip_text="Cài đặt",
		#
		# )
	
	def modify_widgets (self):
		pass
	
	def create_layouts (self):
		self.bg_layout = QHBoxLayout()
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		self.gbox_layout = QVBoxLayout()
		self.groupbox.setLayout(self.gbox_layout)
		
		self.content_layout = QHBoxLayout()
		
		self.content_4g_layout = QHBoxLayout()
		self.content_wifi_layout = QHBoxLayout()
		self.content_proxy_layout = QHBoxLayout()
		self.content_tmproxy_layout = QHBoxLayout()
		self.content_hma_layout = QHBoxLayout()
	
	def add_widgets_to_layouts (self):
		self.bg_layout.addWidget(self.groupbox)
		self.setLayout(self.bg_layout)
		
		self.gbox_layout.addWidget(QLabel(""))
		self.gbox_layout.addLayout(self.content_layout)
		
		self.content_layout.addWidget(self.rad_wifi, 25)
		# self.content_layout.addWidget(self.rad_hma, 25)
		self.content_layout.addLayout(self.content_proxy_layout, 25)
		# self.content_layout.addLayout(self.content_tmproxy_layout, 25)
		
		self.content_proxy_layout.addWidget(self.rad_proxy, 10)
		self.content_proxy_layout.addWidget(self.btn_proxy, 10)
		self.content_proxy_layout.addWidget(QLabel(), 80)
		
		self.content_tmproxy_layout.addWidget(self.rad_tmproxy, 10)
		self.content_tmproxy_layout.addWidget(self.btn_tmproxy, 10)
		self.content_tmproxy_layout.addWidget(QLabel(), 80)
	
	def setup_connections (self):
		# self.groupbox.toggled.connect(self._groupboxStatusChanged)
		self.btn_proxy.clicked.connect(self.open_dialog_proxy)
		self.btn_tmproxy.clicked.connect(self.open_dialog_tmproxy)
		
		self.rad_proxy.clicked.connect(lambda: self.check_radio_button(self.rad_proxy))
		self.rad_tmproxy.clicked.connect(lambda: self.check_radio_button(self.rad_tmproxy))
		self.rad_wifi.clicked.connect(lambda: self.check_radio_button(self.rad_wifi))
		self.rad_hma.clicked.connect(lambda: self.check_radio_button(self.rad_hma))
	
	def loadData (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
		cau_hinh = json.loads(configCurrent.value)
		# print(cau_hinh)
		# self.groupbox.setChecked(cau_hinh["use_proxy"])
		if self.is_save_db is False:
			if cau_hinh["network_actived"] == "proxy":
				self.rad_proxy.setChecked(True)
				self.btn_proxy.setDisabled(False)
			elif cau_hinh["network_actived"] == "tmproxy":
				self.rad_tmproxy.setChecked(True)
				self.btn_tmproxy.setDisabled(False)
			
			elif cau_hinh["network_actived"] == "hma":
				self.rad_hma.setChecked(True)
			
			elif cau_hinh["network_actived"] == "wifi":
				self.rad_wifi.setChecked(True)
		else:
			self.rad_wifi.setChecked(True)
		
		self.dialog_tmproxy.loadData(configCurrent)
		self.dialog_proxy.loadData(configCurrent)
	
	def check_radio_button (self, rad):
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			if rad == self.rad_proxy and self.rad_proxy.isChecked():
				self.btn_proxy.setDisabled(False)
				self.btn_tmproxy.setDisabled(True)
				cau_hinh["network_actived"] = "proxy"
			
			elif rad == self.rad_tmproxy and self.rad_tmproxy.isChecked():
				self.btn_tmproxy.setDisabled(False)
				self.btn_proxy.setDisabled(True)
				cau_hinh["network_actived"] = "tmproxy"
			
			elif rad == self.rad_hma and self.rad_hma.isChecked():
				self.btn_tmproxy.setDisabled(True)
				self.btn_proxy.setDisabled(True)
				cau_hinh["network_actived"] = "hma"
			
			elif rad == self.rad_wifi and self.rad_wifi.isChecked():
				self.btn_tmproxy.setDisabled(True)
				self.btn_proxy.setDisabled(True)
				cau_hinh["network_actived"] = "wifi"
			
			if self.is_save_db is False:
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
		else:
			if rad == self.rad_proxy and self.rad_proxy.isChecked():
				self.btn_proxy.setDisabled(False)
				self.btn_tmproxy.setDisabled(True)
			
			elif rad == self.rad_tmproxy and self.rad_tmproxy.isChecked():
				self.btn_tmproxy.setDisabled(False)
				self.btn_proxy.setDisabled(True)
			
			elif rad == self.rad_hma and self.rad_hma.isChecked():
				self.btn_tmproxy.setDisabled(True)
				self.btn_proxy.setDisabled(True)
			
			elif rad == self.rad_wifi and self.rad_wifi.isChecked():
				self.btn_tmproxy.setDisabled(True)
				self.btn_proxy.setDisabled(True)
	
	def open_dialog_proxy (self):
		
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			self.dialog_proxy.loadData(self.configCurrent)
			if self.dialog_proxy.exec():
				# if not cau_hinh["proxy_raw"] == self.dialog_proxy.getValue():
				cau_hinh["proxy_raw"] = self.dialog_proxy.getValue()
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
			else:
				print("Cancel!")
		else:
			if self.dialog_tmproxy.exec():
				pass
			else:
				print("Cancel!")
	
	def open_dialog_tmproxy (self):
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			
			self.dialog_tmproxy.loadData(self.configCurrent)
			if self.dialog_tmproxy.exec():
				if not cau_hinh["tmproxy"] == self.dialog_tmproxy.getValue():
					cau_hinh["tmproxy"] = self.dialog_tmproxy.getValue()
					
					self.configCurrent.value = json.dumps(cau_hinh)
					self.configCurrent.save()
			else:
				print("Cancel!")
		else:
			if self.dialog_tmproxy.exec():
				pass
			else:
				print("Cancel!")
	
	# def _groupboxStatusChanged(self, status):
	#     if hasattr(self, "configCurrent") :
	#         cau_hinh = json.loads(self.configCurrent.value)
	#         cau_hinh["use_proxy"] = status
	#         self.configCurrent.value = json.dumps(cau_hinh)
	#         self.configCurrent.save()
	
	def clearData (self):
		# if hasattr(self, "cau_hinh"):
		#     delattr(self, "cau_hinh")
		# for rb in self.groupbox.findChildren(QRadioButton):
		#     rb.setAutoExclusive(False)  # chỗ này để uncheck radio
		#     rb.setChecked(False)
		#     rb.setAutoExclusive(True)
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
		self.rad_wifi.setChecked(True)
		# self.groupbox.setChecked(False)
		self.dialog_tmproxy.clearData()
		self.dialog_proxy.clearData()
	
	def getValue (self):
		network_actived = ""
		for rb in self.groupbox.findChildren(QRadioButton):
			if rb.isChecked():
				network_actived = rb.getValue()
		return {
			# "use_proxy": self.groupbox.isChecked(),
			"network_actived": network_actived,
			"proxy_raw": self.dialog_tmproxy.getValue(),
			"tmproxy": self.dialog_proxy.getValue(),
		}
