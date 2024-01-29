import time

import requests
from PySide6.QtCore import Qt, QRect, QRectF, QPointF, QTimer
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView

from gui.helpers.constants import NOTIFICATION_REQUEST_SERVER, USER_DATA, TOOL_CODE_MAIN, \
	SETTING_APP_DATA
from gui.helpers.ect import gm_ae, cr_pc, mh_ae
from gui.helpers.func_helper import getValueSettings
from gui.helpers.get_data import URL_API_BASE
from gui.widgets.py_graphics.py_text_notification import TextNotificationLayer


class GraphicViewNotify(QGraphicsView):
	
	def __init__ (self, manage_thread_pool):
		super().__init__()
		data_setting = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		if data_setting.get('data_setting').get("show_notification"):
			
			self.manage_thread_pool = manage_thread_pool
			self.manage_thread_pool.resultChanged.connect(self.resultChanged)
			self._empty = True
			self.isLoaded = False
			self.code_pc = cr_pc()
			
			self._scene = QGraphicsScene(self)
			
			self._scene.setSceneRect(QRectF(self.rect()))
			
			self.setScene(self._scene)
			self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
			
			self.setStyleSheet('QGraphicsView { border-radius: 30px;border:none; background:#5a5a5a;}')
			
			self.setRenderHint(QPainter.RenderHint.Antialiasing)  # chế độ làm mịn
			
			self.text_notification = TextNotificationLayer(self.manage_thread_pool, data_setting.get('data_setting').get("notification"), QPointF(1920, 0), self._scene)
			
			self._scene.addItem(self.text_notification)
			self.setFixedSize(1920, 30)
			self.height_V = self.rect().height()
			
			self.setSizeScreen(1920, 30)
			
			# self.timer_check_notify = QTimer()
			# self.timer_check_notify.timeout.connect(self.check_notify)
			# self.timer_check_notify.start(10800 * 1000)
			# self.timer_check_notify.start(1000)
		else:
			self.hide()
	
	
	def check_notify (self):
		user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		if self.isHidden():
			return
		print(user_data)
		self.manage_thread_pool.start(self._funcReqNoti, NOTIFICATION_REQUEST_SERVER, NOTIFICATION_REQUEST_SERVER, user_data=user_data)
	
	def _funcReqNoti (self, **kwargs):
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		user_data = kwargs["user_data"]
		
		headers = {"Authorization": f"Bearer {user_data['token']}"}
		
		res_st = requests.post(url=URL_API_BASE + f"/setting-tool/private/notification/{TOOL_CODE_MAIN}", headers=headers, json={
			"data":mh_ae({"cp": cr_pc(), 't': int(float(time.time()))})})
		thread_pool.finishSingleThread(id_worker)
		if res_st.json()["status_code"] == 200:
			data_setting = gm_ae(res_st.json()["data"], user_data['paes'])
			return data_setting
	
	
	def resultChanged (self, id_worker, id_thread, result):
		
		if id_thread == NOTIFICATION_REQUEST_SERVER and result is not None:
			self._scene.removeItem(self.text_notification)
			self.text_notification = TextNotificationLayer(self.manage_thread_pool, result, QPointF(1920, 0), self._scene)
			self._scene.addItem(self.text_notification)
	
	def setSizeScreen (self, width_S, height_S):
		ratio = width_S / height_S
		width_V = self.height_V * (ratio)
		
		self._scene.setSceneRect(0, 0, width_S, height_S);
		self.setSceneRect(0, 0, width_S, height_S);
		
		unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
		self.scale(1 / unity.width(), 1 / unity.height())
		viewrect = QRectF(0, 0, width_V, self.height_V)
		scenerect = self.transform().mapRect(QRect(0, 0, width_S, height_S))
		factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
		self.scale(factor, factor)
