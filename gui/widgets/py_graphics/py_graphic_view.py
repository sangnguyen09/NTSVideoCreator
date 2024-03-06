import glob
import json
import math
import os
import random

from PySide6.QtCore import Qt, QRect, QSize, QRectF, QPointF, QPoint
from PySide6.QtGui import QFont, QColor, QBrush, QPen, QTextDocument, QTextCharFormat, QTextCursor, \
	QPainter, QFontDatabase, QPixmap, QFontMetrics
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QGraphicsTextItem

from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import STATUS_BUTTON_SAVE_CONFIG_CHANGED, LOAD_FONT_FAMILY, \
	PATH_FONT, SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN, POSITION_SUB_ORIGINAL_CHANGED, \
	DELIMITER_POS_SUB, UPDATE_TY_LE_KHUNG_HINH_VIDEO, DELIMITER_CENTER_POS_SUB
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_graphics.py_background_video_main import BackgroundVideoMainItemLayer
from gui.widgets.py_graphics.py_frame_video_main import FrameVideoMainItemLayer
from gui.widgets.py_graphics.py_media_item import MediaItemLayer
from gui.widgets.py_graphics.py_rect_blur import RectBlurItemLayer
from gui.widgets.py_graphics.py_rectangle_item import RectangleItemLayer
from gui.widgets.py_graphics.py_text_item import TextItemLayer
from gui.widgets.py_graphics.py_text_sub import TextSubLayer


class GraphicView(QGraphicsView):
	
	def __init__ (self, gr_show_add_sub, manage_thread_pool):
		super().__init__()
		
		# self.settings = QSettings(*SETTING_CONFIG)
		
		self._zoom = 0
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self.resultThread)
		
		self.gr_show_add_sub = gr_show_add_sub
		self._empty = True
		self.isLoaded = False
		# pen là thêm viền
		# self.pen_blur = QPen(QColor("#17ff53"), 3)
		
		self._scene = QGraphicsScene()
		# self._scene.views()[0].setDpi(72)
		self._scene.setSceneRect(QRectF(self.rect()))
		# self._frame_video_main_sub = None
		self._rectbox_sub = QGraphicsRectItem()
		self._rectblur_area = None
		
		# self._text_sub_origin = QGraphicsTextItem()
		# self._text_sub_translate = QGraphicsTextItem()
		self._frame_blur = QGraphicsPixmapItem()
		self._frame_video_main_sub = QGraphicsPixmapItem()
		self._video_main_blur = QGraphicsPixmapItem()

		self._scene.addItem(self._rectbox_sub)
		# self._scene.addItem(self._video_main_blur)
		# self._scene.addItem(self._frame_blur)
		# self._scene.addItem(self._text_sub_origin)
		# self._scene.addItem(self._text_sub_translate)
		
		self.setScene(self._scene)
		self._scene.selectionChanged.connect(self._onSelectionChanged)
		# self._scene.changed.connect(self._onSceneChanged)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
		
		self.setStyleSheet('QGraphicsView { border-radius: 5px;border:none; background:black;}')
		
		self.setRenderHint(QPainter.RenderHint.Antialiasing)  # chế độ làm mịn
		
		self.height_V = self.rect().height()
		
		self.layers = []
		self.list_blur = []
		self.list_fonts = []
		
		self.text_sub_origin = ""
		self.text_sub_translate = ""
		
		self.text_sub_origin_current = None
		self.text_sub_translate_current = None
		
		self.rectbox_sub_origin_current = None
		self.rectbox_sub_translate_current = None
		
		self.list_text_sub_origin = []
		self.list_rectbox_sub_origin = []
		self.list_text_sub_translate = []
		self.list_rectbox_sub_translate = []
	
	# self.list_text_sub = []
	# self.list_rectbox_sub = []
	
	# self.configSubView = ConfigSubView(self)
	# self.setDPI()
	
	def setDPI (self):
		font = QFont()
		font.setPointSize(72)
		font_metrics = QFontMetrics(font)
		self.setSceneRect(0, 0, font_metrics.horizontalAdvance("X") * 10, font_metrics.height() * 10)
	
	def loadDataConfigCurrent (self, configCurrent: CauHinhTuyChonModel, manage_thread_pool):
		self.configCurrent = configCurrent
		# print('loadData')
		if len(self.list_fonts) == 0:
			manage_thread_pool.start(self.getFontPaths, LOAD_FONT_FAMILY, LOAD_FONT_FAMILY)
		else:
			self.loadDataScreen()
		
		self.setRectScene()

	def resultThread (self, id_worker, typeThread, result):
		
		# if typeThread == POSITION_SUB_ORIGINAL_CHANGED:
		# 	# print(result)
		# 	# print(self.rectbox_sub_origin_current)
		# 	self.rectbox_sub_origin_current.setPos(result)
		#
		# if typeThread == POSITION_SUB_TRANS_CHANGED:
		# 	self.rectbox_sub_translate_current.setPos(result)
		if typeThread == UPDATE_TY_LE_KHUNG_HINH_VIDEO:
			self.setRectScene()
		if typeThread == LOAD_FONT_FAMILY:
			self.list_fonts = result
			self.loadDataScreen()
	
	# @decorator_try_except_class
	def loadDataScreen (self):
		# print('loadData')

		self.resetScreen()
		list_cofig = getValueSettings(SETTING_CONFIG_SCREEN, TOOL_CODE_MAIN)
		if list_cofig is not None:
			layer_conf = list_cofig.get(str(self.configCurrent.id))
			# print(layer_conf)
			if isinstance(layer_conf, dict):
				if len(layer_conf) > 0:
					scene_old = layer_conf.get('rect_scene')
					width_Old = scene_old.get('width')
					height_Old = scene_old.get('height')
					width_New = self._scene.width()
					height_New = self._scene.height()
					ratio_scale_H = width_New / width_Old
					ratio_scale_V = height_New / height_Old
					# print(layer_conf)
					# print(width_Old, height_Old, width_New, height_New)
					# print(ratio_scale_H, ratio_scale_V)
					for layer in layer_conf.get('layers'):
						if layer.get("type") == 'RectangleItemLayer':
							value = layer['value']
							# value = layer['value']
							ite = RectangleItemLayer(self.manage_thread_pool,
								QRectF(0, 0, value['width'] * ratio_scale_H, value['height'] * ratio_scale_V),
								QPointF(
									value['x'] * ratio_scale_H, value['y'] * ratio_scale_V), self.layers, self._scene,
								locked=value['lock'])
							
							color_b = QColor(value['color_nen'])
							color_b.setAlphaF(value['opacity_nen'] / 100)
							brush = QBrush(color_b)
							
							color_p = QColor(value['color_stroke'])
							color_p.setAlphaF(value['opacity_stroke'] / 100)
							
							if value['them_stroke'] is True:
								pen = QPen(color_p, float(value['do_day_stroke']), Qt.PenStyle.SolidLine)
							else:
								pen = (QPen(Qt.PenStyle.NoPen))
							ite.setPen(pen)
							ite.setBrush(brush)
							# list_layers.append(ite)
							ite.addItemToScene(ite)
						
						
						
						elif layer.get("type") == 'TextItemLayer':
							
							value = layer['value']
							ite = TextItemLayer(self.manage_thread_pool,
								value['text'], QPointF(value['x'] * ratio_scale_H, value['y'] * ratio_scale_V),
								self.layers,
								self._scene, self.list_fonts, text_run=value['text_run'],
								locked=value['lock'])
							
							color_b = QColor(value['color_text'])
							color_b.setAlphaF(value['opacity_text'] / 100)
							color_text = QBrush(color_b)
							
							color_p = QColor(value['color_stroke'])
							color_p.setAlphaF(value['opacity_stroke'] / 100)
							
							font = QFont()
							font.setFamily(value['font_family'])
							fontsize_o = value['font_size']
							
							if width_Old > width_New:
								# print('max')
								sla = max(ratio_scale_V, ratio_scale_H)
							else:
								sla = min(ratio_scale_V, ratio_scale_H)
							
							font.setPixelSize(math.ceil(fontsize_o * sla))
							
							font.setBold(True)
							font.setWeight(QFont.Weight.Black)
							
							ite.charFormat = QTextCharFormat()
							ite.document = QTextDocument()
							ite.charFormat.setFont(font)  # font chữ
							ite.charFormat.setForeground(color_text)  # set màu của chữ
							
							if value['them_stroke'] is not False:  # viền chữ
								ite.charFormat.setTextOutline(QPen(color_p, float(value["do_day_stroke"]),
									Qt.PenStyle.SolidLine))
							else:
								ite.charFormat.setTextOutline(QPen(Qt.PenStyle.NoPen))
							
							ite.cursor = QTextCursor(ite.document)
							
							ite.cursor.insertText(value["text"], ite.charFormat)
							
							ite.setDocument(ite.document)
							
							if value['text_run'] is True:
								ite.timer.start(value['speed_text'])
							else:
								ite.timer.stop()
							ite.addItemToScene(ite)
						# list_layers.append(ite)
						
						elif layer.get("type") == 'MediaItemLayer':
							value = layer['value']
							# if value['main_video'] is False:
							pixmap_ori = value['pixmap']
							# if not value['scale'] == "":
							# pixmap = pixmap.scaled(*value['scale'])
							width_o = value['width']
							height_o = value['height']
							
							_scale = (width_o * ratio_scale_H, height_o * ratio_scale_V)
							
							ite = MediaItemLayer(self.manage_thread_pool, pixmap_ori, QPointF(
								value['x'] * ratio_scale_H, value['y'] * ratio_scale_V),
								self.layers, self._scene,
								locked=value['lock'])
							
							pixmap = pixmap_ori.scaled(*_scale)
							ite.setPixmap(pixmap)
							ite.resizer.setPos(ite.boundingRect().bottomRight() - ite.r_offset)
							ite.addItemToScene(ite)
		
		# self.scaleItemRatio(width_Old, height_Old, width_New, height_New)
		# list_layers.append(ite)
		#
		# elif layer['type'] == 'RectBlurItemLayer':
		# 	try:
		# 		value = layer['value']
		# 		ite = RectBlurItemLayer(self.manage_thread_pool,
		# 			QRectF(0, 0, value['width'], value['height']),
		# 			QPointF(value['x'], value['y']), self.layers, self._scene,
		# 			sigma=value['sigma'], steps=value['steps'], locked=value['lock'])
		# 		ite.addItemToScene()
		#
		# 		self.gr_show_add_sub.btn_add_rect_blur.set_active(True)
		#
		# 		self._rectblur_area = ite
		# 	except:
		# 		print("Không thể thêm layer blur")
		# list_layers.append(ite)
		
		self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
			STATUS_BUTTON_SAVE_CONFIG_CHANGED,
			True)
	
	def scaleItemRatio (self, width_Old, height_Old, width_New, height_New):
		if len(self._scene.items()) > 0:
			ratio_scale_H = width_New / width_Old
			ratio_scale_V = height_New / height_Old
			if ratio_scale_H != 1 and ratio_scale_V != 1:
				for item_layer in self.layers:
					item = list(item_layer.values())[0]
					# print(ratio_scale_V, ratio_scale_H)
					
					if isinstance(item, RectangleItemLayer):
						# print('Layer')
						width_o = item.rect().width()
						height_o = item.rect().height()
						x_o = item.pos().x()
						y_o = item.pos().y()
						item.setRect(QRectF(0, 0, width_o * ratio_scale_H, height_o * ratio_scale_V))
						item.setPos(QPointF(x_o * ratio_scale_H, y_o * ratio_scale_V))
						item.resizer.setPos(item.boundingRect().bottomRight() - item.r_offset)
					
					if isinstance(item, TextItemLayer):
						
						x_o = item.pos().x()
						y_o = item.pos().y()
						item.setPos(QPointF(x_o * ratio_scale_H, y_o * ratio_scale_V))
						
						fontsize_o = item.charFormat.font().pixelSize()
						# print(item.pos())
						# print(fontsize_o * ratio_scale_H)
						
						font = item.charFormat.font()
						foreground = item.charFormat.foreground()
						document = item.document
						if width_Old > width_New:
							# print('max')
							sla = max(ratio_scale_V, ratio_scale_H)
						else:
							sla = min(ratio_scale_V, ratio_scale_H)
						font.setPixelSize(math.ceil(fontsize_o * sla))
						# print(font)
						# item.charFormat.setFont(font)
						
						item.charFormat = QTextCharFormat()
						# print(new_value)
						item.charFormat.setFont(font)  # font chữ
						item.charFormat.setForeground(foreground)  # set màu của chữ
						item.charFormat.setTextOutline(QPen(Qt.PenStyle.NoPen))
						# print(item.document)
						
						item.document = QTextDocument()
						# print(1)
						
						item.cursor = QTextCursor(item.document)
						item.cursor.insertText(document.toPlainText(), item.charFormat)
						
						item.setDocument(item.document)
						
						if item.text_run is True:
							item.timer.start(item.timer.interval())
						else:
							item.timer.stop()
					
					if isinstance(item, MediaItemLayer):
						width_o = item.pixmap().rect().width()
						height_o = item.pixmap().rect().height()
						# print(width_o, height_o)
						x_o = item.pos(). \
							x()
						y_o = item.pos().y()
						x_n, y_n = x_o * ratio_scale_H, y_o * ratio_scale_V
						item.setPos(QPointF(x_n, y_n))
						bt_x = item.boundingRect().bottomRight().x() * ratio_scale_H
						bt_y = item.boundingRect().bottomRight().y() * ratio_scale_H
						
						_scale = width_o * ratio_scale_H, height_o * ratio_scale_V
						pixmap = item.pixmap_ori.copy()
						item.resizer.setPos(QPointF(bt_x, bt_y) - item.r_offset)
						pixmap = pixmap.scaled(*_scale)
						item.setPixmap(pixmap)
	
	def resetScreen (self):
		# print('resetScreen')
		self._scene = QGraphicsScene()
		# print('resetScreen')
		self._scene.setSceneRect(QRectF(self.rect()))
		self._frame_video_main_sub = QGraphicsPixmapItem()
		self._rectbox_sub = QGraphicsRectItem()
		self._rectblur_area = None
		
		# self._text_sub_origin = QGraphicsTextItem()
		# self._text_sub_translate = QGraphicsTextItem()
		
		self._scene.addItem(self._rectbox_sub)
		# self._scene.addItem(self._text_sub_origin)
		# self._scene.addItem(self._text_sub_translate)
		
		self.setScene(self._scene)
		self.layers = []
		self.list_text_sub_origin = []
		self.list_rectbox_sub_origin = []
		self.list_text_sub_translate = []
		self.list_rectbox_sub_translate = []
		
		self.setRectScene()
		
		if self.isLoaded is False:
			if hasattr(self.gr_show_add_sub, "path_video") is True:
				self.gr_show_add_sub.loadFrameVideo(1)
				# self.gr_show_add_sub.sliderChangeFrameChanged.emit(1)
				# print('vaoffff')
		self.isLoaded = True
	
	def getFontPaths (self, **kwargs):
		
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		
		# font_paths = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.FontsLocation)
		#
		# accounted = []
		# unloadable = []
		family_to_path = {}
		
		# db = QFontDatabase
		# for fpath in font_paths:  # go through all font paths
		#     for filename in os.listdir(fpath):  # go through all files at each path
		#         path = os.path.join(fpath, filename)
		#
		#         idx = db.addApplicationFont(path)  # add font path
		#
		#         if idx < 0:
		#             unloadable.append(path)  # font wasn't loaded if idx is -1
		#         else:
		#             names = db.applicationFontFamilies(idx)  # load back font family name
		#             # print(names)
		#             for n in names:
		#                 if n in family_to_path:
		#                     accounted.append((n, path))
		#                 else:
		#                     family_to_path[n] = path
		#             # this isn't a 1:1 mapping, for example
		#             # 'C:/Windows/Fonts/HTOWERT.TTF' (regular) and
		#             # 'C:/Windows/Fonts/HTOWERTI.TTF' (italic) are different
		#             # but applicationFontFamilies will return 'High Tower Text' for both
		liss = glob.glob(PATH_FONT + '**/*.ttf', recursive=True)
		# db = QFontDatabase
		for filename in liss:  # go through all files at each path
			path = os.path.join(os.path.abspath(os.getcwd()), filename)
			idx = QFontDatabase.addApplicationFont(path)  # add font path
			
			if idx < 0:
				print("Font Lỗi", path)
			else:
				names = QFontDatabase.applicationFontFamilies(idx)  # load back font family name
				for n in names:
					if not n in family_to_path:
						family_to_path[n] = path
		
		thread_pool.finishSingleThread(id_worker)
		return family_to_path
	
	def _onSelectionChanged (self):
		
		if len(self.layers) > 0:
			for item_layer in self.layers:
				item = list(item_layer.values())[0]
				if hasattr(item, "resizer") is True:
					resizer = item.resizer
					if resizer.isSelected() is False:
						resizer.hide()
	
	def setRectScene (self):
		if hasattr(self, "configCurrent"):
			cau_hinh = json.loads(self.configCurrent.value)
			# print(cau_hinh)
			output_size = cau_hinh["chat_luong_video"]
			# print(output_size)
			# output_quantity = cau_hinh["ti_le_khung_hinh"]
			try:
				width_V, height_V = output_size.split("|")
			except:
				cau_hinh["chat_luong_video"] = "1920|1080"
				cau_hinh["ti_le_khung_hinh"] = "16:9"
				self.configCurrent.value = json.dumps(cau_hinh)
				self.configCurrent.save()
				cau_hinh = json.loads(self.configCurrent.value)
				output_size = cau_hinh["chat_luong_video"]
				width_V, height_V = output_size.split("|")
			
			self.setSizeScreen(int(width_V), int(height_V))
	
	
	def setSizeScreen (self, width_New, height_New):
		
		ratio = width_New / height_New
		width_V = self.height_V * (ratio)
		# print(width_V)
		
		width_Old = self._scene.width()
		height_Old = self._scene.height()
		ratio_scale_H = width_New / width_Old
		ratio_scale_V = height_New / height_Old
		# print(width_Old, height_Old)
		# print(width_S, height_S)
		
		self._scene.setSceneRect(QRect(0, 0, width_New, height_New))
		
		self.setSceneRect(QRect(0, 0, width_New, height_New))
		self.setFixedSize(QSize(int(width_V), self.height_V))
		unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
		self.scale(1 / unity.width(), 1 / unity.height())
		viewrect = QRectF(0, 0, width_V, self.height_V)
		scenerect = self.transform().mapRect(QRect(0, 0, width_New, height_New))
		factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
		self.scale(factor, factor)
		
		self.scaleItemRatio(width_Old, height_Old, width_New, height_New)
	
	def addItemToScene (self, item):
		zindex = len(self.layers) + 1
		item.setZValue(zindex)
		self._scene.addItem(item)
		self.layers.append({item.id_layer: item})
	
	def addText (self, new_value):
		# print(new_value)
		# value = layer['value']
		ite = TextItemLayer(self.manage_thread_pool, new_value['text'], QPointF(new_value['x'], new_value['y']),
			self.layers,
			self._scene, self.list_fonts, text_run=new_value['text_run'],
			locked=False)
		
		ite.charFormat = QTextCharFormat()
		
		ite.charFormat.setFont(new_value["font"])  # font chữ
		ite.charFormat.setForeground(new_value["color_text"])  # set màu của chữ
		
		if new_value['stroke'] is not False:  # viền chữ
			ite.charFormat.setTextOutline(new_value['stroke'])
		
		else:
			ite.charFormat.setTextOutline(QPen(Qt.PenStyle.NoPen))
		document = QTextDocument()
		ite.cursor = QTextCursor(document)
		ite.cursor.insertText(new_value["text"], ite.charFormat)
		
		ite.setDocument(document)
		ite.addItemToScene(ite)
	
	def addRectangle (self):
		# print(self._scene.width() / 1.5)
		# print((self._scene.width() - self._scene.width() / 1.5)/2)
		item = RectangleItemLayer(self.manage_thread_pool, QRectF(0, 0, self._scene.width() / 1.5, self._scene.height() / 6),
			QPointF((
							self._scene.width() - self._scene.width() / 1.5) / 2 - random.randrange(5, 30), self.rect().height() / 2 - random.randrange(5, 30)),
			self.layers, self._scene)
		item.addItemToScene(item)
	
	def addRectBlur (self):
		try:
			_rectblur_area = RectBlurItemLayer(self.manage_thread_pool, QRectF(0, 0, self._scene.width() / 1.5, self._scene.height() / 6),
				QPointF((
								self._scene.width() - self._scene.width() / 1.5) / 2 - random.randrange(5, 30), self._scene.height() - self._scene.height() / 6 - random.randrange(5, 30)),
				self.list_blur, self._scene)
			_rectblur_area.setZValue(self._frame_video_main_sub.zValue() + 0.1 * (len(self.list_blur) + 1))
			_rectblur_area.addItemToScene()
			self.list_blur.append(_rectblur_area)
		except:
			print("Không thể thêm mờ")
	
	
	def removeRectBlur (self):
		try:
			for item in self._scene.items():
				if item is self._frame_blur or item is self._rectblur_area:
					self._scene.removeItem(item)
			# self._scene.removeItem(self._frame_blur)
			# self._scene.removeItem(self._rectblur_area)
			self._rectblur_area = None
		except:
			print("Không thể xóa mờ")
	
	def addImage (self, pixmap: QPixmap):
		item = MediaItemLayer(self.manage_thread_pool, pixmap,
			QPointF(self.rect().width() / 2, self.rect().height() / 2), self.layers,
			self._scene)
		item.addItemToScene(item)
	
	def hasPhoto (self):
		return not self._empty
	
	def setFrameBlur (self, pixmap, stroke_blur, blur, index_blur):
		# try:
		if pixmap and not pixmap.isNull() and self.hasPhoto():
			# zValue = self._frame_video_main_sub.zValue() + 0.1 * (index_blur + 1)
			zValue = blur.zValue()
			for item in self._scene.items():
				if item.zValue() == zValue and isinstance(item, QGraphicsPixmapItem):
					# print(item)
					# item
					self._scene.removeItem(item)
			# self._scene.removeItem(self._frame_blur)
			_frame_blur = QGraphicsPixmapItem()
			_frame_blur.setPixmap(pixmap)
			_frame_blur.setZValue(zValue)
			blur.setZValue(zValue)
			self._scene.addItem(_frame_blur)
			
			r_offset = QPointF(stroke_blur, stroke_blur)
			# self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
			_frame_blur.setPos(blur.pos() + r_offset)
	
	# except:
	# 	print("Không thể setFrameBlur")
	
	# self._frame_blur.(self.rect_selection_sub_area.pos())
	# print(self._scene.items())
	
	# @decorator_try_except_class
	def setVideoMain (self, pixmap,pixmap_bur, width_I, height_I, video_new):
		if pixmap:
			# print("setVideoMain")
			
			self._empty = False
			# print(self._scene.items())
			if isinstance(self._frame_video_main_sub, FrameVideoMainItemLayer):
				# print(video_new)
				# if video_new:
				# 	if hasattr(self._frame_video_main_sub, "_scale"):
				# 		del self._frame_video_main_sub._scale
				#
				# 	# pixmap = pixmap.scaled(width_V / (height_V / self._scene.height()), self._scene.height())
				# 	pixmap = pixmap.scaled(self._scene.width(), self._scene.height())
				# 	self._frame_video_main_sub.setPos(QPoint(0, 0))
				# else:
				#
				# 	if hasattr(self._frame_video_main_sub, "_scale"):
				# 		pixmap = pixmap.scaled(*self._frame_video_main_sub._scale)
				# 	else:
				# 		pixmap = pixmap.scaled(self._scene.width(), self._scene.height())
				# # pixmap = pixmap.scaled(width_V / (height_V / self._scene.height()), self._scene.height())
				ratio = width_I / height_I
				width_i = int(self._scene.height() * (ratio))
				pos_x = (self._scene.width()-width_i)/2

				pixmap = pixmap.scaled(width_i, self._scene.height())

				self._frame_video_main_sub.setPixmap(pixmap)
				self._frame_video_main_sub.pixmap_ = pixmap
				self._frame_video_main_sub.setPos(pos_x,0)
				# self._frame_video_main_sub.refeshZValue()
				if pixmap_bur:
					pixmap_bur = pixmap_bur.scaled(self._scene.width(), self._scene.height())
					self._video_main_blur.setPixmap(pixmap_bur)

			else:
				if pixmap_bur:
					pixmap_bur = pixmap_bur.scaled(self._scene.width(), self._scene.height())
					self._video_main_blur=BackgroundVideoMainItemLayer(self.manage_thread_pool, pixmap, self.layers,self.configCurrent)
					self._video_main_blur.setPixmap(pixmap_bur)
					self._video_main_blur.setZValue(0)
					self._scene.addItem(self._video_main_blur)


				# print(12)
				ratio = width_I / height_I
				width_i = int(self._scene.height() * (ratio))
				pos_x = (self._scene.width()-width_i)/2
				pixmap = pixmap.scaled(width_i, self._scene.height())

				# pixmap = pixmap.scaled(self._scene.width(), self._scene.height())
				# pixmap = pixmap.scaled(width_V / (height_V / self._scene.height()), self._scene.height())
				self._frame_video_main_sub = FrameVideoMainItemLayer(self.manage_thread_pool, pixmap, self.layers, self._frame_blur, self._rectblur_area)
				self._frame_video_main_sub.setPos(pos_x,0)
				self._frame_video_main_sub.setZValue(0.1)
				self._scene.addItem(self._frame_video_main_sub)
				self.layers.insert(0, {self._frame_video_main_sub.id_layer: self._frame_video_main_sub})
				# self._frame_video_main_sub.refeshZValue()

	
	# @decorator_try_except_class
	def getXCenterSub (self, text_, type_sub):
		
		# print("addSubTextOrigin")
		self.text_sub_origin = ''
		self.text_sub_translate = ''
		data_conf: dict = json.loads(self.configCurrent.value)
		
		'''Xử lý vị trí text_sub'''
		if type_sub == 'origin':
			sub = self.changeStyleSubOrigin(data_conf, text_)
		else:
			sub = self.changeStyleSubTranslate(data_conf, text_)
		
		x_sub = (self._scene.width() - sub.width()) / 2
		return x_sub
	
	
	# @decorator_try_except_class
	def addSubTextOrigin (self, text_, position):
		
		# print("addSubTextOrigin")
		data_conf: dict = json.loads(self.configCurrent.value)
		
		# 2 màu trên phải giống nhau
		if data_conf["nen_sub"] is True:
			# màu nền của rect
			color_background = QColor(data_conf["mau_nen_sub"])
			color_background.setAlphaF(data_conf["opacity_nen_sub"] / 100)
			stroke = QPen(color_background)
			brush = QBrush(color_background)
		
		else:
			color_background = QColor("#000000")
			color_background.setAlphaF(0)
			stroke = QPen(color_background)
			brush = QBrush(color_background)
		
		'''Xử lý vị trí text_sub'''
		cach_le = 10
		# print(10)
		sub = self.changeStyleSubOrigin(data_conf, text_)
		# print(111)
		if data_conf.get("split_sub_origin") is False:
			
			list_text = text_.split(" ")
			self.hamDeQuySubOrigin(list_text, data_conf)
			# if len(self.list_text_sub_origin) > 0:
			# print(self.text_sub_origin)
			if len(self.text_sub_origin) > 0:
				# print(000)
				sub = self.changeStyleSubOrigin(data_conf, self.text_sub_origin)
		# print(11)
		self.list_text_sub_origin.append(sub)
		
		width_text = sub.boundingRect().width()
		height_text = sub.boundingRect().height()
		x_sub, y_sub = self.positionSub(data_conf["vi_tri_sub"], width_text, height_text, self._scene.width(),
			self._scene.height(), position, cach_le=cach_le)
		# print(x_sub, y_sub)
		if data_conf["vi_tri_sub"] in [1, 2, 3]:  # vi trí bottom
			y_sub = y_sub - height_text
		else:
			y_sub = y_sub
		
		sub.setPos(x_sub, y_sub)
		
		_rectbox = QGraphicsRectItem()
		_rectbox.setPen(stroke)
		_rectbox.setBrush(brush)
		_rectbox.setRect(sub.boundingRect())
		_rectbox.setPos(x_sub, y_sub)
		
		# print(14)
		sub.rectbox = _rectbox
		sub.setZValue(1003)
		_rectbox.setZValue(1003)
		self.text_sub_origin_current = sub
		self.rectbox_sub_origin_current = _rectbox
		# self.list_rectbox_sub_origin.append(_rectbox)
		self._scene.addItem(_rectbox)
		self._scene.addItem(sub)
	
	
	def positionSub (self, pos, width_text, height_text, video_width, video_heigth, position, cach_le=10):
		x_sub = 0
		y_sub = 0
		
		phan_tram_le = 0.03
		if pos == 1:  # bottom left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = video_heigth - cach_le
		
		elif pos == 2:  # bottom center
			x_sub = video_width / 2 - width_text / 2
			y_sub = video_heigth - cach_le
		
		elif pos == 3:  # bottom right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = video_heigth - cach_le
		
		elif pos == 4:  # middle left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = video_heigth / 2 - height_text
		
		elif pos == 5:  # middle center
			x_sub = video_width / 2 - width_text / 2
			y_sub = video_heigth / 2 - height_text
		
		elif pos == 6:  # middle right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = video_heigth / 2 - height_text
		
		elif pos == 7:  # top right
			x_sub = video_width - (video_width * phan_tram_le + width_text)
			y_sub = cach_le
		
		elif pos == 8:  # top center
			x_sub = video_width / 2 - width_text / 2
			y_sub = cach_le
		
		elif pos == 9:  # top left
			x_sub = video_width * phan_tram_le  # 10%
			y_sub = cach_le
		
		else:
			# print(position)
			
			try:
				x_sub_, y_sub_ = position.split(DELIMITER_POS_SUB)
				x_sub, y_sub = float(x_sub_), float(y_sub_) - height_text
			# print(x_sub, y_sub)
			
			except:
				
				try:
					x_sub_, y_sub_ = position.split(DELIMITER_CENTER_POS_SUB)
					# print(x_sub, y_sub)
					
					x_sub = video_width / 2 - width_text / 2
					
					y_sub = float(y_sub_) - height_text / 2
				
				except:
					x_sub = 10  # 10px
					y_sub = video_heigth - 10 - height_text
		
		# print(x_sub, y_sub)
		
		return x_sub, y_sub
	
	def hamDeQuySubOrigin (self, list_text, data_conf):
		'''tách đoạn sub thành từng từ sau đó kiểm tra độ dài để hiển thị xuống hàng'''
		# print('dequy')
		if len(list_text) == 0:
			return
		for i in range(1, len(list_text) - 1):
			
			item_text = ' '.join([str(elem) for elem in list_text[0:i]])
			
			text_sub_origin = self.changeStyleSubOrigin(data_conf, item_text)
			
			if text_sub_origin.boundingRect().width() / self._scene.width() >= 0.68:
				self.text_sub_origin += item_text + "\n"
				# self.list_text_sub_origin.append(text_sub_origin)
				return self.hamDeQuySubOrigin(list_text[i:], data_conf)
		
		item_text1 = ' '.join([str(elem) for elem in list_text])
		self.text_sub_origin += item_text1
	
	# text_sub_origin = self.changeStyleSubOrigin(data_conf, item_text1)
	# self.list_text_sub_origin.append(text_sub_origin)
	
	def changeStyleSubOrigin (self, data_conf, item_text) -> TextSubLayer:
		
		document = QTextDocument()
		charFormat = QTextCharFormat()
		font = QFont()
		
		fs = int(data_conf["font_size"].replace("px", ""))
		
		if data_conf["font_sub"] is True:
			font.setFamily(data_conf["font_family"])
			font.setPointSize(fs)
			
			text = QGraphicsTextItem(item_text)
			text.setFont(font)
			text_rect = text.boundingRect()
			
			text_ratio = (fs / (text_rect.height())) * len(item_text.split("\n"))
			# print(text_ratio, text_rect)
			# print(font_.pixelSize())
			# print(font.pointSizeF())
			# print(font.pointSizeF() * text_ratio)
			
			font.setPointSize(int(font.pointSizeF() * text_ratio))
		
		else:
			font.setFamily("Arial")
			font.setPointSize(20)
		
		color_text = QColor("#ffffff")
		
		if data_conf["add_mau_sub"] is True:
			# màu chữ
			color_text = QColor(data_conf["mau_sub"])
			color_text.setAlphaF(data_conf["opacity_mau_sub"] / 100)
		brush_text = QBrush(color_text)
		
		charFormat.setFont(font)
		charFormat.setForeground(brush_text)
		
		cursor = QTextCursor(document)
		cursor.insertText(item_text, charFormat)
		# charFormat.setFontWordSpacing(0)
		# charFormat.setFontLetterSpacing(0)
		locked = False if data_conf["vi_tri_sub"] == 0 else True
		
		_text_sub_origin = TextSubLayer(self.manage_thread_pool, item_text, document, self.list_fonts, self.configCurrent, locked=locked)
		# _text_sub_origin.setDocument(document)
		# print(_text_sub_origin.boundingRect().height())
		return _text_sub_origin
	
	def removeTextSubCurrent (self):
		# QGraphicsRectItem
		# print('removeTextSubCurrent')
		
		if len(self.list_text_sub_origin) > 0 :
			# print("removeTextSubCurrent")
			for item in self._scene.items():
				# print(item.zValue())
				if item.zValue() == 1003:
					self._scene.removeItem(item)
			
			self.text_sub_origin = ''
			# self.text_sub_translate = ''
			self.list_text_sub_origin = []
			self.list_rectbox_sub_origin = []
			# self.list_text_sub_translate = []
			# self.list_rectbox_sub_translate = []
# print(self.list_text_sub_origin)
# print(self.list_rectbox_sub_origin)
