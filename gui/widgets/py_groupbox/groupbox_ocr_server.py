# -*- coding: utf-8 -*-
import base64
import json
import os
import random
import time

import imagehash
import requests
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QFileDialog, QProgressBar

from gui.configs.config_resource import ConfigResource
from gui.configs.config_theme import ConfigTheme
from gui.helpers.constants import RESULT_TRANSLATE_SUB_EXTRACT, TRANSLATE_SUB_EXTRACT_FINISHED, APP_PATH, \
    TOGGLE_SPINNER, LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT, \
    UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, USER_DATA, TOOL_CODE_MAIN, LOAD_SUB_TRANSLATE_TXT_TABLE_EXTRACT, \
    JOIN_PATH, PATH_DB, TRANSLATE_SUB_PART_TAB_EXTRACT, RESULT_TRANSLATE_SUB_EXTRACT_PART, \
    LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT_PART, STOP_THREAD_TRANSLATE, LANGUAGE_CODE_SPLIT_NO_SPACE, STOP_THREAD_OCR, \
    DETECT_IMAGE_TO_TEXT, DETECT_IMAGE_TO_TEXT_PART, UPDATE_VALUE_PROGRESS_OCR_TAB_EDIT, OCR_TEXT_FINISHED, \
    OCR_PART_TAB_EDIT
from gui.helpers.ect import cr_pc, mh_ae, gm_ae
from gui.helpers.func_helper import filter_sequence_srt, writeFileSrt, getValueSettings
from gui.helpers.get_data import URL_API_BASE, LANGUAGES_SUPPORT_TRANSPRO1
from gui.helpers.selelium.chatgpt import translateSubChatGPTThuCong, TranslaterServer
from gui.helpers.thread import ManageThreadPool
from gui.helpers.translatepy.translators import GoogleTranslateV2
from gui.helpers.translatepy.translators.server import TranslatorsServer
from gui.helpers.translatepy.translators.tts_online_free import TTSFreeOnlineTranslator
from gui.helpers.translatepy.utils.lru_cacher import LRUDictCache
from gui.widgets.py_combobox import PyComboBox
from gui.widgets.py_dialogs.py_dialog_show_info import PyDialogShowInfo
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_table_widget.model_timeline_addsub import ColumnNumberTabEdit


class GroupboxOCRServer(QWidget):
    def __init__(self, manage_thread_pool, table_timeline, settings):
        self.manage_thread_pool = manage_thread_pool
        self.thread_pool_limit = ManageThreadPool()
        self.thread_pool_limit.setMaxThread(10)
        self.table_timeline_edit = table_timeline
        # self.checker = ProxyChecker(manage_thread_pool)
        self.translate_cache = LRUDictCache()
        self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
        self.translate_server = TranslaterServer(manage_thread_pool)
        self.translator_server_free = TranslatorsServer(manage_thread_pool, self.translate_cache)
        self.translator_google = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)

        self.isStop = False
        self.isStatusOcr = False
        super().__init__()
        # PROPERTIES
        # settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')

        self.language_detect = settings.get("language_support").get("language_detect")
        # self.MODEL_AI_TRANSLATE = settings.get("model_ai_translate")
        self.SERVER_OCR = settings.get("server_ocr")
        # self.TabIndexTranslate = settings.get("TabIndexTranslate")
        # self.GENDER_VOICE_FREE_TTS_ONLINE = settings.get("gender_voice").get("tts_free_v2")
        self.isLoad = True
        self.load_file_srt_finished = False
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()

        self.setup_connections()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()

    def create_widgets(self):
        self.themes = ConfigTheme()

        self.groupbox = QGroupBox("LẤY CHỮ TỪ HÌNH")
        self.lb_language_origin = QLabel("Ngôn Ngữ Gốc:")
        self.cb_languages_origin = PyComboBox()

        self.lb_server_trans = QLabel("Chọn Server:")
        self.cb_server_trans = PyComboBox()

        # self.lb_modelAI = QLabel("Model AI:")
        # self.cb_modelAI = PyComboBox()
        # self.lb_notify = QLabel("Tip: Nên sử dụng proxy khi dịch để hạn chế bị block IP")

        # self.lb_file_srt = QLabel("Load File SRT:")
        # self.btn_dialog_file_srt = PyButtonIcon(
        # 	icon_path=ConfigResource.set_svg_icon("open-file.png"),
        # 	parent=self,
        # 	app_parent=self,
        # 	icon_color="#f5ca1e",
        # 	icon_color_hover="#ffe270",
        # 	icon_color_pressed="#d1a807",
        #
        # )

        text = "- Chức Năng Lấy Chữ Từ Hình"
        text += "\n\n- Bạn cần mua số lượt chuyển đổi thì mới dùng chức năng này"
        text += "\n\n- Mỗi bức hình lấy chữ được tính là 1 lần chuyển đổi"
        text += "\n\n- Chọn server phù hợp"
        text += "\n\n- Sau đó bấm nút LẤY CHỮ, và đợt kết quả"

        self.dialog_info = PyDialogShowInfo(text, 300)
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
        self.progess_convert = QProgressBar(self, objectName="RedProgressBar")
        self.lb_status = QLabel()

        self.btn_ocr_server = QPushButton("LẤY CHỮ Tự ĐỘng")
        self.btn_ocr_server.setCursor(Qt.CursorShape.PointingHandCursor)

        self.btn_load_txt = QPushButton("Nhập Chữ từ FIle TXT")
        self.btn_load_txt.setCursor(Qt.CursorShape.PointingHandCursor)

        self.lb_token_chatgpt = QLabel("")

    def modify_widgets(self):
        self.cb_server_trans.addItems(list(self.SERVER_OCR.keys()))

        # try:

        self.cb_languages_origin.addItems(list(self.language_detect.keys()))

        self.server_changed()
        self.progess_convert.hide()

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()
        self.bg_layout.setContentsMargins(0, 0, 0, 0)

        self.content_layout = QVBoxLayout()
        # self.content_layout.setContentsMargins(0, 0, 0, 0)

        # self.gbox_layout = QVBoxLayout()
        self.groupbox.setLayout(self.content_layout)

        self.content_chat_language = QHBoxLayout()
        self.content_language_layout = QHBoxLayout()

        self.progess_convert_layout = QHBoxLayout()
        self.content_file_layout = QHBoxLayout()
        self.content_btn_layout = QGridLayout()
        self.content_status = QGridLayout()

    # layout bên phải

    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)
        # self.setLayout(self.content_layout)

        self.content_layout.addWidget(QLabel(""))
        self.content_layout.addLayout(self.content_language_layout)
        # self.content_layout.addWidget(QLabel(""))

        # self.content_layout.addLayout(self.content_file_layout)
        self.content_layout.addWidget(QLabel(""))
        self.content_layout.addLayout(self.content_btn_layout)
        self.content_layout.addLayout(self.content_chat_language)

        self.content_layout.addLayout(self.content_status)

        # self.content_language_layout.addWidget(QLabel(""), 20)
        self.content_language_layout.addWidget(self.lb_server_trans, 20)
        self.content_language_layout.addWidget(self.cb_server_trans, 30)
        self.content_language_layout.addWidget(self.lb_language_origin, 20)
        self.content_language_layout.addWidget(self.cb_languages_origin, 30)

        self.content_chat_language.addWidget(self.lb_token_chatgpt)
        # self.content_chat_language.addWidget(self.lb_language_origin, alignment=Qt.AlignmentFlag.AlignRight)

        # self.content_radio.addWidget(self.rad_save_file_origin)
        # self.content_radio.addWidget(self.rad_save_file_trans)
        # self.content_radio.addWidget(self.rad_save_all_file)
        # self.content_file_layout.addWidget(self.lb_modelAI)
        # self.content_file_layout.addWidget(self.cb_modelAI)
        # self.content_file_layout.addWidget(self.lb_file_srt)
        # self.content_file_layout.addWidget(self.btn_dialog_file_srt)
        # self.content_file_layout.addWidget(QLabel(), 20)

        self.content_btn_layout.addWidget(QLabel(), 0, 0, 1, 2)
        self.content_btn_layout.addWidget(self.btn_ocr_server, 0, 2, 1, 4)
        self.content_btn_layout.addWidget(self.btn_load_txt, 0, 6, 1, 4)
        # self.content_btn_layout.addWidget(self.btn_export_srt, 0, 8, 1, 2)
        self.content_btn_layout.addWidget(QLabel(), 0, 10, 1, 2)

        # self.content_btn_layout.addWidget(self.btn_info_frame, 0, 11)

        self.content_status.addWidget(self.lb_status, 0, 0, 1, 4, alignment=Qt.AlignmentFlag.AlignLeft)
        self.content_status.addWidget(QLabel(), 0, 4, 1, 3)
        self.content_status.addWidget(self.progess_convert, 0, 7, 1, 3)
        self.content_status.addWidget(self.btn_info_frame, 0, 10, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)

    def setup_connections(self):
        self.manage_thread_pool.progressChanged.connect(self._progressChanged)
        self.manage_thread_pool.resultChanged.connect(self._resultThread)
        # self.btn_dialog_file_srt.clicked.connect(self._openDialogFileSrt)
        # self.cb_modelAI.currentIndexChanged.connect(self.modelAIChanged)
        # self.checker.finishedCheckLiveProxySignal.connect(self._finishedCheckLiveProxySignal)

        self.cb_server_trans.currentIndexChanged.connect(self.server_changed)
        self.cb_languages_origin.currentIndexChanged.connect(lambda index: self.comboxChanged(index))

        self.btn_info_frame.clicked.connect(self._click_info)
        # self.btn_save_srt.clicked.connect(self.save_srt)

        self.btn_ocr_server.clicked.connect(self.clickStart)

    # self.btn_check_render.clicked.connect(self.clickCheckPreRender)

    def server_changed(self):

        self.check_balance_ocr()

    def _openDialogFileSrt(self):

        path_file, _ = QFileDialog.getOpenFileName(self, caption='Chọn file sub srt',
                                                   dir=(APP_PATH), filter='File Sub (*.srt)')

        if os.path.exists(path_file):
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

            sequences = filter_sequence_srt(path_file, path_video)
            data_table = []
            for (count, item) in enumerate(sequences):
                stt_, time_, content_ = item[0], item[1], item[2]
                data_table.append([time_, content_, ""])

            self.table_timeline_edit.displayTable(data_table, path_video, sequences)

            self.path_srt = path_file

    def comboxChanged(self, index):
        pass

    # self.btn_translate.setDisabled(False)

    def _click_info(self):
        self.dialog_info.exec()

    def loadData(self, configCurrent):

        self.configCurrent = configCurrent

        self.isLoad = False

    # def writeFileSrt (self, filename_srt, data_sub, type_srt="origin"):
    # 	""" Mô tả: Lưu file srt dịch vào thư mục temp"""
    #
    # 	if os.path.isfile(filename_srt):
    # 		os.remove(filename_srt)
    #
    # 	with open(filename_srt, "w", encoding='utf-8') as file_data:
    # 		for index, item in enumerate(data_sub):
    # 			time_, sub_origin, trans_ = item[0], item[1], item[2]
    # 			file_data.write(str(index + 1) + '\n')
    # 			file_data.write(str(time_) + '\n')
    # 			if type_srt == "origin":
    # 				file_data.write(str(sub_origin) + '\n\n')
    # 			else:
    # 				file_data.write(str(trans_) + '\n\n')
    #
    # 	PyMessageBox().show_info("Thông Báo", "Lưu File Thành Công!")
    #
    # @decorator_try_except_class
    def loadFileSRTCurrent(self, fileSRTCurrent):

        self.fileSRTCurrent = fileSRTCurrent

    # cau_hinh_edit: dict = json.loads(fileSRTCurrent.value)
    def clickCheckPreRender(self):
        data_sub = self.table_timeline_edit.getDataSub()
        detect_lang = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
        cau_hinh_edit: dict = json.loads(self.fileSRTCurrent.value)

        sub_random = random.choice(data_sub)
        text_random = sub_random[ColumnNumberTabEdit.column_original.value]
        if cau_hinh_edit.get('sub_hien_thi') == "trans":
            if data_sub[0][ColumnNumberTabEdit.column_translated.value] == "":
                return PyMessageBox().show_warning("Cảnh báo", "Sub chưa được dịch")
            text_random = sub_random[ColumnNumberTabEdit.column_translated.value]
        lang = detect_lang.language(text_random).result
        lang_source = lang.in_foreign_languages.get('en')
        lang_code = lang.alpha2
        is_ok = PyMessageBox().show_question("Thông báo",
                                             f"Ngôn ngữ SUB là {lang_source}, Bạn có muốn tiếp tục Kiểm Tra Lỗi Không ?")
        if is_ok:
            pass
        else:
            return
        if lang_source == 'Filipino':
            # language_tts = 'Tagalog'
            lang_code = 'tl'

        server_trans = TTSFreeOnlineTranslator(self.manage_thread_pool)
        # gender = list(GENDER_VOICE_FREE_TTS_ONLINE.get(self.LANGUAGES_CHANGE_CODE.get(lang_code)).keys())[0]
        # gender = list(self.GENDER_VOICE_FREE_TTS_ONLINE.get(lang_code).keys())[0]
        self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)

    # @decorator_try_except_class
    def clickStart(self):
        self.table_timeline_edit.isOCRing = False
        self.table_timeline_edit.count_result_ocr = 0
        self.table_timeline_edit.list_row_ocr_chunk = []
        # # print(self.isStatusTranslate)
        # # print(self.isStop)
        # # if self.table_timeline_edit.isHasSub is True:
        data_table = self.table_timeline_edit.getDataSub()
        # print(data_table)
        if len(data_table) < 1:
            return PyMessageBox().show_warning('Cảnh Báo', "Chưa có hình ảnh nào nào được load !")

        if self.isStatusOcr:
            self.manage_thread_pool.resultChanged.emit(STOP_THREAD_OCR, STOP_THREAD_OCR, "")
            self.isStop = True
            self.isStatusOcr = False
            self.resetStatus()

        else:
            self.isStatusOcr = True
            self.isStop = False

            self.btn_ocr_server.setText("STOP")

            self.ocrStartThread()

    # else:

    def _progressChanged(self, type_progress, id_thread, proge):
        if type_progress == UPDATE_VALUE_PROGRESS_OCR_TAB_EDIT:
            if self.isStop:
                self.progess_convert.setValue(0)
                return
            self.progess_convert.setValue(proge)
            if proge == self.total_sub:
                self.lb_status.setText("Hoàn thành!")
                self.progess_convert.hide()
                self.progess_convert.setValue(0)

    def _resultThread(self, id_worker, id_thread, result):
        if id_thread == OCR_PART_TAB_EDIT:
            ''' Dịch lại 1 phần trong bảng'''
            # self.btn_convert.setDisabled(False)
            self.isStop = False

            self.resetStatus()
            # print("again")
            self.ocrStartThread(list_sequences=result)

        # if id_thread == ITEM_TABLE_TIMELINE_EXTRACT_CHANGED:
        # 	self.btn_export_srt.setDisabled(False)
        # self.rad_save_file_origin.setDisabled(False)

        if id_thread == OCR_TEXT_FINISHED:

            self.check_balance_ocr()

            self.resetStatus()

    def resetStatus(self):
        self.lb_status.setText("")
        self.btn_ocr_server.setText("DỊCH")
        self.progess_convert.hide()
        self.progess_convert.setValue(0)
        self.isStatusOcr = False
        self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)

    def ocrStartThread(self, list_sequences=None):

        type_thread_ocr = DETECT_IMAGE_TO_TEXT if list_sequences is None else DETECT_IMAGE_TO_TEXT_PART

        sequences = self.table_timeline_edit.getDataSub() if list_sequences is None else list_sequences
        # self.table_timeline_extract.resetDataColumn(ColumnNumberTabEdit.column_translated.value)
        # print(111111)
        self.lb_status.setText("Đang lấy chữ....")
        server_ocr = self.SERVER_OCR.get(self.cb_server_trans.currentText())
        languages = self.language_detect.get(self.cb_languages_origin.currentText())

        # self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
        self.progess_convert.setRange(0, len(sequences))
        self.progess_convert.setValue(0)
        self.progess_convert.show()

        user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)

        # print(chunk_split)
        dataTrans = {
            "hash_image": "CHECK_ACCOUNT_ACCEPT_PRO",
            "source_lang": languages,
            "server": 'sv1',
            "image_string": 'image_string',
            "cp": cr_pc(),
            't': int(float(time.time())),
            "tc": TOOL_CODE_MAIN,
        }

        data_encrypt = mh_ae(dataTrans, user_data['paes'])

        headers = {"Authorization": f"Bearer {user_data['token']}"}
        url = URL_API_BASE + "/ocr/private/image-to-text"

        res = requests.post(url=url,
                            json={"data": data_encrypt}, headers=headers)

        if res.status_code > 200:
            self.resetStatus()
            return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", res.text, "warning")

        self.total_sub = len(sequences)

        self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, True)
        # self.translator_server_free.is_error = False
        # print('ooooo')
        for index, item in enumerate(sequences):
            file_image = item[ColumnNumberTabEdit.column_avatar.value]  # lấy ra mảng sub gốc
            self.thread_pool_limit.start(self._funcDetectText, "_funcDetectText" + str(index), type_thread_ocr,
                                         is_stop=self.get_is_stop, type_thread_server=type_thread_ocr,
                                         server_ocr=server_ocr, file_image=file_image, row_number=index,
                                         source_lang=languages,token=user_data.get('token'))

    def get_is_stop(self):
        # print(self.isStop)
        return self.isStop

    def _funcDetectText(self, **kwargs):
        # try:
        thread_pool = kwargs["thread_pool"]
        id_worker = kwargs["id_worker"]
        row_number = kwargs["row_number"]
        file_image = kwargs["file_image"]
        server_ocr = kwargs["server_ocr"]
        source_lang = kwargs["source_lang"]
        token = kwargs["token"]

        type_thread_server = kwargs["type_thread_server"]
        get_is_stop = kwargs["is_stop"]
        # print(get_is_stop())
        if get_is_stop():
            return

        hash = imagehash.average_hash(Image.open(file_image))
        with open(file_image,'rb') as file :
            image_string = base64.b64encode(file.read()).decode('utf-8')
        # print(image_string[:50])

        dataTrans = {
            "hash_image": str(hash.__str__()),
            "source_lang": source_lang,
            "server": server_ocr,
            "image_string": image_string,
            "cp": cr_pc(),
            't': int(float(time.time())),
            "tc": TOOL_CODE_MAIN,
        }

        data_encrypt = mh_ae(dataTrans, "user_data['paes']")
        # print({"data": data_encrypt})

        headers = {"Authorization": f"Bearer {token}"}
        url = URL_API_BASE + "/ocr/private/image-to-text"

        for i in range(10):
            response = requests.post(url=url,
                                     json={"data": data_encrypt}, headers=headers)
            # print(response.text)
            if response.status_code == 200:
                data = response.json().get('data')
                req_id = data.get('req_id')
                for i in range(60):
                    if get_is_stop():
                        return
                    try:
                        res = requests.get(url=URL_API_BASE + f"/ocr/public/check-task/{req_id}", headers=headers)
                        if res.status_code == 200:
                            try:
                                text_ocr = gm_ae(res.json()["data"], "user_data['paes']")
                                # print(text_ocr)
                                thread_pool.finishSingleThread(id_worker)

                                self.manage_thread_pool.resultChanged.emit(type_thread_server, type_thread_server,
                                                                           {"row": row_number, "text_ocr": text_ocr})
                                return
                            except:
                                print("Lỗi dịch")

                        elif res.status_code == 429:
                            # self.is_error = True
                            # resetStatus()
                            print(response.text)
                            time.sleep(1)
                            continue

                    except:
                        pass
                    time.sleep(1)

            elif response.status_code == 429:
                # self.is_error = True
                # resetStatus()
                print(response.text)
            # return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", "Quá nhiều request", "warning")
            elif response.status_code == 402:
                print(response.text)
            time.sleep(1)

    def save_srt(self):
        data_sub_timeline = self.table_timeline_edit.getDataSub()
        # print(data_sub_timeline)
        if len(data_sub_timeline) == 0:
            return PyMessageBox().show_warning("Thông Báo", "Chưa load file sub")

        data_sub = []
        for sub in data_sub_timeline:
            time, sub_origin, sub_translate = sub
            data_sub.append(["dolech", time, 'pos_ori', sub_origin, sub_translate, 'pos_trans'])

        if hasattr(self, 'path_srt'):
            writeFileSrt(self.path_srt, data_sub, 0)
        else:
            return PyMessageBox().show_warning("Thông Báo", "Chưa load file srt!")

        PyMessageBox().show_info("Thông Báo", "Lưu File Thành Công!")

    def check_balance_ocr(self):
        headers = {"Authorization": f"Bearer {self.user_data['token']}"}
        payload = {
            "cp": cr_pc(),
            "tc": TOOL_CODE_MAIN,
            't': int(float(time.time())),
        }
        response = requests.post(url=URL_API_BASE + f"/ocr/private/check-balance", headers=headers,
                                 json={
                                     "data": mh_ae(payload, p_k=self.user_data['paes'])}
                                 )
        # print(response.json())
        if response.status_code == 200:
            self.lb_token_chatgpt.setText(
                f"Số Chuyển Đổi Còn Lại: {response.json().get('data') if isinstance(response.json().get('data'), str) else '{:,}'.format(response.json().get('data'))} lần")

        # self.lb_token_chatgpt.setText(f"Token Còn Lại: {response.json().get('data')}")
        else:
            self.lb_token_chatgpt.setText(f"Hết Lượt Chuyển Đổi, Liên Hệ Admin Mua")
