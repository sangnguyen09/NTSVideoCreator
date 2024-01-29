import random
import uuid

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QIcon, QColor, QBrush, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsItem, QMenu

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import STATUS_BUTTON_SAVE_CONFIG_CHANGED
from gui.widgets.py_dialogs import PyDialogGraphicRectangle
from gui.widgets.py_graphics.py_resize_item import Resizer


class RectangleItemLayer(QGraphicsRectItem):
	def __init__ (self, manage_thread_pool, rect: QRectF, pos: QPointF, layers: list, scene: QGraphicsScene, locked=False):
		super().__init__()
		
		self.id_layer = uuid.uuid4().__str__()
		self.manage_thread_pool = manage_thread_pool
		self.layers = layers
		self.scene = scene
		self.locked = locked
		
		self.mousePressPos = None
		self.mousePressRect = None
		self.setAcceptHoverEvents(True)
		
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
		
		self.setRect(rect)
		
		self.setPos(pos)
		self.setBrush(QBrush(QColor(random.randrange(0, 255), random.randrange(0, 255), random.randrange(0, 255), a=255)))
		# self.setPen(QPen(QColor(0, 0, 0), 3.4, Qt.SolidLine))
		self.setPen(QPen(Qt.PenStyle.NoPen))
		
		# Resizer actions
		self.resizer = Resizer(self.manage_thread_pool, parent=self)
		self.center_pos_resizer = 12
		r_width = self.resizer.boundingRect().width() - self.center_pos_resizer
		self.r_offset = QPointF(r_width, r_width)
		self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
		self.resizer.resizeSignal.connect(self.resize)
		self.keyboard_offset =1
	
	def reconnect (self):
		self.resizer.resizeSignal.connect(self.resize)
	
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
		# self.prepareGeometryChange()
		# if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
		#     print(change)
		# if change == QGraphicsItem.GraphicsItemChange.ItemSceneHasChanged:
		#     print(change)
		# if change == QGraphicsItem.GraphicsItemChange.ItemEnabledHasChanged:
		#     print(change)
		# if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
		#     print(change)
		# if change == QGraphicsItem.GraphicsItemChange.ItemTransformHasChanged:
		#     print(change)
		# if change == QGraphicsItem.GraphicsItemChange.ItemScaleHasChanged:
		#     print(change)
		if change == QGraphicsItem.GraphicsItemChange.ItemZValueHasChanged or change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
			self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				False)
		return super(RectangleItemLayer, self).itemChange(change, value)
	
	def resize (self, change, value):
		self.setRect(QRectF(self.rect().x(), self.rect().x(), int(value.x()) + self.center_pos_resizer,
			int(value.y() + self.center_pos_resizer)))
		self.prepareGeometryChange()
		# print(self.pos()) vi tri của layer
		self.update()
	
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
				
				# index = self.layers.index({self.id_layer: self}) cách 1
				index = int(self.zValue() - 1)  # cách 2 -1 vì luc đầu +1
				
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
						self.resizer.hide()
				
				if action == action_setting:
					dialog = PyDialogGraphicRectangle()
					
					rgb_nen = [self.brush().color().red(), self.brush().color().green(), self.brush().color().blue()]
					rgb_stroke = [self.pen().color().red(), self.pen().color().green(), self.pen().color().blue()]
					color_nen = '#' + ''.join(
						[hex(v)[2:].ljust(2, '0') for v in rgb_nen]
					)
					color_stroke = '#' + ''.join(
						[hex(v)[2:].ljust(2, '0') for v in rgb_stroke]
					)
					opacity_nen = self.brush().color().alphaF() * 100
					
					them_stroke = False
					if self.pen().style().name == "SolidLine":
						them_stroke = True
					do_day_stroke = self.pen().width()
					opacity_stroke = self.pen().color().alphaF() * 100
					value = {
						"x": self.pos().x(),
						"y": self.pos().y(),
						"width": self.rect().width(),
						"height": self.rect().height(),
						"color_nen": color_nen,
						"opacity_nen": opacity_nen,
						"them_stroke": them_stroke,
						"color_stroke": color_stroke,
						"do_day_stroke": do_day_stroke,
						"opacity_stroke": opacity_stroke
					}
					dialog.loadData(value)
					if dialog.exec():
						new_value = dialog.getValue()
						
						self.setPos(QPointF(new_value["x"], new_value["y"]))
						self.setRect(QRectF(0, 0, new_value["width"], new_value["height"], ))
						self.setBrush(new_value["brush"])
						if new_value['pen'] is not False:
							self.setPen(new_value['pen'])
						else:
							self.setPen(QPen(Qt.PenStyle.NoPen))
						self.prepareGeometryChange()
						self.update()
						self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
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
		it = RectangleItemLayer(self.manage_thread_pool, self.rect(), pos.toPoint(), self.layers, self.scene)
		it.setFlags(self.flags())
		it.setOpacity(self.opacity())
		it.setRotation(self.rotation())
		it.setScale(self.scale())
		it.setPen(self.pen())
		it.setBrush(self.brush())
		self.addItemToScene(it)
		
		return it
	
	def itemToVariant (self):
		rgb_nen = [self.brush().color().red(), self.brush().color().green(), self.brush().color().blue()]
		rgb_stroke = [self.pen().color().red(), self.pen().color().green(), self.pen().color().blue()]
		color_nen = '#' + ''.join(
			[hex(v)[2:].ljust(2, '0') for v in rgb_nen]
		)
		color_stroke = '#' + ''.join(
			[hex(v)[2:].ljust(2, '0') for v in rgb_stroke]
		)
		opacity_nen = self.brush().color().alphaF() * 100
		
		them_stroke = False
		if self.pen().style().name == "SolidLine":
			them_stroke = True
		do_day_stroke = self.pen().width()
		opacity_stroke = self.pen().color().alphaF() * 100
		
		return {
			"type": "RectangleItemLayer",
			"value": {
				"x": self.pos().x(),
				"y": self.pos().y(),
				"width": self.rect().width(),
				"height": self.rect().height(),
				"color_nen": color_nen,
				"opacity_nen": opacity_nen,
				"them_stroke": them_stroke,
				"color_stroke": color_stroke,
				"do_day_stroke": do_day_stroke,
				"opacity_stroke": opacity_stroke,
				"lock": self.locked,
				"z_index": self.zValue()
			}
		}
