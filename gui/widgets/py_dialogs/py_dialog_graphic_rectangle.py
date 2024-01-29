import os

from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog, \
    QColorDialog, QComboBox, \
    QSlider

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP, SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon

style = '''
QDialog {{
	background-color: {_bg_color};
	font-size:15px;
	font-weight:bold;
    
}}
QLabel{{
 color: {_color}
}}

'''


class PyDialogGraphicRectangle(QDialog):
    def __init__(self):
        super().__init__()
        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        st = QSettings(*SETTING_APP)
        self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
        # LOAD THEME COLOR
        # ///////////////////////////////////////////////////////////////
        self.themes = ConfigTheme()
        self.style_format = style.format(
            _bg_color=self.themes.app_color["bg_one"],
            _color=self.themes.app_color["white"],
        )
        self.app_path = os.path.abspath(os.getcwd())

        # SET UP MAIN WINDOW
        self.setWindowTitle("Tuỳ chỉnh thông số")
        self.setStyleSheet(self.style_format)

        # self.setMinimumHeight(self.settings.dialog_size[1])
        self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])

        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.groupbox = QGroupBox("Cài đặt")

        self.lb_x = QLabel("Vị trí x")
        self.input_x = QSpinBox()
        self.input_x.setMaximum(20000)

        self.lb_y = QLabel("Vị Trí y:")
        self.input_y = QSpinBox()
        self.input_y.setMaximum(20000)
        self.input_y.setMinimum(-20000)
        self.input_x.setMinimum(-20000)
        
        self.lb_width = QLabel("Chiều rộng:")
        self.input_width = QSpinBox()
        self.input_width.setMaximum(20000)

        self.lb_height = QLabel("Chiều cao:")
        self.input_height = QSpinBox()
        self.input_height.setMaximum(20000)

        self.lb_mau_nen = QLabel("Màu Nền:")
        self.btn_dialog_mau_nen = PyButtonIcon(
            icon_path=ConfigResource.set_svg_icon("color-picker.png"),
            parent=self,
            app_parent=self,
            icon_color="#f5ca1e",
            width=30,
            height=30,
            icon_color_hover="#ffe270",
            icon_color_pressed="#d1a807",

        )
        self.input_mau_nen = QLineEdit()
        self.color_picker_nen_chu = QColorDialog()

        self.lb_opacity_nen = QLabel("Opacity:")
        self.lb_opacity_nen_value_current = QLabel("")
        self.slider_mau_nen_opacity = QSlider()
        self.slider_mau_nen_opacity.setOrientation(Qt.Orientation.Horizontal)
        self.slider_mau_nen_opacity.setRange(1, 100)
        self.slider_mau_nen_opacity.setValue(100)
        self.lb_opacity_nen_value_current.setText(self.slider_mau_nen_opacity.value().__str__())

        self.groupbox_stroke = QGroupBox("Thêm Stroke:")
        self.groupbox_stroke.setCheckable(True)
        self.groupbox_stroke.setChecked(False)

        self.lb_stroke_color = QLabel("Màu:")
        self.btn_dialog_mau_vien = PyButtonIcon(
            icon_path=ConfigResource.set_svg_icon("color-picker.png"),
            parent=self,
            app_parent=self,
            icon_color="#f5ca1e",
            width=30,
            height=30,
            icon_color_hover="#ffe270",
            icon_color_pressed="#d1a807",

        )
        self.input_stroke_color = QLineEdit()
        self.color_picker_stroke = QColorDialog()

        self.lb_do_day_stroke = QLabel("Độ dày:")
        self.combobox_do_day_stroke = QComboBox()
        self.combobox_do_day_stroke.addItems([str(i) for i in range(1, 20)])
        self.lb_opacity_stroke = QLabel("Opacity:")
        self.lb_opacity_stroke_value_current = QLabel("")
        self.slider_mau_stroke_opacity = QSlider()
        self.slider_mau_stroke_opacity.setOrientation(Qt.Orientation.Horizontal)
        self.slider_mau_stroke_opacity.setRange(1, 100)
        self.slider_mau_stroke_opacity.setValue(100)
        self.lb_opacity_stroke_value_current.setText(self.slider_mau_stroke_opacity.value().__str__())

        self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86",
                                       bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()

        self.gbox_layout = QVBoxLayout()
        self.groupbox.setLayout(self.gbox_layout)
        # self.gbox_layout.setContentsMargins(0, 0, 0, 0)

        self.content_layout = QGridLayout()

        self.gbox_stroke_layout = QGridLayout()
        self.groupbox_stroke.setLayout(self.gbox_stroke_layout)

        self.text_run_layout = QHBoxLayout()

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0, 10, 0, 10)

    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)

        # self.gbox_layout.addWidget(QLabel(""))
        self.gbox_layout.addLayout(self.content_layout)
        self.gbox_layout.addWidget(self.groupbox_stroke)
        self.gbox_layout.addLayout(self.btn_layout)

        self.content_layout.addWidget(self.lb_x, 0, 0, 1, 2)
        self.content_layout.addWidget(self.input_x, 0, 2, 1, 3)
        self.content_layout.addWidget(QLabel(""), 0, 5, 1, 2)
        self.content_layout.addWidget(self.lb_y, 0, 7, 1, 2)
        self.content_layout.addWidget(self.input_y, 0, 9, 1, 3)

        self.content_layout.addWidget(self.lb_width, 1, 0, 1, 2)
        self.content_layout.addWidget(self.input_width, 1, 2, 1, 3)
        self.content_layout.addWidget(QLabel(""), 1, 5, 1, 2)
        self.content_layout.addWidget(self.lb_height, 1, 7, 1, 2)
        self.content_layout.addWidget(self.input_height, 1, 9, 1, 3)

        self.content_layout.addWidget(self.lb_mau_nen, 2, 0, 1, 2)
        self.content_layout.addWidget(self.input_mau_nen, 2, 2, 1, 2)
        self.content_layout.addWidget(self.btn_dialog_mau_nen, 2, 4)
        self.content_layout.addWidget(QLabel(""), 2, 5, 1, 2)
        self.content_layout.addWidget(self.lb_opacity_nen, 2, 7, 1, 2)
        self.content_layout.addWidget(self.slider_mau_nen_opacity, 2, 9, 1, 2)
        self.content_layout.addWidget(self.lb_opacity_nen_value_current, 2, 11)

        self.gbox_stroke_layout.addWidget(self.lb_stroke_color, 0, 0)
        self.gbox_stroke_layout.addWidget(self.input_stroke_color, 0, 1, 1, 2)
        self.gbox_stroke_layout.addWidget(self.btn_dialog_mau_vien, 0, 3)
        self.gbox_stroke_layout.addWidget(self.lb_do_day_stroke, 0, 4)
        self.gbox_stroke_layout.addWidget(self.combobox_do_day_stroke, 0, 5, 1, 2)
        self.gbox_stroke_layout.addWidget(self.lb_opacity_stroke, 0, 7)
        self.gbox_stroke_layout.addWidget(self.slider_mau_stroke_opacity, 0, 8, 1, 3)
        self.gbox_stroke_layout.addWidget(self.lb_opacity_stroke_value_current, 0, 11)

        self.btn_layout.addWidget(QLabel(""), 40)
        self.btn_layout.addWidget(self.buttonSave, 20)
        self.btn_layout.addWidget(QLabel(""), 40)

    def setup_connections(self):
        self.btn_dialog_mau_vien.clicked.connect(self._openDialogMauVien)
        self.btn_dialog_mau_nen.clicked.connect(self._openDialogMauNen)
        self.slider_mau_stroke_opacity.valueChanged.connect(lambda value: self.lb_opacity_stroke_value_current.setText(str(value)))
        self.slider_mau_nen_opacity.valueChanged.connect(lambda value: self.lb_opacity_nen_value_current.setText(str(value)))

        self.buttonSave.clicked.connect(self.save)
        # self.textarea_proxy.textChanged.connect(self.updatePoxy)

    def loadData(self, value):
        self.input_x.setValue(value['x'])
        self.input_y.setValue(value['y'])
        self.input_width.setValue(value['width'])
        self.input_height.setValue(value['height'])
        self.input_mau_nen.setText(value['color_nen'])
        self.slider_mau_nen_opacity.setValue(value['opacity_nen'])
        self.groupbox_stroke.setChecked(value['them_stroke'])
        if value['them_stroke'] is True:
            self.input_stroke_color.setText(value['color_stroke'])
            self.combobox_do_day_stroke.setCurrentText(str(value['do_day_stroke']))
            self.slider_mau_stroke_opacity.setValue(value['opacity_stroke'])

        self.color_picker_nen_chu.setCurrentColor(QColor(value['color_nen']))
        self.color_picker_stroke.setCurrentColor(QColor(value['color_stroke']))

    def _openDialogMauNen(self):
        done = self.color_picker_nen_chu.exec()
        color = self.color_picker_nen_chu.currentColor()
        if done and color.isValid():
            rgb_255 = [color.red(), color.green(), color.blue()]
            color_hex = '#' + ''.join(
                [hex(v)[2:].ljust(2, '0') for v in rgb_255]
            )
            self.input_mau_nen.setText(color_hex)

    def _openDialogMauVien(self):
        done = self.color_picker_stroke.exec()
        color = self.color_picker_stroke.currentColor()
        if done and color.isValid():
            rgb_255 = [color.red(), color.green(), color.blue()]
            color_hex = '#' + ''.join(
                [hex(v)[2:].ljust(2, '0') for v in rgb_255]
            )
            self.input_stroke_color.setText(color_hex)

    def save(self):

        self.accept()

    def getValue(self) -> dict:

        color_b = QColor( self.input_mau_nen.text())
        color_b.setAlphaF( self.slider_mau_nen_opacity.value()/ 100)
        brush = QBrush(color_b)

        color_p = QColor(self.input_stroke_color.text())
        color_p.setAlphaF(self.slider_mau_stroke_opacity.value()/ 100)
        pen = False
        if self.groupbox_stroke.isChecked() is True:
            pen = QPen(color_p, float(self.combobox_do_day_stroke.currentText()), Qt.PenStyle.SolidLine)
        return {
            "x": self.input_x.value(),
            "y": self.input_y.value(),
            "width": self.input_width.value(),
            "height": self.input_height.value(),
            "brush": brush,
            "pen": pen
        }

    # def clearData(self):
    #     if hasattr(self, "cau_hinh"):
    #         delattr(self, "cau_hinh")
