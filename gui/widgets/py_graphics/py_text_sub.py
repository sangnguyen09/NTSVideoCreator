import uuid

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QBrush, QPen, QTextDocument, QTextCharFormat, QFont, QColor, QTextCursor
from PySide6.QtWidgets import QGraphicsItem, QMenu, QGraphicsTextItem

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import STATUS_BUTTON_SAVE_CONFIG_CHANGED, POSITION_SUB_ORIGINAL_CHANGED, \
	POSITION_SUB_CHANGED, CENTER_POSITION_SUB, POSITION_ADD_SUB_CHANGED, CENTER_POSITION_ADD_SUB
from gui.widgets.py_dialogs.py_dialog_graphic_config_add_sub import PyDialogGraphicConfigAddSub


class TextSubLayer(QGraphicsTextItem):
	def __init__ (self, manage_thread_pool, item_text, document: QTextDocument, list_fonts, configCurrent, locked=False):
		super().__init__()
		
		self.id_layer = uuid.uuid4().__str__()
		self.manage_thread_pool = manage_thread_pool
		self.locked = locked
		self.list_fonts = list_fonts
		self.configCurrent = configCurrent
		self.item_text = item_text
		
		self.is_dragging = False
		# self.mousePressPos = None
		# self.mousePressRect = None
		self.rectbox = None
		self.setAcceptHoverEvents(True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
		if locked is False:
			self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
			self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
		
		self.setDocument(document)
		
		self.pos_y_old = self.pos().y()
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
	
	
	def mouseReleaseEvent (self, event):
		if self.is_dragging is True:
			# print("mouseReleaseEvent")
			# print(self.boundingRect().topLeft().x())
			# print(self.pos())
			# print(self.rea())
			x = self.pos().x()
			y = self.pos().y() + self.boundingRect().height()
			# print(x, y)
			# print(self.boundingRect())
			
			# print(self.rectbox.boundingRect())
			# print(self.rectbox)
			# print(self.scene().width())
			self.manage_thread_pool.resultChanged.emit(POSITION_ADD_SUB_CHANGED, POSITION_ADD_SUB_CHANGED, (x, y))
			
			self.is_dragging = False
		super().mouseReleaseEvent(event)
	
	
	def itemChange (self, change, value):
		if change == QGraphicsItem.GraphicsItemChange.ItemZValueHasChanged:
			self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				False)
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
			# pass
			# if self.text_run is False:
			# print(self.type_sub)
			self.is_dragging = True
			if self.rectbox is not None:
				self.rectbox.setPos(self.pos())
		
		# if hasattr(self,"pos_y_old") and not self.pos_y_old == self.pos().y():
		#     self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
		#                                                STATUS_BUTTON_SAVE_CONFIG_CHANGED,
		#                                                False)
		#     self.pos_y_old = self.pos().y()
		
		return super(TextSubLayer, self).itemChange(change, value)
	
	def reconnect (self):  # không xoá được
		pass
	
	def width (self):
		return self.boundingRect().width()
	
	def contextMenuEvent (self, event):
		# if self.locked is False:
		
		if self.isSelected() is True:
			menu = QMenu()
			
			action_setting = menu.addAction(QIcon(ConfigResource.set_svg_icon("settings.svg")), "Setting")
			
			action_center_pos = menu.addAction("")
			action_center_pos.setIcon(QIcon(ConfigResource.set_svg_icon("center.png")))
			action_center_pos.setText("Center Position")
			
			# action_lock = menu.addAction("")
			# action_lock.setIcon(QIcon(ConfigResource.set_svg_icon("lock.png")))
			# action_lock.setText("Lock")
			# action_setting = menu.addAction(QIcon(ConfigResource.set_svg_icon("settings.svg")), "Cài Đặt")
			
			action = menu.exec(event.screenPos())
			
			# if action == action_lock:
			# 	flag: QGraphicsItem.GraphicsItemFlag = self.flags()
			#
			# 	if flag & QGraphicsItem.GraphicsItemFlag.ItemIsMovable:
			# 		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
			# 		self.locked = True
			if action == action_setting:
				
				dialog_settings = PyDialogGraphicConfigAddSub(self.list_fonts, self.manage_thread_pool)
				dialog_settings.loadData(self.configCurrent)
				
				if dialog_settings.exec():
					new_value = dialog_settings.getValue()
				# print(new_value)
				# self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				# 	STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				# 	False)
				else:
					print('cancell')
					
			if action == action_center_pos:
				x = self.scene().width() / 2
				y = self.pos().y() + self.boundingRect().height() / 2
				self.manage_thread_pool.resultChanged.emit(CENTER_POSITION_ADD_SUB,CENTER_POSITION_ADD_SUB,(x, y))
	
	#
	# else:
	# 	self.setSelected(True)
	# 	if self.isSelected() is True:
	# 		menu = QMenu()
	# 		action_unlock = menu.addAction("")
	# 		action_unlock.setIcon(QIcon(ConfigResource.set_svg_icon("unlock.png")))
	# 		action_unlock.setText("Unlock")
	# 		action = menu.exec(event.screenPos())
	# 		if action == action_unlock:
	# 			self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
	# 			self.locked = False
	
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
		
		return {
			"type": "TextSubLayer",
			"value": {
				"x": self.pos().x(),
				"y": self.pos().y(),
				# "color_text": color_text_hex,
				# "opacity_text": opacity_text,
				# "them_stroke": them_stroke,
				# "color_stroke": color_stroke,
				# "do_day_stroke": stroke_text.width(),
				# "opacity_stroke": opacity_stroke,
				# "font_size": font_size,
				# "font_family": font_family,
				# "text": self.document.toPlainText(),
				# "text_run": self.text_run,
				# "speed_text": self.timer.interval(),
				# "lock": self.locked,
			}}
