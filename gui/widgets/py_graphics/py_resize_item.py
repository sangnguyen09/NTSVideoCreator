from PySide6.QtCore import Qt, QRect, Signal, QPointF
from PySide6.QtGui import QColor, QBrush, QPen, QPainter
from PySide6.QtWidgets import QGraphicsItem, QGraphicsObject

from gui.helpers.constants import STATUS_BUTTON_SAVE_CONFIG_CHANGED


class Resizer(QGraphicsObject):
	resizeSignal = Signal(QGraphicsItem.GraphicsItemChange, QPointF)
	
	def __init__ (self, manage_thread_pool, rect=QRect(0, 0, 20, 20), parent=None, scene=None):
		super().__init__(parent)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
		self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
		self.setCursor(Qt.CursorShape.SizeFDiagCursor)
		self.manage_thread_pool = manage_thread_pool
		self.rect = rect
		self.scene = scene
		self.parent = parent
		self.hide()
	
	def boundingRect (self):
		return self.rect
	
	def paint (self, painter, option, widget=None):
		
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)
		painter.setBrush(QBrush(QColor(255, 0, 0, 255)))
		
		painter.setPen(
			QPen(QColor("#ffffff"), 1.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
		
		painter.drawEllipse(self.rect)
	
	# self.update()
	
	def itemChange (self, change, value):
		self.prepareGeometryChange()
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
			self.manage_thread_pool.resultChanged.emit(STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				STATUS_BUTTON_SAVE_CONFIG_CHANGED,
				False)
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
			if self.isSelected():
				
				if self.scene is not None:

					if value.x() + self.parent.center_pos_resizer > self.scene.sceneRect().width() - self.parent.x():
						return super(Resizer, self).itemChange(change, self.parent.boundingRect().bottomRight() - self.parent.r_offset)
					if value.y() + self.parent.center_pos_resizer > self.scene.sceneRect().height() - self.parent.y():
						return super(Resizer, self).itemChange(change, self.parent.boundingRect().bottomRight() - self.parent.r_offset)
				if value.x() < 0:
					return super(Resizer, self).itemChange(change, self.parent.boundingRect().bottomRight() - self.parent.r_offset)
				
				if value.y() < 0:
					return super(Resizer, self).itemChange(change, self.parent.boundingRect().bottomRight() - self.parent.r_offset)
				
				self.resizeSignal.emit(change, self.pos())
				return super(Resizer, self).itemChange(change, value)
		
		return super(Resizer, self).itemChange(change, value)
	
	'''END CLASS'''
