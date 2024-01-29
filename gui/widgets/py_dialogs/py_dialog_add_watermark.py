import json
import os

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, QDialog, \
    QColorDialog, QComboBox, \
    QRadioButton, QFileDialog

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_checkbox import PyCheckBox
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_radio_buttion import PyRadioButton

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

class PyDialogAddWaterMark(QDialog):
    def __init__(self):
        super().__init__()
        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        # st = QSettings(*SETTING_APP)
        self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
        self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
        self.setMinimumHeight(self.settings['data_setting']["dialog_size"][1])

        # LOAD THEME COLOR
        # ///////////////////////////////////////////////////////////////
        self.themes = ConfigTheme()
        self.style_format = style.format(
            _bg_color=self.themes.app_color["bg_one"],
            _color=self.themes.app_color["white"],
        )
        self.app_path = os.path.abspath(os.getcwd())

        # SET UP MAIN WINDOW
        self.setWindowTitle("Thêm Watermark Vào Video")
        self.setStyleSheet(self.style_format)

        self.setMinimumHeight(self.settings.dialog_size[1])
        self.setMinimumWidth(self.settings.dialog_size[0])

        self.setup_ui()

        self.list_proxy = None


    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.groupbox_add_logo = QGroupBox("Thêm Logo")
        self.groupbox_add_logo.setCheckable(True)
        self.groupbox_add_logo.setChecked(False)


        self.lb_file_logo = QLabel("Chọn File:")
        self.input_src_logo = QLineEdit()
        self.input_src_logo.setReadOnly(True)
        self.btn_dialog_file_logo =  PyButtonIcon(
            icon_path=ConfigResource.set_svg_icon("open-file.png"),
            parent=self,
            app_parent=self,
            icon_color="#f5ca1e",
            icon_color_hover="#ffe270",
            icon_color_pressed="#d1a807",

        )
        self.groupbox_position_logo = QGroupBox("Vị Trí Logo:")
        self.rad_position_topleft =  PyRadioButton(value="topleft",text="top left")
        self.rad_position_topcenter =  PyRadioButton(value="topcenter", text="top center")
        self.rad_position_topright =  PyRadioButton(value="topright",text="top right")
        self.rad_position_middleright =  PyRadioButton(value="middleright",text="middle right")
        self.rad_position_middlecenter =  PyRadioButton(value="middlecenter", text="middle center")
        self.rad_position_middleleft =  PyRadioButton(value="middleleft",text="middle left")
        self.rad_position_bottomright =  PyRadioButton(value="bottomright",text="bottom right")
        self.rad_position_bottomcenter =  PyRadioButton(value="bottomcenter", text="bottom center")
        self.rad_position_bottomleft =  PyRadioButton(value="bottomleft",text="bottom left")


        self.groupbox_add_text = QGroupBox("Thêm Chữ")
        self.groupbox_add_text.setCheckable(True)
        self.groupbox_add_text.setChecked(False)

        self.lb_text = QLabel("Nhập Text")
        self.input_text = QLineEdit()
        self.lb_text_position = QLabel("Vị Trí Text:")
        self.cb_position_text = QComboBox()
        self.cb_position_text.addItems(["Top", "Center", "Bottom"])
        self.lb_color_text = QLabel("Màu chữ:")
        self.btn_dialog_color_text = PyButtonIcon(
            icon_path=ConfigResource.set_svg_icon("color-picker.png"),
            parent=self,
            app_parent=self,
            icon_color="#f5ca1e",
            width=30,
            height=30,
            icon_color_hover="#ffe270",
            icon_color_pressed="#d1a807",

        )
        self.input_color_text = QLineEdit()
        self.lb_font_text = QLabel("Font chữ:")
        self.cb_font_text = QComboBox()

        self.cbox_run_text = PyCheckBox(value="text_run", text="Chữ Chạy")
        self.lb_speed_text = QLabel("Tốc độ chạy:")
        self.cb_speed_text = QComboBox()
        self.cb_speed_text.addItems(["Slow", "Normal", "Fast"])
        self.cb_speed_text.setCurrentIndex(1)

        self.color_picker = QColorDialog()

        self.buttonSave = PyPushButton(text="Lưu",font_size="15px",radius="6px", color="#fff",bg_color1="#1aff86",bg_color2="#0bcc5d",bg_color_hover="#0bcc5d",parent=self)


    def modify_widgets(self):
        pass

    def create_layouts(self):

        self.app_layout = QVBoxLayout()
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.content_frame = QWidget()
        # Thêm giao diện tùy chỉnh vào layout này
        self.content_layout = QVBoxLayout(self.content_frame)

        self.groupbox_position_logo_layout = QGridLayout()

        self.add_logo_layout = QVBoxLayout()

        self.add_logo_src_layout = QHBoxLayout()
        self.add_logo_position_layout = QHBoxLayout()

        self.add_text_layout = QVBoxLayout()
        self.add_text_style_layout = QHBoxLayout()
        self.add_text_style_layout.setContentsMargins(0, 10, 0, 10)

        self.text_run_layout = QHBoxLayout()

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0, 10, 0, 10)


    def add_widgets_to_layouts(self):
        self.app_layout.addWidget(self.content_frame)
        self.setLayout(self.app_layout)

        self.content_layout.addWidget(self.groupbox_add_logo,35)
        self.content_layout.addWidget(self.groupbox_add_text,50)
        self.content_layout.addLayout(self.btn_layout,15)

        self.groupbox_add_logo.setLayout(self.add_logo_layout)
        self.groupbox_add_text.setLayout(self.add_text_layout)
        self.groupbox_position_logo.setLayout(self.groupbox_position_logo_layout)


        self.add_logo_layout.addLayout(self.add_logo_src_layout)
        self.add_logo_layout.addLayout(self.add_logo_position_layout)
        self.add_logo_src_layout.addWidget(self.lb_file_logo)
        self.add_logo_src_layout.addWidget(self.input_src_logo)
        self.add_logo_src_layout.addWidget(self.btn_dialog_file_logo)
        self.add_logo_position_layout.addWidget(self.groupbox_position_logo)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_topleft,0,0)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_topcenter, 0, 1)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_topright,0,2)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_middleleft,1,0)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_middlecenter, 1, 1)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_middleright,1,2)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_bottomleft,2,0)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_bottomcenter, 2, 1)
        self.groupbox_position_logo_layout.addWidget(self.rad_position_bottomright,2,2)


        self.add_text_layout.addWidget(self.lb_text)
        self.add_text_layout.addWidget(self.input_text)
        self.add_text_layout.addLayout(self.add_text_style_layout)
        self.add_text_layout.addLayout(self.text_run_layout)

        self.add_text_style_layout.addWidget(self.lb_text_position,10)
        self.add_text_style_layout.addWidget(self.cb_position_text,20)
        self.add_text_style_layout.addWidget(QLabel(""),5)
        self.add_text_style_layout.addWidget(self.lb_color_text)
        self.add_text_style_layout.addWidget(self.input_color_text)
        self.add_text_style_layout.addWidget(self.btn_dialog_color_text)

        self.text_run_layout.addWidget(self.cbox_run_text,20)
        self.text_run_layout.addWidget(self.lb_speed_text,10)
        self.text_run_layout.addWidget(self.cb_speed_text,30)
        self.text_run_layout.addWidget(QLabel(""),40)

        self.btn_layout.addWidget(QLabel(""),40)
        self.btn_layout.addWidget(self.buttonSave,20)
        self.btn_layout.addWidget(QLabel(""),40)

    def setup_connections(self):
        self.btn_dialog_file_logo.clicked.connect(self.openDialogFile)
        self.btn_dialog_color_text.clicked.connect(self.openDialogColor)

        self.buttonSave.clicked.connect(self.save)
        # self.textarea_proxy.textChanged.connect(self.updatePoxy)

    def loadData(self, configCurrent: CauHinhTuyChonModel):
        self.configCurrent  = configCurrent
        cau_hinh : dict = json.loads(configCurrent.value)

        self.groupbox_add_text.setChecked(cau_hinh["them_watermark_text"])
        self.groupbox_add_logo.setChecked(cau_hinh["them_watermark_logo"])
        self.input_src_logo.setText(cau_hinh["src_logo"])
        self.input_text.setText(cau_hinh["watermark_text"])
        self.cb_position_text.setCurrentText(cau_hinh["vi_tri_text"])
        self.cb_speed_text.setCurrentText(cau_hinh["toc_do_chay_text"])
        self.input_color_text.setText(cau_hinh["mau_text"])
        self.cbox_run_text.setChecked(cau_hinh["text_chay"])
        self.color_picker.setCurrentColor(QColor(cau_hinh["mau_text"]))

        for rb in self.groupbox_position_logo.findChildren(QRadioButton):
            if rb.getValue() == cau_hinh["vi_tri_logo"]:
                rb.setChecked(True)

    def openDialogFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, caption='Chọn file hình logo',
                                                dir=(self.app_path), filter='File Ảnh (*.png *.jpg *jpeg)')
        self.input_src_logo.setText(file_name)

    def openDialogColor(self):
        done = self.color_picker.exec()
        color = self.color_picker.currentColor()
        if done and color.isValid():
            rgb_255 = [color.red(), color.green(), color.blue()]
            color_hex = '#' + ''.join(
                [hex(v)[2:].ljust(2, '0') for v in rgb_255]
            )
            self.input_color_text.setText(color_hex)
    def save(self):
        if self.groupbox_add_logo.isChecked() and self.input_src_logo.text() =="" :
           return PyMessageBox().show_warning("Thiếu thông tin","Vui lòng chọn file hình logo")

        if self.groupbox_add_text.isChecked() and self.input_text.text() == "":
            return PyMessageBox().show_warning("Thiếu thông tin", "Vui lòng điền chữ cần thêm vào video")
        else:
            self.accept()

    def getValue(self):
        position_text = ""
        for rb in self.groupbox_position_logo.findChildren(QRadioButton):
            if rb.isChecked():
                position_text = rb.getValue()

        return {
            "them_watermark_text":self.groupbox_add_text.isChecked(),
            "them_watermark_logo":self.groupbox_add_logo.isChecked(),
            "src_logo":self.input_src_logo.text(),
            "watermark_text":self.input_text.text(),
            "vi_tri_text":self.cb_position_text.currentText(),
            "toc_do_chay_text":self.cb_speed_text.currentText(),
            "mau_text":self.input_color_text.text(),
            "text_chay":self.cbox_run_text.isChecked(),
            "vi_tri_logo":position_text
        }


    def clearData(self):
        # if hasattr(self, "cau_hinh"):
        #     delattr(self, "cau_hinh")
        self.groupbox_add_text.setChecked(False)
        self.groupbox_add_logo.setChecked(False)
        self.input_src_logo.clear()
        self.input_text.clear()
        self.cb_position_text.setCurrentText("Top")
        self.cb_speed_text.setCurrentText("Normal")
        self.input_color_text.clear()
        self.cbox_run_text.setChecked(False)
        self.color_picker.setCurrentColor(QColor("#ffffff"))

        for rb in self.groupbox_position_logo.findChildren(QRadioButton):
            if rb.getValue() == "topright":
                rb.setChecked(True)
