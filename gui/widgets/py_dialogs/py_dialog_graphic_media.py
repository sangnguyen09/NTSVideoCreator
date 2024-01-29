import os

from PySide6.QtWidgets import QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QSpinBox, QGroupBox, QGridLayout, QDialog, \
    QFileDialog

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import SETTING_APP_DATA, TOOL_CODE_MAIN
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_checkbox import PyCheckBox
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

class PyDialogGraphicMedia(QDialog):
    def __init__(self,main_video):
        super().__init__()
        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////
        # st = QSettings(*SETTING_APP)
        self.settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
        self.setMinimumWidth(self.settings['data_setting']["dialog_size"][0])
        # LOAD THEME COLOR
        # ///////////////////////////////////////////////////////////////
        self.themes = ConfigTheme()
        self.main_video = main_video
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

        self.lb_file_pixmap = QLabel("Thay đổi hình:")
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

        self.checbox_ratio = PyCheckBox("", "Giữ tỉ lệ")

        self.buttonSave = PyPushButton(text="Lưu",font_size="15px",radius="6px", color="#fff",bg_color1="#1aff86",bg_color2="#0bcc5d",bg_color_hover="#0bcc5d",parent=self)


    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()
        # self.bg_layout.setContentsMargins(0, 0, 0, 0)

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

        if self.main_video is False:
            self.content_layout.addWidget(self.lb_file_pixmap, 0,0,1,2)
            self.content_layout.addWidget(self.input_src_pixmap, 0,2,1,9)
            self.content_layout.addWidget(self.btn_dialog_file_pixmap, 0,11)

        self.content_layout.addWidget(self.lb_x, 1,0,1,2)
        self.content_layout.addWidget(self.input_x, 1,2,1,3)
        self.content_layout.addWidget(QLabel(""), 1,5,1,2)
        self.content_layout.addWidget(self.lb_y, 1,7,1,2)
        self.content_layout.addWidget(self.input_y, 1,9,1,3)

        self.content_layout.addWidget(self.lb_width, 2,0,1,2)
        self.content_layout.addWidget(self.input_width, 2,2,1,3)
        self.content_layout.addWidget(QLabel(""), 2,5,1,2)
        self.content_layout.addWidget(self.lb_height, 2,7,1,2)
        self.content_layout.addWidget(self.input_height, 2,9,1,3)

        self.content_layout.addWidget(self.checbox_ratio, 3,0,1,2)

        self.btn_layout.addWidget(QLabel(""),40)
        self.btn_layout.addWidget(self.buttonSave,20)
        self.btn_layout.addWidget(QLabel(""),40)

    def setup_connections(self):
        self.btn_dialog_file_pixmap.clicked.connect(self.openDialogFile)

        self.buttonSave.clicked.connect(self.save)

        self.checbox_ratio.toggled.connect(self._click_checbox_ratio)
        self.input_width.valueChanged.connect(lambda value: self._check_ratio(value, "width"))
        self.input_height.valueChanged.connect(lambda value :self._check_ratio(value,"height"))

    def _check_ratio(self,value, type):

        if self.checbox_ratio.isChecked() is True  :
            if type == "width" and self.h > 0 and self.isLoading_w is True:
                self.isLoading_h = False
                self.input_height.setValue(value*(self.h/self.w))
                self.isLoading_h = True
            if type == "height" and self.h > 0 and self.isLoading_h is True:
                self.isLoading_w = False
                self.input_width.setValue(value*(self.w/self.h))
                self.isLoading_w = True

    def _click_checbox_ratio(self):
        if self.checbox_ratio.isChecked() is True:
                self.input_height.setValue(self.input_width.value() * (self.h / self.w))

    def loadData(self,x,y,width, height):
        self.w = width
        self.h = height

        self.input_x.setValue(x)
        self.input_y.setValue(y)
        self.input_width.setValue(width)
        self.input_height.setValue(height)

    def openDialogFile(self):
        file_name, _ = QFileDialog.getOpenFileName(self, caption='Chọn file hình logo',
                                                dir=(self.app_path), filter='File Ảnh (*.png *.jpg *jpeg)')
        self.input_src_pixmap.setText(file_name)


    def save(self):

            self.accept()

    def getValue(self) -> dict:
        return {
            "x":self.input_x.value(),
            "y":self.input_y.value(),
            "width":self.input_width.value(),
            "height":self.input_height.value(),
            "pixmap":self.input_src_pixmap.text(),
        }


    # def clearData(self):
        # if hasattr(self, "cau_hinh"):
        #     delattr(self, "cau_hinh")

