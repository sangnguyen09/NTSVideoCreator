# -*- coding: utf-8 -*-
import json
import os

from PySide6.QtCore import Qt, QEvent
from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QPlainTextEdit, QLabel

from gui.configs.config_theme import ConfigTheme
from gui.db.sqlite import ConfigApp_DB, CauHinhTuyChon_DB
from gui.helpers.constants import TOOL_CODE_MAIN, \
    USER_DATA, LOAD_VIDEO_FROM_FILE_SRT, ACTION_PRESS_FIND_REPLACE, ACTION_PRESS_NEXT_LINE_SUB, \
    ACTION_PRESS_PREVIOUS_LINE_SUB, ROW_SELECTION_CHANGED_TABLE_EDIT_SUB, CHANGE_FONT_SIZE_TABLE_EDIT_SUB, \
    CHANGE_COLOR_TABLE_EDIT_SUB, UPDATE_CONTENT_EDIT_BINDING
from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from ..py_groupbox.groupbox_ocr_server import GroupboxOCRServer
from ..py_groupbox.groupbox_setting_edit_sub import GroupboxSetting
from ..py_groupbox.groupbox_show_screen_tab_edit_sub import GroupBoxShowScreenTabEditSub
from ..py_groupbox.groupbox_translate_server import GroupboxTranslateServer
from ..py_messagebox.py_massagebox import PyMessageBox
from ..py_resize.splitter_resize import Resize_Splitter
from ..py_table_widget.table_timeline_edit_sub import TableTimelineEditSub
from ...db.sqlite import CauHinhTuyChonModel
from ...helpers.func_helper import getValueSettings
from ...helpers.thread import ManageCMD


class PlainTextEdit(QPlainTextEdit):

    def __init__(self, manage_thread_pool, *args, **kwargs):
        QPlainTextEdit.__init__(self, *args, **kwargs)
        # self.setStyleSheet("font-size:18px")
        self.manage_thread_pool = manage_thread_pool

    def keyPressEvent(self, event):

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            # print('Key_Enter')
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_NEXT_LINE_SUB, ACTION_PRESS_NEXT_LINE_SUB, "")
            return

        if event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_Up:
            # print('UP')
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_PREVIOUS_LINE_SUB, ACTION_PRESS_PREVIOUS_LINE_SUB,
                                                       "")
        elif event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_Down:
            # print('Key_Down')
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_NEXT_LINE_SUB, ACTION_PRESS_NEXT_LINE_SUB, "")

        super(PlainTextEdit, self).keyPressEvent(event)


class PyTabEditSub(QWidget):
    def __init__(self, manage_thread_pool: ManageThreadPool, manage_cmd: ManageCMD, settings):
        super().__init__()
        # PROPERTIES
        # st = QSettings(*SETTING_APP)
        self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
        # settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
        self.settings = settings

        self.LANGUAGES_CHANGE_CODE = settings.get("language_support").get('language_code')

        self.db_cau_hinh = CauHinhTuyChon_DB()
        self.db_app = ConfigApp_DB()
        self.row_number = 0
        self.list_worker_tts = {}
        self.manage_thread_pool = manage_thread_pool  # tạo trước ui
        self.thread_pool_limit = ManageThreadPool()
        self.thread_pool_limit.setMaxThread(self.user_data["list_tool"][TOOL_CODE_MAIN]["thread"])
        # self.thread_pool_limit.setMaxThread(1)
        self.setAcceptDrops(True)
        self.manage_cmd = manage_cmd  # tạo trước ui

        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()

        self.setup_connections()

        self.modify_widgets()

        self.create_layouts()

        self.add_widgets_to_layouts()

    def create_widgets(self):
        self.themes = ConfigTheme()

        self.tab_addsub = QWidget()
        # =========== Layout bên  Trái ===========
        self.tab_addsub_left = QWidget()
        self.resize_splitter = Resize_Splitter()
        # self.resize_splitter_right_left = Resize_Splitter()
        self.text_edit_origin = PlainTextEdit(self.manage_thread_pool)
        self.text_edit_trans = PlainTextEdit(self.manage_thread_pool)

        self.bg_left_frame = QFrame()
        self.bg_left_frame.setObjectName("bg_frame")
        self.groupbox_timeline = TableTimelineEditSub(self.manage_thread_pool)
        self.groupbox_timeline.setMinimumWidth(900)

        self.gbox_preview = GroupBoxShowScreenTabEditSub(self.manage_thread_pool, self.groupbox_timeline)
        # self.gbox_preview = GroupBoxShowScreenTabEditSub(self.manage_thread_pool, self.groupbox_timeline)

        self.groupbox_setting = GroupboxSetting(self.manage_thread_pool, self.groupbox_timeline, self.settings)

        self.groupbox_translate = GroupboxTranslateServer(self.manage_thread_pool, self.groupbox_timeline,
                                                          self.settings)
        self.groupbox_ocr = GroupboxOCRServer(self.manage_thread_pool, self.groupbox_timeline,
                                              self.settings)

        # =========== Layout bên  Phải ===========
        self.tab_addsub_right = QWidget()
        self.bg_right_frame = QFrame()
        self.bg_right_frame.setObjectName("bg_frame")

    # self.video_render = RenderVideo(self.manage_thread_pool,self.manage_cmd, self.db_app)

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.bg_layout = QVBoxLayout(self)  # lấy self làm cha , tức là bg_layout làm con của self
        self.bg_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.bg_layout)
        self.content_tab_layout = QHBoxLayout()

        # layout bên trái
        self.content_left_layout = QVBoxLayout()
        self.content_edit_text_layout = QHBoxLayout()
        self.content_edit_text_L_layout = QVBoxLayout()
        self.content_edit_text_R_layout = QVBoxLayout()
        # self.tab_addsub_left_layout = QVBoxLayout()
        # self.tab_addsub_left_layout.setContentsMargins(0, 0, 0, 0)

        # layout bên phải
        self.content_right_layout = QVBoxLayout()
        # self.content_right_layout.setContentsMargins(0, 0, 0, 0)

        # layout bên phải
        self.content_bottom_layout = QHBoxLayout()
        self.content_bottom_layout.setContentsMargins(0, 0, 0, 0)

        self.convert_layout = QHBoxLayout()
        self.convert_layout.setContentsMargins(0, 0, 0, 0)

        self.content_config_layout = QHBoxLayout()
        self.content_config_layout.setContentsMargins(0, 0, 0, 0)

        self.bottom_layout = QHBoxLayout()

    # layout bên phải

    def add_widgets_to_layouts(self):
        self.resize_splitter.setOrientation(Qt.Orientation.Horizontal)

        widget_left = QWidget()
        widget_left.setLayout(self.content_left_layout)
        widget_right = QWidget()
        widget_right.setLayout(self.content_right_layout)
        self.resize_splitter.addWidget(widget_left)
        self.resize_splitter.addWidget(widget_right)

        self.bg_layout.addWidget(self.resize_splitter, 80)
        self.bg_layout.addLayout(self.content_bottom_layout, 20)
        self.content_left_layout.addWidget(self.groupbox_timeline, 60)
        self.content_left_layout.addLayout(self.content_edit_text_layout, 40)
        self.content_edit_text_layout.addLayout(self.content_edit_text_L_layout, 50)
        self.content_edit_text_layout.addLayout(self.content_edit_text_R_layout, 50)

        self.content_edit_text_L_layout.addWidget(QLabel("TEXT ORIGIN"))
        self.content_edit_text_L_layout.addWidget(self.text_edit_origin)

        self.content_edit_text_R_layout.addWidget(QLabel("TEXT TRANS"))

        self.content_edit_text_R_layout.addWidget(self.text_edit_trans)

        # self.bg_layout.addLayout(self.content_right_layout)
        self.content_right_layout.addWidget(self.gbox_preview)

        self.content_bottom_layout.addWidget(self.groupbox_ocr, 30)
        self.content_bottom_layout.addWidget(self.groupbox_translate, 30)
        self.content_bottom_layout.addWidget(self.groupbox_setting, 40)

    def setup_connections(self):
        # self.gbox_preview.sliderChangeFrameChanged.connect(self.sliderChangeFrameChanged)
        self.manage_thread_pool.resultChanged.connect(self._resultThreadChanged)
        self.text_edit_origin.textChanged.connect(self.textEditChanged)
        self.text_edit_trans.textChanged.connect(self.textEditChanged)


    def textEditChanged(self):
        self.manage_thread_pool.resultChanged.emit(UPDATE_CONTENT_EDIT_BINDING,
                                                   UPDATE_CONTENT_EDIT_BINDING, (self.text_edit_origin.toPlainText(),self.text_edit_trans.toPlainText()))

    # self.groupbox_timeline.main_table.selectRow(data - 1)

    def _resultThreadChanged(self, id_worker, id_thread, result):
        # print(id_worker, id_thread)
        if id_thread == CHANGE_FONT_SIZE_TABLE_EDIT_SUB or id_thread == CHANGE_COLOR_TABLE_EDIT_SUB:
            self.set_style_text_edit()

        if id_thread == ROW_SELECTION_CHANGED_TABLE_EDIT_SUB:
            file_imgae, text_origin, text_trans = self.groupbox_timeline.getDataRow(result - 1)
            self.text_edit_trans.clear()
            self.text_edit_origin.clear()
            self.text_edit_origin.setPlainText(text_origin)
            self.text_edit_trans.setPlainText(text_trans)

    # if id_thread == LOAD_CONFIG_CHANGED:
    # 	self.loadDataConfigCurrent(result)
    def loadFileSRTCurrent(self, fileSRTCurrent, list_srt, db_app, db_srt_file):
        # print(fileSRTCurrent)

        self.fileSRTCurrent = fileSRTCurrent

        self.groupbox_timeline.loadFileSRTCurrent(fileSRTCurrent)

        self.gbox_preview.loadFileSRTCurrent(fileSRTCurrent)
        self.groupbox_translate.loadFileSRTCurrent(fileSRTCurrent)
        # print('fileSRTCurrent')

        self.groupbox_setting.loadFileSRTCurrent(fileSRTCurrent, list_srt, db_app, db_srt_file)

    def loadDataConfigCurrent(self, configCurrent: CauHinhTuyChonModel):
        # print("loadDataConfigCurrent")

        self.configCurrent = configCurrent

        self.groupbox_timeline.loadDataConfigCurrent(configCurrent)
        self.gbox_preview.loadDataConfigCurrent(configCurrent)
        self.groupbox_translate.loadData(configCurrent)
        self.groupbox_setting.loadDataConfigCurrent(configCurrent)
        self.set_style_text_edit()

    def set_style_text_edit(self):
        cau_hinh = json.loads(self.configCurrent.value)
        try:

            font_size_table_edit = cau_hinh["font_size_table_edit"]
        except:
            cau_hinh["font_size_table_edit"] = 18
            self.configCurrent.value = json.dumps(cau_hinh)
            self.configCurrent.save()
        try:

            color_text_table_edit = cau_hinh["color_text_table_edit"]
        except:
            cau_hinh["color_text_table_edit"] = '#ffffff'
            self.configCurrent.value = json.dumps(cau_hinh)
            self.configCurrent.save()#u"color: rgb(255, 255, 255);"

        self.text_edit_trans.setStyleSheet(
            f"font-size:{cau_hinh['font_size_table_edit']}px;color:{cau_hinh['color_text_table_edit']};")
        self.text_edit_origin.setStyleSheet(
            f"font-size:{cau_hinh['font_size_table_edit']}px;color:{cau_hinh['color_text_table_edit']};")

    def showData(self, data):
        pass

    def dragEnterEvent(self, event):
        # print('drag-enter')
        if event.mimeData().hasUrls():
            # print('has urls')
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        lines = []
        for url in event.mimeData().urls():
            lines.append(url.toLocalFile())
        if len(lines) > 0:
            srt_path = lines[0]
            if os.path.isfile(srt_path) is True:
                name, ext = os.path.splitext(srt_path)
                if not ext.lower() in ['.srt']:
                    return PyMessageBox().show_warning("Thông báo", f"File {ext} không được hỗ trợ")
                self.manage_thread_pool.resultChanged.emit(LOAD_VIDEO_FROM_FILE_SRT, LOAD_VIDEO_FROM_FILE_SRT, srt_path)
            else:
                return PyMessageBox().show_warning("Thông báo", "File SUB srt không không tồn tại ")

# def keyPressEvent (self, event):
# 	print('111111')
