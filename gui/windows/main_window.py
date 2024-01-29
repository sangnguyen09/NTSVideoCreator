import atexit
import os
import sys
import time

import requests
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout, QMainWindow

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN, \
	USER_DATA, \
	SC_D_CL, PAE_LG, PROCESS_FFSUB_THREAD
from gui.helpers.ect import mh_ae_w
from gui.helpers.func_helper import setValueSettings, s_d_u, \
	r_p_c_e
from gui.helpers.get_data import URL_API_BASE, VERSION_CURRENT
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_credits_bar import PyCredits
from gui.widgets.py_grips import PyGrips
from gui.widgets.py_tab.py_tab_main import PyTab
from gui.widgets.py_title_bar import PyTitleBar


class MainWindow(QMainWindow):
	def __init__ (self, file_run_app, data_setting, data_user):
		QMainWindow.__init__(self)
		self.thread_pool = ManageThreadPool()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# self.st = QSettings(*SETTING_APP)
		setValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN, data_setting)
		setValueSettings(USER_DATA, TOOL_CODE_MAIN, data_user)
		self.settings = data_setting
		self.user_data = data_user
		# self.version = getValueSettings(SETTING_VERSION_APP, TOOL_CODE_AUTOSUB)
		self.version = VERSION_CURRENT
		self.file_run_app = file_run_app
		
		# print(self.user_data)
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		
		# SET INITIAL PARAMETERS
		self.resize(self.settings['data_setting']["startup_size"][0], self.settings['data_setting']["startup_size"][1])
		self.setMinimumSize(
			self.settings['data_setting']["minimum_size"][0], self.settings['data_setting']["minimum_size"][1])
		if not self.settings['data_setting']["fixedSize"]:
			self.setFixedSize(self.size())
		
		# SET UP MAIN WINDOW
		self.setWindowTitle(self.settings['data_setting']["app_name"])
		self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		
		self.setup_ui()
		
		self.title_bar.set_title(self.settings['data_setting']["app_name"])
		self.setCentralWidget(self.central_widget)
		
		# reside ứng dụng
		self.left_grip = PyGrips(self, "left", True)
		self.right_grip = PyGrips(self, "right", True)
		self.top_grip = PyGrips(self, "top", True)
		# self.bottom_grip = PyGrips(self, "bottom", True)
		self.top_left_grip = PyGrips(self, "top_left", True)
		self.top_right_grip = PyGrips(self, "top_right", True)
		self.bottom_left_grip = PyGrips(self, "bottom_left", True)
		self.bottom_right_grip = PyGrips(self, "bottom_right", True)
		#
		if self.settings['data_setting']["isMaximized"] is True:
			self.title_bar.maximize_restore_button.click()
	
	def s_d (self, code_pc, username):
		self.thread_pool.start(self._f_s_d, SC_D_CL, SC_D_CL, file_run_app=self.file_run_app, code_pc=code_pc, username=username)
	
	def _f_s_d (self, **kwargs):
		# print("scan")
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		file_run_app = kwargs["file_run_app"]
		code_pc = kwargs["code_pc"]
		username = kwargs["username"]
		# //////////////////////check client//////////////////////////////////
		is_check, path = s_d_u()
		
		if is_check is True:
			dataReq = {
				"cp": code_pc,
				"tool_code": TOOL_CODE_MAIN,
				"username": username,
				"path": path,
				't': int(float(time.time())),
			}
			data_encrypt = mh_ae_w(dataReq, PAE_LG)
			try:
				res = requests.post(url=URL_API_BASE + "/check-user/public/add",
					json={"data": data_encrypt})
			except:
				pass
		
		thread_pool.finishSingleThread(id_worker)
		return is_check, file_run_app
	
	def resultChanged (self, id_worker, id_thread, result):
		#
		if id_thread == PROCESS_FFSUB_THREAD:
			if result:
				self.process = result
			
		if id_thread == SC_D_CL:
			is_check, file_run_app = result
			if is_check is True:
				namefile, ext = os.path.splitext(file_run_app)
				path = namefile + ".exe"
				# print('CÓ')
				atexit.register(lambda path=path: r_p_c_e(path))
				sys.exit()
	
	# self.dragPos =QPoint(0,0)
	def setup_ui (self):
		self.create_widgets()
		
		self.modify_widgets()
		
		self.create_layouts()
		
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	
	# print(self.move())
	
	def create_widgets (self):
		# SET CENTRAL WIDGET
		# Add central widget to app
		# ///////////////////////////////////////////////////////////////
		self.central_widget = QWidget()
		
		self.app_frame = QFrame()
		self.app_frame.setProperty("class", "border_none")
		
		self.title_bar_frame = QFrame()
		self.title_bar_frame.setMinimumHeight(40)
		self.title_bar_frame.setMaximumHeight(40)
		self.title_bar_frame.setProperty("class", "border_none")
		
		# ADD CUSTOM TITLE BAR TO LAYOUT
		self.title_bar = PyTitleBar(
			self,
			logo_width=100,
			app_parent=self,
			logo_image="icon_logo.svg",
			bg_color=self.themes.app_color["bg_two"],
			div_color=self.themes.app_color["bg_three"],
			btn_bg_color=self.themes.app_color["bg_two"],
			btn_bg_color_hover=self.themes.app_color["bg_three"],
			btn_bg_color_pressed=self.themes.app_color["bg_one"],
			icon_color=self.themes.app_color["icon_color"],
			icon_color_hover=self.themes.app_color["icon_hover"],
			icon_color_pressed=self.themes.app_color["icon_pressed"],
			icon_color_active=self.themes.app_color["icon_active"],
			context_color=self.themes.app_color["context_color"],
			dark_one=self.themes.app_color["dark_one"],
			text_foreground=self.themes.app_color["text_foreground"],
			radius=8,
			font_family=self.settings['data_setting']["font"]["family"],
			title_size=self.settings['data_setting']["font"]["title_size"],
		
		)
		
		# Footer ứng dụng
		self.credits = PyCredits(
			self.thread_pool,
			bg_two=self.themes.app_color["bg_two"],
			copyright=self.settings['data_setting']["copyright"],
			version=self.version,
			token=self.user_data.get('token'),
			expried=self.user_data['list_tool'].get(TOOL_CODE_MAIN).get('expire_date'),
			font_family=self.settings['data_setting']["font"]["family"],
			text_size=self.settings['data_setting']["font"]["text_size"],
			text_description_color=self.themes.app_color["text_description"]
		)
		
		self.tabMain = PyTab(self.file_run_app, self.thread_pool,self.settings.get('data_setting'))
	
	def modify_widgets (self):
		self.central_widget.setStyleSheet("padding:0;margin:0;border-radius:0")
	
	# self.central_widget.setAttribute(Qt.WA_TranslucentBackground)
	
	def create_layouts (self):
		self.central_widget_layout = QVBoxLayout(self.central_widget)
		self.central_widget_layout.setContentsMargins(0, 0, 0, 0)
		
		self.app_layout = QVBoxLayout(self.app_frame)
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.app_layout.setSpacing(0)
		
		self.title_bar_layout = QVBoxLayout(self.title_bar_frame)
		self.title_bar_layout.setContentsMargins(0, 0, 0, 0)
		self.content_frame = QWidget()
		# self.content_frame.setStyleSheet(" border-style: none");
		# Thêm giao diện tùy chỉnh vào layout này
		self.content_layout = QVBoxLayout(self.content_frame)
		self.content_layout.setContentsMargins(5, 0, 0, 5)
		self.content_layout.setSpacing(0)
		
		# self.content_layout.
		
		self.credits_frame = QFrame()
		self.credits_frame.setObjectName("bg_frame")
		
		self.credits_frame.setMinimumHeight(30)
		self.credits_frame.setMaximumHeight(30)
		self.credits_layout = QVBoxLayout(self.credits_frame)
		self.credits_layout.setContentsMargins(0, 0, 0, 5)
		self.credits_frame.setProperty("class", "border_none")
	
	
	def add_widgets_to_layouts (self):
		self.central_widget_layout.addWidget(self.app_frame)
		
		self.title_bar_layout.addWidget(self.title_bar)
		self.credits_layout.addWidget(self.credits)
		# Thêm tùy chỉnh ở đây
		self.content_layout.addWidget(self.tabMain)
		
		self.app_layout.addWidget(self.title_bar_frame)
		self.app_layout.addWidget(self.content_frame)
		self.app_layout.addWidget(self.credits_frame)
	
	# self.window.layout.addWidget(self.app_frame)
	
	def setup_connections (self):
		self.thread_pool.resultChanged.connect(self.resultChanged)
		
		pass
	
	def resize_grips (self):
		self.left_grip.setGeometry(5, 10, 10, self.height())
		self.right_grip.setGeometry(self.width() - 15, 10, 10, self.height())
		self.top_grip.setGeometry(5, 5, self.width() - 10, 10)
		# self.bottom_grip.setGeometry(5, self.height() - 15, self.width() - 10, 10)
		self.top_right_grip.setGeometry(self.width() - 20, 5, 15, 15)
		self.bottom_left_grip.setGeometry(5, self.height() - 20, 15, 15)
		self.bottom_right_grip.setGeometry(self.width() - 20, self.height() - 20, 15, 15)
	
	def resizeEvent (self, event):
		self.resize_grips()
	
	def closeEvent (self, event):
		setValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN, '')
		setValueSettings(USER_DATA, TOOL_CODE_MAIN, '')
		try:
			if hasattr(self, "process"):
				self.process.kill()
				self.process.terminate()
				print('close')
		except:
			pass
	# self.st.remove(UPDATE_APP_DATA)
	
	# rp_f()
