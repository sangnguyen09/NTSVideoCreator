import uuid

from PySide6.QtCore import QPointF, QPoint, Slot, Qt
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QGraphicsItem, QMenu, QGraphicsPixmapItem

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import SELECTION_AREA_BLUR_CHANGED
from gui.widgets.py_dialogs import PyDialogGraphicMedia
from gui.widgets.py_dialogs.py_dialog_graphic_background_main import PyDialogGraphicBackgroundMain
from gui.widgets.py_graphics.py_resize_item import Resizer


class BackgroundVideoMainItemLayer(QGraphicsPixmapItem):
    def __init__(self, manage_thread_pool, pixmap,layers ,configCurrent):
        super().__init__()

        self.id_layer = uuid.uuid4().__str__()
        self.manage_thread_pool = manage_thread_pool
        self.layers = layers
        self.configCurrent = configCurrent

        # self.scene = scene
        # self._frame_blur =_frame_blur
        # self._rectblur_area =_rectblur_area

        self.setPixmap(pixmap)
        self.locked = False
        self.pixmap_ori = pixmap
        # print(self.pixmap)
        # self.mousePressPos = None
        # self.mousePressRect = None
        self.setAcceptHoverEvents(True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        # self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

        self.setPos(QPoint(0,0))
        # Resizer actions
        # self.resizer = Resizer(self.manage_thread_pool, parent=self)
        # self.center_pos_resizer = 12
        # r_width = self.resizer.boundingRect().width() - self.center_pos_resizer
        # self.r_offset = QPointF(r_width, r_width)
        # self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)
        # self.resizer.resizeSignal.connect(self.resizeSignal)
        # self.keyboard_offset = 1


    def hoverMoveEvent(self, event):
        if self.locked is True:
            return
        # if self.isSelected():
        #     self.resizer.show()
        # else:
        #     self.resizer.hide()

    # def itemChange(self, change, value):
    #     if change == QGraphicsItem.GraphicsItemChange.ItemZValueHasChanged or change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
    #         self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_BLUR_CHANGED,
    #                                                    SELECTION_AREA_BLUR_CHANGED,"")
    #     return super(BackgroundVideoMainItemLayer, self).itemChange(change, value)

    def hoverLeave(self, event):
        if self.locked is True:
            return
        self.resizer.hide()

    @Slot()
    def resizeSignal(self, change, value):
        if self.locked is False:
            print(111)
            # self._scale = int(value.x()) + self.center_pos_resizer, int(value.y() + self.center_pos_resizer)
            # # print(112)
            # pixmap = self.pixmap_.scaled(*self._scale)
            # # print(113)
            #
            # self.setPixmap(pixmap)
            # self.prepareGeometryChange()
            # self.update()
            # self.manage_thread_pool.resultChanged.emit(SELECTION_AREA_BLUR_CHANGED,
            #                                            SELECTION_AREA_BLUR_CHANGED,"")
            # self.resizer.setPos(self.boundingRect().bottomRight() - self.r_offset)

    def contextMenuEvent(self, event):
            print(self.isSelected())
            self.setSelected(True)

            if self.isSelected() is True:
                menu = QMenu()

                action_setting = menu.addAction(QIcon(ConfigResource.set_svg_icon("settings.svg")), "Cài Đặt")
                action = menu.exec(event.screenPos())

                if action == action_setting:
                    pixmap = self.pixmap_ori
                    if hasattr(self, "_scale"):
                        pixmap = self.pixmap_ori.scaled(*self._scale)
                    rect = pixmap.rect()
                    dialog = PyDialogGraphicBackgroundMain(self.manage_thread_pool)
                    dialog.loadData( self.configCurrent)

                    if dialog.exec():
                        pass
                        # new_value = dialog.getValue()
                        # if not new_value['pixmap'] == "":
                        #     self.pixmap_ori = QPixmap(new_value['pixmap'])
                        #     pixmap = self.pixmap_ori
                        #     if hasattr(self, "_scale"):
                        #         pixmap = self.pixmap_ori.scaled(*self._scale)
                        #
                        #     self.setPixmap(pixmap)
                    else:
                        print("Cancel!")



    def itemToVariant(self):

        return {
            "type": "BackgroundVideoMainItemLayer",
            "value": {
                # "scale": self._scale if hasattr(self, "_scale") is True else '',
                "pixmap": self.pixmap_ori,

            }}
