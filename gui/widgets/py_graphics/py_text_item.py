import uuid

from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtGui import QIcon, QFont, QColor, QBrush, QPen, QTextDocument, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem, QMenu, QGraphicsTextItem

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import STATUS_BUTTON_SAVE_CONFIG_CHANGED
from gui.widgets.py_dialogs import PyDialogGraphicText


class TextItemLayer(QGraphicsTextItem):
	def __init__ (self, manage_thread_pool, _text: str, pos: QPointF, layers: list, scene: QGraphicsScene, list_fonts, text_run=False, locked=False):
		super().__init__()
		
		self.id_layer = uuid.uuid4().__str__()
		self.manage_thread_pool = manage_thread_pool
		self.layers = layers
		self.scene = scene
		self.locked = locked
		self.text_run = text_run
		
		self.mousePressPos = None
		self.mousePressRect = None
		self.setAcceptHoverEvents(True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
		
		self.setPos(pos)
		self.keyboard_offset = 1
		self.speed_text = 0
		self.list_fonts = list_fonts
		self.text = _text
		self.document = QTextDocument()
		self.charFormat = QTextCharFormat()
		self.font = QFont()
		# self.font.setFamily("Arial")
		self.font.setPixelSize(28)
		self.font.setBold(True)
		self.font.setWeight(QFont.Weight.Black)
		
		self.color_text = QColor("#ff0000")
		# color_text.setAlphaF(data_conf["opacity_mau_sub"] / 100)
		
		self.charFormat.setFont(self.font)  # font chữ
		self.charFormat.setForeground(QBrush(self.color_text))  # set màu của chữ
		
		self.charFormat.setTextOutline(QPen(Qt.PenStyle.NoPen))  # viền chữ
		
		self.cursor = QTextCursor(self.document)
		self.cursor.insertText(self.text, self.charFormat)
		
		self.setDocument(self.document)
		
		self.timer = QTimer()
		self.timer.timeout.connect(self._run_text)
		if self.text_run is True:
			self.timer.start(15)  # 5 nhanh 15 trung bình 25 chậm
		self.pos_y_old = self.pos().y()
	
	def itemChange (self, change, value):
		if change == QGraphicsItem.GraphicsItemChange.ItemZValueHasChanged:
			self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				False)
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
			if self.text_run is False:
				self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
					STATUS_BUTTON_SAVE_CONFIG_CHANGED,
					False)
			elif hasattr(self, "pos_y_old") and not self.pos_y_old == self.pos().y():
				self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
					STATUS_BUTTON_SAVE_CONFIG_CHANGED,
					False)
				self.pos_y_old = self.pos().y()
		
		return super(TextItemLayer, self).itemChange(change, value)
	
	def reconnect (self):  # không xoá được
		pass
		# self.timer = QTimer()
		# self.timer.timeout.connect(self._run_text)
		# if self.text_run is True:
		#     print('1234')
		#
		#     self.timer.start(100)
		# else:
		#     self.timer.stop()
	
	def keyPressEvent (self, e):
		
		if e.key() == Qt.Key.Key_Down:
			self.setPos(self.x(), self.y() + self.keyboard_offset)

			# print('Press Down')
		elif e.key() == Qt.Key.Key_Up:
			self.setPos(self.x(), self.y() - self.keyboard_offset)

			# print('Press Key_Up')
		
		elif e.key() == Qt.Key.Key_Right:
			self.setPos(self.x() + self.keyboard_offset, self.y())

			# print('Press Key_Right')
		
		elif e.key() == Qt.Key.Key_Left:
			self.setPos(self.x() - self.keyboard_offset, self.y())

			# print('Press Key_Left')
		elif e.key() == Qt.Key.Key_Delete:
			index = int(self.zValue() - 1)
			del self.layers[index]
			self.scene.removeItem(self)
			self.refeshZValue()  # cập nhật lại zvalue tưng layer để khi action up down thực hiện ko lỗi
			self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				False)
	
	def contextMenuEvent (self, event):
		if self.locked is False:
			
			if self.isSelected() is True:
				menu = QMenu()
				
				action_delete = menu.addAction(QIcon(ConfigResource.set_svg_icon("delete.png")),
					"Xoá")  # (QAction('test'))
				
				action_clone = menu.addAction(QIcon(ConfigResource.set_svg_icon("clone.png")), "Clone")
				action_up = menu.addAction(QIcon(ConfigResource.set_svg_icon("up-arrow.png")), "Lên 1 Lớp")
				action_top = menu.addAction(QIcon(ConfigResource.set_svg_icon("top-arrow.png")), "Lên trên cùng")
				action_down = menu.addAction(QIcon(ConfigResource.set_svg_icon("down-arrow.png")), "Xuống 1 Lớp")
				action_bottom = menu.addAction(QIcon(ConfigResource.set_svg_icon("bottom-arrow.png")),
					"Xuống dưới cùng")
				action_lock = menu.addAction("")
				action_lock.setIcon(QIcon(ConfigResource.set_svg_icon("lock.png")))
				action_lock.setText("Khoá")
				
				action_setting = menu.addAction(QIcon(ConfigResource.set_svg_icon("settings.svg")), "Cài Đặt")
				action = menu.exec(event.screenPos())

				index = self.layers.index({self.id_layer: self})  # cách 1

				# index = int(self.zValue() - 1)  # cách 2 -1 vì luc đầu +1
				
				if action == action_delete:
					del self.layers[index]
					self.scene.removeItem(self)
					self.refeshZValue()  # cập nhật lại zvalue tưng layer để khi action up down thực hiện ko lỗi
					self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
						STATUS_BUTTON_SAVE_CONFIG_CHANGED,
						False)
				if action == action_clone:
					self.clone(event.scenePos())
					self.refeshZValue()
				if action == action_up:
					if int(self.zValue()) < len(self.layers):
						_pop = self.layers.pop(index)
						self.layers.insert(index + 1, _pop)
						self.refeshZValue()
				
				if action == action_down:
					if int(self.zValue()) > 1:
						_pop = self.layers.pop(index)
						self.layers.insert(index - 1, _pop)
						self.refeshZValue()
				
				if action == action_top:
					_pop = self.layers.pop(index)
					self.layers.insert(len(self.layers), _pop)
					self.refeshZValue()
				if action == action_bottom:
					_pop = self.layers.pop(index)
					self.layers.insert(0, _pop)
					self.refeshZValue()
				
				if action == action_lock:
					flag: QGraphicsItem.GraphicsItemFlag = self.flags()
					
					if flag & QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
						self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
						self.locked = True
				
				if action == action_setting:
					font = self.charFormat.font()
					font_size = font.pixelSize()
					font_family = font.family()
					
					color_text: QBrush = self.charFormat.foreground()
					rgb_color_text = [color_text.color().red(), color_text.color().green(), color_text.color().blue()]
					color_text_hex = '#' + ''.join(
						[hex(v)[2:].ljust(2, '0') for v in rgb_color_text]
					)
					opacity_text = color_text.color().alphaF() * 100
					
					stroke_text: QPen = self.charFormat.textOutline()
					rgb_color_stroke_text = [stroke_text.color().red(), stroke_text.color().green(),
											 stroke_text.color().blue()]
					color_stroke = '#' + ''.join(
						[hex(v)[2:].ljust(2, '0') for v in rgb_color_stroke_text]
					)
					
					them_stroke = False
					if stroke_text.style().name == "SolidLine":
						them_stroke = True
					
					opacity_stroke = stroke_text.color().alphaF() * 100
					
					value = {
						"x": self.pos().x(),
						"y": self.pos().y(),
						"color_text": color_text_hex,
						"opacity_text": opacity_text,
						"them_stroke": them_stroke,
						"color_stroke": color_stroke,
						"do_day_stroke": stroke_text.width(),
						"opacity_stroke": opacity_stroke,
						"font_size": font_size,
						"font_family": font_family,
						"text": self.document.toPlainText(),
						"text_run": self.text_run,
						"speed_text": self.timer.interval(),
					}
					# print(value)
					
					dialog_settings = PyDialogGraphicText(self.list_fonts)
					
					dialog_settings.loadData(value)
					if dialog_settings.exec():
						new_value = dialog_settings.getValue()
						self.setPos(QPointF(new_value["x"], new_value["y"]))
						
						self.charFormat = QTextCharFormat()
						# print(new_value)
						self.charFormat.setFont(new_value["font"])  # font chữ
						self.charFormat.setForeground(new_value["color_text"])  # set màu của chữ
						
						if new_value['stroke'] is not False:  # viền chữ
							self.charFormat.setTextOutline(new_value['stroke'])
						
						else:
							self.charFormat.setTextOutline(QPen(Qt.PenStyle.NoPen))
						# print(self.document)
						
						self.document = QTextDocument()
						# print(1)
						
						self.cursor = QTextCursor(self.document)
						self.cursor.insertText(new_value["text"], self.charFormat)
						
						self.setDocument(self.document)
						
						self.text_run = new_value['text_run']
						
						if new_value['text_run'] is True:
							self.timer.start(new_value['speed_text'])
						
						else:
							self.timer.stop()
						
						self.prepareGeometryChange()
						self.update()
						self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
							STATUS_BUTTON_SAVE_CONFIG_CHANGED,
							False)
					
					else:
						print("Cancel!")
		
		else:
			self.setSelected(True)
			if self.isSelected() is True:
				menu = QMenu()
				action_unlock = menu.addAction("")
				action_unlock.setIcon(QIcon(ConfigResource.set_svg_icon("unlock.png")))
				action_unlock.setText("Mở Khoá")
				action = menu.exec(event.screenPos())
				if action == action_unlock:
					self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
					self.locked = False
	
	def _run_text (self):
		
		wt = int(self.boundingRect().width())
		sreen_width = int(self.scene.width())
		x = int(self.pos().x())
		x_new = x - 1
		if x_new <= -wt:
			x_new = sreen_width
		
		self.setPos(float(x_new), float(self.pos().y()))
	
	def refeshZValue (self):
		for idx, layer in enumerate(self.layers):
			item = list(layer.values())[0]
			item.setZValue(idx + 1)
	
	def addItemToScene (self, item):
		zindex = len(self.layers) + 1
		item.setZValue(zindex)
		self.scene.addItem(item)
		self.layers.append({item.id_layer: item})
	
	
	def clone (self, pos):
		
		it = TextItemLayer(self.manage_thread_pool, self.toPlainText(), pos.toPoint(), self.layers, self.scene, self.list_fonts)
		
		it.setFlags(self.flags())
		it.setOpacity(self.opacity())
		it.setRotation(self.rotation())
		it.setScale(self.scale())
		
		charFormat = QTextCharFormat()
		document = QTextDocument()
		
		charFormat.setFont(self.charFormat.font())  # font chữ
		charFormat.setForeground(self.charFormat.foreground())  # set màu của chữ
		charFormat.setTextOutline(self.charFormat.textOutline())
		
		cursor = QTextCursor(document)
		cursor.insertText(self.document.toPlainText(), charFormat)
		
		it.charFormat = charFormat
		it.cursor = cursor
		it.document = document
		
		it.setDocument(document)
		if self.text_run is True:
			it.text_run = True
			it.timer.start(self.timer.interval())
		
		self.addItemToScene(it)
		
		return it
	
	def itemToVariant (self):
		
		font = self.charFormat.font()
		font_size = font.pixelSize()
		font_family = font.family()
		
		color_text: QBrush = self.charFormat.foreground()
		rgb_color_text = [color_text.color().red(), color_text.color().green(), color_text.color().blue()]
		color_text_hex = '#' + ''.join(
			[hex(v)[2:].ljust(2, '0') for v in rgb_color_text]
		)
		opacity_text = color_text.color().alphaF() * 100
		
		stroke_text: QPen = self.charFormat.textOutline()
		rgb_color_stroke_text = [stroke_text.color().red(), stroke_text.color().green(),
								 stroke_text.color().blue()]
		color_stroke = '#' + ''.join(
			[hex(v)[2:].ljust(2, '0') for v in rgb_color_stroke_text]
		)
		
		them_stroke = False
		if stroke_text.style().name == "SolidLine":
			them_stroke = True
		
		opacity_stroke = stroke_text.color().alphaF() * 100
		# print(self.pos())
		return {
			"type": "TextItemLayer",
			"value": {
				"x": self.pos().x(),
				"y": self.pos().y() + 12,
				"color_text": color_text_hex,
				"opacity_text": opacity_text,
				"them_stroke": them_stroke,
				"color_stroke": color_stroke,
				"do_day_stroke": stroke_text.width(),
				"opacity_stroke": opacity_stroke,
				"font_size": font_size,
				"font_family": font_family,
				"text": self.document.toPlainText(),
				"text_run": self.text_run,
				"speed_text": self.timer.interval(),
				"lock": self.locked,
				"z_index": self.zValue(),
			}}
