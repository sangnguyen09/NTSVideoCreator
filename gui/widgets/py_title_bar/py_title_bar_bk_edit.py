from PySide6 import QtGui
from PySide6.QtCore import Qt, Signal, QSize, QByteArray
from PySide6.QtGui import QCursor, QMouseEvent
from PySide6.QtWidgets import QWidget, QLabel, QFrame, QHBoxLayout, QVBoxLayout

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import NOTIFICATION_TOGGLE_CHANGED
from style import icon_logo
from .py_div import PyDiv
# IMPORT BUTTON
# ///////////////////////////////////////////////////////////////
from .py_title_button import PyTitleButton

# IMPORT QT CORE

# GLOBALS
# ///////////////////////////////////////////////////////////////
_is_maximized = False
_old_size = QSize()

# PY TITLE BAR
# Top bar with move application, maximize, restore, minimize,
# close buttons and extra buttons
# ///////////////////////////////////////////////////////////////
class PyTitleBar(QWidget):
    # SIGNALS
    clicked = Signal(object)
    released = Signal(object)

    def __init__(
        self,
        parent,
        app_parent,
        logo_image = "icon_logo.svg",
        logo_width = 50,
        buttons = None,
        dark_one = "#1b1e23",
        bg_color = "#343b48",
        div_color = "#3c4454",
        btn_bg_color = "#343b48",
        btn_bg_color_hover = "#3c4454",
        btn_bg_color_pressed = "#2c313c",
        icon_color = "#c3ccdf",
        icon_color_hover = "#dce1ec",
        icon_color_pressed = "#edf0f5",
        icon_color_active = "#f5f6f9",
        context_color = "#6c99f4",
        text_foreground = "#8a95aa",
        radius = 8,
        font_family = "Segoe UI",
        title_size = 10,
        is_custom_title_bar = True,
        is_notification = True,
    ):
        super().__init__()


        # PARAMETERS
        self._logo_image = logo_image
        self._dark_one = dark_one
        self._bg_color = bg_color
        self._div_color = div_color
        self._parent = parent
        self._app_parent = app_parent
        self._btn_bg_color = btn_bg_color
        self._btn_bg_color_hover = btn_bg_color_hover
        self._btn_bg_color_pressed = btn_bg_color_pressed  
        self._context_color = context_color
        self._icon_color = icon_color
        self._icon_color_hover = icon_color_hover
        self._icon_color_pressed = icon_color_pressed
        self._icon_color_active = icon_color_active
        self._font_family = font_family
        self._title_size = title_size
        self._text_foreground = text_foreground
        self._is_custom_title_bar = is_custom_title_bar
        self._is_notification =is_notification
        # SETUP UI
        self.setup_ui()
        if self._is_custom_title_bar is True:
            self.top_logo.mouseMoveEvent = self.moveWindow
            self.div_1.mouseMoveEvent = self.moveWindow
            self.title_label.mouseMoveEvent = self.moveWindow
            self.div_2.mouseMoveEvent = self.moveWindow
            self.div_3.mouseMoveEvent = self.moveWindow

        # ADD BG COLOR
        self.bg.setStyleSheet(f"background-color: {bg_color}")
        self.setProperty("class", "border_none")
        self.bg.setProperty("class", "border_none")
        # SET LOGO AND WIDTH
        # self.top_logo.setMinimumWidth(logo_width)
        # self.top_logo.setMaximumWidth(logo_width)

        # MOVE WINDOW / MAXIMIZE / RESTORE
        # ///////////////////////////////////////////////////////////////

        self.is_custom_title_bar =is_custom_title_bar

        # MAXIMIZE / RESTORE
        if is_custom_title_bar is True:
            self.top_logo.mouseDoubleClickEvent = self.maximize_restore
            self.div_1.mouseDoubleClickEvent = self.maximize_restore
            self.title_label.mouseDoubleClickEvent = self.maximize_restore
            self.div_2.mouseDoubleClickEvent = self.maximize_restore

        # ADD WIDGETS TO TITLE BAR
        # ///////////////////////////////////////////////////////////////
 
        self.top_logo.setMaximumWidth(30)
        # self.bg_layout.addWidget(self.top_logo,5)
        self.bg_layout.addWidget(self.div_1,1)
        self.bg_layout.addWidget(self.title_label,90)
        self.bg_layout.addWidget(self.div_2)

        # ADD BUTTONS BUTTONS
        # ///////////////////////////////////////////////////////////////
        # Functions
        self.notification_off_button.clicked.connect(lambda: self.notification_check(True))
        self.notification_on_button.clicked.connect(lambda: self.notification_check(False))
        self.minimize_button.released.connect(lambda: parent.showMinimized())
        self.maximize_restore_button.released.connect(lambda: self.maximize_restore())
        self.close_button.released.connect(lambda: parent.close())

        # Extra BTNs layout
        self.bg_layout.addLayout(self.custom_buttons_layout)

        # ADD Buttons
        if is_custom_title_bar:
            # self.bg_layout.addWidget(self.notification_on_button)
            # self.bg_layout.addWidget(self.notification_off_button)
            self.bg_layout.addWidget(self.minimize_button)
            self.bg_layout.addWidget(self.maximize_restore_button)
            self.bg_layout.addWidget(self.close_button)

    def notification_check(self, status):
        self._is_notification = status
        
        if self._is_notification is True:
            self.notification_on_button.show()
            self.notification_off_button.hide()
        else:
            self.notification_on_button.hide()
            self.notification_off_button.show()
            
        self._parent.thread_pool.resultChanged.emit(NOTIFICATION_TOGGLE_CHANGED,
            NOTIFICATION_TOGGLE_CHANGED,status)
        # self._parent.thread_pool.resu
    # ADD BUTTONS TO TITLE BAR
    # Add btns and emit signals
    # ///////////////////////////////////////////////////////////////
    def add_menus(self, parameters):
        if parameters != None and len(parameters) > 0:
            for parameter in parameters:
                _btn_icon = ConfigResource.set_svg_icon(parameter['btn_icon'])
                _btn_id = parameter['btn_id']
                _btn_tooltip = parameter['btn_tooltip']
                _is_active = parameter['is_active']

                self.menu = PyTitleButton(
                    self._parent,
                    self._app_parent,
                    btn_id = _btn_id,
                    tooltip_text = _btn_tooltip,
                    dark_one = self._dark_one,
                    bg_color = self._bg_color,
                    bg_color_hover = self._btn_bg_color_hover,
                    bg_color_pressed = self._btn_bg_color_pressed,
                    icon_color = self._icon_color,
                    icon_color_hover = self._icon_color_active,
                    icon_color_pressed = self._icon_color_pressed,
                    icon_color_active = self._icon_color_active,
                    context_color = self._context_color,
                    text_foreground = self._text_foreground,
                    icon_path = _btn_icon,
                    is_active = _is_active
                )
                self.menu.clicked.connect(self.btn_clicked)
                self.menu.released.connect(self.btn_released)

                # ADD TO LAYOUT
                self.custom_buttons_layout.addWidget(self.menu)

            # ADD DIV
            if self._is_custom_title_bar:
                self.custom_buttons_layout.addWidget(self.div_3)

    # TITLE BAR MENU EMIT SIGNALS
    # ///////////////////////////////////////////////////////////////
    def btn_clicked(self):
        self.clicked.emit(self.menu)
    
    def btn_released(self):
        self.released.emit(self.menu)

    # SET TITLE BAR TEXT
    # ///////////////////////////////////////////////////////////////
    def set_title(self, title):
        self.title_label.setText('EDIT MANGA')

    # MAXIMIZE / RESTORE
    # maximize and restore parent window
    # ///////////////////////////////////////////////////////////////
    def maximize_restore(self, e = None):
        global _is_maximized
        global _old_size
        
        # CHANGE UI AND RESIZE GRIP
        def change_ui():
            if _is_maximized:
                # self._parent.central_widget_layout.setContentsMargins(0,0,0,0)
                # self._parent.window.set_stylesheet(border_radius = 0, border_size = 0)
                self.maximize_restore_button.set_icon(
                    ConfigResource.set_svg_icon("icon_restore.svg")
                )
            else:
                # self._parent.central_widget_layout.setContentsMargins(10,10,10,10)
                # self._parent.window.set_stylesheet(border_radius = 10, border_size = 2)
                self.maximize_restore_button.set_icon(
                    ConfigResource.set_svg_icon("icon_maximize.svg")
                )

        # CHECK EVENT
        if self._parent.isMaximized():
            _is_maximized = False
            self._parent.showNormal()
            change_ui()
        else:
            _is_maximized = True
            _old_size = QSize(self._parent.width(), self._parent.height())
            self._parent.showMaximized()
            change_ui()

    # SETUP APP
    # ///////////////////////////////////////////////////////////////
    def setup_ui(self):
        # ADD MENU LAYOUT
        self.title_bar_layout = QVBoxLayout(self)
        self.title_bar_layout.setContentsMargins(0,0,0,0)

        # ADD BG
        self.bg = QFrame()

        # ADD BG LAYOUT
        self.bg_layout = QHBoxLayout(self.bg)
        self.bg_layout.setContentsMargins(10,0,5,0)
        self.bg_layout.setSpacing(0)



        # DIVS
        self.div_1 = PyDiv(self._div_color)
        self.div_2 = PyDiv(self._div_color)
        self.div_3 = PyDiv(self._div_color)

        # LEFT FRAME WITH MOVE APP pp
        self.top_logo = QLabel()
        self.top_logo_layout = QHBoxLayout(self.top_logo)
        self.top_logo_layout.setContentsMargins(0,0,0,0)
        self.logo_svg = QLabel()
        icon_dl = QtGui.QPixmap()
        icon_dl.loadFromData(QByteArray.fromBase64(icon_logo))
  
        self.logo_svg.setPixmap(icon_dl)
        self.top_logo_layout.addWidget(self.logo_svg)

        # TITLE LABEL
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.title_label.setStyleSheet(f'font: {self._title_size}pt "{self._font_family}"')

        # CUSTOM BUTTONS LAYOUT
        self.custom_buttons_layout = QHBoxLayout()
        self.custom_buttons_layout.setContentsMargins(0,0,0,0)
        self.custom_buttons_layout.setSpacing(3)

        # notification_on BUTTON
        self.notification_on_button = PyTitleButton(
            self._parent,
            self._app_parent,
            tooltip_text = "Bật Thông báo",
            dark_one = self._dark_one,
            bg_color = self._btn_bg_color,
            bg_color_hover = self._btn_bg_color_hover,
            bg_color_pressed = self._btn_bg_color_pressed,
            icon_color = self._icon_color,
            icon_color_hover = self._icon_color_hover,
            icon_color_pressed = self._icon_color_pressed,
            icon_color_active = self._icon_color_active,
            context_color = self._context_color,
            text_foreground = self._text_foreground,
            radius = 6,
            icon_path = ConfigResource.set_svg_icon("notification_on.svg")
        )
        # notification_on BUTTON
        self.notification_off_button = PyTitleButton(
            self._parent,
            self._app_parent,
            tooltip_text = "Tắt Thông báo",
            dark_one = self._dark_one,
            bg_color = self._btn_bg_color,
            bg_color_hover = self._btn_bg_color_hover,
            bg_color_pressed = self._btn_bg_color_pressed,
            icon_color = self._icon_color,
            icon_color_hover = self._icon_color_hover,
            icon_color_pressed = self._icon_color_pressed,
            icon_color_active = self._icon_color_active,
            context_color = self._context_color,
            text_foreground = self._text_foreground,
            radius = 6,
            icon_path = ConfigResource.set_svg_icon("notication_off.svg")
        )
        if self._is_notification:
            self.notification_off_button.hide()
        else:
            self.notification_on_button.hide()

        
        # MINIMIZE BUTTON
        self.minimize_button = PyTitleButton(
            self._parent,
            self._app_parent,
            tooltip_text = "Close app",
            dark_one = self._dark_one,
            bg_color = self._btn_bg_color,
            bg_color_hover = self._btn_bg_color_hover,
            bg_color_pressed = self._btn_bg_color_pressed,
            icon_color = self._icon_color,
            icon_color_hover = self._icon_color_hover,
            icon_color_pressed = self._icon_color_pressed,
            icon_color_active = self._icon_color_active,
            context_color = self._context_color,
            text_foreground = self._text_foreground,
            radius = 6,
            icon_path = ConfigResource.set_svg_icon("icon_minimize.svg")
        )

        # MAXIMIZE / RESTORE BUTTON
        self.maximize_restore_button = PyTitleButton(
            self._parent,
            self._app_parent,
            tooltip_text = "Maximize app",
            dark_one = self._dark_one,
            bg_color = self._btn_bg_color,
            bg_color_hover = self._btn_bg_color_hover,
            bg_color_pressed = self._btn_bg_color_pressed,
            icon_color = self._icon_color,
            icon_color_hover = self._icon_color_hover,
            icon_color_pressed = self._icon_color_pressed,
            icon_color_active = self._icon_color_active,
            context_color = self._context_color,
            text_foreground = self._text_foreground,
            radius = 6,
            icon_path = ConfigResource.set_svg_icon("icon_maximize.svg")
        )

        # CLOSE BUTTON
        self.close_button = PyTitleButton(
            self._parent,
            self._app_parent,
            tooltip_text = "Close app",
            dark_one = self._dark_one,
            bg_color = self._btn_bg_color,
            bg_color_hover = self._btn_bg_color_hover,
            bg_color_pressed = self._context_color,
            icon_color = self._icon_color,
            icon_color_hover = self._icon_color_hover,
            icon_color_pressed = self._icon_color_active,
            icon_color_active = self._icon_color_active,
            context_color = self._context_color,
            text_foreground = self._text_foreground,
            radius = 6,
            icon_path = ConfigResource.set_svg_icon("icon_close.svg")
        )

        # ADD TO LAYOUT
        self.title_bar_layout.addWidget(self.bg)
        
        
    def moveWindow(self, event: QMouseEvent):
        # IF MAXIMIZED CHANGE TO NORMAL
        if self._parent.isMaximized():
            self.maximize_restore()
            #self.resize(_old_size)
            curso_x = self._parent.pos().x()
            curso_y = event.globalPosition().y() - QCursor.pos().y()
            self._parent.move(curso_x, curso_y)

        # MOVE WINDOW
        if event.buttons() == Qt.MouseButton.LeftButton:
            # print(event.pos())
            self._parent.move(self._parent.pos() + event.scenePosition().toPoint() - self.dragPos)
            # self.dragPos = event.scenePosition().toPoint()
            # event.accept()
        else:
            super().mouseMoveEvent(event)
    def mousePressEvent(self, event):
        # SET DRAG POS WINDOW
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.dragPos = event.scenePosition().toPoint()
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragPos = None
        super().mouseReleaseEvent(event)


