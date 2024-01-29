import json

from PySide6.QtCore import Qt, QRect, QRectF, QPointF
from PySide6.QtGui import QFont, QColor, QBrush, QPen, QTextDocument, QTextCharFormat, QTextCursor, \
	QPainter
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView, QGraphicsPixmapItem

from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.custom_logger import decorator_try_except_class
from gui.widgets.py_graphics.py_rect_selection_sub import RectSelectionSubItemLayer


class GraphicViewGenerateSub(QGraphicsView):
	
	def __init__ (self, manage_thread_pool):
		super().__init__()
		
		self._zoom = 0
		self.manage_thread_pool = manage_thread_pool
		self._empty = True
		self.isLoaded = False
		# pen là thêm viền
		# self.pen_blur = QPen(QColor("#17ff53"), 3)
		
		self._scene = QGraphicsScene(self)

		self._scene.setSceneRect(QRectF(self.rect()))
		self._frame_video_main_sub = QGraphicsPixmapItem()
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
		self._scene.addItem(self._frame_video_main_sub)
		self._scene.addItem(self._frame_blur)
		self._scene.addItem(self.rect_selection_sub_area)
		
		self.layers = []
		# self._text_sub_origin_extract = QGraphicsTextItem()

		self.list_text_sub_origin_extract = []
		self.list_rectbox_sub_origin_extract = []

	# self.configSubView = ConfigSubView(self)
	
	def loadData (self, configCurrent: CauHinhTuyChonModel, manage_thread_pool):
		self.configCurrent = configCurrent
		cau_hinh = json.loads(self.configCurrent.value)
		self.setSizeScreen(1280, 720)
	
	
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
			self.height_V = 750
			
		width_V = self.height_V * (ratio)
		
		self._scene.setSceneRect(0, 0, width_S, height_S);
		self.setSceneRect(0, 0, width_S, height_S);
		self.setFixedSize(int(width_V), self.height_V)
		unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
		self.scale(1 / unity.width(), 1 / unity.height())
		viewrect = QRectF(0, 0, width_V, self.height_V)
		scenerect = self.transform().mapRect(QRect(0, 0, width_S, height_S))
		factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
		self.scale(factor, factor)
	
	@decorator_try_except_class
	def addRectBlur (self):
		
		self.rect_selection_sub_area = RectSelectionSubItemLayer(self.manage_thread_pool, QRectF(0, 0, self._scene.width() - 100, self._scene.height() / 4), QPointF(50, self._scene.height() - (
				self._scene.height() / 4) - 20),
			self.layers, self._scene)
		self.rect_selection_sub_area.addItemToScene()
	
	def removeRectBlur (self):
		
		self._scene.removeItem(self.rect_selection_sub_area)
	
	# self._rect_selection_sub_area = None
	
	@decorator_try_except_class
	def addSubTextOrigin (self, text_: str):
		
		self.removeBoxSubOriginExtract()
		
		color_background = QColor("#000000")
		color_background.setAlphaF(0.8)
		stroke = QPen(color_background)
		brush = QBrush(color_background)
		
		'''Xử lý vị trí text_sub'''
		list_text = text_.strip().split(" ")
		self.hamDeQuySubOriginExtract(list_text)
		
		if len(self.list_text_sub_origin_extract) > 0:
			
			for index, sub in enumerate(self.list_text_sub_origin_extract):
				width_text = sub.boundingRect().width()
				height_text = sub.boundingRect().height()
				
				x_sub, y_sub = self.positionSub(6, width_text, height_text, self._scene.width(),
					self._scene.height())
				
				y_sub = y_sub + height_text * index
				
				sub.setPos(x_sub, y_sub)
				_rectbox = self._scene.addRect(x_sub, y_sub, width_text, height_text, stroke,
					brush)  # addRect(self, x: float, y: float, w: float, h: float,
				sub.setZValue(1003)
				_rectbox.setZValue(1003)
				self.list_rectbox_sub_origin_extract.append(_rectbox)
				self._scene.addItem(sub)
	
	def positionSub (self, pos, width_text, height_text, video_width, video_heigth):
		x_sub = 0
		y_sub = 0
		phan_tram_le = 0.03
		if pos == 1:  # bottom left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = video_heigth - height_text
		
		elif pos == 2:  # bottom center
			x_sub = video_width / 2 - width_text / 2
			y_sub = video_heigth - height_text
		
		elif pos == 3:  # bottom right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = video_heigth - height_text
		
		elif pos == 11:  # middle left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = video_heigth / 2 - height_text
		
		elif pos == 10:  # middle center
			x_sub = video_width / 2 - width_text / 2
			y_sub = video_heigth / 2 - height_text
		
		elif pos == 8:  # middle right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = video_heigth / 2 - height_text
		
		elif pos == 7:  # top right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = height_text
		
		elif pos == 6:  # top center
			x_sub = video_width / 2 - width_text / 2
			y_sub = height_text
		
		elif pos == 4:  # top left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = height_text
		
		return x_sub, y_sub
	
	
	def hasPhoto (self):
		return not self._empty
	
	def setFrameVideo (self, pixmap, video_width, video_height):
		if pixmap and not pixmap.isNull():
			self._empty = False
			self._scene.removeItem(self._frame_video_main_sub)
			self._frame_video_main_sub = QGraphicsPixmapItem()
			self._frame_video_main_sub.setPixmap(pixmap)
			self._scene.addItem(self._frame_video_main_sub)
			
			self.setSizeScreen(video_width, video_height)
	
	
	def setFrameSelectionArea (self, pixmap):
		if pixmap and not pixmap.isNull():
			self._scene.removeItem(self._frame_blur)
			self._frame_blur = QGraphicsPixmapItem()
			self._frame_blur.setPixmap(pixmap)
			self._scene.addItem(self._frame_blur)
			self._frame_blur.setPos(self.rect_selection_sub_area.pos())
	
	# self._frame_blur.(self.rect_selection_sub_area.pos())
	
	
	def hamDeQuySubOriginExtract (self, list_text):
		'''tách đoạn sub thành từng từ sau đó kiểm tra độ dài để hiển thị xuống hàng'''
		if len(list_text) == 0:
			return
		for i in range(1, len(list_text) - 1):
			# self._scene.removeItem(self._text_sub_origin_extract)
			item_text = ' '.join([str(elem) for elem in list_text[0:i]])
			
			_text_sub_origin_extract = self.changeStyleSubOriginExtract(item_text)
			
			if _text_sub_origin_extract.boundingRect().width() / self._scene.width() >= 0.68:
				self.list_text_sub_origin_extract.append(_text_sub_origin_extract)
				return self.hamDeQuySubOriginExtract(list_text[i:])
		
		# self._scene.removeItem(self._text_sub_origin_extract)
		item_text1 = ' '.join([str(elem) for elem in list_text])
		_text_sub_origin_extract = self.changeStyleSubOriginExtract(item_text1)
		self.list_text_sub_origin_extract.append(_text_sub_origin_extract)
	
	def changeStyleSubOriginExtract (self, item_text):
		
		document = QTextDocument()
		charFormat = QTextCharFormat()
		font = QFont()
		font.setFamily("Roboto")
		font.setPixelSize(40)
		font.setBold(True)
		font.setWeight(QFont.Weight.Black)
		color_text = QColor("#ffffff")
		brush_text = QBrush(color_text)
		charFormat.setFont(font)
		charFormat.setForeground(brush_text)
		cursor = QTextCursor(document)
		cursor.insertText(item_text, charFormat)
		_text_sub_origin_extract = QGraphicsTextItem()
		_text_sub_origin_extract.setDocument(document)
		return _text_sub_origin_extract
	
	def removeBoxSubOriginExtract (self):
		
		if len(self.list_text_sub_origin_extract) > 0:
			
			for item in self._scene.items():
				if item.zValue() == 1003:
					self._scene.removeItem(item)
		
		self.list_text_sub_origin_extract = []
		self.list_rectbox_sub_origin_extract = []
