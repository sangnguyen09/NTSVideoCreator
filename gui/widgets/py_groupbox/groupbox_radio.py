from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QRadioButton


class GroupBoxRadio(QWidget):
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
        self.rad1 = QRadioButton("Apple")
        self.rad2 = QRadioButton("Banana")
        self.rad3 = QRadioButton("Melon")

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.hbox = QHBoxLayout()
        self.groupbox = QGroupBox("Lựa chọn trái cây ưa thích của bạn ")
        self.groupbox.setFont(QFont("Sanserif", 15))
        self.vbox = QVBoxLayout()
        self.groupbox.setLayout(self.vbox)


    def add_widgets_to_layouts(self):
        self.hbox.addWidget(self.groupbox)
        self.setLayout(self.hbox)
        self.vbox.addWidget(self.rad1)
        self.vbox.addWidget(self.rad2)
        self.vbox.addWidget(self.rad3)

    def setup_connections(self):
        pass
