import uuid

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem, QMenu, QGraphicsPixmapItem

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import STATUS_BUTTON_SAVE_CONFIG_CHANGED
from gui.widgets.py_dialogs import PyDialogGraphicMedia
from gui.widgets.py_graphics.py_resize_item import Resizer


class MediaItemLayer(QGraphicsPixmapItem):
	def __init__ (self, manage_thread_pool, pixmap: QPixmap, pos, layers: list, scene: QGraphicsScene,
				  main_video=False, locked=False):
		super().__init__()
		self.id_layer = uuid.uuid4().__str__()
		self.manage_thread_pool = manage_thread_pool
		self.layers = layers
		self.scene = scene
		self.locked = locked
		self.main_video = main_video  # video gốc
		
		self.setPixmap(pixmap)
		self.pixmap_ori = pixmap
		self.mousePressPos = None
		self.mousePressRect = None
		self.setAcceptHoverEvents(True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
		
		self.setPos(pos)
		
		# Resizer actions
		self.resizer = Resizer(self.manage_thread_pool, parent=self)
		self.center_pos_resizer = 12
		r_width = self.resizer.boundingRect().width() - self.center_pos_resizer
		self.r_offset = QPointF(r_width, r_width)
		self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
		self.resizer.resizeSignal.connect(self.resizeSignal)
		self.keyboard_offset =1
	
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
	
	def itemChange (self, change, value):
		if change == QGraphicsItem.GraphicsItemChange.ItemZValueHasChanged or change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
			self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				False)
		return super(MediaItemLayer, self).itemChange(change, value)
	
	def hoverLeave (self, event):
		if self.locked is True:
			return
		self.resizer.hide()
	
	# @pyqtSlot()
	def resizeSignal (self, change, value):
		if self.locked is False:
			_scale = int(value.x()) + self.center_pos_resizer, int(value.y() + self.center_pos_resizer)
			
			pixmap = self.pixmap_ori.copy()
			# print("Resizing",_scale)
			self.setPixmap(pixmap.scaled(*_scale))
			self.prepareGeometryChange()
			self.update()
			# self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
	
	def contextMenuEvent (self, event):
		if self.locked is False:
			
			if self.isSelected() is True:
				menu = QMenu()
				action_delete = None
				action_clone = None
				if self.main_video is False:
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
				
				if action == action_delete and self.main_video is False:
					del self.layers[index]
					self.scene.removeItem(self)
					self.refeshZValue()  # cập nhật lại zvalue tưng layer để khi action up down thực hiện ko lỗi
					self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
						STATUS_BUTTON_SAVE_CONFIG_CHANGED,
						False)
				if action == action_clone and self.main_video is False:
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
					# pixmap = self.pixmap_ori.copy()
					# if hasattr(self, "_scale"):
					#     pixmap = pixmap.scaled(*self._scale)
					rect = self.pixmap().rect()
					dialog = PyDialogGraphicMedia(self.main_video)
					dialog.loadData(self.pos().x(), self.pos().y(), rect.width(), rect.height())
					
					if dialog.exec():
						new_value = dialog.getValue()
						self.setPos(QPointF(new_value["x"], new_value["y"]))
						_scale = new_value["width"], new_value["height"]
						pixmap = self.pixmap_ori.copy()
						pixmap = pixmap.scaled(*_scale)
						
						self.setPixmap(pixmap)
						self.prepareGeometryChange()
						self.update()
						if not new_value['pixmap'] == "":
							self.pixmap_ori = QPixmap(new_value['pixmap'])
							pixmap = self.pixmap_ori.copy()
							# if hasattr(self, "_scale"):
							#     pixmap = pixmap.scaled(*self._scale)
							
							self.setPixmap(pixmap)
							
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
		self.scene.addItem(item)
		
		if item.main_video is True:
			self.layers.insert(0, {item.id_layer: item})
			self.refeshZValue()
		else:
			zindex = len(self.layers) + 1
			item.setZValue(zindex)
			self.layers.append({item.id_layer: item})
	
	def clone (self, pos):
		pixmap = self.pixmap_ori.copy()
		w_o, h_o = pixmap.width(), pixmap.height()
		
		w_c, h_c = self.pixmap().width(), self.pixmap().height()
		
		it = MediaItemLayer(self.manage_thread_pool, pixmap, pos.toPoint(), self.layers, self.scene)
		
		if w_o != w_c or h_o != h_c:
			pixmap = pixmap.scaled(w_c, h_c)
			it.setPixmap(pixmap)
			it.resizer.setPos(it.boundingRect().bottomRight() - it.r_offset)
			
		it.setFlags(self.flags())
		it.setOpacity(self.opacity())
		it.setRotation(self.rotation())
		it.setScale(self.scale())
		
		self.addItemToScene(it)
		
		return it
	
	# def reconnect(self):
	#     self.resizer.resizeSignal.connect(self.resize)
	
	def itemToVariant (self):
		
		return {
			"type": "MediaItemLayer",
			"value": {
				# "scale": self._scale if hasattr(self, "_scale") is True else '',
				"pixmap": self.pixmap_ori,
				"main_video": self.main_video,
				"x": self.pos().x(),
				"y": self.pos().y(),
				"z_index":self.zValue(),
				"width": self.pixmap().rect().width(),
				"height": self.pixmap().rect().height(),
				# "width": self.pixmap_ori.rect().width() if hasattr(self, "_scale") is False else self._scale[0],
				# "height": self.pixmap_ori.rect().height() if hasattr(self, "_scale") is False else self._scale[1],
				"lock": self.locked,
			}}
