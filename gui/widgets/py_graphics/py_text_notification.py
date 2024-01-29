import uuid

from PySide6.QtCore import Qt, QPointF, QTimer
from PySide6.QtGui import QFont, QColor, QBrush, QPen, QTextDocument, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsTextItem


class TextNotificationLayer(QGraphicsTextItem):
	def __init__ (self, manage_thread_pool, _text: str, pos: QPointF, scene: QGraphicsScene):
		super().__init__()
		
		self.id_layer = uuid.uuid4().__str__()
		self.manage_thread_pool = manage_thread_pool
		
		self.scene = scene
		
		self.mousePressPos = None
		self.mousePressRect = None
		self.setAcceptHoverEvents(True)
 
		
		self.setPos(pos)
		self.speed_text = 0
		self.text = _text
		self.document = QTextDocument()
		self.charFormat = QTextCharFormat()
		self.font = QFont()
		self.font.setFamily("Roboto")
		self.font.setPixelSize(20)
		self.font.setBold(True)
		self.font.setWeight(QFont.Weight.Black)
		
		self.color_text = QColor("#ffffff")
		
		self.charFormat.setFont(self.font)  # font chữ
		self.charFormat.setForeground(QBrush(self.color_text))  # set màu của chữ
		self.charFormat.setTextOutline(QPen(Qt.PenStyle.NoPen))  # viền chữ
		
		self.cursor = QTextCursor(self.document)
		self.cursor.insertText(self.text, self.charFormat)
		
		self.setDocument(self.document)
		
		self.timer_run_text = QTimer()
		self.timer_run_text.timeout.connect(self._run_text)
		self.timer_run_text.start(15)  # 5 nhanh 15 trung bình 25 chậm
		self.pos_y_old = self.pos().y()
	
	def itemChange (self, change, value):
		if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
			
			if hasattr(self, "pos_y_old") and not self.pos_y_old == self.pos().y():
				self.pos_y_old = self.pos().y()
		
		return super(TextNotificationLayer, self).itemChange(change, value)
	
	def reconnect (self):  # không xoá được
		pass
	
	def _run_text (self):
		
		wt = int(self.boundingRect().width())
		sreen_width = int(self.scene.width())
		x = int(self.pos().x())
		x_new = x - 1
		if x_new <= -wt:
			x_new = sreen_width
		
		self.setPos(float(x_new), float(self.pos().y()))
