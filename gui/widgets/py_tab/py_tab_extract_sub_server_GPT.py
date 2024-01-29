# -*- coding: utf-8 -*-
import re
import uuid

import requests

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	RESULT_EXTRACT_SUB_SERVER_AI, \
	ADD_TO_TABLE_EXTRACT_PROCESS, LANGUAGES_EXTRACT_AI, SETTING_APP_DATA, TOOL_CODE_MAIN, \
	USER_DATA, URL_API_BASE, APP_PATH
from gui.helpers.translatepy.utils.request import Request
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from PySide6.QtCore import Qt, QRect, QCoreApplication, QMetaObject
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QCheckBox, \
    QLineEdit, QFrame, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog
from ..py_dialogs.py_dialog_show_info import PyDialogShowInfo
from ..py_icon_button.py_button_icon import PyButtonIcon
from ..py_table_widget.table_process_extract import TableProcessExtractSUB
from ...configs.config_resource import ConfigResource
from ...helpers.custom_logger import decorator_try_except_class
from ...helpers.ect import mh_ae
from ...helpers.func_helper import getValueSettings, get_duaration_video_cv2
from ...helpers.http_request.check_proxy import ProxyChecker
from ...helpers.thread import ManageThreadPool
from six.moves import urllib_parse


class PyTabExtractSubServerAI(QWidget):
	def __init__ (self, group_parent, manage_thread_pool, thread_pool_limit, manage_cmd, table_process: TableProcessExtractSUB, groupBox_network):
		super().__init__()
		
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.group_parent = group_parent
		
		self.manage_thread_pool = manage_thread_pool
		self.thread_pool_limit = thread_pool_limit
		self.thread_pool_limit_convert = ManageThreadPool()
		self.thread_pool_limit_convert.setMaxThread(10)
		self.manage_cmd = manage_cmd
		self.table_process = table_process
		self.checker = ProxyChecker(manage_thread_pool)
		self.groupBox_network = groupBox_network
		
		# self.extractVoice = ExtractSubVoice(self.manage_thread_pool, self.manage_cmd)
		self.count = 0
		# PROPERTIES
		self.languages = LANGUAGES_EXTRACT_AI
		self.isLoad = True
		self.load_file_srt_finished = False
		self.setup_ui()
	
	
	def setup_ui (self):
		self.create_widgets()
		
		self.setup_connections()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
	
	# Too many requests, please try again later.
	def create_widgets (self):
		self.themes = ConfigTheme()
		
		self.lb_link_video = QLabel("Link Video:")
		self.input_link_video = QLineEdit()
		
		self.lb_tk_user = QLabel("Số phút còn lại: Free dưới 5p")
		# self.cb_server_STT = PyComboBox()
		
		self.lb_notify = QLabel("Được free video dưới 5 phút, Trên 5 phút giá 150Đ/1 phút. Liên hệ admin để được hỗ trợ")
		self.btn_info_frame = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("info.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#2678ff",
			icon_color_hover="#4d8df6",
			icon_color_pressed="#6f9deb",
			app_parent=self,
			tooltip_text="Hướng dẫn"
		
		)
		self.btn_start = QPushButton("Start")
		self.btn_start.setCursor(Qt.CursorShape.PointingHandCursor)
		
		text = "Bước 1. Tải video lên Drive Google, nhớ mở chia sẻ file thành công khai"
		text += "\n\n"
		
		text += "Bước 2. Nhập link vào input "
		text += "\n\n"
		
		text += "Bước2. Bấm START rồi ngồi uống ly cà phê đợi kết quả"
		text += "\n\n"
		text += "LƯU Ý: Tài khoản free chỉ được sử dụng video dưới 5 phút"
		
		self.dialog_info = PyDialogShowInfo(text, 370)
	
	def modify_widgets (self):
		pass
	
	def create_layouts (self):
		self.content_layout = QVBoxLayout()
		self.content_layout.setContentsMargins(0, 0, 0, 0)
		
		self.content_status = QHBoxLayout()
		self.content_link_layout = QHBoxLayout()
		
		self.progess_convert_layout = QHBoxLayout()
		self.content_btn_layout = QGridLayout()
	
	# layout bên phải
	
	def add_widgets_to_layouts (self):
		self.setLayout(self.content_layout)
		
		# self.content_layout.addWidget(QLabel(""), 5)
		self.content_layout.addLayout(self.content_link_layout)
		self.content_layout.addLayout(self.content_status)
		self.content_layout.addLayout(self.content_btn_layout)
		
		self.content_link_layout.addWidget(self.lb_link_video, 10)
		self.content_link_layout.addWidget(self.input_link_video, 60)
		self.content_link_layout.addWidget(self.lb_tk_user, 30)
		# self.content_link_layout.addWidget(self.cb_server_STT, 30)
		
		self.content_status.addWidget(self.lb_notify)
		
		self.content_btn_layout.addWidget(QLabel(), 0, 0, 1, 4)
		self.content_btn_layout.addWidget(self.btn_start, 0, 4, 1, 4)
		self.content_btn_layout.addWidget(QLabel(), 0, 8, 1, 3)
		
		self.content_btn_layout.addWidget(self.btn_info_frame, 0, 11)
	
	def setup_connections (self):
		# self.thread_pool_limit_convert.resultChanged.connect(self._resultThread)
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.thread_pool_limit.resultChanged.connect(self._resultThread)
		# self.manage_thread_pool.progressChanged.connect(self._progressChanged)
		# self.checker.finishedCheckLiveProxySignal.connect(self._finishedCheckLiveProxySignal)
		
		self.btn_start.clicked.connect(self.clickStart)
		self.btn_info_frame.clicked.connect(self._click_info)
	
	def _click_info (self):
		self.dialog_info.exec()
	
	def loadData (self, configCurrent):
		
		self.configCurrent = configCurrent
		
		self.isLoad = False
	
	def loadFileInput (self, path):
		self.path_input = path
	
	def parse_url (self, url):
		"""Parse URLs especially for Google Drive links.

		file_id: ID of file on Google Drive.
		is_download_link: Flag if it is download link of Google Drive.
		"""
		parsed = urllib_parse.urlparse(url)
		query = urllib_parse.parse_qs(parsed.query)
		is_gdrive = parsed.hostname in ["drive.google.com", "docs.google.com"]
		is_download_link = parsed.path.endswith("/uc")
		
		if not is_gdrive:
			return is_gdrive, is_download_link
		
		file_id = None
		if "id" in query:
			file_ids = query["id"]
			if len(file_ids) == 1:
				file_id = file_ids[0]
		else:
			patterns = [r"^/file/d/(.*?)/view$", r"^/presentation/d/(.*?)/edit$"]
			for pattern in patterns:
				match = re.match(pattern, parsed.path)
				if match:
					file_id = match.groups()[0]
					break
		
		return file_id, is_download_link
	
	def get_url_from_gdrive_confirmation (self, contents):
		url = ""
		for line in contents.splitlines():
			m = re.search(r'href="(\/uc\?export=download[^"]+)', line)
			if m:
				url = "https://docs.google.com" + m.groups()[0]
				url = url.replace("&amp;", "&")
				break
			m = re.search('id="download-form" action="(.+?)"', line)
			if m:
				url = m.groups()[0]
				url = url.replace("&amp;", "&")
				break
			m = re.search('"downloadUrl":"([^"]+)', line)
			if m:
				url = m.groups()[0]
				url = url.replace("\\u003d", "=")
				url = url.replace("\\u0026", "&")
				break
			m = re.search('<p class="uc-error-subcaption">(.*)</p>', line)
			if m:
				error = m.groups()[0]
				raise RuntimeError(error)
		if not url:
			raise RuntimeError(
				"Cannot retrieve the public link of the file. "
				"You may need to change the permission to "
				"'Anyone with the link', or have had many accesses."
			)
		return url
	
	
	@decorator_try_except_class
	def clickStart (self):
		# try:
		url = self.input_link_video.text()
		
		if url == '':
			return PyMessageBox().show_warning("Thông Báo", "Vui lòng nhập link video")
		
		if not 'drive.google.com' in url:
			return PyMessageBox().show_warning("Thông Báo", "Vui lòng nhập link drive và mở công khai")
		
		gdrive_file_id, is_gdrive_download_link = self.parse_url(url)
		print(gdrive_file_id, is_gdrive_download_link)
		if gdrive_file_id:
			# overwrite the url with fuzzy match of a file id
			# url_download = f"https://drive.google.com/uc?export=download&id={gdrive_file_id}"
			url_download = "https://drive.google.com/uc?id={id}".format(id=gdrive_file_id)
		
		else:
			return PyMessageBox().show_warning("Thông Báo", "Vui lòng nhập đúng link file")
		
		
		
		file_name, _ = QFileDialog.getSaveFileName(self, caption='Nhập tên file muốn lưu',
			dir=(APP_PATH),
			filter='File sub (*.srt)')
		
		if file_name == "":
			return PyMessageBox().show_warning("Thông Báo", "Vui lòng chọn file để lưu")
		

		
		# res = request.get(url, stream=True, verify=True)
		
		# if not "Content-Disposition" in res.headers:
		# 	return PyMessageBox().show_warning("Thông Báo", "Vui lòng nhập đúng link file")
		# try:
		# 	url_download = self.get_url_from_gdrive_confirmation(res.text)
		# except RuntimeError as e:
		# 	return  PyMessageBox().show_warning("Thông Báo", "Vui lòng mở quyền truy cập file là công khai")
		# print(url)
		
		
		# self.group_parent.setDisabled(True)
		row_number = self.table_process.main_table.rowCount()
		#
 
		data_item_table = []
		data_item_table.append(url)
		data_item_table.append('')
		data_item_table.append("Trích xuất từ AI trả phí")

		self.manage_thread_pool.resultChanged.emit(str(row_number), ADD_TO_TABLE_EXTRACT_PROCESS, data_item_table)

		# base, ext = os.path.splitext(source_path)
		# subtitle_file = "{base}.{format}".format(base=base, format='srt')
		# if os.path.isfile(subtitle_file):
		# 	os.remove(subtitle_file)
		
		# cau_hinh = json.loads(self.configCurrent.value)
		
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Đang đợi...")
		
		self.thread_pool_limit.start(self._funcExtractThread, "_extractStartThreadAITraPhi" + uuid.uuid4().__str__(), RESULT_EXTRACT_SUB_SERVER_AI, limit_thread=True, row_number=row_number, file_name=file_name, video_url=url_download)
	
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == RESULT_EXTRACT_SUB_SERVER_AI:
			if result is not None:
				is_ok, data = result
				if is_ok:
					print(data)
				else:
					PyMessageBox().show_warning("Lỗi", data)
	
	
	# @decorator_try_except_class
	def _funcExtractThread (self, **kwargs):
		# try:
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		row_number = kwargs["row_number"]
		file_name = kwargs["file_name"]
		video_url = kwargs["video_url"]
		request = Request()
		
		sess = requests.session()
		
		sess.headers.update(
			{"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6)"}
		)
 
		print(video_url)

		while True:
			try:
				res = sess.get(video_url, stream=True, verify=True)
			except:
				return False,  "Lỗi link not found"
			
			if "Content-Disposition" in res.headers:
				# This is the file
				break
			# Need to redirect with confirmation
			try:
				video_url = self.get_url_from_gdrive_confirmation(res.text)
			except RuntimeError as e:
				return False,  "Vui lòng mở quyền truy cập file là công khai"
			
		print(video_url)
		try:
			# get_duaration_video_cv2(video_url)
			# cap = cv2.VideoCapture(video_url)
			# fps = cap.get(cv2.CAP_PROP_FPS)
			# totalNoFrames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
			durationInSeconds,fps = get_duaration_video_cv2(video_url)
		except:
			return False, "Chỉ hỗ trợ các định dạng video"
		print("durationInSeconds:", durationInSeconds, "s")
		# print("fps:", fps, "s")
		# print("totalNoFrames:", totalNoFrames, "s")
		if durationInSeconds > 300:
			return False, "Video của bạn vượt quá 5 phút, hãy mua thêm số phút để trích xuất video dài hơn"
 
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Đang khởi tạo tiến trình ...")

		data_req = {
			"video_url": video_url,
			"duration": durationInSeconds,
			
		}

		user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		data_encrypt = mh_ae(data_req, p_k=user_data['paes'])

		headers = {"Authorization": f"Bearer {user_data['token']}"}

		res = request.post(url=URL_API_BASE + "/generate-code/private/render-add-sub", json={
			"data": data_encrypt},
			headers=headers)
		# # print(res.json())
		#
		# if res.json()["status_code"] == 200:
		# 	done = True
		# 	thread_pool.finishSingleThread(id_worker, limit_thread=True)
		# 	return row_number if done is True else None
