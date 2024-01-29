import sys
import time

import requests
# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QFrame, QHBoxLayout, QSpacerItem, QSizePolicy

from gui.helpers.constants import TOOL_CODE_MAIN, PAE_LG, SETTING_APP_DATA, USER_DATA
from gui.helpers.ect import cr_pc, mh_ae, gm_ae
from gui.helpers.func_helper import get_expired, setValueSettings
from gui.helpers.get_data import URL_API_BASE
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox


# PY CREDITS BAR AND VERSION
# ///////////////////////////////////////////////////////////////
class PyCredits(QWidget):
	def __init__ (
			self,
		
			manage_thread_pool,
			copyright,
			version,
			token,
			expried,
			bg_two,
			font_family,
			text_size,
			text_description_color,
			radius=8,
			padding=10
	):
		super().__init__()
		
		# PROPERTIES
		self._copyright = copyright
		self._version = version
		self.expried = expried
		self.token = token
		self._bg_two = bg_two
		self._font_family = font_family
		self._text_size = text_size
		self._text_description_color = text_description_color
		self._radius = radius
		self._padding = padding
		self.manage_thread_pool = manage_thread_pool
		# self.dialog = PyDialogShop(self.manage_thread_pool,self.token)
		
		# SETUP UI
		self.setup_ui()
	
	def setup_ui (self):
		# ADD LAYOUT
		self.widget_layout = QHBoxLayout(self)
		self.widget_layout.setContentsMargins(0, 0, 0, 0)
		
		# BG STYLE
		style = f"""
     
        QLabel {{
            font: {self._text_size}pt "{self._font_family}";
          
            padding-left: {self._padding}px;
            padding-right: {self._padding}px;
        }}
        """
		self.setProperty("class", "border_none")
		# BG FRAME
		self.bg_frame = QFrame()
		self.bg_frame.setProperty("class", "border_none")
		self.bg_frame.setObjectName("bg_frame")
		self.bg_frame.setStyleSheet(style)
		
		# ADD TO LAYOUT
		self.widget_layout.addWidget(self.bg_frame)
		self.widget_layout.setProperty("class", "border_none")
		# ADD BG LAYOUT
		self.bg_layout = QHBoxLayout(self.bg_frame)
		self.bg_layout.setContentsMargins(0, 0, 0, 0)
		
		# ADD COPYRIGHT TEXT
		self.copyright_label = QLabel('Copyright: ' + self._copyright)
		self.copyright_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
		
		# ADD VERSION TEXT
		self.version_label = QLabel('Version: ' + self._version)
		self.version_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
		
		# SEPARATOR
		self.separator = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
		
		self.lb_fb = QLabel()
		self.lb_fb.setText('''<a style="color:white;" href='http://fb.com/sangcta86'>Facebook Admin</a>''')
		self.lb_fb.setOpenExternalLinks(True)
		
		self.lb_zalo = QLabel()
		self.lb_zalo.setText('''<a style="color:white" href='https://zalo.me/0985026855'>Zalo Admin</a>''')
		self.lb_zalo.setOpenExternalLinks(True)
		
		self.lb_group = QLabel()
		self.lb_group.setText('''<a style="color:white" href='https://zalo.me/g/lqzmdi108'>Group Hỗ Trợ</a>''')
		self.lb_group.setOpenExternalLinks(True)
		
		self.lb_video = QLabel()
		self.lb_video.setText('''<a style="color:white" href='https://www.youtube.com/channel/UCduIMFQGBWb2wm41XcKlTvw'>Video Hướng Dẫn</a>''')
		self.lb_video.setOpenExternalLinks(True)
		
		self.lb_expire_date = QLabel("Thời gian hết hạn: " + get_expired(self.expried))
		
		self.btn_logout = QPushButton("Đăng Xuất")
		self.btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_logout.setStyleSheet("padding-left:10px;padding-right:10px;")
		self.btn_logout.clicked.connect(self.clickLogout)
		
		
		# self.btn_shop = PyButtonIcon(
        #     icon_path=ConfigResource.set_svg_icon("shop.png"),
        #     parent=self,
        #     app_parent=self,
		# 	width=30,
		# 	height=30,
        #     icon_color="#ff0b2d",
        #     icon_color_hover="#ffe270",
        #     icon_color_pressed="#d1a807",
        #     tooltip_text="Shopping"
        # )
		self.btn_shop = QPushButton("NTS SHOP")
		self.btn_shop.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_shop.setStyleSheet("padding-left:10px;padding-right:10px;border-radius: 25px")
		# self.btn_shop.clicked.connect(self.openShop)
		
		
		# ADD TO LAYOUT
		self.bg_layout.addSpacerItem(self.separator)
		self.bg_layout.addWidget(self.lb_fb)
		self.bg_layout.addWidget(QLabel(""))
		self.bg_layout.addWidget(self.lb_zalo)
		self.bg_layout.addWidget(QLabel(""))
		
		self.bg_layout.addWidget(self.lb_group)
		self.bg_layout.addWidget(QLabel(""))
		self.bg_layout.addWidget(self.lb_video)
		self.bg_layout.addWidget(QLabel(""))
		self.bg_layout.addWidget(self.lb_expire_date)
		# self.bg_layout.addWidget(QLabel(""))
		self.bg_layout.addWidget(QLabel(""))
		# self.bg_layout.addWidget(self.btn_shop)
		self.bg_layout.addSpacerItem(self.separator)
		self.bg_layout.addWidget(self.copyright_label)
		self.bg_layout.addWidget(self.version_label)
		self.bg_layout.addWidget(QLabel(""))
	
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
			self.dialog.loadData(data_info)
			if self.dialog.exec():
				print('ok')
			else:
				print('cancel')
				
	def clickLogout (self):
		dataLogin = {
			"cp": cr_pc(),
			"tool_code": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		headers = {
			"Authorization": f"Bearer {self.token}"}
		data_encrypt = mh_ae(dataLogin, PAE_LG)
		res = requests.post(url=URL_API_BASE + "/users/private/logout",
			json={"data": data_encrypt}, headers=headers)
		
		if res.status_code == 200:
			

			setValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN, '')
			setValueSettings(USER_DATA, TOOL_CODE_MAIN, '')
			sys.exit()

		else:
			return PyMessageBox().show_warning("Lỗi", res.json()["message"])
