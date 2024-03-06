from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox

from gui.widgets.py_table_widget.table_timeline_add_sub import TableTimelineAddSub


class GroupBoxTimeLine(QWidget):
    def __init__(self):
        super().__init__()

        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):

        self.table_timeline = TableTimelineAddSub()


    def modify_widgets(self):
        pass
        # self.setStyleSheet(style_format)

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()
        self.bg_layout.setContentsMargins(0,0,0,0)
        self.groupbox = QGroupBox("Timeline")

        self.content_layout = QVBoxLayout()
        self.groupbox.setLayout(self.content_layout)


    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)

        self.content_layout.addWidget(QLabel(""))
        self.content_layout.addWidget(self.table_timeline,80)

    def setup_connections(self):
        pass
        # self.text_fixed_password.textChanged.connect(self.saveConfig)
        # self.textarea_list_password.textChanged.connect(self.saveConfig)
        # self.rad_random_password.toggled.connect(lambda: self.check_radio_button(self.rad_random_password))
        # self.rad_fixed_password.toggled.connect(lambda: self.check_radio_button(self.rad_fixed_password))
        # self.rad_list_password.toggled.connect(lambda: self.check_radio_button(self.rad_list_password))


    def loadData(self,data):
        self.table_timeline.displayTable(data)

