from PySide6.QtWidgets import QDialog, QMessageBox

from gui.configs.config_theme import ConfigTheme


style = '''
QDialog {{
	background-color: {_bg_color};
	font-size:15px;
	font-weight:bold;
	color: {_color};
	 min-width: 200px; min-height: 100px;


}}
QLabel{{
 color: {_color};
}}
QGroupBox{{
 color: {_color}
}}
 
'''


# call api load dịch vụ


class PyMessageBox(QDialog):
    def __init__(self):
        super().__init__()
        self.msg = QMessageBox()
        self.msg.setObjectName(u"messageBox")

        self.themes = ConfigTheme()
        self.style_format = style.format(
            _bg_color="#4b4b4b",
            _color=self.themes.app_color["white"],
        )

        self.msg.setStyleSheet("background-color: rgb(0, 0, 0);color: rgb(255, 255, 255);")
        self.setStyleSheet(self.style_format)

    def show_about(self, title, message):
        message = f'<p style="font-size:15px; font-weight:bold; ">{message}</p>'
        self.msg.about(self, title, message)

    def show_warning(self, title, message):
        message = f'<p style="font-size:15px; font-weight:bold; color: #fcff0b;">{message}</p>'
        self.msg.warning(self, title, message)

    def show_error(self, title, message):
        message = f'<p style="font-size:15px; font-weight:bold; color: #ff0000;">{message}</p>'
        self.msg.critical(self, title, message)

    def show_info(self, title, message):
        message = f'<p style="font-size:15px; font-weight:bold; color: #30ff00;">{message}</p>'
        self.msg.information(self, title, message)

    def show_question(self, title, message):
        message = f'<p style="font-size:15px; font-weight:bold; color: #30ff00;">{message}</p>'
        reply = self.msg.question(self, title, message, QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            return True

        elif reply == QMessageBox.No:
            return False
