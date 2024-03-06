from __future__ import print_function

import builtins
import os
import sys

from PySide6.QtCore import QDir

from gui.helpers.check_single_app import QtSingleApplication
from gui.helpers.func_helper import iconFromBase64
from gui.windows.login_window import LoginWindow
from style import style, icon_logo, mytheme




if __name__ == "__main__":
	
	app = QtSingleApplication('82A6DB9245A2-F3FF80BA-BA05-4277-8063_NTSVIDEO_CREATOR', sys.argv)
	# print(app.isRunning())
	if app.isRunning():
		sys.exit(0)
	
	extra = {
		
		# Button colors
		'danger': '#dc3545',
		'warning': '#ffc107',
		'success': '#17a2b8',
		
		# Font
		'font_family': 'Roboto',
		'density_scale': '-1',
	}
	app.setWindowIcon(iconFromBase64(icon_logo))
	# setup stylesheet
	# apply_stylesheet(app, theme='my_theme.xml', extra=extra)
	# Load styles
	# with open('my_theme.qss', 'r') as file:
		# print(file.read())
	app.setStyleSheet(mytheme + style.format(**os.environ))
	# Load icons
	QDir.addSearchPath('icon', 'theme')
	
	# stylesheet = app.styleSheet()
	# app.setStyleSheet(stylesheet + style.format(**os.environ))

	_print = print  # keep a local copy of the original print
	# print( 'self' in sys._getframe(1).f_locals.keys())
	#            f"{sys._getframe().f_back.f_lineno} {' - ' + sys._getframe(1).f_locals['self'].__class__.__name__ + ' - ' + sys._getframe().f_back.f_code.co_name} \n",

	builtins.print = lambda *args, **kwargs: _print(
		f"{sys._getframe().f_back.f_lineno} {' - ' + sys._getframe().f_back.f_code.co_name} \n",
		*args, **kwargs)

	window = LoginWindow(sys.argv[0])
	window.show()
	
	sys.exit(app.exec())
