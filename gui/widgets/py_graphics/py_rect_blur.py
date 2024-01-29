import uuid

from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QIcon, QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsItem, QMenu, QGraphicsPixmapItem

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import STATUS_BUTTON_SAVE_CONFIG_CHANGED, SELECTION_AREA_BLUR_CHANGED
from gui.widgets.py_dialogs.py_dialog_graphic_rect_blur import PyDialogGraphicRectBlur
from gui.widgets.py_graphics.py_resize_item import Resizer


class RectBlurItemLayer(QGraphicsRectItem):
	def __init__ (self, manage_thread_pool, rect: QRectF, pos: QPointF, list_blur: list, scene: QGraphicsScene, sigma=15, steps=1, locked=False):
		super().__init__()
		
		self.id_layer = uuid.uuid4().__str__()
		self.manage_thread_pool = manage_thread_pool
		self.list_blur = list_blur
		self.scene = scene
		self.locked = locked
		self.steps = steps
		self.sigma = sigma
		
		self.mousePressPos = None
		self.mousePressRect = None
		self.setAcceptHoverEvents(True)
		
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
		
		self.setRect(rect)
		
		self.setPos(pos)
		# self.setBrush(QBrush(QColor("#ffffff")))
		# self.setPen(QPen(QColor(0, 0, 0), 3.4, Qt.SolidLine))
		
		self.setPen(QPen(QColor("#17ff53"), 3))
		
		# Resizer actions
		self.resizer = Resizer(self.manage_thread_pool, parent=self, scene=self.scene)
		self.center_pos_resizer = 12
		r_width = self.resizer.boundingRect().width() - self.center_pos_resizer
		self.r_offset = QPointF(r_width, r_width)
		self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
		self.resizer.resizeSignal.connect(self.resize)
		self.keyboard_offset = 1
	
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
		
		elif e.key() == Qt.Key.Key_Delete:
			del self.list_blur[self.list_blur.index(self)]
			for item in self.scene.items():
				if item.zValue() == self.zValue() and isinstance(item, QGraphicsPixmapItem):
					self.scene.removeItem(item)
					self.scene.removeItem(self)
			self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				False)
	def reconnect (self):
		self.resizer.resizeSignal.connect(self.resize)
	
	def hoverMoveEvent (self, event):
		if self.locked is True:
			return
		
		if self.isSelected():
			
			self.resizer.show()
		
		else:
			self.resizer.hide()
	
	def hoverLeave (self, event):
		if self.locked is True:
			return
		self.resizer.hide()
	
	def itemChange (self, change, value):
		self.prepareGeometryChange()
		
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
			if value.x() <= 0:
				self.setX(0)
			
			if value.y() <= 0:
				self.setY(0)
			if value.x() + self.rect().width() >= self.scene.sceneRect().width():
				self.setX(self.scene.sceneRect().width() - self.rect().width())
			
			if value.y() + self.rect().height() >= self.scene.sceneRect().height():
				self.setY(self.scene.sceneRect().height() - self.rect().height())
			
			self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				False)
			self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_BLUR_CHANGED,
				SELECTION_AREA_BLUR_CHANGED, "")
		
		return super(RectBlurItemLayer, self).itemChange(change, value)
	
	def resize (self, change, value):
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
			self.setRect(QRectF(self.rect().x(), self.rect().y(), int(value.x()) + self.center_pos_resizer,
				int(value.y() + self.center_pos_resizer)))

		self.prepareGeometryChange()
		# print(self.pos()) vi tri của layer
		self.update()
		self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_BLUR_CHANGED,
			SELECTION_AREA_BLUR_CHANGED, "")
	
	def contextMenuEvent (self, event):
		if self.locked is False:
			
			if self.isSelected() is True:
				menu = QMenu()
				
				action_clone = menu.addAction(QIcon(ConfigResource.set_svg_icon("clone.png")), "Clone")
				# action_up = menu.addAction(QIcon(ConfigResource.set_svg_icon("up-arrow.png")), "Lên 1 Lớp")
				# action_top = menu.addAction(QIcon(ConfigResource.set_svg_icon("top-arrow.png")), "Lên trên cùng")
				# action_down = menu.addAction(QIcon(ConfigResource.set_svg_icon("down-arrow.png")), "Xuống 1 Lớp")
				# action_bottom = menu.addAction(QIcon(ConfigResource.set_svg_icon("bottom-arrow.png")),
				action_delete = menu.addAction(QIcon(ConfigResource.set_svg_icon("delete.png")),
					"Xoá")
				#                                "Xuống dưới cùng")
				action_lock = menu.addAction("")
				action_lock.setIcon(QIcon(ConfigResource.set_svg_icon("lock.png")))
				action_lock.setText("Khoá")
				
				action_setting = menu.addAction(QIcon(ConfigResource.set_svg_icon("settings.svg")), "Cài Đặt")
				action = menu.exec(event.screenPos())
				
				if action == action_delete:
					del self.list_blur[self.list_blur.index(self)]
					# print(self.zValue())
					
					for item in self.scene.items():
						# print(item)
						if item.zValue() == self.zValue() and isinstance(item, QGraphicsPixmapItem):
							self.scene.removeItem(item)
							self.scene.removeItem(self)

					# self.refeshZValue()  # cập nhật lại zvalue tưng layer để khi action up down thực hiện ko lỗi
					self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
						STATUS_BUTTON_SAVE_CONFIG_CHANGED,
						False)
					# print(self.list_blur)
				if action == action_clone:
					self.clone(event.scenePos())
					# self.refeshZValue()
				
				if action == action_lock:
					flag: QGraphicsItem.GraphicsItemFlag = self.flags()
					
					if flag & QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
						self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
						self.locked = True
						self.resizer.hide()
				
				if action == action_setting:
					dialog = PyDialogGraphicRectBlur()
					
					value = {
						"x": self.pos().x(),
						"y": self.pos().y(),
						"width": self.rect().width(),
						"height": self.rect().height(),
						"sigma": self.sigma,
						"steps": self.steps,
						
					}
					dialog.loadData(value)
					if dialog.exec():
						new_value = dialog.getValue()
						
						self.setPos(QPointF(new_value["x"], new_value["y"]))
						self.setRect(QRectF(0, 0, new_value["width"], new_value["height"], ))
						self.sigma = new_value["sigma"]
						self.steps = new_value["steps"]
						self.prepareGeometryChange()
						self.update()
						self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
						self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
							STATUS_BUTTON_SAVE_CONFIG_CHANGED,
							False)
						self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_BLUR_CHANGED,
							SELECTION_AREA_BLUR_CHANGED, "")
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
	
	def refeshZValue (self):
		for idx, layer in enumerate(self.list_blur):
			item = list(layer.values())[0]
			item.setZValue(idx + 1)
	
	def addItemToScene (self):
		# zindex = len(self.layers) + 1
		# self.setZValue(1000)
		self.scene.addItem(self)
	
	# self.layers.append({item.id_layer: item})
	def clone (self, pos):
		it = RectBlurItemLayer(self.manage_thread_pool, self.rect(), pos.toPoint(), self.list_blur, self.scene)
		it.setFlags(self.flags())
		it.setOpacity(self.opacity())
		it.setRotation(self.rotation())
		it.setScale(self.scale())
		it.setPen(self.pen())
		it.setBrush(self.brush())
		self.scene.addItem(it)
		it.setZValue(self.zValue()+0.1*(len(self.list_blur)+1))
		self.list_blur.append(it)
		
		return it
	def itemToVariant (self):
		
		return {
			"type": "RectBlurItemLayer",
			"value": {
				"x": self.pos().x(),
				"y": self.pos().y(),
				"width": self.rect().width(),
				"height": self.rect().height(),
				"sigma": self.sigma,
				"steps": self.steps,
				
				"lock": self.locked,
			}
		}
