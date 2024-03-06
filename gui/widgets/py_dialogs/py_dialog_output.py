import json
import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, QDialog, \
	QComboBox, \
	QSlider, QRadioButton, QFileDialog, QSpinBox

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import PATH_OUTPUT, SETTING_APP_DATA, TOOL_CODE_MAIN, FORMAT_OUTPUT_VIDEO, \
	PRESET_OUTPUT_VIDEO, RENDER_STYLE
from gui.helpers.func_helper import getValueSettings
from gui.widgets.py_buttons.py_push_button import PyPushButton
from gui.widgets.py_checkbox import PyCheckBox
from gui.widgets.py_dialogs.py_dialog_show_info import PyDialogShowInfo
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


class PyDialogOutput(QDialog):
	def __init__ (self):
		super().__init__()
		# LOAD SETTINGS
		# ///////////////////////////////////////////////////////////////
		# st = QSettings(*SETTING_APP)
		self.settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN)
		self.setMinimumWidth(900)
		# LOAD THEME COLOR
		# ///////////////////////////////////////////////////////////////
		self.themes = ConfigTheme()
		self.style_format = style.format(
			_bg_color=self.themes.app_color["bg_one"],
			_color=self.themes.app_color["white"],
		)
		
		# SET UP MAIN WINDOW
		self.setWindowTitle("Định Dạng Xuất Ra Video")
		self.setStyleSheet(self.style_format)
		
		self.src_ouput_default = PATH_OUTPUT
		self.setup_ui()
		
		self.list_proxy = None
	
	def setup_ui (self):
		self.create_widgets()
		self.modify_widgets()
		self.create_layouts()
		self.add_widgets_to_layouts()
		self.setup_connections()
	
	def create_widgets (self):
		self.groupbox_bit_rate = QGroupBox("Cân Chỉnh Mã Hóa Đầu Ra:")
		
		self.lb_bitrate_video = QLabel("Bit Rate Video")
		
		self.slider_bitrate_video = QSlider()
		self.slider_bitrate_video.setOrientation(Qt.Orientation.Horizontal)
		self.slider_bitrate_video.setRange(2000, 100000)
		self.slider_bitrate_video.setValue(10000)
		self.lb_number_slider_video = QLabel()
		self.lb_number_slider_video.setText(str(self.slider_bitrate_video.value()) + "kb/s")
		
		self.lb_bitrate_audio = QLabel("Bit Rate Audio")
		
		self.slider_bitrate_audio = QSlider()
		self.slider_bitrate_audio.setOrientation(Qt.Orientation.Horizontal)
		self.slider_bitrate_audio.setRange(2000, 100000)
		self.slider_bitrate_audio.setValue(10000)
		
		self.lb_number_slider_audio = QLabel()
		self.lb_number_slider_audio.setText(str(self.slider_bitrate_audio.value()) + "kb/s")
		
		self.lb_slider_crf = QLabel("Hệ số chất lượng:")
		self.slider_crf = QSlider()
		self.slider_crf.setOrientation(Qt.Orientation.Horizontal)
		self.slider_crf.setRange(0, 46)
		self.slider_crf.setValue(20)
		self.lb_number_slider_crf = QLabel()
		self.lb_number_slider_crf.setText(str(self.slider_crf.value()))
		
		self.lb_preset = QLabel("Tốc Độ Mã Hóa:")
		self.cbobox_preset = QComboBox()  # tốc độ mã hóa
		self.cbobox_preset.addItems(PRESET_OUTPUT_VIDEO)
		
		self.lb_frame = QLabel("Tốc Độ Khung Hình FPS:")
		self.cbobox_fps = QComboBox()
		self.cbobox_fps.addItems([str(i) for i in range(20, 61)])
		# self.cbobox_fps.setCurrentText(str(30))
		
		self.lb_thread = QLabel("Số Luồng:")
		self.cbobox_thread = QComboBox()
		self.cbobox_thread.addItems([str(i) for i in range(1, 15)])
		# self.cbobox_thread.setCurrentText(str(2))
		
		self.cbobox_preset.setCurrentText("superfast")
		
		self.cb_delete_data = PyCheckBox(value="delete_data_output", text="Xóa Dữ Liệu Sau Khi Hoàn Thành")
		self.cb_show_log = PyCheckBox(value="show_log", text="Show Log")
		

		
		self.lb_render_style = QLabel("Render Style:")
		self.cbobox_render_style = QComboBox()
		self.cbobox_render_style.addItems(RENDER_STYLE)
		
		self.groupbox_ouput = QGroupBox("OUTPUT Format")
		
		self.lb_folder_output = QLabel("Thư Mục Output:")
		self.btn_dialog_folder_output = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("open-file.png"),
			parent=self,
			app_parent=self,
			icon_color="#f5ca1e",
			icon_color_hover="#ffe270",
			icon_color_pressed="#d1a807",
		
		)
		self.input_src_output = QLineEdit()
		self.input_src_output.setReadOnly(True)
		
		self.lb_rate_format = QLabel("Tỉ lệ Video:")
		self.cbobox_rate_format = QComboBox()
		
		self.lb_quantity_format = QLabel("Chất lượng Video:")
		self.cbobox_quantity_format = QComboBox()
		#
		
		self.lb_input_width = QLabel("Width:")
		self.input_width = QSpinBox()
		self.input_width.setMinimum(300)
		self.input_width.setMaximum(5000)
		
		self.lb_input_height = QLabel("Height:")
		self.input_height = QSpinBox()
		self.input_height.setMinimum(300)
		self.input_height.setMaximum(5000)
		#
		
		self.lb_quantity_format = QLabel("Chất lượng Video:")
		self.cbobox_quantity_format = QComboBox()
		#
		
		self.lb_ext_output = QLabel("Định Dạng Video:")
		self.cbobox_ext_format = QComboBox()
		self.cbobox_ext_format.addItems(['mp4', 'avi', 'wmv', 'flv', 'mkv', 'mov'])
		self.cbobox_ext_format.setCurrentText("mp4")
		
		self.lb_hau_to_video_output = QLabel("Thêm Hậu Tố Vào Tên Video Output:")
		self.input_hau_to_video_output = QLineEdit()
		
		self.buttonSave = PyPushButton(text="Lưu", font_size="15px", radius="6px", color="#fff", bg_color1="#1aff86",
			bg_color2="#0bcc5d", bg_color_hover="#0bcc5d", parent=self)
		
		text = "- Bitrate:"
		text += "\n + Là lượng dữ liệu được gửi trong một thời gian nhất định."
		text += "\n + Nếu bitrate thấp, tốc độ khung hình và độ phân giải của video sẽ bị ảnh hưởng."
		
		text += "\n\n- Hệ Số Chất Lượng:"
		text += "\n + Số càng bé thì chất lượng đầu ra càng tốt nhưng dung lượng file sẽ càng lớn và ngược lại."
		text += "\n + Nếu muốn giảm dung lượng mà chất lượng tốt thì chọn Tốc Độ Mã Hóa chậm hơn để nén file tốt hơn."
		
		text += "\n\n- Tốc Độ Mã Hóa:"
		text += "\n + Là tốc độ nén file đầu ra."
		text += "\n + Giá trị chậm hơn sẽ có thời gian render lâu hơn nhưng dung lượng file sẽ nhỏ hơn."
		text += "\n + Nếu bạn không quan tâm đến dung lượng file thì có thể chọn tốc độ cao."
		text += "\n + Kết hợp với Hệ Số Chất Lượng để có thể tối ưu theo nhu cầu của bạn."
		
		text += "\n\n- Tốc Độ Khung Hình FBS:"
		text += "\n + Là số lượng khung hình trên giây."
		text += "\n + FPS càng cao, thì hình ảnh sẽ mượt hơn."
		text += "\n + Trong khoảng 25-30 fps là tốc độ chuẩn thường được sử dụng, hình ảnh mượt mà và không gây mỏi mắt."
		text += "\n + Tốc độ cao lên đến 60 fps cho trải nghiệm chất lượng tốt nhất. "
		
		text += "\n\n- Xoá Dữ Liệu Sau Khi Hoàn Thành:"
		text += "\n + Nếu tích chọn thì sub đã chuyển theo giọng đọc được lấy trước đó sẽ bị xóa"
		text += "\n + Nếu bạn muốn sử dụng lại GIỌNG ĐỌC cũ và MODE cũ chỉ thay đổi lại hình ảnh video thì bỏ tích chọn. Tool sẽ bỏ qua phần tạo giọng đọc, giúp tiết kiệm ký tự."
		
		self.dialog_info = PyDialogShowInfo(text, 600, font_size=14)
		self.btn_info_frame = PyButtonIcon(
			icon_path=ConfigResource.set_svg_icon("info.png"),
			parent=self,
			width=30,
			height=30,
			icon_color="#2678ff",
			icon_color_hover="#4d8df6",
			icon_color_pressed="#6f9deb",
			app_parent=self,
			tooltip_text="Hướng dẫn"
		
		)
	
	def modify_widgets (self):
		self.cbobox_rate_format.addItems(list(FORMAT_OUTPUT_VIDEO.keys()))
		format = FORMAT_OUTPUT_VIDEO.get(self.cbobox_rate_format.currentText())
		self.cbobox_quantity_format.addItems(list(format.values()))
	
	def create_layouts (self):
		self.app_layout = QVBoxLayout()
		self.app_layout.setContentsMargins(0, 0, 0, 0)
		self.content_frame = QWidget()
		self.content_layout = QVBoxLayout(self.content_frame)
		
		self.gbox_bitrate_layout = QGridLayout()
		self.gbox_bitrate_layout.setContentsMargins(0, 0, 0, 0)
		
		self.gbox_format_layout = QGridLayout()
		self.gbox_format_layout.setContentsMargins(0, 0, 0, 0)
		
		self.btn_layout = QHBoxLayout()
	
	def add_widgets_to_layouts (self):
		self.app_layout.addWidget(self.content_frame)
		self.setLayout(self.app_layout)
		
		self.content_layout.addWidget(self.groupbox_bit_rate, 10)
		self.content_layout.addWidget(self.groupbox_ouput, 70)
		self.content_layout.addLayout(self.btn_layout, 20)
		
		self.groupbox_bit_rate.setLayout(self.gbox_bitrate_layout)
		
		self.gbox_bitrate_layout.addWidget(self.lb_bitrate_video, 0, 0, 1, 2)
		self.gbox_bitrate_layout.addWidget(self.slider_bitrate_video, 0, 2, 1, 7)
		self.gbox_bitrate_layout.addWidget(self.lb_number_slider_video, 0, 9, 1, 3)
		
		self.gbox_bitrate_layout.addWidget(self.lb_bitrate_audio, 1, 0, 1, 2)
		self.gbox_bitrate_layout.addWidget(self.slider_bitrate_audio, 1, 2, 1, 7)
		self.gbox_bitrate_layout.addWidget(self.lb_number_slider_audio, 1, 9, 1, 3)
		
		# self.gbox_bitrate_layout.addWidget(QLabel(), 1, 0)
		
		self.gbox_bitrate_layout.addWidget(self.lb_slider_crf, 2, 0, 1, 2)
		self.gbox_bitrate_layout.addWidget(self.slider_crf, 2, 2, 1, 7)
		self.gbox_bitrate_layout.addWidget(self.lb_number_slider_crf, 2, 9, 1, 3)
		# self.gbox_bitrate_layout.addWidget(QLabel(), 3, 0)
		
		self.gbox_bitrate_layout.addWidget(self.lb_preset, 4, 0, 1, 2)
		self.gbox_bitrate_layout.addWidget(self.cbobox_preset, 4, 2)
		# self.gbox_bitrate_layout.addWidget(QLabel(), 4, 3)
		self.gbox_bitrate_layout.addWidget(self.lb_frame, 4, 3, alignment=Qt.AlignmentFlag.AlignRight)
		self.gbox_bitrate_layout.addWidget(self.cbobox_fps, 4, 4,1,2)
		self.gbox_bitrate_layout.addWidget(self.lb_thread, 4, 6, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)
		self.gbox_bitrate_layout.addWidget(self.cbobox_thread, 4, 8,1,2)
		self.gbox_bitrate_layout.addWidget(self.cb_show_log, 4, 10, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)
		# self.gbox_bitrate_layout.addWidget(self.cb_concat2, 4, 10, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)
		
		self.gbox_bitrate_layout.addWidget(self.lb_render_style, 5, 0, 1, 2)
		self.gbox_bitrate_layout.addWidget(self.cbobox_render_style, 5, 2, 1, 2)
		self.gbox_bitrate_layout.addWidget(QLabel(), 5, 4)
		self.gbox_bitrate_layout.addWidget(self.cb_delete_data, 5, 5, 1, 6)
		# self.gbox_bitrate_layout.addWidget(self.cb_show_log, 5, 10)
		self.gbox_bitrate_layout.addWidget(self.btn_info_frame, 5, 11)
		
		self.groupbox_ouput.setLayout(self.gbox_format_layout)
		
		self.gbox_format_layout.addWidget(self.lb_folder_output, 0, 0, 1, 2)
		self.gbox_format_layout.addWidget(self.input_src_output, 0, 2, 1, 9)
		self.gbox_format_layout.addWidget(self.btn_dialog_folder_output, 0, 11)
		
		self.gbox_format_layout.addWidget(self.lb_rate_format, 1, 0, 1, 2)
		self.gbox_format_layout.addWidget(self.cbobox_rate_format, 1, 2, 1, 3)
		self.gbox_format_layout.addWidget(QLabel(""), 1, 5, 1, 2)
		self.gbox_format_layout.addWidget(self.lb_quantity_format, 1, 7, 1, 2)
		self.gbox_format_layout.addWidget(self.cbobox_quantity_format, 1, 9, 1, 3)
		
		self.gbox_format_layout.addWidget(self.lb_input_width, 2, 0, 1, 2)
		self.gbox_format_layout.addWidget(self.input_width, 2, 2, 1, 3)
		self.gbox_format_layout.addWidget(QLabel(""), 2, 5, 1, 2)
		self.gbox_format_layout.addWidget(self.lb_input_height, 2, 7, 1, 2)
		self.gbox_format_layout.addWidget(self.input_height, 2, 9, 1, 3)
		
		self.gbox_format_layout.addWidget(self.lb_ext_output, 3, 0, 1, 2)
		self.gbox_format_layout.addWidget(self.cbobox_ext_format, 3, 2, 1, 3)
		# self.gbox_format_layout.addWidget(QLabel(""), 2, 5, 1, 4)
		self.gbox_format_layout.addWidget(self.lb_hau_to_video_output, 3, 5, 1, 4, alignment=Qt.AlignmentFlag.AlignRight)
		self.gbox_format_layout.addWidget(self.input_hau_to_video_output, 3, 9, 1, 3)
		
		self.btn_layout.addWidget(QLabel(""), 40)
		self.btn_layout.addWidget(self.buttonSave, 20)
		self.btn_layout.addWidget(QLabel(""), 40)
	
	def setup_connections (self):
		self.buttonSave.clicked.connect(self.save)
		self.btn_dialog_folder_output.clicked.connect(self.openDialogFolder)
		self.cbobox_rate_format.currentIndexChanged.connect(self.index_rate_format_Changed)
		self.cbobox_quantity_format.currentIndexChanged.connect(self.change_size_format)
		# self.rad_bitrate_tuy_chinh.clicked.connect(lambda: self.check_radio_changed())
		# self.lb_bitrate_video.clicked.connect(lambda: self.check_radio_changed())
		self.slider_bitrate_video.valueChanged.connect(self.sliderVideoValueChanged)
		self.slider_bitrate_audio.valueChanged.connect(self.sliderAudioValueChanged)
		self.slider_crf.valueChanged.connect(self.sliderCRFValueChanged)
		self.btn_info_frame.clicked.connect(self.dialog_info.exec)
	
	def sliderCRFValueChanged (self, value):
		self.lb_number_slider_crf.setText(str(value))
	
	def sliderAudioValueChanged (self, value):
		self.lb_number_slider_audio.setText(str(value) + "kb/s")
	
	def sliderVideoValueChanged (self, value):
		self.lb_number_slider_video.setText(str(value) + "kb/s")
	
	def index_rate_format_Changed (self):
		self.change_size_format()
	
	def change_size_format (self):
		format_quantity = FORMAT_OUTPUT_VIDEO.get(self.cbobox_rate_format.currentText())
		kich_thuoc = list(format_quantity.keys())[self.cbobox_quantity_format.currentIndex()]
		try:
			w, h = kich_thuoc.split("|")
			# print(w, h)
			self.input_width.setValue(int(w))
			self.input_height.setValue(int(h))
		
		except:
			print("Không lấy được kích thước")
	
	def loadData (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
		cau_hinh: dict = json.loads(configCurrent.value)
		# print(cau_hinh)
		for rb in self.groupbox_bit_rate.findChildren(QRadioButton):
			if rb.getValue() == cau_hinh["bit_rate"]:
				# self.rad_bitrate_tuy_chinh.setChecked()
				rb.setChecked(True)
		# self.lb_number_slider.setText(str(cau_hinh.get('bit_rate_value_tuy_chinh')) + "kb/s")
		self.slider_bitrate_video.setValue(cau_hinh.get('bit_rate_video'))
		self.slider_bitrate_audio.setValue(cau_hinh.get('bit_rate_audio'))
		# if cau_hinh["bit_rate"] == 'tuy_chinh':
		# 	self.slider_bitrate_video.setDisabled(False)
		# 	self.lb_bitrate_video.setChecked(False)
		# 	self.rad_bitrate_tuy_chinh.setChecked(True)
		# 	self.lb_number_slider_video.setText(str(cau_hinh.get('bit_rate_value_tuy_chinh')) + "kb/s")
		
		# cau_hinh["bit_rate"] = self.rad_bitrate_tuy_chinh.getValue()
		# else:
		# 	# cau_hinh["bit_rate"] = self.rad_bitrate_goc.getValue()
		# 	self.lb_bitrate_video.setChecked(True)
		# 	self.rad_bitrate_tuy_chinh.setChecked(False)
		# 	self.slider_bitrate_video.setDisabled(True)
		
		# self.check_radio_changed()
		
		self.slider_crf.setValue(cau_hinh.get('he_so_crf'))
		self.cb_delete_data.setChecked(cau_hinh.get('delete_data_output'))
		self.cb_show_log.setChecked(cau_hinh.get('show_log'))
		# self.cb_concat2.setChecked(cau_hinh.get('concat_v2'))
		# self.cb_fast.setChecked(cau_hinh.get('mode_fast'))
		self.cbobox_preset.setCurrentText(cau_hinh.get('he_so_preset'))
		self.cbobox_fps.setCurrentText(str(cau_hinh.get('he_so_fps')))
		# print(cau_hinh.get('so_luong_render'))
		self.cbobox_thread.setCurrentText(str(cau_hinh.get('so_luong_render')))
		
		self.cbobox_render_style.setCurrentIndex(cau_hinh.get('render_style'))
		
		if cau_hinh["src_output"] == '' or os.path.exists(cau_hinh["src_output"]) is False:
			cau_hinh["src_output"] = self.src_ouput_default
			self.configCurrent.value = json.dumps(cau_hinh)
			self.configCurrent.save()
			self.input_src_output.setText(self.src_ouput_default)
		
		else:
			self.input_src_output.setText(cau_hinh["src_output"])
		
		self.cbobox_rate_format.setCurrentText(cau_hinh["ti_le_khung_hinh"])
		
		format_quantity = FORMAT_OUTPUT_VIDEO.get(self.cbobox_rate_format.currentText())
		
		self.cbobox_quantity_format.setCurrentText(format_quantity.get(cau_hinh["chat_luong_video"]))
		self.change_size_format()
		self.cbobox_ext_format.setCurrentText(cau_hinh["dinh_dang_video"])
		self.input_hau_to_video_output.setText(cau_hinh["ten_hau_to_video"])
 
	def openDialogFolder (self):
		folder_name = QFileDialog.getExistingDirectory(self, caption='Chọn thư mục output',
			dir=self.input_src_output.text())
		self.input_src_output.setText(folder_name)
	
	def save (self):
		self.accept()
	
	def getValue (self):
		
		format_quantity = FORMAT_OUTPUT_VIDEO.get(self.cbobox_rate_format.currentText())
		# self.cbobox_quantity_format.setCurrentText(format_quantity.get(cau_hinh["chat_luong_video"]))
		bit_rate = ""
		for rb in self.groupbox_bit_rate.findChildren(QRadioButton):
			if rb.isChecked():
				bit_rate = rb.getValue()
		# print(list(format_quantity.keys())[self.cbobox_quantity_format.currentIndex()])
		return {
			"bit_rate": bit_rate,
			"he_so_crf": self.slider_crf.value(),
			"he_so_preset": self.cbobox_preset.currentText(),
			"render_style": self.cbobox_render_style.currentIndex(),
			"delete_data_output": self.cb_delete_data.isChecked(),
			"show_log": self.cb_show_log.isChecked(),
			"he_so_fps": int(self.cbobox_fps.currentText()),
			# "concat_v2": self.cb_concat2.isChecked(),
			# "mode_fast": self.cb_fast.isChecked(),
			"so_luong_render": int(self.cbobox_thread.currentText()),
			"bit_rate_audio": self.slider_bitrate_audio.value(),
			"bit_rate_video": self.slider_bitrate_video.value(),
			# "chat_luong_video": list(format_quantity.keys())[self.cbobox_quantity_format.currentIndex()],
			"chat_luong_video": f"{self.input_width.value()}|{self.input_height.value()}",
			"dinh_dang_video": self.cbobox_ext_format.currentText(),
			"ti_le_khung_hinh": self.cbobox_rate_format.currentText(),
			"src_output": self.input_src_output.text(),
			"ten_hau_to_video": self.input_hau_to_video_output.text()
		}
	
	def clearData (self):
		if hasattr(self, "configCurrent"):
			delattr(self, "configCurrent")
# print("clearData")
# self.cbobox_rate_format.setCurrentText("16:9")
# self.cbobox_quantity_format.setCurrentText("FullHD")
# self.input_src_output.setText(self.src_ouput_default)
#
# self.rad_bitrate_goc.setChecked(True)
# self.input_hau_to_video_output.setText('finished')
# self.cbobox_ext_format.setCurrentText("mp4")
