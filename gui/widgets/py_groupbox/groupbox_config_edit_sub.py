import json
import os
import subprocess

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QHBoxLayout, QVBoxLayout, QGroupBox, QFileDialog, \
    QSlider, QComboBox, QColorDialog

from gui.configs.config_resource import ConfigResource
from gui.helpers.constants import CHANGE_HIEN_THI_TAB_EDIT_SUB, APP_PATH, FormatSubEnum, \
    LOAD_CONFIG_TAB_EDIT_SUB_CHANGED, \
    REFRESH_CONFIG_FILE_SRT, ADDNEW_SRT_FILE_EDIT_SUB, \
    CHANGE_HIEN_THI_TAB_ADD_SUB, LOAD_CONFIG_SRT_FILE_CHANGED, REMOVE_CONFIG_FILE_SRT, REFRESH_REMOVE_CONFIG_FILE_SRT, \
    CHANGE_FONT_SIZE_TABLE_EDIT_SUB, CHANGE_COLOR_TABLE_EDIT_SUB, JOIN_PATH
from gui.helpers.func_helper import filter_sequence_srt, writeFileTXT, writeFileSrt, is_chinese_char
from gui.helpers.server import TYPE_TTS_SUB
from gui.helpers.thread import ManageThreadPool
from gui.widgets.py_checkbox import PyCheckBox
from gui.widgets.py_combobox import PyComboBox
from gui.widgets.py_dialogs.py_dialog_get_select import PyDialogGetOutputFormatSub
from gui.widgets.py_icon_button.py_button_icon import PyButtonIcon
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


class GroupBoxConfigEditSub(QWidget, QObject):
    signalDataConfigCurrentChanged = Signal(
        object)  # object cấu hình hiện tại , chỉ cần khởi tạo db tại 1 cái rồi chuyền qua các Widget còn lại
    signalRefeshChanged = Signal(object)

    def __init__(self, manage_thread_pool: ManageThreadPool):
        super().__init__()
        self.manage_thread_pool = manage_thread_pool
        self.manage_thread_pool.resultChanged.connect(self._resultThread)

        # self.db_cau_hinh = db_cau_hinh
        self.db_app = None
        # self.settings = QSettings(*SETTING_CONFIG)

        self.list_config = []
        self.loadConfigFinish = False
        self.name_edit = ""
        self.fileSRTCurrent = None

        self.setup_ui()

    # self.loadConfig()
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

        self.input_color.setText(f"{cau_hinh['color_text_table_edit']}")
        self.combobox_font_size.setCurrentText(f"{cau_hinh['font_size_table_edit']}")

    def loadFileSRTCurrent(self, fileSRTCurrent, list_srt, db_app, db_cau_hinh):
        # print('11111111111111')
        # xoá dữ liệu cũ
        self.loadConfigFinish = False

        self.cb_config_list.clear()

        self.fileSRTCurrent = fileSRTCurrent
        # self.text_edit_config_name.setText(fileSRTCurrent.ten_cau_hinh)
        # self.name_edit = fileSRTCurrent.ten_cau_hinh
        cau_hinh = json.loads(fileSRTCurrent.value)
        sub_hien_thi = cau_hinh.get('sub_hien_thi', 'origin')
        self.cbox_sub_hien_thi.setCurrentText(TYPE_TTS_SUB.get(sub_hien_thi))

        # self.checkbox_auto_play.setChecked(cau_hinh.get('auto_play', True))
        # self.slider_volume.setValue(cau_hinh.get('volume_phat', 100))

        self.db_app = db_app
        self.db_cau_hinh = db_cau_hinh
        self.list_config = list_srt
        self.cb_config_list.addItems([cf.ten_cau_hinh for cf in self.list_config])

        for idex, cf in enumerate(self.list_config):  # kiểm tra trạng thai cấu hình nào được active
            # print(int(configActive.configValue))
            if cf is fileSRTCurrent:
                self.cb_config_list.setCurrentIndex(idex)
                if idex == 0:
                    self.configIndexChanged(idex)

                self.loadConfigFinish = True

                return
        # print('ddđ')
        self.loadConfigFinish = True

    def configIndexChanged(self, index):
        # if index > 0:  # cấu hình hiện tại
        # print(index)
        # print(self.list_config)

        if len(self.list_config) > 0 and index >= 0 and (self.loadConfigFinish):  # cấu hình hiện tại
            # print('2222')

            self.saveConfigActive(index)
            # self.button_save.setDisabled(True)
            # print('qua')
            self.manage_thread_pool.resultChanged.emit(REFRESH_CONFIG_FILE_SRT, REFRESH_CONFIG_FILE_SRT, "")

    # print(REFRESH_CONFIG_FILE_SRT)

    # self.signalDataConfigCurrentChanged.emit(self.fileSRTCurrent)

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.groupbox = QGroupBox("Cấu Hình Project")

        self.text_edit_config_name = QLineEdit()
        self.cb_config_list = PyComboBox()

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

        self.lb_font_size = QLabel("Font Size Bảng Sub:")

        self.combobox_font_size = QComboBox()
        # self.combobox_font_size.addItems(
        # 	["6px", "8px", "9px", "10px", "11px", "12px", "14px", "16px", "18px", "24px", "30px", "36px", "48px",
        # 	 "60px", "72px"])
        self.combobox_font_size.addItems([str(i) for i in range(8, 50)])
        self.combobox_font_size.setCurrentIndex(10)

        self.color_picker = QColorDialog()
        self.input_color = QLineEdit()
        self.input_color.setReadOnly(True)
        self.label_color = QLabel("Màu Chữ Bảng Sub:")
        self.btn_dialog_color = PyButtonIcon(
            icon_path=ConfigResource.set_svg_icon("color-picker.png"),
            parent=self,
            app_parent=self,
            icon_color="#f5ca1e",
            width=30,
            height=30,
            icon_color_hover="#ffe270",
            icon_color_pressed="#d1a807",

        )
        # self.lb_file_srt = QLabel("Load File .SRT có sẵn:")
        self.btn_dialog_folder_image = QPushButton("Load Folder Image")

        self.btn_export_srt = QPushButton("Xuất Nội Dung")
        self.btn_export_srt.setCursor(Qt.CursorShape.PointingHandCursor)

        self.button_import_project = QPushButton("Nhập Project")
        self.button_import_project.setCursor(Qt.CursorShape.PointingHandCursor)

        self.button_export_project = QPushButton("Xuất Project")
        self.button_export_project.setCursor(Qt.CursorShape.PointingHandCursor)

        self.button_remove = QPushButton("Xóa Project")
        self.button_remove.setCursor(Qt.CursorShape.PointingHandCursor)

    def modify_widgets(self):
        self.setStyleSheet(style_format)

    def create_layouts(self):
        self.bg_layout = QHBoxLayout()
        self.bg_layout.setContentsMargins(0, 0, 0, 0)

        self.gbox_layout = QVBoxLayout()
        self.content_layout = QVBoxLayout()
        self.content_top_layout = QHBoxLayout()
        self.content_mid_layout = QHBoxLayout()
        self.content_btn_layout = QHBoxLayout()
        self.groupbox.setLayout(self.gbox_layout)

    def add_widgets_to_layouts(self):
        self.bg_layout.addWidget(self.groupbox)
        self.setLayout(self.bg_layout)
        self.gbox_layout.addLayout(self.content_layout)

        self.content_layout.addWidget(QLabel(""))

        self.content_layout.addLayout(self.content_top_layout)
        self.content_layout.addWidget(QLabel(""))

        self.content_layout.addLayout(self.content_mid_layout)
        self.content_layout.addWidget(QLabel(""))

        self.content_layout.addLayout(self.content_btn_layout)

        self.content_top_layout.addWidget(QLabel("Chọn Project Hiển Thị:"), 10)
        self.content_top_layout.addWidget(self.cb_config_list, 70)
        self.content_top_layout.addWidget(self.button_remove, 20)
        # self.content_top_layout.addWidget(QLabel(""))

        self.content_mid_layout.addWidget(QLabel(""))

        self.content_mid_layout.addWidget(self.lb_font_size, 10)
        self.content_mid_layout.addWidget(self.combobox_font_size, 10)
        self.content_mid_layout.addWidget(QLabel(""), 10)
        self.content_mid_layout.addWidget(self.label_color, 10)
        self.content_mid_layout.addWidget(self.input_color)
        self.content_mid_layout.addWidget(self.btn_dialog_color)

        # self.content_mid_layout.addWidget(QLabel(""), 20)

        self.content_btn_layout.addWidget(self.btn_dialog_folder_image)
        # self.content_btn_layout.addWidget(self.button_save)
        self.content_btn_layout.addWidget(self.button_import_project)
        self.content_btn_layout.addWidget(self.button_export_project)
        self.content_btn_layout.addWidget(self.btn_export_srt)
        # self.content_mid_layout.addWidget(QLabel(""), 20)

    def setup_connections(self):
        self.cb_config_list.currentIndexChanged.connect(self.configIndexChanged)
        self.cbox_sub_hien_thi.currentIndexChanged.connect(self.cbox_sub_hien_thiChanged)
        # self.button_save.clicked.connect(self.saveConfig)
        self.button_remove.clicked.connect(self._removeConfig)
        # self.text_edit_config_name.textChanged.connect(self.check_button_disabled)
        self.btn_dialog_folder_image.clicked.connect(self._openDialogFolder)

        self.btn_export_srt.clicked.connect(self.clickSaveFile)
        self.button_import_project.clicked.connect(self.clickImportProject)
        self.button_export_project.clicked.connect(self.clickExportProject)

        self.slider_volume.valueChanged.connect(self.sliderVolumeValueChanged)
        # self.checkbox_auto_play.stateChanged.connect(self.checkbox_auto_playChanged)

        self.combobox_font_size.currentIndexChanged.connect(self.cb_fontsize_changed)

        self.btn_dialog_color.clicked.connect(self._openDialogColorSub)

    def _openDialogColorSub(self):
        done = self.color_picker.exec()
        color = self.color_picker.currentColor()
        if done and color.isValid():
            rgb_255 = [color.red(), color.green(), color.blue()]
            color_hex = '#' + ''.join(
                [hex(v)[2:].ljust(2, '0') for v in rgb_255]
            )
            if hasattr(self, "configCurrent") and self.configCurrent:
                # print(value)
                cau_hinh = json.loads(self.configCurrent.value)
                cau_hinh["color_text_table_edit"] = color_hex
                self.configCurrent.value = json.dumps(cau_hinh)
                self.configCurrent.save()
                self.manage_thread_pool.resultChanged.emit(CHANGE_COLOR_TABLE_EDIT_SUB, CHANGE_COLOR_TABLE_EDIT_SUB,
                                                           cau_hinh["color_text_table_edit"])
            self.input_color.setText(color_hex)

    def _resultThread(self, id_worker, id_thread, result):

        if id_thread == REMOVE_CONFIG_FILE_SRT:
            self._removeConfig()
        if id_thread == CHANGE_HIEN_THI_TAB_ADD_SUB:
            self.cbox_sub_hien_thi.setCurrentText(TYPE_TTS_SUB.get(result))

        if id_thread == ADDNEW_SRT_FILE_EDIT_SUB:
            self.addNewConfig(*result)

    def cb_fontsize_changed(self):
        if hasattr(self, "configCurrent") and self.configCurrent:
            # print(value)
            cau_hinh = json.loads(self.configCurrent.value)
            cau_hinh["font_size_table_edit"] = int(self.combobox_font_size.currentText())
            self.configCurrent.value = json.dumps(cau_hinh)
            self.configCurrent.save()
            self.manage_thread_pool.resultChanged.emit(CHANGE_FONT_SIZE_TABLE_EDIT_SUB, CHANGE_FONT_SIZE_TABLE_EDIT_SUB,
                                                       cau_hinh["font_size_table_edit"])

    def sliderVolumeValueChanged(self, value):
        if hasattr(self, "fileSRTCurrent") and self.fileSRTCurrent:
            # print(value)
            self.lb_number_volume_tts.setText(str(value))
            cau_hinh = json.loads(self.fileSRTCurrent.value)
            cau_hinh["volume_phat"] = value
            self.fileSRTCurrent.value = json.dumps(cau_hinh)
            self.fileSRTCurrent.save()

    def checkbox_auto_playChanged(self):
        if hasattr(self, "fileSRTCurrent") and self.fileSRTCurrent:
            cau_hinh = json.loads(self.fileSRTCurrent.value)
            cau_hinh["auto_play"] = self.checkbox_auto_play.isChecked()
            self.fileSRTCurrent.value = json.dumps(cau_hinh)
            self.fileSRTCurrent.save()

    def clickSaveFile(self):
        # TODO:[time, sub_origin, sub_translate]
        if hasattr(self, "fileSRTCurrent"):
            cau_hinh = json.loads(self.fileSRTCurrent.value)
            data_sub_timeline = cau_hinh.get('data_table')
            # base, ext = os.path.splitext(self.table_timeline.path_video)
            # srt_path = "{base}.{format}".format(base=base, format='srt')
            if len(data_sub_timeline) == 0:
                return PyMessageBox().show_warning("Thông Báo", "Chưa load file sub")

            dialog = PyDialogGetOutputFormatSub(height=200)
            if dialog.exec():
                pass
            # print(dialog.getIndex())
            else:
                return
            type_sub, format_sub = dialog.getIndex()

            if type_sub == 1:
                if data_sub_timeline[0][2] == "":
                    return PyMessageBox().show_warning("Thông Báo", "Sub chưa được dịch")

            if format_sub == FormatSubEnum.TXT.value:
                file_name, _ = QFileDialog.getSaveFileName(self, caption='Nhập tên file muốn lưu',
                                                           dir=APP_PATH,
                                                           filter='File txt (*.txt)')
                if file_name == "":
                    return
                writeFileTXT(file_name, data_sub_timeline, type_sub)

            PyMessageBox().show_info("Thông Báo", "Lưu File Thành Công!")

    def clickExportProject(self):
        if hasattr(self, "fileSRTCurrent"):
            id_remove = self.fileSRTCurrent.id
            if id_remove == 1:
                return PyMessageBox().show_warning("Cảnh Báo", "Không thể xuất Project này")

            cau_hinh = json.loads(self.fileSRTCurrent.value)
            data_sub_timeline = cau_hinh.get('data_table')
            if len(data_sub_timeline) == 0:
                return PyMessageBox().show_warning("Thông Báo", "Vui lòng tạo dự án mới")

            file_name, _ = QFileDialog.getSaveFileName(self, caption='Nhập tên file muốn lưu',

                                                       filter='File json (*.json)')
            if file_name == "":
                return

            with open(file_name, "w") as file_data:
                file_data.write(json.dumps(cau_hinh))

            PyMessageBox().show_info("Thông Báo", "Xuất Project Thành Công!")

    def clickImportProject(self):
        if hasattr(self, "fileSRTCurrent"):

            file_name, _ = QFileDialog.getOpenFileName(self, caption='Chọn file project',

                                                       filter='File json (*.json)')
            if file_name == "":
                return
            folder_name = QFileDialog.getExistingDirectory(self, caption='Chọn thư mục chứa hình ảnh')
            if not os.path.isdir(folder_name):
                return
            print(1)
            with open(file_name, "r") as file_data:
                data_project = json.load(file_data)
            print(2)

            data_project.update({'folder_name': folder_name})
            data_sub_timeline = data_project.get('data_table')
            list_new = []
            for index, item in enumerate(data_sub_timeline):
                file_image, sub_origin, sub_translate = item
                name_file = os.path.basename(file_image)
                file_new = JOIN_PATH(folder_name, name_file)
                list_new.append([file_new, sub_origin, sub_translate])

            data_project.update({'data_table': list_new})
            print(data_project)
            name_project = os.path.basename(folder_name)
            data_db = {}
            data_db["ten_cau_hinh"] = name_project
            data_db["value"] = json.dumps(data_project)
            print(3)
            dataAdd, created = self.db_cau_hinh.insert_one(data_db)
            if created is False:
                PyMessageBox().show_error('Cảnh Báo', "Không thể lưu cấu hình trạng thái")

            if created is True:
                self.saveConfigActive(0)
                self.manage_thread_pool.resultChanged.emit(REFRESH_CONFIG_FILE_SRT, REFRESH_CONFIG_FILE_SRT, "")

    def _openDialogFolder(self):
        folder_name = QFileDialog.getExistingDirectory(self, caption='Chọn thư mục hình ảnh')
        # print(folder_name)
        if os.path.isdir(folder_name):
            cmd = '''powershell -Command "(Get-ChildItem | Sort-Object { [regex]::Replace($_.Name, '\d+', { $args[0].Value.PadLeft(20) }) }).Name"'''
            process = subprocess.Popen(cmd, shell=True,
                                       cwd=rf'{folder_name}',
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
            out = process.communicate()[0].decode('ascii').split('\r\n')
            # list_file_image = []
            data_table = []

            # num_max=1
            for file_name_ in out:
                name, ext = os.path.splitext(file_name_)
                if ext.lower() in ['.jpg', '.png', '.jpeg']:
                    data_table.append([JOIN_PATH(folder_name, file_name_), "", ""])

            # print(data_table)
            if len(data_table) < 1:
                return PyMessageBox().show_error('Cảnh Báo', "Không tìm thấy file hình ảnh nào!")
                # sequences = filter_sequence_srt(path_file, path_video)

            self.addNewConfig(folder_name, data_table)

    def cbox_sub_hien_thiChanged(self, index):
        if hasattr(self, "fileSRTCurrent") and self.fileSRTCurrent:
            cau_hinh = json.loads(self.fileSRTCurrent.value)
            cau_hinh["sub_hien_thi"] = list(TYPE_TTS_SUB.keys())[index]  # vi,en
            self.fileSRTCurrent.value = json.dumps(cau_hinh)
            self.fileSRTCurrent.save()
            # print('vào')
            self.manage_thread_pool.resultChanged.emit(CHANGE_HIEN_THI_TAB_EDIT_SUB, CHANGE_HIEN_THI_TAB_EDIT_SUB,
                                                       cau_hinh["sub_hien_thi"])

    def saveConfigActive(self, id):
        # print(id)
        if hasattr(self, "db_app") and self.db_app:
            configActive = self.db_app.select_one_name(
                "configEditSubActive")  # chọn cấu hình với tên được lưu configEditSubActive để lấy ra giá trị
            configActive.configValue = id
            configActive.save()

    # @decorator_try_except_class
    def addNewConfig(self, folder_name, data_table):
        data_config = {

            "sub_hien_thi": 'origin',
            "folder_name": folder_name,
            # "video_file": path_video,
            "data_table": data_table
        }

        # print(data_config)
        # print()
        name_video = os.path.basename(folder_name)
        # print(name_video)
        # raise Exception
        data_db = {}
        if data_config is not None:
            data_db["ten_cau_hinh"] = name_video
            data_db["value"] = json.dumps(data_config)

            dataAdd, created = self.db_cau_hinh.insert_one(data_db)
            if created is False:
                PyMessageBox().show_error('Cảnh Báo', "Không thể lưu cấu hình trạng thái")

            if created is True:
                # print('ok')
                self.saveConfigActive(0)
                # self.loadConfig()
                self.manage_thread_pool.resultChanged.emit(REFRESH_CONFIG_FILE_SRT, REFRESH_CONFIG_FILE_SRT, "")

    # @decorator_try_except_class
    def _removeConfig(self):
        id_remove = self.fileSRTCurrent.id
        if id_remove == 1:
            return PyMessageBox().show_warning("Cảnh Báo", "Không thể xóa cấu hình này")

        req = PyMessageBox().show_question("Xách Nhận", "Bạn có chắc chắn muốn xóa !")

        if req is True:
            id_remove = self.fileSRTCurrent.id
            result = self.db_cau_hinh.remove_one(id_remove)
            if result == 1:
                self.saveConfigActive(0)
                self.manage_thread_pool.resultChanged.emit(REFRESH_REMOVE_CONFIG_FILE_SRT,
                                                           REFRESH_REMOVE_CONFIG_FILE_SRT, "")
