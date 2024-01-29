import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import budoux
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import Qt, Signal, QEvent, QPoint, QItemSelection, QItemSelectionModel, Slot, \
    QCoreApplication
from PySide6.QtGui import QColor, QKeyEvent, QKeySequence, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu, QTableWidgetItem, QAbstractItemView, \
    QHeaderView, QTableView, QStyledItemDelegate, QPlainTextEdit

from gui.helpers.constants import ROW_SELECTION_CHANGED_TABLE_EDIT_SUB, RESULT_TRANSLATE_SUB_EXTRACT, \
    TRANSLATE_SUB_EXTRACT_FINISHED, ITEM_TABLE_TIMELINE_EDIT_SUB_CHANGED, TOGGLE_SPINNER, \
    LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT, \
    UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, TOOL_CODE_MAIN, SETTING_APP_DATA, \
    LOAD_SUB_TRANSLATE_TXT_TABLE_EXTRACT, RESULT_TRANSLATE_SUB_EXTRACT_PART, \
    LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT_PART, TRANSLATE_SUB_PART_TAB_EXTRACT, STOP_THREAD_TRANSLATE, \
    PLAY_VIDEO_AGAIN, LANGUAGE_CODE_SPLIT_NO_SPACE, ACTION_PRESS_FIND_REPLACE, \
    ACTION_PRESS_RUT_GON_NOI_DUNG, ACTION_PRESS_TRANSLATE_AGAIN, ACTION_PRESS_DELETE, ACTION_PRESS_GOP_SUB, \
    ACTION_PRESS_TACH_SUB, UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, CHANGE_FONT_SIZE_TABLE_EDIT_SUB, \
    CHANGE_COLOR_TABLE_EDIT_SUB, DETECT_IMAGE_TO_TEXT, STOP_THREAD_OCR, DETECT_IMAGE_TO_TEXT_PART, \
    UPDATE_VALUE_PROGRESS_OCR_TAB_EDIT, OCR_TEXT_FINISHED, OCR_PART_TAB_EDIT, ACTION_PRESS_OCR_AGAIN, \
    ACTION_PRESS_PREVIOUS_LINE_SUB, ACTION_PRESS_NEXT_LINE_SUB, UPDATE_CONTENT_EDIT_BINDING
from gui.helpers.thread.manage_thread_pool import ManageThreadPool
from .model_timeline_addsub import ColumnNumberTabEdit, TableEditModel
from ..py_dialogs.py_dialog_find_replace import PyDialogFindReplace
from ..py_dialogs.py_dialog_get_int import PyDialogGetInt
from ..py_dialogs.py_dialog_summary import PyDialogSummary
from ..py_messagebox.py_massagebox import PyMessageBox
from ...helpers.func_helper import getValueSettings, seconds_to_timestamp, string_time_to_seconds
from ...helpers.translatepy.translators import GoogleTranslateV2


class PlainTextDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QPlainTextEdit(parent)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setPlainText(value)

    def setModelData(self, editor, model, index):
        value = editor.toPlainText()
        model.setData(index, value, Qt.EditRole)


class TableView(QTableView):
    def __init__(self, manage_thread_pool, *args, **kwargs):
        QTableView.__init__(self, *args, **kwargs)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        # self.setStyleSheet("QAbstractItemView{font-size:14px}")

        self.manage_thread_pool = manage_thread_pool

    def keyPressEvent(self, event):
        # print(event.text())
        # print(event.key())
        # print(event.type())
        if event.key() == Qt.Key_Up:
            # self.selectRow(self.currentIndex().row() - 1)
            index = self.moveCursor(
                QtWidgets.QAbstractItemView.MoveUp, QtCore.Qt.NoModifier
            )
            command = self.selectionCommand(self.currentIndex(), event)
            self.selectionModel().setCurrentIndex(index, command)

        # elif event.key() == Qt.S:
        # 	self.selectRow(self.currentIndex().row() + 1)

        elif event.key() == Qt.Key_Down:
            # self.selectRow(self.currentIndex().row() + 1)
            index = self.moveCursor(
                QtWidgets.QAbstractItemView.MoveDown, QtCore.Qt.NoModifier
            )
            command = self.selectionCommand(self.currentIndex(), event)
            self.selectionModel().setCurrentIndex(index, command)

        elif event.type() == QEvent.KeyPress and (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter):
            if self.state() != QAbstractItemView.EditingState:
                self.edit(self.currentIndex())


        elif event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_Space:
            # print('dddđ')
            self.manage_thread_pool.resultChanged.emit(PLAY_VIDEO_AGAIN, PLAY_VIDEO_AGAIN,
                                                       self.currentIndex().row() + 1)

        elif event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_F:
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_FIND_REPLACE, ACTION_PRESS_FIND_REPLACE, "")

        elif event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_R:
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_RUT_GON_NOI_DUNG, ACTION_PRESS_RUT_GON_NOI_DUNG, "")

        elif event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_T:
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_TRANSLATE_AGAIN, ACTION_PRESS_TRANSLATE_AGAIN, "")

        elif event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_E:
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_OCR_AGAIN, ACTION_PRESS_OCR_AGAIN, "")

        elif event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_D:
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_DELETE, ACTION_PRESS_DELETE, "")

        elif event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_Delete:
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_DELETE, ACTION_PRESS_DELETE, "")

        elif event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_M:
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_GOP_SUB, ACTION_PRESS_GOP_SUB, "")

        elif event.modifiers() & Qt.ControlModifier and event.type() == QEvent.KeyPress and event.key() == Qt.Key.Key_X:
            self.manage_thread_pool.resultChanged.emit(ACTION_PRESS_TACH_SUB, ACTION_PRESS_TACH_SUB, "")

        # elif event.type() == QEvent.KeyPress and event.key() == Qt.Key.:
        # 	# print('dddđ')
        # 	self.manage_thread_pool.resultChanged.emit(PLAY_VIDEO_AGAIN, PLAY_VIDEO_AGAIN, self.currentIndex().row()+1)

        else:
            super().keyPressEvent(event)


class TableTimelineEditSub(QWidget):
    rowSelectionChanged = Signal(int)

    def __init__(self, manage_thread_pool: ManageThreadPool):
        super().__init__()
        # SET STYLESHEET

        self.manage_thread_pool = manage_thread_pool  # tạo trước ui
        self.thread_limit_update = ThreadPoolExecutor(max_workers=1)

        self.listRowPause = {}
        self.listIItemAction = {}
        self.resultThread = {}
        self.isHasSub = False
        self.isLoadSrtFinish = True
        self.listRowTransPart = []
        self.listRowOCRPart = []
        self.setMinimumHeight(200)
        self.list_row_trans_chunk = []
        self.list_row_ocr_chunk = []
        self.data_sub_origin = []
        self.count_result_trans = 0
        self.count_result_ocr = 0

        self.count_result_pos = 0
        self.total_pos_update = 0
        self.count_split_sub = 0
        self.count_result_check_lech = 0
        self.resultThread = {}
        self.isLoadSrtFinish = True
        self.isCheckingDoLech = True
        self.isCheckFinish = False
        self.isTranslating = False
        self.isOCRing = False

        self.getXCenterSub = None
        settings = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting')
        self.chunk_split = settings.get('chunk_split', 5)
        self.list_language_support = settings.get("language_support")
        self.init_ui()

    def init_ui(self):
        self.create_widgets()

        self.create_layouts()
        self.add_widgets_to_layouts()

        self.setup_table()
        # show dư liệu
        # self.displayTable()

        self.setup_connections()

    def create_widgets(self):
        self.main_table = TableView(self.manage_thread_pool)
        self.main_table.setObjectName(u"tableWidget")
        # self.main_table.setAlternatingRowColors(True)
        # tạo Nút CheckBox trên tiêu đề

        # menu ngữ cảnh
        self.menu = QMenu()
        # newAct = contextMenu.addAction(
        # 	"New (&A)", self.triggered, shortcut=QtGui.QKeySequence.New)
        trans_act = QAction("Dịch Lại ()", self)

        self.menu.addAction("Dịch Lại", self.signal_translate_again, shortcut=QKeySequence(Qt.CTRL | Qt.Key_T))
        self.menu.addAction("Tách Chữ Lại", self.signal_ocr_again, shortcut=QKeySequence(Qt.CTRL | Qt.Key_E))
        self.menu.addAction("Xóa", self.signal_remove, shortcut=QKeySequence(Qt.CTRL | Qt.Key_D))
        self.menu.addAction("Rút Gọn Nội Dung", self.signal_summary, shortcut=QKeySequence(Qt.CTRL | Qt.Key_R))

        self.menu.addAction("Find And Replace", self.signal_find_replace,
                            shortcut=QKeySequence(Qt.CTRL | Qt.Key_F))  # (QAction('test'))
        self.menu.addAction("Gộp Lại Sub", self.signal_concat_sub,
                            shortcut=QKeySequence(Qt.CTRL | Qt.Key_M))  # (QAction('test'))
        self.menu.addAction("Tách Sub Thành Nhiều Dòng", self.signal_split_sub,
                            shortcut=QKeySequence(Qt.CTRL | Qt.Key_X))  # (QAction('test'))

    def signal_find_replace(self):
        # print(self.getDataSub())
        dialog = PyDialogFindReplace(self, self.manage_thread_pool, self.getDataSub())

        if dialog.exec():
            pass

    # self.manage_thread_pool.resultChanged.emit(UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, "")

    # self.model.update_data = dialog.getValue()

    # print(dialog.getValue())

    def signal_split_sub(self):
        items_selected = self.main_table.selectionModel().selectedRows()
        if len(items_selected) < 1:
            return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn tách")
        elif len(items_selected) > 1:
            return PyMessageBox().show_warning('Cảnh Báo', "Chỉ có thể tách từng dòng")
        row_number = items_selected[0].row()

        time_line = self.getValueItem(row_number, ColumnNumberTabEdit.column_avatar.value)

        start = time_line.split(' --> ')[0]
        end = time_line.split(' --> ')[1]
        sub_origin = self.getValueItem(row_number, ColumnNumberTabEdit.column_original.value)
        translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)
        lang_source = translator_server.language(sub_origin)
        count_chars = 0
        if 'jpn' in str(lang_source.result):
            parser = budoux.load_default_japanese_parser()
            content = sub_origin.strip().replace("\n", "")
            count_chars = len(content)
            list_content = parser.parse(content)

        elif 'zho' in str(lang_source.result):  # tieng trun gian the
            parser = budoux.load_default_simplified_chinese_parser()
            content = sub_origin.strip().replace("\n", "")
            count_chars = len(content)
            list_content = parser.parse(content)

        elif 'och' in str(lang_source.result):  # tieng trung quoc te
            parser = budoux.load_default_traditional_chinese_parser()
            content = sub_origin.strip().replace("\n", "")
            count_chars = len(content)
            list_content = parser.parse(content)
        else:
            list_content = sub_origin.strip().replace("\n", " ").split(" ")
            count_chars = len(list_content)

        content = "- Bạn muốn tách tối đa bao nhiêu từ trên 1 dòng ?"
        # content += "\n + Đối với ngôn ngữ không có dấu khoảng cách như Trung Quốc, Nhật Bản,... thì lên để số từ lớn."
        # content += "\n + Đối với ngôn ngữ có dấu khoảng cách thì lên để số từ bé."
        # content += f"\n\n- Đoạn Sub này là ngôn ngữ {lang_source.result.in_foreign_languages.get('vi')}"
        content += f"\n\n- Đoạn Sub này có tổng cộng {count_chars} từ "

        dialog = PyDialogGetInt(content, "Tách Sub Thành Nhiều Dòng", "Số từ/dòng: ", 2, 50, height=150)

        if dialog.exec():

            list_text = []
            text_c = ''
            for index, text_ in enumerate(list_content):
                max_length = dialog.getValue()

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

            start_time = datetime.strptime(start, "%H:%M:%S,%f")
            end_time = datetime.strptime(end, "%H:%M:%S,%f")

            time_split = (end_time - start_time).total_seconds() / len(list_text)

            self.model.removeRows(row_number)
            # print(list_text)
            for ind, text in enumerate(list_text):
                # for index, item in enumerate(items_selected):
                # 	print()
                start_pre = seconds_to_timestamp((
                        string_time_to_seconds(start) + time_split * ind))
                end_pre = seconds_to_timestamp((
                        string_time_to_seconds(start_pre) + time_split))
                # print(start_pre)
                # print(end_pre)
                row_cur = row_number + ind

                self.model.insertRows(row_cur)
                # print(row_start, [None, None, f"{time_start} --> {time_end}", sub_origin_concat.strip("\n"),
                # 				  sub_trans_concat.strip("\n")])
                # ['1', None, '00:00:00,390 --> 00:00:01,160', 'All righty, guys.']
                # ["Ratio", "Time", "Pos Ori", "Original", "Translation", "Pos Trans"]
                self.addDataRow(row_cur, [f"{start_pre} --> {end_pre}", text, ''])

            # self.main_table.selectRow(row_number)
            self.manage_thread_pool.resultChanged.emit(UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED,
                                                       UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, "")

            self.selectRowDown()
        else:
            return

    def signal_concat_sub(self):
        time_start = ''
        time_end = ''
        sub_origin_concat = ''
        sub_trans_concat = ''

        items_selected = self.main_table.selectionModel().selectedRows()
        if len(items_selected) < 2:
            return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn gộp")

        row_start = items_selected[0].row()
        # pos_ori = self.getValueItem(row_start, ColumnNumber.column_position_origin.value)
        # pos_trans = self.getValueItem(row_start, ColumnNumber.column_position_trans.value)
        # print(items_selected)
        row_pre = 0
        for index, item in enumerate(items_selected):
            if not index == 0:
                if not (item.row() - row_pre) == 1:
                    return PyMessageBox().show_warning('Cảnh Báo', "Chỉ được gộp các hàng liền nhau")
            row_pre = item.row()

        for index, item in enumerate(items_selected):

            time_line = self.getValueItem(row_start, ColumnNumberTabEdit.column_avatar.value)
            start = time_line.split(' --> ')[0]
            end = time_line.split(' --> ')[1]

            if index == 0:
                time_start = start

            time_end = end
            sub_org = self.getValueItem(row_start, ColumnNumberTabEdit.column_original.value)
            sub_trans = self.getValueItem(row_start, ColumnNumberTabEdit.column_translated.value)
            # print(sub_org)
            sub_origin_concat += sub_org + " "
            sub_trans_concat += sub_trans + " "

            self.model.removeRow(row_start)

        self.model.insertRow(row_start)

        self.addDataRow(row_start, [f"{time_start} --> {time_end}", sub_origin_concat.strip("\n"),
                                    sub_trans_concat.strip("\n")])

        self.manage_thread_pool.resultChanged.emit(UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED,
                                                   UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, "")

        self.selectRowDown()

    def signal_summary(self):
        cau_hinh = json.loads(self.configCurrent.value)
        cau_hinh_edit_sub = json.loads(self.fileSRTCurrent.value)
        type_tts_sub = cau_hinh_edit_sub["sub_hien_thi"]

        # list_language_tts = SERVER_TAB_TTS.get(
        # 	list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("language_tts")
        #
        # language_tts = list_language_tts.get(cau_hinh["servers_tts"]["language_tts"])
        # server_trans = SERVER_TAB_TTS.get(
        # 	list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]])
        # key_lang = server_trans.get("key_lang")
        # language_tts = self.list_language_support.get(key_lang).get(cau_hinh["servers_tts"]["language_tts"])

        items_selected = self.main_table.selectionModel().selectedRows()
        if len(items_selected) < 1:
            return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn rút gọn")

        translator_server = GoogleTranslateV2(manage_thread_pool=self.manage_thread_pool)

        if type_tts_sub == "trans":
            item_sub_trans = self.getValueItem(
                items_selected[0].row(), ColumnNumberTabEdit.column_translated.value)
            if item_sub_trans == "":
                return PyMessageBox().show_warning("Thông Báo", "Sub chưa được dịch")

            lang_result = translator_server.language(item_sub_trans)

        else:
            item_sub_org = self.getValueItem(
                items_selected[0].row(), ColumnNumberTabEdit.column_original.value)

            lang_result = translator_server.language(item_sub_org)
        #
        # # lang_source = lang_result.result.alpha3
        # lang_tts = Language(cau_hinh["servers_tts"]["language_tts"].split("-")[0]).alpha3
        #
        # if not lang_result.result.alpha3 == lang_tts:
        # 	return PyMessageBox().show_warning('Cảnh Báo', "Ngôn ngữ SUB không trùng với ngôn ngữ đọc. Vui lòng chọn đúng ngôn ngữ đọc, hoặc Chế Độ Đọc khác")
        # if hasattr(self, 'model_AI'):
        for index, item in enumerate(items_selected):
            # item_sub_trans = self.getValueItem(item.row(), ColumnNumber.column_sub_translate.value)
            # item_sub_org = self.getValueItem(item.row(), ColumnNumber.column_sub_original.value)
            # item_time = self.getValueItem(item.row(), ColumnNumber.column_time.value)
            data_sub = self.getDataRow(item.row())
            # print(data_sub)

            dialog = PyDialogSummary(self.manage_thread_pool, data_sub, mode_doc=type_tts_sub,
                                     language=lang_result.result.in_foreign_languages.get("en"),
                                     source_lang=lang_result.result.alpha2)
            if dialog.exec():
                if type_tts_sub == "trans":
                    self.setValueItem(item.row(), ColumnNumberTabEdit.column_translated.value, dialog.getValue())
                # item_sub_trans.setText(dialog.getValue())
                else:
                    self.setValueItem(item.row(), ColumnNumberTabEdit.column_original.value, dialog.getValue())

            else:
                continue
        self.manage_thread_pool.resultChanged.emit(UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED,
                                                   UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, "")

    # self.timer = QTimer()  # thực hiện việc gi đó sau khoảng thời gian
    def signal_remove(self):
        items_selected = self.main_table.selectionModel().selectedRows()
        if len(items_selected) < 1:
            return PyMessageBox().show_warning('WARNING', "Please select the line you want to delete")

        req = PyMessageBox().show_question("CONFIRM", "Are you sure you want to delete ?")
        row_start = items_selected[0].row()

        if req is True:
            row_pre = 0
            for index, item in enumerate(items_selected):
                if not index == 0:
                    if not (item.row() - row_pre) == 1:
                        return PyMessageBox().show_warning('WARNING', "Chỉ được xóa các hàng liền nhau")
                row_pre = item.row()

            # for index, item in enumerate(items_selected):
            self.model.removeRows(items_selected[0].row(), len(items_selected))
        else:
            return
        self.selectRowDown()
        self.main_table.selectRow(row_start)

        self.manage_thread_pool.resultChanged.emit(UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED,
                                                   UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, "")

    def signal_ocr_again(self):
        self.listRowOCRPart = []
        self.list_row_trans_chunk = []
        self.count_result_trans = 0
        self.isTranslating = False

        items_selected = self.main_table.selectionModel().selectedRows()
        if len(items_selected) < 1:
            return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn dịch")

        data = []

        for index, item in enumerate(items_selected):
            self.listRowOCRPart.append(item.row())
            # ("Ratio", "Time", "Pos Ori", "Original", "Translation", "Pos Trans")
            time, origin, translate = self.getDataRow(item.row())
            # print(time, origin, translate)
            data.append([time, origin, translate])
        # print(self.listRowTransPart)
        if len(data) > 0:
            self.manage_thread_pool.resultChanged.emit(OCR_PART_TAB_EDIT, OCR_PART_TAB_EDIT,
                                                       data)

    def signal_translate_again(self):
        self.listRowTransPart = []
        self.list_row_trans_chunk = []
        self.count_result_trans = 0
        self.isTranslating = False

        items_selected = self.main_table.selectionModel().selectedRows()
        if len(items_selected) < 1:
            return PyMessageBox().show_warning('Cảnh Báo', "Vui lòng chọn dòng muốn dịch")

        data = []

        for index, item in enumerate(items_selected):
            self.listRowTransPart.append(item.row())
            # ("Ratio", "Time", "Pos Ori", "Original", "Translation", "Pos Trans")
            time, origin, translate = self.getDataRow(item.row())

            data.append([time, origin, translate])
        # print(self.listRowTransPart)
        if len(data) > 0:
            self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_PART_TAB_EXTRACT, TRANSLATE_SUB_PART_TAB_EXTRACT,
                                                       data)

    def selectRowDown(self):
        # Tạo một sự kiện phím giả
        key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Down, Qt.NoModifier)
        #
        # # Gửi sự kiện đến table_view
        QCoreApplication.postEvent(self.main_table, key_event)

    def selectRowUp(self):
        # Tạo một sự kiện phím giả
        key_event = QKeyEvent(QEvent.KeyPress, Qt.Key_Up, Qt.NoModifier)
        #
        # # Gửi sự kiện đến table_view
        QCoreApplication.postEvent(self.main_table, key_event)

    def setup_table(self):
        # ========== Cài đặt cho table============
        data = [["", "", ""]]
        name_column = ["Time", "Original", "Translation"]
        self.model = TableEditModel(data, name_column)
        self.main_table.setModel(self.model)
        # self.main_table.setItemDelegateForColumn(ColumnNumberTabEdit.column_original.value,PlainTextDelegate())

        self.main_table.setAlternatingRowColors(True)  # hiện màu dòng xen kẽ

        self.main_table.horizontalHeader().setStretchLastSection(True)  # cái này cho kéo dãn full table
        # self.main_table.horizontalHeader().setDefaultSectionSize(126)
        self.main_table.horizontalHeader().setMinimumSectionSize(126)
        self.main_table.verticalHeader().setDefaultSectionSize(100)
        # self.main_table.verticalHeader().setMinimumHeight(100)
        # self.main_table.verticalHeader().resizeSection(row, height)
        # self.main_table.verticalHeader().setSectionResizeMode(
        # 	QHeaderView.ResizeMode.ResizeToContents)  # làm cho content xuống dòng
        # QHeaderView.setSectionsClickable()

        self.main_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)  # cho phép chọn thành dòng
        # self.main_table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)  # cho phép chọn 1 dòng

        # self.main_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)  # không cho edit

        # ------------------------ Set FIxed tiêu đề ko cho di chuyển

        self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumberTabEdit.column_avatar.value,
                                                                QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content

        # self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumberTabEdit.column_original.value,
        #                                                         QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content
        # #
        # self.main_table.horizontalHeader().setSectionResizeMode(ColumnNumberTabEdit.column_original.value,
        #                                                         QHeaderView.ResizeMode.ResizeToContents)  # gian cách vừa với content

        # tao menucontext
        self.main_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.main_table.customContextMenuRequested.connect(self.generateMenu)

    def generateMenu(self, pos):
        x = pos.x() + 10
        y = pos.y() + 30
        self.menu.exec(self.main_table.mapToGlobal(QPoint(x, y)))

    def setup_connections(self):
        ##==================Các sự kiện của table ========

        # self.main_table.doubleClicked.connect(self.cellDoubleClicked)  # nhận đc row và colum
        # self.main_table.itemDoubleClicked.connect(self.itemDoubleClicked)  # nhận đc item
        # self.main_table.itemChanged.connect(self.itemDataChanged)  # nh# nhận đc item
        self.model.dataChanged.connect(self.itemDataChanged)
        self.model.layoutChanged.connect(self.itemLayoutChanged)
        self.main_table.selectionModel().selectionChanged.connect(self._rowSelectionChanged)  # nhận đc item

        self.manage_thread_pool.resultChanged.connect(self.resultThreadChanged)

    def selectListRow(self, list_row):
        selection = QItemSelection()
        for row in list_row:
            self.main_table.selectRow(row)
            model_index = self.model.index(row, 0)
            # Select single row.
            selection.select(model_index, model_index)  # top left, bottom right identical
        mode = QItemSelectionModel.SelectionFlag.Select | QItemSelectionModel.SelectionFlag.Rows
        # Apply the selection, using the row-wise mode.
        resultselection = self.main_table.selectionModel()
        resultselection.select(selection, mode)

    @Slot(QItemSelection, QItemSelection)
    def _rowSelectionChanged(self, selected,
                             deselected):  # emit bên widget kia kết nối với resultChanged  để nhận thông tin qua các widget khác nhau
        # print(11)
        self.manage_thread_pool.resultChanged.emit(ROW_SELECTION_CHANGED_TABLE_EDIT_SUB,
                                                   ROW_SELECTION_CHANGED_TABLE_EDIT_SUB,
                                                   self.main_table.currentIndex().row() + 1)

    def create_layouts(self):
        self.widget_layout = QVBoxLayout(self)
        self.widget_layout.setContentsMargins(0, 0, 0, 0)

    def add_widgets_to_layouts(self):
        self.widget_layout.addWidget(self.main_table)

    # @decorator_try_except_class
    def displayTable(self, data, path_video):
        """ Mô tả: Hiển thị dữ liệu vừa lấy được trong video """
        self.isLoadSrtFinish = True
        if data == [] or len(data) < 1:
            return

        self.model.update_data = data

        self.main_table.selectRow(0)
        self.path_video = path_video
        self.isHasSub = True
        self.isLoadSrtFinish = False

    # print("Ok")
    def saveDataToDB(self):
        if hasattr(self, "fileSRTCurrent") and self.fileSRTCurrent:
            # print(1)

            cau_hinh = json.loads(self.fileSRTCurrent.value)
            cau_hinh["data_table"] = self.getDataSub()
            self.fileSRTCurrent.value = json.dumps(cau_hinh)
            self.fileSRTCurrent.save()

    # print(2)

    # print('saveDataToDB')

    def itemLayoutChanged(self):

        if self.isLoadSrtFinish is False:
            self.saveDataToDB()

    def itemDataChanged(self, item):
        if self.isLoadSrtFinish is False:
            # items_selected = self.main_table.selectionModel().selectedRows()
            # if len(items_selected)>0:
            self.saveDataToDB()
            self.manage_thread_pool.resultChanged.emit(ITEM_TABLE_TIMELINE_EDIT_SUB_CHANGED,
                                                       ITEM_TABLE_TIMELINE_EDIT_SUB_CHANGED, item.row() + 1)

    def item_table(self, row_number, data):

        item = QTableWidgetItem(str(data))
        item.setForeground(QColor("#ffffff"))
        return item

    def resultThreadChanged(self, id_worker, typeThread, result):

        if typeThread == UPDATE_CONTENT_EDIT_BINDING:
            text_or, text_tr = result
            self.setValueItem(self.main_table.currentIndex().row(), ColumnNumberTabEdit.column_original.value, text_or)
            self.setValueItem(self.main_table.currentIndex().row(), ColumnNumberTabEdit.column_translated.value, text_tr)

        if typeThread == ACTION_PRESS_PREVIOUS_LINE_SUB:
            self.selectRowUp()
        if typeThread == ACTION_PRESS_NEXT_LINE_SUB:
            self.selectRowDown()

        if typeThread == ACTION_PRESS_RUT_GON_NOI_DUNG:
            self.signal_summary()
        if typeThread == ACTION_PRESS_DELETE:
            self.signal_remove()

        if typeThread == ACTION_PRESS_OCR_AGAIN:
            self.signal_ocr_again()

        if typeThread == ACTION_PRESS_TRANSLATE_AGAIN:
            self.signal_translate_again()

        if typeThread == ACTION_PRESS_GOP_SUB:
            self.signal_concat_sub()

        if typeThread == ACTION_PRESS_TACH_SUB:
            self.signal_split_sub()

        if typeThread == ACTION_PRESS_FIND_REPLACE:
            self.signal_find_replace()

        if typeThread == CHANGE_FONT_SIZE_TABLE_EDIT_SUB and not result is None:
            self.model.update_font(result)
            self.refresh()

        if typeThread == CHANGE_COLOR_TABLE_EDIT_SUB and not result is None:
            self.model.update_color(result)
            self.refresh()

        if typeThread == STOP_THREAD_OCR:
            self.count_result_ocr = 0
            self.isOCRing = False
            self.list_row_ocr_chunk = []
            self.listRowOCRPart = []

        if typeThread == STOP_THREAD_TRANSLATE:
            self.count_result_trans = 0
            self.isTranslating = False
            self.list_row_trans_chunk = []
            self.listRowTransPart = []

        if typeThread == DETECT_IMAGE_TO_TEXT and not result is None:

            if "row" in result.keys() and "text_ocr" in result.keys():
                # print(RESULT_TRANSLATE_SUB_EXTRACT)
                self.isOCRing = True

                self.count_result_ocr = self.count_result_ocr + 1

                self.list_row_ocr_chunk.append(result)
                if len(self.list_row_ocr_chunk) == int(30 * (self.model.rowCount() / 1000)):
                    data = [item for item in self.list_row_ocr_chunk]
                    self.list_row_ocr_chunk = []
                    data_list = []
                    for index, item_ in enumerate(data):
                        data_list.append((
                            int(item_["row"]), ColumnNumberTabEdit.column_original.value, item_["text_ocr"]))

                    # self.thread_limit_update.submit(self.model.update_list_item, data_list)
                    self.model.update_list_item(data_list)
                # print('1111')
                self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_OCR_TAB_EDIT, "",
                                                             self.count_result_ocr)
                print(f"Dòng đã lấy: {self.count_result_ocr}", f"Tổng số dòng: {self.model.rowCount()}")

            if self.count_result_ocr == self.model.rowCount():
                if len(self.list_row_ocr_chunk) > 0:
                    data_list = []
                    for index, item_ in enumerate(self.list_row_ocr_chunk):
                        data_list.append((
                            int(item_["row"]), ColumnNumberTabEdit.column_original.value, item_["text_ocr"]))

                    # self.thread_limit_update.submit(self.model.update_list_item, data_list)
                    self.model.update_list_item(data_list)

                self.isOCRing = False
                self.count_result_ocr = 0
                # if self.isCheckFinish:
                # 	self.isCheckingDoLech = False
                self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
                self.manage_thread_pool.resultChanged.emit(OCR_TEXT_FINISHED,
                                                           OCR_TEXT_FINISHED, None)
                self.refresh()
        if typeThread == DETECT_IMAGE_TO_TEXT_PART and not result is None:

            if "row" in result.keys() and "text_ocr" in result.keys():
                # print(RESULT_TRANSLATE_SUB_EXTRACT_PART)

                # if result and isinstance(result, dict):
                self.isOCRing = True
                # if self.isCheckFinish:
                # 	self.isCheckingDoLech = True
                # print(result)
                self.count_result_ocr = self.count_result_ocr + 1
                self.list_row_ocr_chunk.append(result)

                self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_OCR_TAB_EDIT, "",
                                                             self.count_result_ocr)
                # row = self.listRowTransPart[int(result["row"])]
                # self.setValueItem(row, ColumnNumberTabEdit.column_translated.value,
                # 	result["text_trans"])
                print(f"Dòng đã lấy: {self.count_result_ocr}", f"Tổng số dòng: {len(self.listRowOCRPart)}")

            if self.count_result_ocr == len(self.listRowOCRPart):

                if len(self.list_row_ocr_chunk) > 0:
                    data_list = []
                    # print(self.listRowTransPart)
                    for index, item_ in enumerate(self.list_row_ocr_chunk):
                        # print(item_)

                        row = self.listRowOCRPart[int(item_["row"])]

                        data_list.append((row, ColumnNumberTabEdit.column_original.value, item_["text_ocr"]))

                    self.model.update_list_item(data_list)

                self.list_row_ocr_chunk = []

                self.isOCRing = False
                self.count_result_ocr = 0
                self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
                self.manage_thread_pool.resultChanged.emit(OCR_TEXT_FINISHED,
                                                           OCR_TEXT_FINISHED, None)
                print('qua')
                self.refresh()

        if typeThread == RESULT_TRANSLATE_SUB_EXTRACT and not result is None:

            if "row" in result.keys() and "text_trans" in result.keys():
                # print(RESULT_TRANSLATE_SUB_EXTRACT)
                self.isTranslating = True

                self.count_result_trans = self.count_result_trans + 1

                self.list_row_trans_chunk.append(result)
                if len(self.list_row_trans_chunk) == int(30 * (self.model.rowCount() / 1000)):
                    data = [item for item in self.list_row_trans_chunk]
                    self.list_row_trans_chunk = []
                    data_list = []
                    for index, item_ in enumerate(data):
                        data_list.append((
                            int(item_["row"]), ColumnNumberTabEdit.column_translated.value, item_["text_trans"]))

                    # self.thread_limit_update.submit(self.model.update_list_item, data_list)
                    self.model.update_list_item(data_list)
                # print('1111')
                self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "",
                                                             self.count_result_trans)
                print(f"Dòng đã dịch: {self.count_result_trans}", f"Tổng số dòng: {self.model.rowCount()}")

            if self.count_result_trans == self.model.rowCount():
                if len(self.list_row_trans_chunk) > 0:
                    data_list = []
                    for index, item_ in enumerate(self.list_row_trans_chunk):
                        data_list.append((
                            int(item_["row"]), ColumnNumberTabEdit.column_translated.value, item_["text_trans"]))

                    # self.thread_limit_update.submit(self.model.update_list_item, data_list)
                    self.model.update_list_item(data_list)

                self.isTranslating = False
                self.count_result_trans = 0
                # if self.isCheckFinish:
                # 	self.isCheckingDoLech = False
                self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
                self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED,
                                                           TRANSLATE_SUB_EXTRACT_FINISHED, None)
                self.refresh()

        if typeThread == RESULT_TRANSLATE_SUB_EXTRACT_PART and not result is None:

            if "row" in result.keys() and "text_trans" in result.keys():
                # print(RESULT_TRANSLATE_SUB_EXTRACT_PART)

                # if result and isinstance(result, dict):
                self.isTranslating = True
                # if self.isCheckFinish:
                # 	self.isCheckingDoLech = True
                # print(result)
                self.count_result_trans = self.count_result_trans + 1
                self.list_row_trans_chunk.append(result)

                self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "",
                                                             self.count_result_trans)
                # row = self.listRowTransPart[int(result["row"])]
                # self.setValueItem(row, ColumnNumberTabEdit.column_translated.value,
                # 	result["text_trans"])
                print(f"Dòng đã dịch: {self.count_result_trans}", f"Tổng số dòng: {len(self.listRowTransPart)}")

            if self.count_result_trans == len(self.listRowTransPart):

                if len(self.list_row_trans_chunk) > 0:
                    data_list = []
                    # print(self.listRowTransPart)
                    for index, item_ in enumerate(self.list_row_trans_chunk):
                        # print(item_)

                        row = self.listRowTransPart[int(item_["row"])]

                        data_list.append((row, ColumnNumberTabEdit.column_translated.value, item_["text_trans"]))

                    self.model.update_list_item(data_list)

                self.list_row_trans_chunk = []

                self.isTranslating = False
                self.count_result_trans = 0
                self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
                self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED,
                                                           TRANSLATE_SUB_EXTRACT_FINISHED, None)
                print('qua')
                self.refresh()

        if typeThread == LOAD_SUB_TRANSLATE_TXT_TABLE_EXTRACT:
            self.isTranslating = True
            data_list = []
            for index, sub in enumerate(result):
                # self.setValueItem(index, ColumnNumber.column_sub_translate.value, sub)
                data_list.append((index, ColumnNumberTabEdit.column_translated.value, sub))
                self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "",
                                                             index + 1)

            # self.thread_limit_update.submit(self.model.update_list_item, data_list)
            self.model.update_list_item(data_list)
            self.isTranslating = False
            self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
            self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED, TRANSLATE_SUB_EXTRACT_FINISHED,
                                                       None)
            self.refresh()

        if typeThread == LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT:
            self.isTranslating = True

            ind_chunk, data_res, chunk_split = result
            # print(ind_chunk, data_res )
            data_list = []
            for index, sub in enumerate(data_res):
                if ind_chunk == -1:
                    data_list.append((self.count_result_trans, ColumnNumberTabEdit.column_translated.value, sub))
                # self.setValueItem(self.count_result_trans, ColumnNumber.column_sub_translate.value, sub)

                else:
                    data_list.append((
                        index + (chunk_split * ind_chunk), ColumnNumberTabEdit.column_translated.value, sub))
                # self.setValueItem(index + (chunk_split * ind_chunk), ColumnNumber.column_sub_translate.value, sub)

                self.count_result_trans = self.count_result_trans + 1

            # self.thread_limit_update.submit(self.model.update_list_item, data_list)
            self.model.update_list_item(data_list)
            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "",
                                                         self.count_result_trans)

            print(f"Dòng đã dịch: {self.count_result_trans}", f"Tổng số dòng: {self.model.rowCount()}")
            if self.count_result_trans == self.model.rowCount():
                self.isTranslating = False
                self.count_result_trans = 0
                self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
                self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED,
                                                           TRANSLATE_SUB_EXTRACT_FINISHED, None)
                self.refresh()

        if typeThread == LOAD_SUB_TRANSLATE_CHATGPT_TABLE_EXTRACT_PART:
            self.isTranslating = True

            data_list = []
            ind_chunk, data_res, chunk_split = result

            for index, sub in enumerate(data_res):
                if ind_chunk == -1:
                    row = self.listRowTransPart[self.count_result_trans]

                    data_list.append((row, ColumnNumberTabEdit.column_translated.value, sub))
                # self.setValueItem(self.count_result_trans, ColumnNumber.column_sub_translate.value, sub)

                else:
                    row = self.listRowTransPart[index + (chunk_split * ind_chunk)]

                    data_list.append((row, ColumnNumberTabEdit.column_translated.value, sub))
                # self.setValueItem(index + (chunk_split * ind_chunk), ColumnNumber.column_sub_translate.value, sub)
                self.count_result_trans = self.count_result_trans + 1

                print(f"Dòng đã dịch: {self.count_result_trans}", f"Tổng số dòng: {len(self.listRowTransPart)}")

                self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TRANSLATE_SUB_TAB_EXTRACT, "",
                                                             self.count_result_trans)

            # self.thread_limit_update.submit(self.model.update_list_item, data_list)
            self.model.update_list_item(data_list)
            if self.count_result_trans == len(self.listRowTransPart):
                self.isTranslating = False
                self.count_result_trans = 0

                self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)
                self.manage_thread_pool.resultChanged.emit(TRANSLATE_SUB_EXTRACT_FINISHED,
                                                           TRANSLATE_SUB_EXTRACT_FINISHED, None)
                self.refresh()

    def getValueItem(self, row, column):
        return self.model.data(self.model.index(row, column))

    def setValueItem(self, row, column, value):
        return self.model.update_item(row, column, value)

    def refresh(self):
        # print("Refreshing")
        self.manage_thread_pool.resultChanged.emit(UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED,
                                                   UPDATE_TABLE_TIMELINE_TEXT_SUB_CHANGED, "")

        self.model.layoutChanged.emit()

    def loadDataConfigCurrent(self, configCurrent):
        self.configCurrent = configCurrent
        cau_hinh = json.loads(configCurrent.value)

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
            self.configCurrent.save()

        self.model.update_color(cau_hinh["color_text_table_edit"])
        self.model.update_font(cau_hinh["font_size_table_edit"])

    def loadFileSRTCurrent(self, fileSRTCurrent):

        self.fileSRTCurrent = fileSRTCurrent
        data_sub = json.loads(self.fileSRTCurrent.value)
        self.displayTable(data_sub.get('data_table'), data_sub.get('video_file'))

    def getDataRow(self, row):
        """["Time", Origin", "Trans"]"""

        # """:return [time, sub_origin, sub_translate,do_lech, pos_ori, pos_trans]"""
        # data = list(self.getValueItem(row, i) for i in range(self.model.columnCount()))
        return self.model.getData()[row]

    def getDataRowCurrent(self):
        """["Time", Origin", "Trans"]"""

        # """:return [time, sub_origin, sub_translate,do_lech, pos_ori, pos_trans]"""
        data = list(self.getValueItem(self.main_table.currentIndex().row(), i) for i in range(self.model.columnCount()))
        return data

    def addDataRow(self, row, data):
        """["Time", Origin", "Trans"]"""

        for i in range(self.model.columnCount()):
            self.setValueItem(row, i, data[i])

    def getDataSub(self):
        """["Time", Origin", "Trans"]"""

        return self.model.getData()

    def resetDataColumn(self, col):
        """["Time", Origin", "Trans"]"""
        self.count_result_trans = 0
        self.isTranslating = False
        self.isOCRing = False
        self.list_row_trans_chunk = []
        self.model.resetDataColumn(col)
