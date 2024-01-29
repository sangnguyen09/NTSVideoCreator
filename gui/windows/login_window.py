import atexit
import os
import subprocess
import sys
import time

import gdown
from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMainWindow, QGraphicsDropShadowEffect
from pypdl import Downloader

from gui.helpers.constants import TOOL_CODE_MAIN, PAE_LG, SETTING_APP, NAME_APP_UPDATE, \
	USER_DATA, LOGIN_ACCOUNT, \
	UPDATE_TOOL_AUTOSUB, ACCOUNT_LOCKED, CLOSE_APP, DOWNLOAD_FILE_UPDATE, JOIN_PATH, \
	APP_PATH, REMEMBER_ME, LOGOUT_ACCOUNT_FE, REG_ACCOUNT, REG_SUCCESS
from gui.helpers.get_data import URL_API_BASE, VERSION_CURRENT
from .main_window import MainWindow
from ..helpers.custom_logger import customLogger
from ..helpers.ect import cr_pc, gm_ae_w, mh_ae_w
from ..helpers.func_helper import which, r_p_c_e, setValueSettings, getValueSettings
from ..helpers.http_request.request import HTMLSession
from ..helpers.thread import ManageThreadPool
from ..uis.ui_login import Ui_Login
from ..widgets.py_dialogs.py_dialog_show_version import PyDialogShowVersion
from ..widgets.py_messagebox.py_massagebox import PyMessageBox
from ..widgets.py_spinner.spinner import WaitingSpinner


class LoginWindow(QMainWindow):
	def __init__ (self, file_run_app):
		QMainWindow.__init__(self)
		self.ui = Ui_Login()  # khởi tạo
		self.ui.setupUi(self)  # hàm này trong class
		self.isFormLogin = True  # hiện form đăng nhập
		self.file_run_app = file_run_app  # file chạy
		self.thread_pool = ManageThreadPool()
		self.thread_pool.resultChanged.connect(self.resultChanged)
		
		self.settings = QSettings(*SETTING_APP)
		# self.main = main_window
		
		self.request = HTMLSession()
		
		# _____________ Remember me-------------
		remember_me = getValueSettings(REMEMBER_ME, TOOL_CODE_MAIN)
		
		if remember_me is None:
			setValueSettings(REMEMBER_ME, TOOL_CODE_MAIN, {"username": "", "password": ""})
		else:
			self.ui.username.setText(remember_me.get('username'))
			self.ui.password.setText(remember_me.get('password'))
			if not remember_me.get('username') == '' and not remember_me.get('password') == '':
				self.ui.remember_account.setChecked(True)
		
		# Xóa title bar mặc định
		# ///////////////////////////////////////////////////////////////
		self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
		self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
		
		# ADD DROP SHADOW
		# ///////////////////////////////////////////////////////////////
		self.shadow = QGraphicsDropShadowEffect(self)
		self.shadow.setBlurRadius(15)
		self.shadow.setXOffset(0)
		self.shadow.setYOffset(0)
		self.shadow.setColor(QColor(0, 0, 0, 80))
		self.ui.bg_img.setGraphicsEffect(self.shadow)
		
		# ///////////////////////////////////////////////////////////////
		# bấm nút đăng ký hoặc đăng nhâp
		self.ui.saveForm.clicked.connect(self.check_login)
		self.ui.username.returnPressed.connect(self.check_login)
		self.ui.password.returnPressed.connect(self.check_login)
		self.ui.logout.clicked.connect(self.check_logout)
		self.ui.dangKy.clicked.connect(self.toggleForm)
		# self.thread_pool.start(self.loadSpinner,LOADING_SPINNER,LOADING_SPINNER)
		
		
		self.show()
	
	def toggleForm (self):
		self.isFormLogin = not self.isFormLogin
		if self.isFormLogin:
			self.ui.remember_account.show()
			self.ui.lb_title_form.setText("Đăng Nhập")
			self.ui.saveForm.setText("Đăng Nhập")
			self.ui.label_7.setText("Bạn chưa có tài khoản ?")
			self.ui.dangKy.setText("Đăng Ký")
		else:
			
			self.ui.remember_account.hide()
			self.ui.lb_title_form.setText("Đăng Ký")
			self.ui.saveForm.setText("Đăng Ký")
			self.ui.label_7.setText("Bạn đã có tài khoản ?")
			self.ui.dangKy.setText("Đăng Nhập")
	
	def check_logout (self):
		username = self.ui.username.text()
		password = self.ui.password.text()
		
		if not username or not password:
			return PyMessageBox().show_warning("Lỗi", "Bạn phải nhập đầy đủ thông tin!")
		
		is_ok = PyMessageBox().show_question("Thông báo", "LOG OUT sẽ làm cho tất cả các máy cùng 1 tài khoản sẽ bị LOG OUT ra, và phải đăng nhập lại mới sử dụng được. Bạn có chắc chắn muốn LOG OUT ?")
		if is_ok:
			self.thread_pool.start(self._func_check_logout, LOGOUT_ACCOUNT_FE, LOGOUT_ACCOUNT_FE, username=username, password=password)
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
	
	def _func_check_logout (self, **kwargs):
		try:
			username = kwargs["username"]
			password = kwargs["password"]
			
			dataLogin = {
				"cp": cr_pc("tool_khac"),
				"tool_code": TOOL_CODE_MAIN,
				"username": username,
				"password": password,
				't': int(float(time.time())),
			}
			data_encrypt = mh_ae_w(dataLogin, PAE_LG)
			
			res = self.request.post(url=URL_API_BASE + "/users/public/logout-fe",
				json={"data": data_encrypt})
			
			if res.status_code == 200:
				return True, ""
			elif res.status_code == 423:  # tài khoản bị khóa
				self.thread_pool.resultChanged.emit(ACCOUNT_LOCKED, ACCOUNT_LOCKED, "")
				return None
			else:
				return False, res.json()["message"]
		except Exception as e:
			print('Lỗi', str(e))
	
	def check_login (self):
		
		if " " in APP_PATH:
			return PyMessageBox().show_warning("Lỗi", "Thư mực chứa tool không được có khoảng trắng")

		username = self.ui.username.text()
		password = self.ui.password.text()
		
		if not username or not password:
			return PyMessageBox().show_warning("Lỗi", "Bạn phải nhập đầy đủ thông tin!")
		
		self.thread_pool.start(self._func_check_login, LOGIN_ACCOUNT, LOGIN_ACCOUNT, username=username, password=password)
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
	
	def _func_check_login (self, **kwargs):
		try:
			thread_pool = kwargs["thread_pool"]
			id_worker = kwargs["id_worker"]
			username = kwargs["username"]
			password = kwargs["password"]
			if self.isFormLogin:
				dataLogin = {
					"cp": cr_pc("tool_khac"),
					"tool_code": TOOL_CODE_MAIN,
					"username": username,
					"password": password,
					't': int(float(time.time())),
				}
				data_encrypt = mh_ae_w(dataLogin, PAE_LG)
				
				res = self.request.post(url=URL_API_BASE + "/users/public/login",
					json={"data": data_encrypt})
				# print(res.text)
				if res.status_code == 200:
					data_user = gm_ae_w(res.json()["data"], PAE_LG)
					# print(data_user['token'])
					# raise Exception
					headers = {
						"Authorization": f"Bearer {data_user['token']}"}
					datareq = {
						"cp": cr_pc("tool_khac"),
						't': int(float(time.time())),
					}
					res_st = self.request.post(url=URL_API_BASE + f"/setting-tool/private/{TOOL_CODE_MAIN}", headers=headers, json={
						"data": mh_ae_w(datareq, PAE_LG)})
					
					if res_st.status_code == 200:
						data_setting = gm_ae_w(res_st.json()["data"], data_user['paes'])
						# print(data_setting)
						# sau kiểm tra cập nhật mới
						res_vs = self.request.post(url=URL_API_BASE + f"/list-tool/private/check-version/{TOOL_CODE_MAIN}", headers=headers, json={
							"data": mh_ae_w(datareq, PAE_LG)})
						if res_vs.status_code == 200:
							version_new = gm_ae_w(res_vs.json()["data"], data_user['paes'])
							# version_current_autosub = getValueSettings(SETTING_VERSION_APP, TOOL_CODE_AUTOSUB)
							# if version_current_autosub is None:
							# 	return False, f'Tool {version_new.get("name_tool")} chưa đươợc cài đặt, vui lòng cài đặt nó trong tool "Installer"'
							#
							if not VERSION_CURRENT == version_new.get('version'):
								self.thread_pool.resultChanged.emit(UPDATE_TOOL_AUTOSUB, UPDATE_TOOL_AUTOSUB, {
									"version_new": version_new, "version_current_autosub": VERSION_CURRENT,
									"username": username, 'data_setting': data_setting, 'data_user': data_user})
								return None
						
						else:
							return False, res_vs.text
						
						return True, (username, password, data_setting, data_user)
					else:
						return False, res_st.text
				
				elif res.status_code == 423:  # tài khoản bị khóa
					self.thread_pool.resultChanged.emit(ACCOUNT_LOCKED, ACCOUNT_LOCKED, "")
					return None
				else:
					return False, res.text
			else:
				dataReg = {
					# "cp": self.code_pc,
					"username": username,
					"password": password,
					't': int(float(time.time())),
				}
				data_encrypt = mh_ae_w(dataReg, PAE_LG)
				
				res = self.request.post(url=URL_API_BASE + "/users/public/register",
					json={"data": data_encrypt})
				# print(res.text)
				if res.status_code == 200:
					self.thread_pool.resultChanged.emit(REG_ACCOUNT, REG_ACCOUNT, "")
					return None
				else:
					return False,res.text

		
		except Exception as e:
			customLogger("check_login", 140)
			self.thread_pool.resultChanged.emit(CLOSE_APP, CLOSE_APP, "")
	
	def resultChanged (self, id_worker, id_thread, result):
		# self.thread_pool.finishSingleThread(id_worker)
		# print(id_worker, id_thread, result)
		if id_thread == REG_ACCOUNT:
			self.spiner.stop()
			
			return PyMessageBox().show_info("Thông Báo", REG_SUCCESS)
		if id_thread == CLOSE_APP:
			sys.exit()
		
		if id_thread == ACCOUNT_LOCKED:
			PyMessageBox().show_error("Lỗi", "Tài khoản bị lỗi, vui lòng liên hệ admin !")
			# print('Sau này mở ra cận thận bị xóa het file')
			namefile, ext = os.path.splitext(self.file_run_app)
			path = namefile + ".exe"
			# print(path)
			atexit.register(lambda path=path: r_p_c_e(path))
			sys.exit()
		
		if id_thread == LOGOUT_ACCOUNT_FE:
			self.spiner.stop()
			if result is not None:
				is_ok, data = result
				if is_ok:
					return PyMessageBox().show_info("Thông báo", 'Bạn đã logout thành công, hãy đăng nhập lại để sử dụng tool')
				else:
					return PyMessageBox().show_warning("Lỗi", data)
		
		if id_thread == LOGIN_ACCOUNT:
			self.spiner.stop()
			if result is not None:
				is_ok, data = result
				if is_ok:
					username, password, data_setting, data_user = data
					
					if self.ui.remember_account.isChecked():
						setValueSettings(REMEMBER_ME, TOOL_CODE_MAIN,
							{"username": username, "password": password})
					else:
						setValueSettings(REMEMBER_ME, TOOL_CODE_MAIN, {"username": '', "password": ''})
					
					return self.open_main(username, data_setting, data_user)
				
				else:
					return PyMessageBox().show_warning("Lỗi", data)
		
		if id_thread == UPDATE_TOOL_AUTOSUB:
			version_current_autosub = result.get("version_current_autosub")
			version_new = result.get("version_new")
			username = result.get("username")
			data_setting = result.get("data_setting")
			data_user = result.get("data_user")
			
			if not version_current_autosub == version_new.get('version'):
				dialog = PyDialogShowVersion(text=version_new.get('ìnfo_version'), width=
				data_setting['data_setting']["dialog_size"][
					0], title=f'Những cập nhật mới của {version_new.get("name_tool")}')
				if dialog.exec():
					if dialog.is_skip is False:
						file_update = JOIN_PATH(APP_PATH, NAME_APP_UPDATE)
						
						if data_setting.get('data_setting').get("download_file_update"):
							if os.path.exists(file_update):
								os.unlink(file_update)
							# tải bản update mới về
							self.thread_pool.start(self._func_download, DOWNLOAD_FILE_UPDATE, DOWNLOAD_FILE_UPDATE, data_user=data_user,  file_update=file_update, url_file_update=data_setting.get('data_setting').get("url_file_update"))
							self.spiner.start()
						else:
							# open cập nhật
							if not which(file_update) is None:  # mở file cập nhật
								setValueSettings(USER_DATA, TOOL_CODE_MAIN, data_user)
								
								os.startfile(file_update)
								return self.close()
					else:
						return self.open_main(username, data_setting, data_user)
				else:
					return self.close()
		if id_thread == DOWNLOAD_FILE_UPDATE:
			# print("vapo")
			# print(which(APP_UPDATE))
			# if not which(APP_UPDATE) is None:  # mở file cập nhật
			# 	# print("vapo")
			file_update = JOIN_PATH(APP_PATH, NAME_APP_UPDATE)
			
			setValueSettings(USER_DATA, TOOL_CODE_MAIN, result)
			
			os.startfile(file_update)
			return self.close()
	
	def _func_download (self, **kwargs):
		# try:
		thread_pool = kwargs["thread_pool"]
		file_update = kwargs["file_update"]
		data_user = kwargs["data_user"]
		url_file_update = kwargs["url_file_update"]
		file_temp = JOIN_PATH(APP_PATH, "update.zip")
		# gdown.download(id=id, output=file_temp, quiet=False)
		dl = Downloader()
		
		try:
			# start the download
			dl.start(
				url=url_file_update,
				filepath=file_temp,
				num_connections=10,
				display=True,
				multithread=True,
				# block=True,
				retries=3,
				retry_func=None,
			)
			if os.path.exists(file_temp):
				print("Downloading")
				cmd = f'{which("7z.exe")} x "{file_temp}" -p"123456" -bsp1 -y -o"{APP_PATH}"'
				process = subprocess.Popen(
					cmd,
					stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT,
					shell=True,
					creationflags=0x08000000,
					encoding='utf-8',
					errors='replace'
				)
			if os.path.exists(file_update):
				os.unlink(file_temp)
				print('ok')
				time.sleep(2)
		except:
			print("Không thể tải file update")
		return data_user
	
	def open_main (self, username, data_setting, data_user):
		# SHOW MAIN WINDOW
		self.close()
		main_window = MainWindow(self.file_run_app, data_setting, data_user)
		main_window.show()
		main_window.s_d(cr_pc("tool_khac"), username)
	
	def closeEvent (self, event) -> None:
		self.spiner.stop()

# except Exception as e:
#     print(e)
