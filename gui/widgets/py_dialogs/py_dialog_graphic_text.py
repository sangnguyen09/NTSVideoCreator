import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QBrush, QPen
from PySide6.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog, \
    QColorDialog, QComboBox, \
    QSlider

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_checkbox import PyCheckBox
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox

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


class PyDialogGraphicText(QDialog):
    def __init__(self,list_fonts):
        super().__init__()
        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        # st = QSettings(*SETTING_APP)
        self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
        self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])

        self.list_fonts = list_fonts
        self.manage_thread_pool = ManageThreadPool()
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


        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.groupbox = QGroupBox("Cài đặt")

        self.lb_text = QLabel("Nội Dung:")
        self.input_text = QLineEdit()

        self.lb_x = QLabel("Vị Trí X")
        self.input_x = QSpinBox()
        self.input_x.setMaximum(20000)

        self.lb_y = QLabel("Vị Trí Y:")
        self.input_y = QSpinBox()
        self.input_y.setMaximum(20000)
        self.input_y.setMinimum(-20000)
        self.input_x.setMinimum(-20000)

        self.lb_mau_text = QLabel("Màu Chữ:")
        self.btn_dialog_mau_text = PyButtonIcon(
            icon_path=ConfigResource.set_svg_icon("color-picker.png"),
            parent=self,
            app_parent=self,
            icon_color="#f5ca1e",
            width=30,
            height=30,
            icon_color_hover="#ffe270",
            icon_color_pressed="#d1a807",

        )
        self.input_text_color = QLineEdit()
        self.color_picker_mau_text = QColorDialog()

        self.lb_opacity_text = QLabel("Opacity:")
        self.lb_opacity_text_value_current = QLabel("")
        self.slider_mau_text_opacity = QSlider()
        self.slider_mau_text_opacity.setOrientation(Qt.Orientation.Horizontal)
        self.slider_mau_text_opacity.setRange(1, 100)
        self.slider_mau_text_opacity.setValue(100)
        self.lb_opacity_text_value_current.setText(self.slider_mau_text_opacity.value().__str__())

        self.groupbox_stroke = QGroupBox("Thêm Viền Chữ:")
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

        self.lb_do_day_stroke = QLabel("Độ Dày:")
        self.combobox_do_day_stroke = QComboBox()
        self.combobox_do_day_stroke.addItems([str(i) for i in range(1, 5)])
        self.lb_opacity_stroke = QLabel("Opacity:")
        self.lb_opacity_stroke_value_current = QLabel("")
        self.slider_mau_stroke_opacity = QSlider()
        self.slider_mau_stroke_opacity.setOrientation(Qt.Orientation.Horizontal)
        self.slider_mau_stroke_opacity.setRange(1, 100)
        self.slider_mau_stroke_opacity.setValue(100)
        self.lb_opacity_stroke_value_current.setText(self.slider_mau_stroke_opacity.value().__str__())

        self.groupbox_font = QGroupBox("Font:")
        self.groupbox_font.setCheckable(True)
        self.groupbox_font.setChecked(False)
        self.lb_font_text = QLabel("Font Chữ:")
        self.lb_font_size_text = QLabel("Font Size:")

        self.combobox_font_family = QComboBox()

        self.combobox_font_size = QComboBox()
        self.combobox_font_size.addItems([str(i) for i in range(8,500)])
        self.combobox_font_size.setCurrentIndex(6)

        self.checkbox_run_text = PyCheckBox(value="text_run", text="Chữ Chạy")
        self.lb_speed_text = QLabel("Tốc Độ Chạy:")
        self.combox_speed_text = QComboBox()
        self.combox_speed_text.setDisabled(True)
        self.combox_speed_text.addItems([str(i) for i in range(5, 26)])
        self.combox_speed_text.setCurrentIndex(10)

        self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86",
                                       bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)

    def modify_widgets(self):
        for index, font in enumerate(self.list_fonts):
            self.combobox_font_family.addItem(font)
            self.combobox_font_family.setItemData(index, QFont(font, 14), Qt.ItemDataRole.FontRole)

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()

        self.gbox_layout = QVBoxLayout()
        self.groupbox.setLayout(self.gbox_layout)
        # self.gbox_layout.setContentsMargins(0, 0, 0, 0)

        self.content_layout = QGridLayout()

        self.gbox_stroke_layout = QGridLayout()
        self.groupbox_stroke.setLayout(self.gbox_stroke_layout)

        self.gbox_font_layout = QGridLayout()
        self.groupbox_font.setLayout(self.gbox_font_layout)

        self.text_run_layout = QHBoxLayout()

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0, 10, 0, 10)

    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)

        # self.gbox_layout.addWidget(QLabel(""))
        self.gbox_layout.addLayout(self.content_layout)
        self.gbox_layout.addWidget(self.groupbox_stroke)
        # self.gbox_layout.addWidget(self.groupbox_font)
        self.gbox_layout.addLayout(self.btn_layout)

        self.content_layout.addWidget(self.lb_text, 0, 0, 1, 2)
        self.content_layout.addWidget(self.input_text, 0, 2, 1, 10)

        self.content_layout.addWidget(self.lb_x, 1, 0, 1, 2)
        self.content_layout.addWidget(self.input_x,1, 2, 1, 3)
        self.content_layout.addWidget(QLabel(""), 1, 5, 1, 2)
        self.content_layout.addWidget(self.lb_y, 1, 7, 1, 2)
        self.content_layout.addWidget(self.input_y, 1, 9, 1, 3)

        self.content_layout.addWidget(self.lb_mau_text, 2, 0, 1, 2)
        self.content_layout.addWidget(self.input_text_color, 2, 2, 1, 2)
        self.content_layout.addWidget(self.btn_dialog_mau_text, 2, 4)
        self.content_layout.addWidget(QLabel(""), 2, 5, 1, 2)
        self.content_layout.addWidget(self.lb_opacity_text, 2, 7, 1, 2)
        self.content_layout.addWidget(self.slider_mau_text_opacity, 2, 9, 1, 2)
        self.content_layout.addWidget(self.lb_opacity_text_value_current, 2, 11)

        self.content_layout.addWidget(self.lb_font_text, 3, 0, 1, 2)
        self.content_layout.addWidget(self.combobox_font_family, 3, 2, 1, 3)
        self.content_layout.addWidget(QLabel(""), 3, 5, 1, 2)
        self.content_layout.addWidget(self.lb_font_size_text, 3, 7, 1, 2)
        self.content_layout.addWidget(self.combobox_font_size, 3, 9, 1, 3)


        self.content_layout.addWidget(self.checkbox_run_text, 4, 0, 1, 2)
        self.content_layout.addWidget(self.lb_speed_text, 4, 2)
        self.content_layout.addWidget(self.combox_speed_text, 4, 3, 1, 4)
        self.content_layout.addWidget(QLabel("(Số càng nhỏ thì càng chạy nhanh) "), 4,7, 1, 2)



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
        self.btn_dialog_mau_text.clicked.connect(self._openDialogMauText)
        self.slider_mau_stroke_opacity.valueChanged.connect(lambda value: self.lb_opacity_stroke_value_current.setText(str(value)))
        self.slider_mau_text_opacity.valueChanged.connect(lambda value: self.lb_opacity_text_value_current.setText(str(value)))
        self.checkbox_run_text.toggled.connect(lambda : self.combox_speed_text.setDisabled(not self.checkbox_run_text.isChecked()))
        self.buttonSave.clicked.connect(self.save)
        # self.textarea_proxy.textChanged.connect(self.updatePoxy)

    def loadData(self, value):
        self.input_x.setValue(value['x'])
        self.input_y.setValue(value['y'])
        self.input_text_color.setText(value['color_text'])
        self.slider_mau_text_opacity.setValue(value['opacity_text'])
        self.groupbox_stroke.setChecked(value['them_stroke'])
        if value['them_stroke'] is True:
            self.input_stroke_color.setText(value['color_stroke'])
            self.combobox_do_day_stroke.setCurrentText(str(value['do_day_stroke']))
            self.slider_mau_stroke_opacity.setValue(value['opacity_stroke'])
            
        if not value['font_family'] == '':
            self.combobox_font_family.setCurrentText(value['font_family'])

        self.combobox_font_size.setCurrentText(str(value['font_size']))

        self.input_text.setText(value['text'])
        self.checkbox_run_text.setChecked(value['text_run'])
        if value['text_run'] is True:
            self.combox_speed_text.setCurrentText(str(value['speed_text']))

        self.color_picker_mau_text.setCurrentColor(QColor(value['color_text']))
        self.color_picker_stroke.setCurrentColor(QColor(value['color_stroke']))


    def _openDialogMauText(self):
        done = self.color_picker_mau_text.exec()
        color = self.color_picker_mau_text.currentColor()
        if done and color.isValid():
            rgb_255 = [color.red(), color.green(), color.blue()]
            color_hex = '#' + ''.join(
                [hex(v)[2:].ljust(2, '0') for v in rgb_255]
            )
            self.input_text_color.setText(color_hex)

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
        if self.input_text.text() == "":
            return PyMessageBox().show_warning("Lỗi", "Vui lòng nhập chữ !")
        self.accept()

    def getValue(self) -> dict:
        color_b = QColor(self.input_text_color.text())
        color_b.setAlphaF(self.slider_mau_text_opacity.value() / 100)
        color_text = QBrush(color_b)

        color_p = QColor(self.input_stroke_color.text())
        color_p.setAlphaF(self.slider_mau_stroke_opacity.value()/ 100)
        stroke = False
        if self.groupbox_stroke.isChecked() is True:
            stroke = QPen(color_p, int(self.combobox_do_day_stroke.currentText()), Qt.PenStyle.SolidLine)

        font = QFont()
        font.setFamily(self.combobox_font_family.currentText())
        font.setPixelSize(int(self.combobox_font_size.currentText()))
        font.setBold(True)
        font.setWeight(QFont.Weight.Black)



        return {
            "x": self.input_x.value(),
            "y": self.input_y.value(),
            "color_text": color_text,
            "stroke": stroke,
            "text": self.input_text.text(),
            "font": font,
            "text_run": self.checkbox_run_text.isChecked(),
            "speed_text": int(self.combox_speed_text.currentText()),
        }

    # def clearData(self):
    #     if hasattr(self, "cau_hinh"):
    #         delattr(self, "cau_hinh")
