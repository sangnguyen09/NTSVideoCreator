import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog, \
    QSlider, QComboBox, QRadioButton

from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN, TypeTocDoChayAnh
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_checkbox import PyCheckBox
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


class PyDialogLachVideo(QDialog):
    def __init__(self):
        super().__init__()
        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        # st = QSettings(*SETTING_APP)
        self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
        self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
        # LOAD THEME COLOR
        # ///////////////////////////////////////////////////////////////
        self.themes = ConfigTheme()
        self.style_format = style.format(
            _bg_color=self.themes.app_color["bg_one"],
            _color=self.themes.app_color["white"],
        )

        # SET UP MAIN WINDOW
        self.setWindowTitle("Tùy Chỉnh Render")
        self.setStyleSheet(self.style_format)

        self.setup_ui()

        self.list_proxy = None

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.groupbox_edit = QGroupBox("EDIT Video")

        self.rad_toc_do_theo_voice = PyRadioButton(value=TypeTocDoChayAnh.THEO_VOICE.value, text="Tốc Độ Theo Voice")
        self.rad_toc_do_co_dinh = PyRadioButton(value=TypeTocDoChayAnh.CO_DINH.value, text="Tốc Độ Cố Định")
        
        self.slider_speed = QSlider()
        self.slider_speed.setMinimum(5)
        self.slider_speed.setMaximum(100)
        self.slider_speed.setPageStep(1)
        self.slider_speed.setValue(40)
        self.slider_speed.setOrientation(Qt.Orientation.Horizontal)

        self.lb_speed_number = QLabel(str(self.slider_speed.value()) + "x")

        self.cbobox_time_no_text = QComboBox()
        self.cbobox_time_no_text.addItems([str(i) for i in range(1, 10)])

        self.cb_concat2 = PyCheckBox(value="concat2", text="Concat V2")

        self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86",
                                       bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.app_layout = QVBoxLayout()
        self.app_layout.setContentsMargins(0, 0, 0, 0)
        self.content_frame = QWidget()
        self.content_layout = QVBoxLayout(self.content_frame)

        self.gbox_edit_layout = QGridLayout()
        self.gbox_edit_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.app_layout.addWidget(self.content_frame)
        self.setLayout(self.app_layout)

        self.content_layout.addWidget(self.groupbox_edit, 80)
        self.content_layout.addLayout(self.btn_layout, 20)

        self.groupbox_edit.setLayout(self.gbox_edit_layout)

        self.gbox_edit_layout.addWidget(self.rad_toc_do_theo_voice, 1, 0, 1, 2)
        self.gbox_edit_layout.addWidget(self.rad_toc_do_co_dinh, 1, 2, 1, 2)
        self.gbox_edit_layout.addWidget(self.slider_speed, 1, 4, 1, 7)
        self.gbox_edit_layout.addWidget(self.lb_speed_number, 1, 11)

        self.gbox_edit_layout.addWidget(QLabel(""), 2,2)

        self.gbox_edit_layout.addWidget(QLabel("Thời Gian Hình Ảnh Không Chữ Xuất Hiện (giây):"), 3, 0, 1, 2)
        self.gbox_edit_layout.addWidget(self.cbobox_time_no_text, 3, 2, 1, 2)
        self.gbox_edit_layout.addWidget(QLabel(""), 3, 4)

        self.gbox_edit_layout.addWidget(self.cb_concat2, 3, 5, 1, 2)
        self.gbox_edit_layout.addWidget(QLabel(""), 3, 7, 1, 5)


        self.btn_layout.addWidget(QLabel(""), 40)
        self.btn_layout.addWidget(self.buttonSave, 20)
        self.btn_layout.addWidget(QLabel(""), 40)

    def setup_connections(self):
        self.slider_speed.valueChanged.connect(self.sliderValueChanged)
        self.buttonSave.clicked.connect(self.save)

    def loadData(self, configCurrent: CauHinhTuyChonModel):
        self.configCurrent = configCurrent
        cau_hinh: dict = json.loads(configCurrent.value)

        # self.cb_speed_video.setChecked(cau_hinh["tang_speed"])
        self.slider_speed.setValue(int(cau_hinh["toc_do_chay_hinh"]))
        self.cbobox_time_no_text.setCurrentText(str(cau_hinh["time_no_text"]))
        self.cb_concat2.setChecked(cau_hinh.get('concat_v2'))

        self.checkRadioDisabled()

    def checkRadioDisabled(self):
        cau_hinh: dict = json.loads(self.configCurrent.value)

        for rb in self.groupbox_edit.findChildren(QRadioButton):
            if rb.getValue() == cau_hinh["speed_image_run"]:
                rb.setChecked(True)
    def save(self):
        self.accept()

    def sliderValueChanged(self):
        self.lb_speed_number.setText(str(self.slider_speed.value()) + "x")

    def getValue(self):

        speed_image_run = ""
        for rb in self.groupbox_edit.findChildren(QRadioButton):
            if rb.isChecked():
                speed_image_run = rb.getValue()

        return {
            "time_no_text": int(self.cbobox_time_no_text.currentText()),
            "toc_do_chay_hinh": self.slider_speed.value(),
            "concat_v2": self.cb_concat2.isChecked(),
            "speed_image_run": speed_image_run,
        }

    def clearData(self):
        if hasattr(self, "configCurrent"):
            delattr(self, "configCurrent")
        self.slider_speed.setValue(40)
