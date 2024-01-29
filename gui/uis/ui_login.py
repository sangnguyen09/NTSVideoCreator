from PySide6.QtCore import Qt, QRect, QCoreApplication, QMetaObject
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QCheckBox, \
	QLineEdit

from gui.configs.config_resource import ConfigResource


# from resource import *
resource = ConfigResource


class PasswordEdit(QLineEdit):
	"""
	A LineEdit with icons to show/hide password entries
	"""
	CSS = """QLineEdit {
        border-radius: 0px;
        height: 30px;
        margin: 0px 0px 0px 0px;
    }
    """
	
	def __init__ (self, parent):
		self.parent = parent
		super().__init__(self.parent)
		
		# Set styles
		# self.setStyleSheet(self.CSS)
		
		self.visibleIcon = QIcon(resource.set_svg_icon('eye_on.png'))
		self.hiddenIcon = QIcon(resource.set_svg_icon('eye_off.png'))
		
		self.setEchoMode(QLineEdit.EchoMode.Password)
		self.togglepasswordAction = self.addAction(self.visibleIcon, QLineEdit.ActionPosition.TrailingPosition)
		self.togglepasswordAction.triggered.connect(self.on_toggle_password_Action)
		self.password_shown = False
	
	def on_toggle_password_Action (self):
		if not self.password_shown:
			self.setEchoMode(QLineEdit.EchoMode.Normal)
			self.password_shown = True
			self.togglepasswordAction.setIcon(self.hiddenIcon)
		else:
			self.setEchoMode(QLineEdit.EchoMode.Password)
			self.password_shown = False
			self.togglepasswordAction.setIcon(self.visibleIcon)


class Ui_Login(object):
	def setupUi (self, Login):
		if not Login.objectName():
			Login.setObjectName(u"Login")
		Login.resize(450, 550)
		self.widget = QWidget(Login)
		self.widget.setObjectName(u"widget")
		self.widget.setEnabled(True)
		self.widget.setStyleSheet("background-color:None")
		self.widget.setGeometry(QRect(30, 30, 400, 600))
		
		self.bg_img = QLabel(self.widget)
		self.bg_img.setObjectName(u"bg_img")
		self.bg_img.setGeometry(QRect(0, 0, 350, 500))
		style = f"""
            #bg_img {{
             border-image: url(images/bg_login.jpg);
             border-radius:20px;
            }}
        """
		self.bg_img.setStyleSheet(style)
		
		self.bg_gradient = QLabel(self.widget)
		self.bg_gradient.setObjectName(u"label_2")
		self.bg_gradient.setGeometry(QRect(0, 0, 350, 500))
		self.bg_gradient.setStyleSheet(u"\n"
									   "border-radius:20px;\n"
									   "background-color: qlineargradient(spread:pad, x1:0.547949, y1:0.29, x2:0.537746, y2:0.671, stop:0 rgba(0, 0, 0, 0), stop:1 rgba(50, 50, 50, 147));")
		self.bg_gradient.setIndent(0)
		self.bg_form = QLabel(self.widget)
		self.bg_form.setObjectName(u"label_3")
		self.bg_form.setGeometry(QRect(10, 10, 330, 480))
		self.bg_form.setStyleSheet(u"background-color:rgba(0,0,0,100);\n"
								   "border-radius:15px;")
		self.lb_title_form = QLabel(self.widget)
		self.lb_title_form.setObjectName(u"lb_title_form")
		self.lb_title_form.setGeometry(QRect(100, 30, 161, 41))
		
		self.lb_title_form.setStyleSheet(u"color: rgb(230, 230, 230); font-size:30px")
		self.lb_title_form.setAlignment(Qt.AlignmentFlag.AlignCenter)
		
		self.label_username = QLabel(self.widget)
		self.label_username.setObjectName(u"label_5")
		self.label_username.setGeometry(QRect(30, 120, 91, 16))
		# font1 = QFont()
		# font1.setPointSize(11)
		# font1.setBold(True)
		# self.label_5.setFont(font1)
		self.label_username.setStyleSheet(u"color: rgb(255, 255, 255);")
		self.username = QLineEdit(self.widget)
		self.username.setObjectName(u"username")
		self.username.setGeometry(QRect(30, 150, 290, 31))
		self.username.setStyleSheet(u"background-color: rgba(0, 0, 0,0);\n"
									"border:none;\n"
									"border-bottom:2px solid rgba(105,118,132,255);\n"
									"color:rgba(255,255,255,230);\n"
									"padding-bottom:7px;")
		self.password = PasswordEdit(self.widget)
		self.password.setObjectName(u"password")
		self.password.setGeometry(QRect(30, 240, 290, 31))
		self.password.setStyleSheet(u"background-color: rgba(0, 0, 0,0);\n"
									"border:none;\n"
									"border-bottom:2px solid rgba(105,118,132,255);\n"
									"color:rgba(255,255,255,230);\n"
									"padding-bottom:7px;")
		self.password.setEchoMode(QLineEdit.EchoMode.Password)
		self.label_pass = QLabel(self.widget)
		self.label_pass.setObjectName(u"label_6")
		self.label_pass.setGeometry(QRect(30, 210, 91, 16))
		# self.label_6.setFont(font1)
		self.label_pass.setStyleSheet(u"color: rgb(255, 255, 255);")
		
		self.remember_account = QCheckBox(self.widget)
		self.remember_account.setText("Remember me")
		self.remember_account.setGeometry(QRect(30, 280, 161, 41))
		
		self.logout = QPushButton(self.widget)
		self.logout.setText("Đăng Xuất")
		self.logout.setObjectName(u"logout")
		
		self.logout.setCursor(Qt.CursorShape.PointingHandCursor)
		
		self.logout.setGeometry(QRect(220, 290, 100, 20))
		self.logout.setStyleSheet(u"QPushButton#logout{\n"
								  "	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(20, 47, 78, 219), stop:1 rgba(85, 98, 112, 226));\n"
								  "color:rgba(255,255,255,210);\n"
								  "border-radius:5px;\n"
								  "}\n"
								  "QPushButton#logout:hover {\n"
								  "	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(40, 67, 98, 219), stop:1 rgba(105, 118, 132, 226));\n"
								  " \n"
								  "}\n"
								  "QPushButton#logout:pressed {\n"
								  "	background-color: rgba(105,118,132,200); \n"
								  "padding-left:5px;\n"
								  "padding-top:5px;\n"
								  "}")
		
		self.saveForm = QPushButton(self.widget)
		self.saveForm.setCursor(Qt.CursorShape.PointingHandCursor)
		self.saveForm.setObjectName(u"saveForm")
		self.saveForm.setGeometry(QRect(100, 330, 150, 41))
		
		self.saveForm.setAutoFillBackground(False)
		self.saveForm.setStyleSheet(u"QPushButton#saveForm{\n"
									"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(20, 47, 78, 219), stop:1 rgba(85, 98, 112, 226));\n"
									"color:rgba(255,255,255,210);\n"
									"border-radius:5px;\n"
									"}\n"
									"QPushButton#saveForm:hover {\n"
									"	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(40, 67, 98, 219), stop:1 rgba(105, 118, 132, 226));\n"
									" \n"
									"}\n"
									"QPushButton#saveForm:pressed {\n"
									"	background-color: rgba(105,118,132,200); \n"
									"padding-left:5px;\n"
									"padding-top:5px;\n"
									"}")
		self.saveForm.setAutoDefault(False)
		self.saveForm.setFlat(False)
		#
		self.label_7 = QLabel(self.widget)
		self.label_7.setObjectName(u"label_7")
		self.label_7.setGeometry(QRect(60, 380, 131, 21))
		self.label_7.setStyleSheet(u"color: rgb(255, 255, 255);")
		
		self.dangKy = QPushButton(self.widget)
		self.dangKy.setObjectName(u"dangNhap")
		self.dangKy.setGeometry(QRect(200, 380, 100, 21))
		self.dangKy.setAutoFillBackground(False)
		self.dangKy.setStyleSheet(u"QPushButton#dangNhap{\n"
								  "	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(20, 47, 78, 219), stop:1 rgba(85, 98, 112, 226));\n"
								  "color:rgba(255,255,255,210);\n"
								  "border-radius:5px;\n"
								  "}\n"
								  "QPushButton#dangNhap:hover {\n"
								  "	background-color: qlineargradient(spread:pad, x1:0, y1:0.505682, x2:1, y2:0.477, stop:0 rgba(40, 67, 98, 219), stop:1 rgba(105, 118, 132, 226));\n"
								  " \n"
								  "}\n"
								  "QPushButton#dangNhap:pressed {\n"
								  "	background-color: rgba(105,118,132,200); \n"
								  "padding-left:1px;\n"
								  "padding-top:1px;\n"
								  "}")
		self.dangKy.setCheckable(False)
		self.dangKy.setAutoDefault(False)
		self.dangKy.setFlat(False)
		
		self.lb_contact_admin = QLabel(self.widget)
		self.lb_contact_admin.setObjectName(u"lb_contact_admin")
		self.lb_contact_admin.setGeometry(QRect(30, 420, 290, 16))
		self.lb_contact_admin.setStyleSheet(u"color: rgb(255, 0, 0);")
		
		self.lb_fb = QLabel()
		self.lb_fb.setParent(self.widget)
		self.lb_fb.setGeometry(QRect(30, 450, 290, 16))
		self.lb_fb.setText('''<a style="color:white" href='http://fb.com/sangnguyen09'>Facebook Admin</a>''')
		self.lb_fb.setOpenExternalLinks(True)
		
		self.lb_zalo = QLabel()
		self.lb_zalo.setParent(self.widget)
		self.lb_zalo.setGeometry(QRect(150, 450, 290, 16))
		self.lb_zalo.setText('''<a style="color:white" href='https://zalo.me/0985026855'>Zalo Admin</a>''')
		self.lb_zalo.setOpenExternalLinks(True)
		
		# self.lb_spinner = QLabel()
		# self.lb_spinner.setParent(self.widget)
		# self.lb_spinner.setGeometry(QRect(150, 200, 200, 200))
		# print(ConfigResource.set_svg_icon("Spinner.gif"))
		# self.movie = QMovie(ConfigResource.set_svg_icon("Spinner.gif"))
		# self.lb_spinner.setMovie(QMovie(self.movie ))
		# self.movie.start()
		#
		self.retranslateUi(Login)
		
		QMetaObject.connectSlotsByName(Login)
	
	# setupUi
	
	def retranslateUi (self, Login):
		Login.setWindowTitle(QCoreApplication.translate("Login", u"Form", None))
		self.bg_img.setText("")
		self.bg_gradient.setText("")
		self.bg_form.setText("")
		self.lb_title_form.setText(QCoreApplication.translate("Login", u"\u0110\u0103ng Nh\u1eadp", None))
		self.label_username.setText(QCoreApplication.translate("Login", u"Username", None))
		self.username.setPlaceholderText(QCoreApplication.translate("Login", u"Nh\u1eadp t\u00ean username", None))
		self.password.setPlaceholderText(QCoreApplication.translate("Login", u"Nh\u1eadp m\u1eadt kh\u1ea9u", None))
		self.label_pass.setText(QCoreApplication.translate("Login", u"Password", None))
		self.saveForm.setText(QCoreApplication.translate("Login", u"\u0110\u0103ng Nh\u1eadp", None))
		self.label_7.setText(QCoreApplication.translate("Login", u"B\u1ea1n ch\u01b0a c\u00f3 t\u00e0i kho\u1ea3n ?", None))
		self.dangKy.setText(QCoreApplication.translate("Login", u"\u0110\u0103ng K\u00fd", None))
		self.lb_contact_admin.setText(QCoreApplication.translate("Login", u"Vui l\u00f2ng li\u00ean h\u1ec7 admin \u0111\u1ec3 \u0111\u01b0\u1ee3c k\u00edch ho\u1ea1t t\u00e0i kho\u1ea3n", None))
# retranslateUi
