import json
import os

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog, \
    QFileDialog, QColorDialog, QRadioButton

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN, CHANGE_BACKGROUND_MAIN_VIDEO, \
    TypeBackgroundMainVideo
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

class PyDialogGraphicBackgroundMain(QDialog):
    def __init__(self,manage_thread_pool):
        super().__init__()
        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        # st = QSettings(*SETTING_APP)
        self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
        self.setMinimumWidth(400)
        # LOAD THEME COLOR
        # ///////////////////////////////////////////////////////////////
        self.manage_thread_pool = manage_thread_pool
        self.themes = ConfigTheme()

        self.style_format = style.format(
            _bg_color=self.themes.app_color["bg_one"],
            _color=self.themes.app_color["white"],
        )
        self.app_path = os.path.abspath(os.getcwd())

        # SET UP MAIN WINDOW
        self.setWindowTitle("Tuỳ chỉnh thông số")
        self.setStyleSheet(self.style_format)

        self.isLoading_w = True
        self.isLoading_h = True

        self.setup_ui()

        self.list_proxy = None


    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.groupbox = QGroupBox("Cài đặt")

        self.rad_bg_image_origin = PyRadioButton(value=TypeBackgroundMainVideo.BG_IMAGE_ORIGIN.value, text="Ảnh Nền Theo Hình Gốc")
        self.rad_bg_image_new = PyRadioButton(value=TypeBackgroundMainVideo.BG_IMAGE_NEW.value, text="Ảnh Nền Cố Định")
        self.rad_bg_color = PyRadioButton(value=TypeBackgroundMainVideo.BG_COLOR.value, text="Màu Nền Cố Định")

        self.lb_sigma_image_ori = QLabel("Độ Mờ:")
        self.input_sigma_image_ori = QSpinBox()
        self.input_sigma_image_ori.setMaximum(80)

        self.lb_sigma_image_new = QLabel("Độ Mờ:")
        self.input_sigma_image_new = QSpinBox()
        self.input_sigma_image_new.setMaximum(80)

        self.label_mau_nen = QLabel("Màu Nền:")
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
        self.input_mau_nen.setReadOnly(True)
        self.color_picker_bg = QColorDialog()

        self.lb_file_pixmap = QLabel("Chọn File Ảnh:")
        self.input_src_pixmap = QLineEdit()
        self.input_src_pixmap.setReadOnly(True)
        self.btn_dialog_file_pixmap =  PyButtonIcon(
            icon_path=ConfigResource.set_svg_icon("open-file.png"),
            parent=self,
            app_parent=self,
            icon_color="#f5ca1e",
            icon_color_hover="#ffe270",
            icon_color_pressed="#d1a807",

        )



        self.buttonSave = PyPushButton(text="Đóng",font_size="15px",radius="6px", color="#fff",bg_color1="#1aff86",bg_color2="#0bcc5d",bg_color_hover="#0bcc5d",parent=self)


    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()
        # self.bg_layout.setContentsMargins(0, 0, 0, 0)

        self.gbox_layout = QVBoxLayout()
        self.groupbox.setLayout(self.gbox_layout)
        # self.gbox_layout.setContentsMargins(0, 0, 0, 0)

        self.content_layout = QVBoxLayout()
        self.bg_image_origin_layout = QHBoxLayout()
        self.bg_image_new_layout = QHBoxLayout()
        self.bg_color_layout = QHBoxLayout()


        self.text_run_layout = QHBoxLayout()

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0, 10, 0, 10)


    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)

        # self.gbox_layout.addWidget(QLabel(""))
        self.gbox_layout.addLayout(self.content_layout)
        self.gbox_layout.addLayout(self.btn_layout)

        self.content_layout.addWidget(self.rad_bg_image_origin)
        self.content_layout.addLayout(self.bg_image_origin_layout)
        self.bg_image_origin_layout.addWidget(self.lb_sigma_image_ori)
        self.bg_image_origin_layout.addWidget(self.input_sigma_image_ori)
        self.bg_image_origin_layout.addWidget(QLabel(),20)

        self.content_layout.addWidget(QLabel())

        self.content_layout.addWidget(self.rad_bg_image_new)
        self.content_layout.addLayout(self.bg_image_new_layout)
        self.bg_image_new_layout.addWidget(self.lb_file_pixmap)
        self.bg_image_new_layout.addWidget(self.input_src_pixmap )
        self.bg_image_new_layout.addWidget(self.btn_dialog_file_pixmap)
        self.bg_image_new_layout.addWidget(self.lb_sigma_image_new)
        self.bg_image_new_layout.addWidget(self.input_sigma_image_new)
        self.bg_image_new_layout.addWidget(QLabel(),20)

        self.content_layout.addWidget(QLabel())

        self.content_layout.addWidget(self.rad_bg_color)
        self.content_layout.addLayout(self.bg_color_layout)
        self.bg_color_layout.addWidget(self.label_mau_nen)
        self.bg_color_layout.addWidget(self.input_mau_nen)
        self.bg_color_layout.addWidget(self.btn_dialog_mau_nen)
        self.bg_color_layout.addWidget(QLabel(),20)


        self.btn_layout.addWidget(QLabel(""),40)
        self.btn_layout.addWidget(self.buttonSave,20)
        self.btn_layout.addWidget(QLabel(""),40)

    def setup_connections(self):
        self.btn_dialog_file_pixmap.clicked.connect(self.openDialogFile)

        self.buttonSave.clicked.connect(self.save)
        self.btn_dialog_mau_nen.clicked.connect(self._openDialogMauNen)

        self.rad_bg_image_origin.clicked.connect(self.checkRadioBg_Main)
        self.rad_bg_image_new.clicked.connect(self.checkRadioBg_Main)
        self.rad_bg_color.clicked.connect(self.checkRadioBg_Main)
        # self.checbox_ratio.toggled.connect(self._click_checbox_ratio)
        self.input_sigma_image_ori.valueChanged.connect(lambda value: self.sigma_image_changed(value, "sigma_bg_image_ori"))
        self.input_sigma_image_new.valueChanged.connect(lambda value: self.sigma_image_changed(value, "sigma_bg_image_new"))
        # self.input_height.valueChanged.connect(lambda value :self._check_ratio(value,"height"))

    def loadData(self, configCurrent):
        self.configCurrent = configCurrent
        cau_hinh: dict = json.loads(configCurrent.value)

        self.color_picker_bg.setCurrentColor(QColor(cau_hinh["bg_color_main"]))
        self.input_mau_nen.setText(cau_hinh["bg_color_main"])
        self.input_src_pixmap.setText(cau_hinh["src_bg_co_dinh"])
        self.input_sigma_image_new.setValue(cau_hinh["sigma_bg_image_new"])
        self.input_sigma_image_ori.setValue(cau_hinh["sigma_bg_image_ori"])

        self.checkRadioDisabled()

    def checkRadioDisabled(self):
        cau_hinh: dict = json.loads(self.configCurrent.value)

        for rb in self.groupbox.findChildren(QRadioButton):
            if rb.getValue() == cau_hinh["bg_video_main"]:
                rb.setChecked(True)

    def openDialogFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, caption='Chọn file hình logo',
                                                dir=(self.app_path), filter='File Ảnh (*.png *.jpg *jpeg)')
        self.input_src_pixmap.setText(file_name)
        cau_hinh = json.loads(self.configCurrent.value)
        cau_hinh['src_bg_co_dinh'] = file_name
        self.configCurrent.value = json.dumps(cau_hinh)
        self.configCurrent.save()
        self.manage_thread_pool.resultChanged.emit(CHANGE_BACKGROUND_MAIN_VIDEO, CHANGE_BACKGROUND_MAIN_VIDEO, "")


    def _openDialogMauNen(self):
        done = self.color_picker_bg.exec()
        color = self.color_picker_bg.currentColor()
        if done and color.isValid():
            rgb_255 = [color.red(), color.green(), color.blue()]
            color_hex = '#' + ''.join(
                [hex(v)[2:].ljust(2, '0') for v in rgb_255]
            )
            self.input_mau_nen.setText(color_hex)
            cau_hinh = json.loads(self.configCurrent.value)
            cau_hinh['bg_color_main'] = color_hex
            self.configCurrent.value = json.dumps(cau_hinh)
            self.configCurrent.save()
            self.manage_thread_pool.resultChanged.emit(CHANGE_BACKGROUND_MAIN_VIDEO, CHANGE_BACKGROUND_MAIN_VIDEO, "")

    def checkRadioBg_Main(self):
        position_text = ""
        for rb in self.groupbox.findChildren(QRadioButton):
            if rb.isChecked():
                position_text = rb.getValue()
        cau_hinh = json.loads(self.configCurrent.value)
        cau_hinh['bg_video_main'] = position_text
        self.configCurrent.value = json.dumps(cau_hinh)
        self.configCurrent.save()
        self.manage_thread_pool.resultChanged.emit(CHANGE_BACKGROUND_MAIN_VIDEO, CHANGE_BACKGROUND_MAIN_VIDEO, "")


    def sigma_image_changed(self, value, key):
        cau_hinh = json.loads(self.configCurrent.value)
        cau_hinh[key] = value
        self.configCurrent.value = json.dumps(cau_hinh)
        self.configCurrent.save()
        self.manage_thread_pool.resultChanged.emit(CHANGE_BACKGROUND_MAIN_VIDEO, CHANGE_BACKGROUND_MAIN_VIDEO, "")
        
    def save(self):
        for rb in self.groupbox.findChildren(QRadioButton):
            if rb.isChecked():
                if rb.getValue() == TypeBackgroundMainVideo.BG_IMAGE_NEW.value and self.input_src_pixmap.text() =='':
                    PyMessageBox().show_warning("Lỗi", "Vui lòng chọn file ảnh nền")
                    return False
        self.accept()

    def getValue(self) -> dict:
        return {
            "pixmap":self.input_src_pixmap.text(),
        }


    # def clearData(self):
        # if hasattr(self, "cau_hinh"):
        #     delattr(self, "cau_hinh")

