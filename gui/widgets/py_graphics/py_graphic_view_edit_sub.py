import json
import os.path

from PySide6.QtCore import Qt, QRect, QRectF, QUrl, QSizeF, QTimer
from PySide6.QtGui import QFont, QColor, QBrush, QPen, QTextDocument, QTextCharFormat, QTextCursor, \
	QPainter
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGraphicsPixmapItem

from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import LOAD_FONT_FAMILY, DELIMITER_POS_SUB, \
	DELIMITER_CENTER_POS_SUB
from gui.widgets.py_graphics.py_text_edit_sub import TextEditSubLayer


class GraphicViewEditSub(QGraphicsView):
	
	def __init__ (self, manage_thread_pool):
		super().__init__()
		
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self.resultChanged)
		self._empty = True
		self.isLoaded = False
		self.video_url = ''
		# pen là thêm viền
		# self.pen_blur = QPen(QColor("#17ff53"), 3)

		# self.audio_output.setProperty("-shortest",'')
		self.video_main_sub = QGraphicsVideoItem()
		self._frame_video_main_sub = QGraphicsPixmapItem()
		self.player = QMediaPlayer()
		self.audio_output = QAudioOutput()
		# self.audio_output.setVolume(1)
		self.player.setAudioOutput(self.audio_output)
		self.player.setVideoOutput(self.video_main_sub)
		
		self.player.durationChanged.connect(self.duration_changed)
		self.player.positionChanged.connect(self.position_changed)
		
		self._scene = QGraphicsScene(self)
		
		self._scene.setSceneRect(QRectF(self.rect()))
		self._scene.addItem(self._frame_video_main_sub)
		
		self._frame_blur = QGraphicsPixmapItem()
		self.rect_selection_sub_area = QGraphicsRectItem()
		
		self.setScene(self._scene)
		self._scene.selectionChanged.connect(self._onSelectionChanged)
		# self._scene.changed.connect(self._onSceneChanged)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		
		self.setStyleSheet('QGraphicsView { border-radius: 5px;border:none; background:black;}')
		
		self.setRenderHint(QPainter.RenderHint.Antialiasing)  # chế độ làm mịn
		
		self.height_V = self.rect().height()
		self.weight_V = self.rect().width()

		
		self.layers = []
		self.list_fonts = []
		# self._text_sub_origin_extract = QGraphicsTextItem()
		
		self.list_text_sub_origin_extract = []
		self.list_rectbox_sub_origin_extract = []
		
		self.text_sub_translate = ""
		
		self.text_sub_translate_current = None
		
		self.rectbox_sub_translate_current = None
		
		self.list_text_sub_translate = []
		self.list_rectbox_sub_translate = []
		
		# Đặt QTimer để gọi stop_playback() khi đạt end_pos
		self.timer_play = QTimer()
		self.timer_play.timeout.connect(self.stop_playback)
		self.timer_play.setSingleShot(True)
		self.end_pos = None
	
	# timer.start(end - start)  # Chạy timer với khoảng thời gian là độ dài đoạn cần phát
	# self.configSubView = ConfigSubView(self)
	def resultChanged (self, id_worker, typeThread, result):
		if typeThread == LOAD_FONT_FAMILY:
			self.list_fonts = result
	
	def stop_playback (self):
		# print('stop')
		# self.player.stop()
		self.player.pause()
	
	def position_changed (self, position):
		pass
	
	# print('position ',position)
	def duration_changed (self, duration):
		# print(self.end_pos)
		if self.end_pos:
			# self.player.play() nếu mở lên play thi mở cái này
			self.timer_play.start(self.end_pos)
	
	# print('duration ',duration)
	def loadDataConfigCurrent (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
	
		cau_hinh = json.loads(self.configCurrent.value)
		# print(cau_hinh)
	# self.setSizeScreen(1280, 720)
	
	
	def _onSelectionChanged (self):
		
		if len(self.layers) > 0:
			for item_layer in self.layers:
				item = list(item_layer.values())[0]
				if hasattr(item, "resizer") is True:
					resizer = item.resizer
					if resizer.isSelected() is False:
						resizer.hide()
	
	def setSizeScreen (self, width_S, height_S):
		ratio = width_S / height_S
		if ratio > 1:
			self.height_V = 500
		else:
			self.height_V = 600

		width_V = self.height_V * (ratio)

		self._scene.setSceneRect(0, 0, width_S, height_S)
		self.setSceneRect(0, 0, width_S, height_S)
		self.setFixedSize(int(width_V), self.height_V)
		unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
		self.scale(1 / unity.width(), 1 / unity.height())
		viewrect = QRectF(0, 0, width_V, self.height_V)
		scenerect = self.transform().mapRect(QRect(0, 0, width_S, height_S))
		factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
		self.scale(factor, factor)
	
	
	def addSubTextTranslate (self, text_, pos_edit_sub):
		if hasattr(self, 'configCurrent'):
			# print(33333333)
			self.removeTextSubCurrent()
			data_conf: dict = json.loads(self.configCurrent.value)
			
			# 2 màu trên phải giống nhau
			if data_conf["nen_sub_dich"] is True:
				# màu nền của rect
				color_background = QColor(data_conf["mau_nen_sub_dich"])
				color_background.setAlphaF(data_conf["opacity_nen_sub_dich"] / 100)
				stroke = QPen(color_background)
				brush = QBrush(color_background)
			
			else:
				color_background = QColor("#000000")
				color_background.setAlphaF(0)
				stroke = QPen(color_background)
				brush = QBrush(color_background)
			
			'''Xử lý vị trí text_sub'''
			cach_le = 30
			list_text = text_.split(" ")
			self.hamDeQuySubTranslate(list_text, data_conf)
			# if len(self.list_text_sub_origin) > 0:
			# print(self.text_sub_origin)
			# if len(self.text_sub_translate) > 0:
			# print(000)
			sub = self.changeStyleSubTranslate(data_conf, self.text_sub_translate)
			
			# sub = self.changeStyleSubTranslate(data_conf, text_)
			self.list_text_sub_translate.append(sub)
			width_text = sub.boundingRect().width()
			height_text = sub.boundingRect().height()
			
			x_sub, y_sub = self.positionSub(0, width_text, height_text, self._scene.width(),
				self._scene.height(), pos_edit_sub, cach_le=cach_le)
			
			if data_conf["vi_tri_sub_dich"] in [1, 2, 3]:  # vi trí bottom
				y_sub = y_sub - height_text
			else:
				y_sub = y_sub
			
			sub.setPos(x_sub, y_sub)
			# _rectbox = self._scene.addRect(x_sub, y_sub, width_text, height_text, stroke,
			# 	brush)  # addRect(self, x: float, y: float, w: float, h: float,
			
			_rectbox = QGraphicsRectItem()
			_rectbox.setPos(x_sub, y_sub)
			_rectbox.setRect(0, 0, width_text, height_text)
			_rectbox.setPen(stroke)
			_rectbox.setBrush(brush)
			
			sub.rectbox = _rectbox
			sub.setZValue(1003)
			_rectbox.setZValue(1003)
			
			self.text_sub_translate_current = sub
			self.rectbox_sub_translate_current = _rectbox
			self.list_rectbox_sub_translate.append(_rectbox)
			self._scene.addItem(_rectbox)
			self._scene.addItem(sub)
	
	
	def positionSub (self, vitri, width_text, height_text, video_width, video_heigth, position, cach_le=10):
		x_sub = 0
		y_sub = 0
		# 98.0:365.0
		phan_tram_le = 0.03
		if vitri == 1:  # bottom left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = video_heigth - cach_le
		
		elif vitri == 2:  # bottom center
			x_sub = video_width / 2 - width_text / 2
			y_sub = video_heigth - cach_le
		
		elif vitri == 3:  # bottom right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = video_heigth - cach_le
		
		elif vitri == 4:  # middle left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = video_heigth / 2 - height_text
		
		elif vitri == 5:  # middle center
			x_sub = video_width / 2 - width_text / 2
			y_sub = video_heigth / 2 - height_text
		
		elif vitri == 6:  # middle right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = video_heigth / 2 - height_text
		
		elif vitri == 7:  # top right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = cach_le
		
		elif vitri == 8:  # top center
			x_sub = video_width / 2 - width_text / 2
			y_sub = cach_le
		
		elif vitri == 9:  # top left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = cach_le
		
		else:
			# print(position)
			
			try:
				x_sub_, y_sub_ = position.split(DELIMITER_POS_SUB)
				x_sub, y_sub = float(x_sub_), float(y_sub_)
			# print(x_sub, y_sub)
			
			except:
				
				try:
					x_sub_, y_sub_ = position.split(DELIMITER_CENTER_POS_SUB)
					# print(x_sub, y_sub)
					
					x_sub = video_width / 2 - width_text / 2
					
					y_sub = float(y_sub_) - height_text / 2
				
				except:
					x_sub = cach_le  # 10px
					y_sub = video_heigth - height_text
		
		# print(x_sub, y_sub)
		
		return x_sub, y_sub
	
	
	def hamDeQuySubTranslate (self, list_text, data_conf):
		'''tách đoạn sub thành từng từ sau đó kiểm tra độ dài để hiển thị xuống hàng'''
		if len(list_text) == 0:
			return
		for i in range(1, len(list_text) - 1):
			
			item_text = ' '.join([str(elem) for elem in list_text[0:i]])
			
			_text_sub_translate = self.changeStyleSubTranslate(data_conf, item_text)
			
			if _text_sub_translate.boundingRect().width() / self._scene.width() >= 0.68:
				# self.list_text_sub_translate.append(_text_sub_translate)
				self.text_sub_translate += item_text + "\n"
				return self.hamDeQuySubTranslate(list_text[i:], data_conf)
		
		item_text1 = ' '.join([str(elem) for elem in list_text])
		self.text_sub_translate += item_text1
	
	def changeStyleSubTranslate (self, data_conf, item_text) -> TextEditSubLayer:
		# print(data_conf)
		document = QTextDocument()
		charFormat = QTextCharFormat()
		font = QFont()
		fs = int(data_conf["font_size_sub_dich"].replace("px", ""))
		
		if data_conf["font_sub_dich"] is True:
			font.setFamily(data_conf["font_family_sub_dich"])
			font.setPointSize(fs)
			
			text = QGraphicsTextItem(item_text)
			text.setFont(font)
			text_rect = text.boundingRect()
			
			# text_ratio = fs / text_rect.height()
			text_ratio = (fs / (text_rect.height())) * len(item_text.split("\n"))
			font.setPointSize(int(font.pointSizeF() * text_ratio))
		
		else:
			font.setFamily("Arial")
			font.setPointSize(20)
		
		color_text = QColor("#ffffff")
		
		if data_conf["add_mau_sub_dich"] is True:
			# màu chữ
			color_text = QColor(data_conf["mau_sub_dich"])
			color_text.setAlphaF(data_conf["opacity_mau_sub_dich"] / 100)
		brush_text = QBrush(color_text)
		
		charFormat.setFont(font)
		charFormat.setForeground(brush_text)
		
		cursor = QTextCursor(document)
		cursor.insertText(item_text, charFormat)
		
		locked = False
		
		_text_sub_translate = TextEditSubLayer(self.manage_thread_pool, item_text, document, self.list_fonts, self.configCurrent, locked=locked)
		
		return _text_sub_translate
	
	
	def setFrameVideo (self, pixmap,frame_width, frame_height):
		# if pixmap and not pixmap.isNull():
		# if os.path.exists(video_url):
			self._empty = False
			# self._scene.removeItem(self._frame_video_main_sub)
			# try:
			# 	self._scene.removeItem(self.video_main_sub)
			# except:
			# 	pass
			# self._frame_video_main_sub = QGraphicsPixmapItem()
			self._frame_video_main_sub.setPixmap(pixmap)

			self.setSizeScreen(frame_width, frame_height)
	
	
	def removeTextSubCurrent (self):
		
		if len(self.list_text_sub_translate) > 0:
			# print("removeTextSubCurrent")
			for item in self._scene.items():
				# print(item.zValue())
				if item.zValue() == 1003:
					self._scene.removeItem(item)
			
			self.text_sub_translate = ''
			self.list_text_sub_translate = []
			self.list_rectbox_sub_translate = []
