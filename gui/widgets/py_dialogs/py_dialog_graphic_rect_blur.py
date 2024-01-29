import os

from PySide6.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog

from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton

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


class PyDialogGraphicRectBlur(QDialog):
    def __init__(self):
        super().__init__()
        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////

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
        # st = QSettings(*SETTING_APP)
        self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
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

        self.lb_sigma = QLabel("Độ Mờ:")
        self.input_sigma = QSpinBox()
        self.input_sigma.setMaximum(80)

        self.lb_steps = QLabel("Số Lần Lặp:")
        self.input_steps = QSpinBox()
        self.input_steps.setMaximum(10)

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


        self.text_run_layout = QHBoxLayout()

        self.btn_layout = QHBoxLayout()
        self.btn_layout.setContentsMargins(0, 10, 0, 10)

    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)

        # self.gbox_layout.addWidget(QLabel(""))
        self.gbox_layout.addLayout(self.content_layout)
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

        self.content_layout.addWidget(self.lb_sigma, 2, 0, 1, 2)
        self.content_layout.addWidget(self.input_sigma, 2, 2, 1, 3)
        self.content_layout.addWidget(QLabel(""), 2, 5, 1, 2)
        self.content_layout.addWidget(self.lb_steps, 2, 7, 1, 2)
        self.content_layout.addWidget(self.input_steps, 2, 9, 1, 3)



        self.btn_layout.addWidget(QLabel(""), 40)
        self.btn_layout.addWidget(self.buttonSave, 20)
        self.btn_layout.addWidget(QLabel(""), 40)

    def setup_connections(self):
        self.buttonSave.clicked.connect(self.save)
        # self.textarea_proxy.textChanged.connect(self.updatePoxy)

    def loadData(self, value):
        self.input_x.setValue(value['x'])
        self.input_y.setValue(value['y'])
        self.input_width.setValue(value['width'])
        self.input_height.setValue(value['height'])
        try:
            self.input_sigma.setValue(value['sigma'])
            self.input_steps.setValue(value['steps'])
        except:
            pass
    def save(self):

        self.accept()

    def getValue(self) -> dict:
        return {
            "x": self.input_x.value(),
            "y": self.input_y.value(),
            "width": self.input_width.value(),
            "height": self.input_height.value(),
            "sigma": self.input_sigma.value(),
            "steps": self.input_steps.value(),

        }

    # def clearData(self):
    #     if hasattr(self, "cau_hinh"):
    #         delattr(self, "cau_hinh")
