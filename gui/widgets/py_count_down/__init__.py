import enum

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QColorConstants
from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout, QLabel


class TimerStatus(enum.Enum):
	init, counting, paused = 1, 2, 3


class ButtonText:
	start, pause, reset = "Start", "Pause", "Reset"


class TimeCountDown(QWidget):
	finishedSignal = Signal()
	def __init__ (self, time_count, parent=None):
		super().__init__(parent)
		self.displayArea = QTextEdit()
		self.displayArea.setTextColor("#f6f2c8")
		self.displayArea.setStyleSheet("border: none")
		self.displayArea.setFontFamily("Arial")
		self.displayArea.setFontPointSize(18)
		self.displayArea.setTextInteractionFlags(Qt.NoTextInteraction)
		self.displayArea.viewport().setCursor(Qt.ArrowCursor)
		self.displayArea.viewport().installEventFilter(self)
		self.displayArea.setMaximumHeight(45)
		self.setWidgets()
		self._status = TimerStatus.init
		self._left_seconds = 0
		self.time_count = time_count
		self.timer = QTimer()
		self.timer.timeout.connect(self._countdown_and_show)
		self.showTime()
		self._countdown_and_show()
		self._start_event()
	
	
	def _countdown_and_show (self):
		# print('_countdown_and_show')
		if self._left_seconds > 0:
			self._left_seconds -= 1
			self.showTime()
		else:
			self.timer.stop()
			self.showTime()
			# self.startButton.setText(ButtonText.start)
			self._status = TimerStatus.init
			self._left_seconds = self.time_count * 60
		
		if self._left_seconds == 0:
			self.finishedSignal.emit()
	
	def _start_event (self):
		# print('_start_event')

		if (self._status == TimerStatus.init or self._status == TimerStatus.paused) and self._left_seconds > 0:
			self._left_seconds -= 1
			self._status = TimerStatus.counting
			self.showTime()
			self.timer.start(1000)
		# self.startButton.setText(ButtonText.pause)
		elif self._status == TimerStatus.counting:
			self.timer.stop()
			self._status = TimerStatus.paused
		# self.startButton.setText(ButtonText.start)
	
	def _reset_event (self):
		self._status = TimerStatus.init
		self._left_seconds = self.time_count * 60
		# self.startButton.setText(ButtonText.start)
		self.timer.stop()
		self.showTime()
	
	def _edit_event (self):
		if self._status == TimerStatus.init:
			self._left_seconds = self.time_count * 60
			self.showTime()
	
	def showTime (self):
		total_seconds = min(self._left_seconds, 359940)  # Max time: 99:59:00
		hours = total_seconds // 3600
		total_seconds = total_seconds - (hours * 3600)
		minutes = total_seconds // 60
		seconds = total_seconds - (minutes * 60)
		self.displayArea.setText("{:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds)))
		self.displayArea.setAlignment(Qt.AlignHCenter)
	
	def setWidgets (self):
		# hbox = QHBoxLayout()
		# hbox.addWidget(self.minutesLabel)
		# hbox.addWidget(self.minutesSpinBox)
		# hbox.addWidget(self.startButton)
		# hbox.addWidget(self.resetButton)
		# hbox.setAlignment(Qt.AlignLeft)
		vbox = QVBoxLayout()
		# vbox.addLayout(hbox)
		vbox.addWidget(QLabel("Thời Gian Hết Hạn:"))
		vbox.addWidget(self.displayArea)
		vbox.addWidget(QLabel(""),30)
		self.setLayout(vbox)
