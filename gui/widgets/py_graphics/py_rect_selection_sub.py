import uuid

from PySide6.QtCore import QRectF, QPointF, Qt
from PySide6.QtGui import QIcon, QColor, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsScene, QGraphicsItem, QMenu

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import SELECTION_AREA_SUB_CHANGED
from gui.widgets.py_dialogs.py_dialog_graphic_rect_blur import PyDialogGraphicRectBlur
from gui.widgets.py_graphics.py_resize_item import Resizer


class RectSelectionSubItemLayer(QGraphicsRectItem):
    def __init__(self,manage_thread_pool, rect: QRectF, pos: QPointF, layers: list, scene: QGraphicsScene, locked= False):
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
        # self.setBrush(QBrush(QColor("#ffffff")))
        # self.setPen(QPen(QColor(0, 0, 0), 3.4, Qt.SolidLine))

        self.setPen(QPen(QColor("#17ff53"), 3))

        # Resizer actions
        self.resizer = Resizer(self.manage_thread_pool,parent=self,scene=scene)
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
            
    def reconnect(self):
        self.resizer.resizeSignal.connect(self.resize)

    def hoverMoveEvent(self, event):
        if self.locked is True:
            return

        if self.isSelected():

            self.resizer.show()

        else:
            self.resizer.hide()

    def hoverLeave(self, event):
        if self.locked is True:
            return
        self.resizer.hide()

    def itemChange(self, change, value):
        
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            if value.x() <= 0:
                self.setX(0)
    
            if value.y() <= 0:
                self.setY(0)
            if value.x() + self.rect().width() >= self.scene.sceneRect().width():
                self.setX(self.scene.sceneRect().width() - self.rect().width())
    
            if value.y() + self.rect().height() >= self.scene.sceneRect().height():
                self.setY(self.scene.sceneRect().height() - self.rect().height())
                
            self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_SUB_CHANGED,
                                                       SELECTION_AREA_SUB_CHANGED,
                                                       "")
        return super(RectSelectionSubItemLayer, self).itemChange(change, value)

    def resize(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
            self.setRect(QRectF(self.rect().x(), self.rect().y(), int(value.x()) + self.center_pos_resizer,
                int(value.y() + self.center_pos_resizer)))
            
        self.prepareGeometryChange()
        # print(self.pos()) vi tri của layer
        self.update()
        self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_SUB_CHANGED,
                                                   SELECTION_AREA_SUB_CHANGED,
                                                   "")

    def contextMenuEvent(self, event):
        if self.locked is False:

            if self.isSelected() is True:
                menu = QMenu()

                action_lock = menu.addAction("")
                action_lock.setIcon(QIcon(ConfigResource.set_svg_icon("lock.png")))
                action_lock.setText("Khoá")

                action_setting = menu.addAction(QIcon(ConfigResource.set_svg_icon("settings.svg")), "Cài Đặt")
                action = menu.exec(event.screenPos())

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

                    }
                    dialog.loadData(value)
                    if dialog.exec():
                        new_value = dialog.getValue()

                        self.setPos(QPointF(new_value["x"], new_value["y"]))
                        self.setRect(QRectF(0, 0, new_value["width"], new_value["height"], ))

                        self.prepareGeometryChange()
                        self.update()
                        self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)

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


    def addItemToScene(self):
        self.setZValue(1000)
        self.scene.addItem(self)

    def itemToVariant(self):

        return {
            "type": "RectSelectionSubItemLayer",
            "value": {
                "x": self.pos().x(),
                "y": self.pos().y(),
                "width": self.rect().width(),
                "height": self.rect().height(),

                "lock": self.locked,
            }
        }

