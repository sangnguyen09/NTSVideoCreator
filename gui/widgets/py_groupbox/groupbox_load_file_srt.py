import json
import os
import random

import budoux
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGroupBox, QFileDialog

from gui.configs.config_resource import ConfigResource
from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import LOAD_VIDEO_FROM_FILE_SRT, LANGUAGE_CODE_SPLIT_NO_SPACE, FILE_SRT_CURRENT
from gui.helpers.func_helper import filter_sequence_srt
from gui.helpers.thread import ManageThreadPool
from gui.helpers.translatepy.translators import GoogleTranslateV2
from gui.widgets.py_groupbox.groupbox_show_screen_tab_add_sub import GroupBoxShowScreenTabAddSub
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox


class GroupBoxLoadFileSRT(QWidget):
    loadSrtFished = Signal(object)
    def __init__(self,manage_thread_pool:ManageThreadPool,groupBox_showscreen:GroupBoxShowScreenTabAddSub):
        super().__init__()
        self.app_path = os.path.abspath(os.getcwd())
        self.frames_storage = os.path.join(self.app_path, 'frames/')
        self.manage_thread_pool = manage_thread_pool
        self.groupBox_showscreen = groupBox_showscreen
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.groupbox = QGroupBox("Load SRT")

        self.lb_file_srt = QLabel("SRT File:")

        self.btn_dialog_file_srt = PyButtonIcon(
            icon_path=ConfigResource.set_svg_icon("open-file.png"),
            parent=self,
            app_parent=self,
            icon_color="#f5ca1e",
            icon_color_hover="#ffe270",
            icon_color_pressed="#d1a807",
            tooltip_text="Open file SRT"
        )

        self.text_src_file = QLineEdit()
        self.text_src_file.setReadOnly(True)  # chỉ đọc

        self.lb_split_srt = QLabel("Tách Sub:")
        # self.progees_split_srt = QProgressBar(self, minimum=0, objectName="RedProgressBar")
        # self.progees_split_srt.setMinimum(0)
        # self.progees_split_srt.setMaximum(100)

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()
        self.bg_layout.setContentsMargins(0, 0, 0, 0)

        self.content_layout = QVBoxLayout()
        self.groupbox.setLayout(self.content_layout)

        self.content_file_layout = QHBoxLayout()
        self.content_split_layout = QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)

        self.content_layout.addWidget(QLabel(""), 5)
        self.content_layout.addLayout(self.content_file_layout, 45)
        self.content_layout.addLayout(self.content_split_layout, 45)

        # self.content_file_layout.addWidget(self.lb_file_srt, 10)
        self.content_file_layout.addWidget(self.btn_dialog_file_srt, 20)
        self.content_file_layout.addWidget(self.text_src_file, 80)

        # self.content_split_layout.addWidget(self.lb_split_srt, 10)
        # self.content_split_layout.addWidget(self.progees_split_srt, 80)

    def setup_connections(self):
        self.btn_dialog_file_srt.clicked.connect(self._openDialogFileSrt)
        self.manage_thread_pool.resultChanged.connect(self._resultThread)
        # self.manage_thread_pool.progressChanged.connect(self._progressChanged)

    def loadDataConfigCurrent(self, configCurrent: CauHinhTuyChonModel):
        self.configCurrent = configCurrent

    def remove_all_frames(self):
        """ Mô tả: Xóa toàn bộ hình ảnh trong frames folder """
        all_files = os.listdir(self.frames_storage)
        for f in all_files:
            os.remove(os.path.join(self.frames_storage, f))

    def _openDialogFileSrt(self):
            path_file, _ = QFileDialog.getOpenFileName(self, caption='Chọn file sub srt',
                                                       dir=(self.app_path), filter='File Sub (*.srt)')

            if os.path.exists(path_file):
                # return PyMessageBox().show_error("Lỗi","Vui lòng chọn file srt")
                self.loadVideoData(path_file)

    # @decorator_try_except_class
    def loadVideoData(self,srt_path):
            # print(srt_path)
            video_temporary_mp4 = srt_path[:-4] + '.mp4'
            video_temporary_avi = srt_path[:-4] + '.avi'
            video_temporary_mkv = srt_path[:-4] + '.mkv'
            video_temporary_wmv = srt_path[:-4] + '.wmv'
            video_temporary_flv = srt_path[:-4] + '.flv'
            video_temporary_mov = srt_path[:-4] + '.mov'
            # *wmv * flv * mkv * mov
            # print(video_temporary_mp4)

            if os.path.isfile(f'{video_temporary_mp4}'):
                self.path_video = video_temporary_mp4
            elif os.path.isfile(video_temporary_avi):
                self.path_video = video_temporary_avi

            elif os.path.isfile(video_temporary_mkv):
                self.path_video = video_temporary_mkv

            elif os.path.isfile(video_temporary_wmv):
                self.path_video = video_temporary_wmv

            elif os.path.isfile(video_temporary_flv):
                self.path_video = video_temporary_flv

            elif os.path.isfile(video_temporary_mov):
                self.path_video = video_temporary_mov

            else:
                return PyMessageBox().show_warning("Cảnh báo", "Không tìm thấy file 'Video'. Tên file srt phải trùng với tên file video trong cùng một thư mục")
                
            self.text_src_file.setText(srt_path)
            self.manage_thread_pool.resultChanged.emit(FILE_SRT_CURRENT, FILE_SRT_CURRENT, srt_path)
            
            # content_srt = self.read_srt(srt_path)
            # print(content_srt)
            sequences = filter_sequence_srt(srt_path, self.path_video)
            data = []
            cau_hinh: dict = json.loads(self.configCurrent.value)
            translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)

            lang_source = translator_server.language(random.choice(sequences)[-1])
            # print(1)
            # self.lb_language_origin.setText(f"Ngôn Ngữ Gốc: {lang_source.result.as_dict().get('in_foreign_languages')['vi']}")
            for (count, item) in enumerate(sequences):
                stt_, time_, content_ = item[0], item[1], item[2]
                
                if cau_hinh.get("split_sub_origin") is True:
                    list_content = content_.strip().replace("\n", " ").split(" ")
                    if 'jpn' in str(lang_source.result):
                        parser = budoux.load_default_japanese_parser()
                        list_content = parser.parse(content_.strip())
    
                    elif 'zho' in str(lang_source.result):  # tieng trun gian the
                        parser = budoux.load_default_simplified_chinese_parser()
                        list_content = parser.parse(content_.strip())
                    elif 'och' in str(lang_source.result):  # tieng trung quoc te
                        parser = budoux.load_default_traditional_chinese_parser()
                        list_content = parser.parse(content_.strip())
                    list_text = []
                    text_c = ''
                    for index, text_ in enumerate(list_content):
                        max_length = 20 if cau_hinh.get("max_character_inline_origin") is None else cau_hinh.get("max_character_inline_origin")
        
                        if str(lang_source.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
                            if len(text_c) + len(text_) > max_length:
                                list_text.append(text_c.strip())
                                text_c = ''
                            text_c += text_
                        else:
                            if len(text_c.strip().split()) + 1 > max_length:
                                list_text.append(text_c.strip())
                                text_c = ''
                            elif not text_c == '':
                                if len(text_c.strip().split()) > max_length / 2 and text_c.strip()[
                                    -1] in '''.,!;?'"]:)>/\\}''':
                                    list_text.append(text_c.strip())
                                    text_c = ''
                            text_c += text_ + " "
                        if index == len(list_content) - 1:
                            list_text.append(text_c.strip())
                    # print(list_text)

                    data.append([stt_, None, time_, "\n".join(list_text)])
                else:
                    data.append([stt_, None, time_, content_])
            # print(data)

            sequences = [list(filter(None, sequence)) for sequence in data]
            # print(4)
            self.groupBox_showscreen.loadDataFrameVideo(self.path_video, data)
            # print(5)
            self.loadSrtFished.emit(data)

    def _resultThread(self,id_worker, id_thread, result):

        # if id_thread ==GET_FRAME_FROM_VIDEO:
        #     self.loadSrtFished.emit(result)

        if id_thread ==LOAD_VIDEO_FROM_FILE_SRT: # cái này là bên tách sub add qua
            self.loadVideoData(result)

    # def _progressChanged(self,type_progress, id_worker, prgess):
    #
    #     if type_progress ==UPDATE_VALUE_PROGRESS_GET_FRAME_IMAGE:
    #         # self.progees_split_srt.setValue(prgess)

    def read_srt(self, path):
        """ Mô tả: Đọc tệp phụ đề"""
        content = ''
        with open(path, 'r', encoding='UTF-8') as f:
            content = f.read()
            return content



    # def getFramesFromVideo(self, **kwargs):
    #
    #     """ Mô tả: Tách hình ảnh frames và hiển thị data lên bảng """
    #     try:
    #         sequences = kwargs["sequences"]
    #         manage_thread = kwargs["parent"]
    #         id_worker = kwargs["id_worker"]
    #         path_video = kwargs["path_video"]
    #         self.remove_all_frames() # xoá bỏ hình ảnh cũ
    #
    #
    #         data_video = cv2.VideoCapture(path_video)
    #
    #         video_width = int(data_video.get(cv2.CAP_PROP_FRAME_WIDTH))
    #         video_heigth = int(data_video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    #
    #         data = []
    #         for (count, item) in enumerate(sequences):
    #             stt_, time_, content_ = item[0], item[1], item[2]
    #             manage_thread.progressChanged.emit(UPDATE_VALUE_PROGRESS_GET_FRAME_IMAGE,id_worker,count + 1)
    #             start = item[1].split(' --> ')[0]
    #             end = item[1].split(' --> ')[1]
    #             start = self.strFloatTime(start)
    #             end = self.strFloatTime(end)
    #             (start, end) = map(float, (start, end))
    #             span = (end + start) / 2
    #             data_video.set(cv2.CAP_PROP_POS_MSEC, span * 1000)
    #             (success, frame) = data_video.read()
    #             if success:
    #                 cv2.imwrite(self.frames_storage + str(count + 1) + '.jpg', frame)
    #                 data.append([stt_, None, time_, content_])
    #
    #         data_video.release()
    #         self.manage_thread_pool.resultChanged.emit("sizeVideo","sizeVideo",{"width":video_width,"height":video_heigth})
    #
    #         return data
    #         # self.signal_done_get_data.emit(data)
    #     except Exception as e:
    #         try:
    #             PyMessageBox().show_warning('Cảnh Báo', str(e))
    #         finally:
    #             e = None
    #             del e
    #
    #
    def convertCvImage2QtImage(self,cv_img):
        pixmap =QPixmap()
        pixmap.loadFromData(cv_img)
        return pixmap
