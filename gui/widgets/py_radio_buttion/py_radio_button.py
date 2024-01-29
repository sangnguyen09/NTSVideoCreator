
# IMPORT QT CORE
# ///////////////////////////////////////////////////////////////
from PySide6.QtWidgets import QRadioButton


class PyRadioButton(QRadioButton):
    def __init__(
            self,
            value,
            text="",

    ):
        super().__init__()

        # self.setup_ui()
        # # PARAMETERS
        if text:
            self.setText(text)

        self.value = value

    def getValue(self):
        return self.value
