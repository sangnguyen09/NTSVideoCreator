import uuid

from PySide6.QtCore import QPointF, QPoint, Slot, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QGraphicsItem, QMenu, QGraphicsPixmapItem

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import SELECTION_AREA_BLUR_CHANGED
from gui.widgets.py_dialogs import PyDialogGraphicMedia
from gui.widgets.py_graphics.py_resize_item import Resizer


class FrameVideoMainItemLayer(QGraphicsPixmapItem):
    def __init__(self, manage_thread_pool, pixmap,layers,  _frame_blur,_rectblur_area):
        super().__init__()

        self.id_layer = uuid.uuid4().__str__()
        self.manage_thread_pool = manage_thread_pool
        self.layers = layers
        # self.scene = scene
        self._frame_blur =_frame_blur
        self._rectblur_area =_rectblur_area

        self.setPixmap(pixmap)
        self.locked = False
        self.pixmap_ = pixmap
        # print(self.pixmap)
        # self.mousePressPos = None
        # self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

        self.setPos(QPoint(0,0))
        # Resizer actions
        self.resizer = Resizer(self.manage_thread_pool, parent=self)
        self.center_pos_resizer = 12
        r_width = self.resizer.boundingRect().width() - self.center_pos_resizer
        self.r_offset = QPointF(r_width, r_width)
        self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
        self.resizer.resizeSignal.connect(self.resizeSignal)
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

    def hoverMoveEvent(self, event):
        if self.locked is True:
            return
        if self.isSelected():
            self.resizer.show()
        else:
            self.resizer.hide()

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemZValueHasChanged or change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_BLUR_CHANGED,
                                                       SELECTION_AREA_BLUR_CHANGED,"")
        return super(FrameVideoMainItemLayer, self).itemChange(change, value)

    def hoverLeave(self, event):
        if self.locked is True:
            return
        self.resizer.hide()

    @Slot()
    def resizeSignal(self, change, value):
        if self.locked is False:
            # print(111)
            self._scale = int(value.x()) + self.center_pos_resizer, int(value.y() + self.center_pos_resizer)
            # print(112)
            pixmap = self.pixmap_.scaled(*self._scale)
            # print(113)

            self.setPixmap(pixmap)
            self.prepareGeometryChange()
            self.update()
            self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_BLUR_CHANGED,
                                                       SELECTION_AREA_BLUR_CHANGED,"")
            # self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)

    def contextMenuEvent(self, event):
        if self.locked is False:

            if self.isSelected() is True:
                menu = QMenu()

                action_lock = menu.addAction("")
                action_lock.setIcon(QIcon(ConfigResource.set_svg_icon("lock.png")))
                action_lock.setText("Khoá")
                
                action_up = menu.addAction(QIcon(ConfigResource.set_svg_icon("up-arrow.png")), "Lên 1 Lớp")
                action_top = menu.addAction(QIcon(ConfigResource.set_svg_icon("top-arrow.png")), "Lên trên cùng")
                action_down = menu.addAction(QIcon(ConfigResource.set_svg_icon("down-arrow.png")), "Xuống 1 Lớp")
                action_bottom = menu.addAction(QIcon(ConfigResource.set_svg_icon("bottom-arrow.png")),
                                               "Xuống dưới cùng")

                action_setting = menu.addAction(QIcon(ConfigResource.set_svg_icon("settings.svg")), "Cài Đặt")
                action = menu.exec(event.screenPos())

                # index = self.layers.index({self.id_layer: self}) cách 1
                index = int(self.zValue() - 1)  # cách 2 -1 vì luc đầu +1

                # print(index)
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
                    pixmap = self.pixmap_
                    if hasattr(self, "_scale"):
                        pixmap = self.pixmap_.scaled(*self._scale)
                    rect = pixmap.rect()
                    dialog = PyDialogGraphicMedia(True)
                    dialog.loadData(self.pos().x(), self.pos().y(), rect.width(), rect.height())

                    if dialog.exec():
                        new_value = dialog.getValue()
                        self.setPos(QPointF(new_value["x"], new_value["y"]))
                        self._scale = new_value["width"], new_value["height"]
                        pixmap = self.pixmap_.scaled(*self._scale)
                        self.setPixmap(pixmap)
                        self.prepareGeometryChange()
                        self.update()
                        self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
                        if not new_value['pixmap'] == "":
                            self.pixmap_ = QPixmap(new_value['pixmap'])
                            pixmap = self.pixmap_
                            if hasattr(self, "_scale"):
                                pixmap = self.pixmap_.scaled(*self._scale)

                            self.setPixmap(pixmap)
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

    def refeshZValue(self):
        try:
            for idx, layer in enumerate(self.layers):
                item = list(layer.values())[0]
                item.setZValue(idx + 1)
    
            if not self._rectblur_area is None and not self._frame_blur is None:
                self._frame_blur.setZValue(self.zValue()+0.5)
                self._rectblur_area.setZValue(self.zValue()+0.5)
                # print(self._rectblur_area.zValue())
        except:
            pass

    # def addItemToScene(self):
    #     self.scene.addItem(self)
    #     self.layers.insert(0, {self.id_layer: self})
    #     self.refeshZValue()


    # def reconnect(self):
    #     self.resizer.resizeSignal.connect(self.resize)

    def itemToVariant(self):

        return {
            "type": "FrameVideoMainItemLayer",
            "value": {
                # "scale": self._scale if hasattr(self, "_scale") is True else '',
                # "pixmap": self.pixmap_,
                # "width_scene": self.scene().width(),
                # "height_scene": self.scene().height(),
                "x": self.pos().x(),
                "y": self.pos().y(),
                "width": self.pixmap_.rect().width() if hasattr(self, "_scale") is False else self._scale[0],
                "height": self.pixmap_.rect().height() if hasattr(self, "_scale") is False else self._scale[1],
                # "lock": self.locked,
            }}
