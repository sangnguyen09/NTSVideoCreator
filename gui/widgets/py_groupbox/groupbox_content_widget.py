import json
import os
import re

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGroupBox, QFileDialog, \
    QSlider, QScrollArea, QPlainTextEdit

from gui.helpers.constants import CHANGE_HIEN_THI_TAB_EDIT_SUB, APP_PATH, ADDNEW_SRT_FILE_EDIT_SUB, \
    REFRESH_CONFIG_FILE_SRT, LOAD_CONFIG_TAB_EDIT_SUB_CHANGED, \
    CHANGE_HIEN_THI_TAB_ADD_SUB, REMOVE_CONFIG_FILE_SRT, LOAD_VIDEO_FROM_FILE_SRT, REMOVE_CONTENT_WIDGET
from gui.helpers.func_helper import filter_sequence_srt, is_chinese_char
from gui.helpers.server import TYPE_TTS_SUB
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_checkbox import PyCheckBox
from gui.widgets.py_combobox import PyComboBox
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox

style = '''
QRadioButton {{
    color: #c3f0ff;

}}
QRadioButton:hover {{

            color: #ff0000;

}}
QRadioButton:checked  {{
            color: #34c950;

}}

'''
# APPLY STYLESHEET
style_format = style.format()


class GroupBoxContentWidget(QWidget, QObject):

    def __init__(self, manage_thread_pool: ManageThreadPool,id_widget):
        super().__init__()
        # self.db_app = db_app
        self.id_widget = id_widget
        self.manage_thread_pool = manage_thread_pool
        self.manage_thread_pool.resultChanged.connect(self._resultThread)

        # self.settings = QSettings(*SETTING_CONFIG)

        self.list_config = []
        self.loadConfigFinish = False
        self.name_edit = ""
        self.fileSRTCurrent = None

        self.setup_ui()

    # self.loadConfig()

    def loadFileSRTCurrent(self, fileSRTCurrent, db_app, db_srt_file):
        self.db_srt_file = db_srt_file
        self.db_app = db_app

        self.fileSRTCurrent = fileSRTCurrent
        cau_hinh = json.loads(fileSRTCurrent.value)
        sub_hien_thi = cau_hinh.get('sub_hien_thi', 'origin')
        self.cbox_sub_hien_thi.setCurrentText(TYPE_TTS_SUB.get(sub_hien_thi))
        self.refreshData()
        self.loadConfigFinish = True

    # self.signalDataConfigCurrentChanged.emit(self.db_cau_hinh, self.list_config[idex]) # bỏ load dữ liệu qua các widgets khác

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.groupbox = QGroupBox(f"Scene {self.id_widget}")
        self.groupbox.setStyleSheet(u"border-radius: 20px;")

        self.scroll_bar = QScrollArea()


        self.text_origin = QPlainTextEdit()
        self.text_origin.setFixedHeight(50)

        self.text_translate = QPlainTextEdit()
        self.text_translate.setFixedHeight(50)

        self.avatar_image = QLabel()
        pixmap = QPixmap('1.png')
        pixmap= pixmap.scaled(150,150,Qt.AspectRatioMode.KeepAspectRatio)
        self.avatar_image.setPixmap(pixmap)
        self.cbox_sub_hien_thi = PyComboBox()
        self.cbox_sub_hien_thi.addItems(list(TYPE_TTS_SUB.values()))

        self.checkbox_auto_play = PyCheckBox(value="auto_play", text="Auto Play Video")

        self.lb_volume = QLabel("Âm Lượng Phát:")
        self.slider_volume = QSlider()
        self.slider_volume.setOrientation(Qt.Orientation.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.setPageStep(1)
        self.slider_volume.setValue(100)
        self.lb_number_volume_tts = QLabel(str(self.slider_volume.value()))

        # self.lb_file_srt = QLabel("Load File .SRT có sẵn:")
        self.btn_dialog_file_srt = QPushButton("Load File SRT Mới")
        self.btn_dialog_file_srt.setCursor(Qt.CursorShape.PointingHandCursor)

        # self.btn_dialog_file_srt = QPushButton("Show Dữ Liệu")
        self.button_remove = QPushButton("Delete")
        self.button_remove.setCursor(Qt.CursorShape.PointingHandCursor)

    def modify_widgets(self):
        self.setStyleSheet(style_format)

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()
        self.bg_layout.setContentsMargins(0, 0, 0, 0)

        self.gbox_layout = QVBoxLayout()
        self.content_layout = QVBoxLayout()
        self.content_image_layout = QHBoxLayout()
        self.content_text_layout = QVBoxLayout()

        self.content_top_layout = QHBoxLayout()
        self.content_mid_layout = QHBoxLayout()
        self.content_btn_layout = QHBoxLayout()
        self.groupbox.setLayout(self.gbox_layout)

    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)
        self.gbox_layout.addLayout(self.content_layout)

        self.content_layout.addWidget(QLabel(""))
        self.content_layout.addLayout(self.content_image_layout)

        self.content_image_layout.addWidget(self.avatar_image,20)
        self.content_image_layout.addLayout(self.content_text_layout,80)

        self.content_text_layout.addLayout(self.content_top_layout)
        self.content_text_layout.addLayout(self.content_mid_layout)
        # self.content_layout.addLayout(self.content_btn_layout)

        self.content_top_layout.addWidget(QLabel("Văn Bản Gốc: "))
        self.content_top_layout.addWidget(self.text_origin)
        # self.content_top_layout.addWidget(self.btn_dialog_file_srt, 30)
        # self.content_top_layout.addWidget(self.button_remove, 15)

        self.content_mid_layout.addWidget(QLabel("Văn Bản Dịch"))
        self.content_mid_layout.addWidget(self.text_translate)
        # self.content_mid_layout.addWidget(QLabel(""), 20)

    def setup_connections(self):
        # self.text_src_file.currentIndexChanged.connect(self.configIndexChanged)
        self.cbox_sub_hien_thi.currentIndexChanged.connect(self.cbox_sub_hien_thiChanged)
        # self.button_save.clicked.connect(self.saveConfig)
        self.button_remove.clicked.connect(self._removeConfig)
        # self.text_edit_config_name.textChanged.connect(self.check_button_disabled)
        self.btn_dialog_file_srt.clicked.connect(self._openDialogFileSrt)

    # self.btn_export_srt.clicked.connect(self.clickSaveFile)

    def _resultThread(self, id_worker, id_thread, result):

        if id_thread == LOAD_VIDEO_FROM_FILE_SRT:
            self.loadVideoData(result)

        if id_thread == CHANGE_HIEN_THI_TAB_EDIT_SUB:
            self.cbox_sub_hien_thi.setCurrentText(TYPE_TTS_SUB.get(result))

        if id_thread == LOAD_CONFIG_TAB_EDIT_SUB_CHANGED:

            if result:
                # print(result)
                self.fileSRTCurrent = result
                self.refreshData()

    def refreshData(self):
        # print(self.fileSRTCurrent)
        if hasattr(self, 'fileSRTCurrent') and self.fileSRTCurrent:
            print('refreshData')
            # self.text_origin.setText(self.fileSRTCurrent.ten_cau_hinh)

    # @decorator_try_except_class
    def _removeConfig(self):

        self.manage_thread_pool.resultChanged.emit(REMOVE_CONTENT_WIDGET, REMOVE_CONTENT_WIDGET, self.id_widget)

    def loadVideoData(self, path_file):
        video_temporary_mp4 = path_file[:-4] + '.mp4'
        video_temporary_avi = path_file[:-4] + '.avi'
        video_temporary_mkv = path_file[:-4] + '.mkv'
        video_temporary_wmv = path_file[:-4] + '.wmv'
        video_temporary_flv = path_file[:-4] + '.flv'
        video_temporary_mov = path_file[:-4] + '.mov'
        # *wmv * flv * mkv * mov
        # print(video_temporary_mp4)

        if os.path.isfile(f'{video_temporary_mp4}'):
            path_video = video_temporary_mp4
        elif os.path.isfile(video_temporary_avi):
            path_video = video_temporary_avi

        elif os.path.isfile(video_temporary_mkv):
            path_video = video_temporary_mkv

        elif os.path.isfile(video_temporary_wmv):
            path_video = video_temporary_wmv

        elif os.path.isfile(video_temporary_flv):
            path_video = video_temporary_flv

        elif os.path.isfile(video_temporary_mov):
            path_video = video_temporary_mov

        else:
            PyMessageBox().show_error('Cảnh Báo', "Không tìm thấy file 'Video' tương ứng!")
            return

        name = os.path.basename(path_file)
        if is_chinese_char(name):
            PyMessageBox().show_error('Cảnh Báo', "Tên file phải để tiếng anh không dấu")
            return
        # self.text_src_file.setText(path_file)

        sequences = filter_sequence_srt(path_file, path_video)
        data_table = []
        for (count, item) in enumerate(sequences):
            stt_, time_, content_ = item[0], item[1], item[2]
            data_table.append([time_, content_, ""])

        self.manage_thread_pool.resultChanged.emit(ADDNEW_SRT_FILE_EDIT_SUB, ADDNEW_SRT_FILE_EDIT_SUB, (
            path_file, path_video, data_table))

    def _openDialogFileSrt(self):

        path_file, _ = QFileDialog.getOpenFileName(self, caption='Chọn file sub .srt',
                                                   dir=(APP_PATH), filter='File Sub (*.srt)')

        if os.path.exists(path_file):
            self.loadVideoData(path_file)

    def cbox_sub_hien_thiChanged(self, index):
        if hasattr(self, "fileSRTCurrent") and self.fileSRTCurrent:
            cau_hinh = json.loads(self.fileSRTCurrent.value)
            cau_hinh["sub_hien_thi"] = list(TYPE_TTS_SUB.keys())[index]  # vi,en
            self.fileSRTCurrent.value = json.dumps(cau_hinh)
            self.fileSRTCurrent.save()
            self.manage_thread_pool.resultChanged.emit(CHANGE_HIEN_THI_TAB_ADD_SUB, CHANGE_HIEN_THI_TAB_ADD_SUB,
                                                       cau_hinh["sub_hien_thi"])

    def saveConfigActive(self, id):
        # print(id)
        configActive = self.db_app.select_one_name(
            "configEditSubActive")  # chọn cấu hình với tên được lưu configEditSubActive để lấy ra giá trị
        configActive.configValue = id
        configActive.save()
