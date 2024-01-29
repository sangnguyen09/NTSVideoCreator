from PySide6.QtWidgets import QWidget


class TenClass(QWidget):
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
        pass

    def modify_widgets(self):
        pass

    def create_layouts(self):
        pass

    def add_widgets_to_layouts(self):
        pass

    def setup_connections(self):
        pass
