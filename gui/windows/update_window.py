from __future__ import print_function

import atexit
import builtins
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import time

import requests
import six
from PySide6 import QtGui
from PySide6.QtCore import Qt, QPersistentModelIndex, QByteArray
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import QMainWindow, QWidget, QProgressBar, QVBoxLayout, QMessageBox, QTableWidget, \
    QAbstractItemView, QAbstractScrollArea, QTableWidgetItem, QHeaderView, QHBoxLayout, \
    QPushButton, QLabel, QDialog
from platformdirs import user_data_dir
from gui.helpers.get_data import URL_API_BASE
from gui.helpers.constants import  DOWNLOAD_FILE_UPDATE, TOOL_CODE_MAIN, EXTRACT_FILE_UPDATE, APP_PATH
from gui.helpers.dowload_file import _get_session, _download_and_parse_google_drive_link, indent, \
    _get_directory_structure, parse_url, get_url_from_gdrive_confirmation, CHUNK_SIZE
from gui.helpers.ect import cr_pc
from gui.helpers.func_helper import which
from gui.helpers.thread import ManageThreadPool
from gui.helpers.thread.manage_cmd import progessPercentDetectSub


class UpdateDialog(QDialog):
    def __init__(self,user_data):
        super().__init__()

        self.thread_pool = ManageThreadPool()
        self.total_chunk = 0
        self.chunk = 0
        self.total_update = 0
        self.count_update = 0
        self.list_link_update = {}
        self.pz = {}
        # LOAD SETTINGS
        # ///////////////////////////////////////////////////////////////

        self.code_pc = cr_pc()
 
    
        self.user_data = user_data

 
        if self.user_data is None:
            QMessageBox().warning(self, "Lỗi", "Bạn hãy đăng nhập vào tool trước khi cập nhật phiên bản mới!")
            sys.exit()

 

        self.setup_ui()

        # self.setCentralWidget(self.central_widget)
        self.setWindowTitle("Cập Nhật Phần Mềm")
        self.setFixedSize(500, 100)
        # width = self.frameGeometry().width()
        # height = self.frameGeometry().height()
        #
        # screenWidth = self.central_widget.screen().size().width()
        # screenHeight = self.central_widget.screen().size().height()
        # self.setGeometry(int((screenWidth / 2) - (width / 2)), int((screenHeight / 2) - (height / 2)), width, height);

        # self.load_data()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        # print(self.move())

    def create_widgets(self):

        self.main_table = QTableWidget()
        self.lb_status = QLabel("Trạng Thái:")
        self.progess = QProgressBar(self, objectName="RedProgressBar")
        # self.progess.hide()
        self.btnClose = QPushButton("Close")

        # menu ngữ cảnh


    def modify_widgets(self):
        self.btnClose.setDisabled(False)

    def create_layouts(self):
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 10, 0, 10)

    def add_widgets_to_layouts(self):
        self.setLayout(self.content_layout)
        
        self.content_layout.addWidget(self.lb_status)
        self.content_layout.addWidget(self.progess)
        self.content_layout.addLayout(self.btn_layout)
 
        self.btn_layout.addWidget(QLabel(), 40)
        self.btn_layout.addWidget(self.btnClose, 20)
        self.btn_layout.addWidget(QLabel(), 40)
        
    def setup_connections(self):
        # self.thread_pool.progressChanged.connect(self.progressChanged)
        self.thread_pool.resultChanged.connect(self.resultChanged)
        self.btnClose.clicked.connect(self.accept)

 

    def resultChanged(self, id_worker, id_thread, result):

        if id_thread == DOWNLOAD_FILE_UPDATE:
            if not result is None:
                file_names, row_number, tool_code = result

                self.extractall(file_names[0], id_worker, row_number, tool_code)

 
        if id_thread == EXTRACT_FILE_UPDATE:
            #giaải  nen xon
            pass

    def download_file (self):
        headers = {
            "Authorization": f"Bearer {self.user_data.get('token')}"}
        dataTrans = {
            "tc": TOOL_CODE_MAIN,
            "cp": cr_pc(),
            't': int(float(time.time())),
        }
        res = requests.get(
            url=URL_API_BASE + f"/users/private/check-token",
            headers=headers)
        if res.json()["status_code"] == 200:
        
            self.thread_pool.start(self._func_download_thread, DOWNLOAD_FILE_UPDATE, DOWNLOAD_FILE_UPDATE,
                url=self.list_link_update.get(TOOL_CODE_MAIN))
    
    
        else:
            QMessageBox().warning("Lỗi", res.json()["message"])
            self.close()
            
    def _func_download_thread(self, **kwargs):
        url = kwargs["url"]
        list_file = self.download_folder_drive(url=url, output=APP_PATH)
        return list_file
 
    def _download_file_drive(self,
                             row_number,
                             url: str,
                             output=None,
                             quiet=False,
                             proxy=None,
                             speed=None,
                             use_cookies=True,
                             verify=True,
                             id=None,
                             fuzzy=False,
                             resume=False,
                             ):

        if not (id is None) ^ (url is None):
            raise ValueError("Either url or id has to be specified")
        if id is not None:
            url = "https://drive.google.com/uc?id={id}".format(id=id)

        url_origin = url

        sess, cookies_file = _get_session(
            proxy=proxy, use_cookies=use_cookies, return_cookies_file=True
        )

        gdrive_file_id, is_gdrive_download_link = parse_url(url, warning=not fuzzy)
#https://drive.google.com/file/d/1QzFz76AjFwZfXNJVVgo9iBLChOjmUeHy/view?usp=share_link
        if fuzzy and gdrive_file_id:
            # overwrite the url with fuzzy match of a file id
            url = "https://drive.google.com/uc?id={id}".format(id=gdrive_file_id)
            url_origin = url
            is_gdrive_download_link = True

        while True:
            try:
                res = sess.get(url, stream=True, verify=verify)
            except requests.exceptions.ProxyError as e:
                print(
                    "An error has occurred using proxy:",
                    sess.proxies,
                    file=sys.stderr,
                )
                print(e, file=sys.stderr)
                return

            if use_cookies:
                if not os.path.exists(os.path.dirname(cookies_file)):
                    os.makedirs(os.path.dirname(cookies_file))
                # Save cookies
                with open(cookies_file, "w") as f:
                    cookies = [
                        (k, v)
                        for k, v in sess.cookies.items()
                        if not k.startswith("download_warning_")
                    ]
                    json.dump(cookies, f, indent=2)

            if "Content-Disposition" in res.headers:
                # This is the file
                break
            if not (gdrive_file_id and is_gdrive_download_link):
                break

            # Need to redirect with confirmation
            try:
                url = get_url_from_gdrive_confirmation(res.text)
            except RuntimeError as e:
                print("Access denied with the following error:")
                error = "\n".join(textwrap.wrap(str(e)))
                error = indent(error, "\t")
                print("\n", error, "\n", file=sys.stderr)
                print(
                    "You may still be able to access the file from the browser:",
                    file=sys.stderr,
                )
                print("\n\t", url_origin, "\n", file=sys.stderr)
                return

        if gdrive_file_id and is_gdrive_download_link:
            content_disposition = six.moves.urllib_parse.unquote(
                res.headers["Content-Disposition"]
            )
            m = re.search(r"filename\*=UTF-8''(.*)", content_disposition)
            filename_from_url = m.groups()[0]
            filename_from_url = filename_from_url.replace(os.path.sep, "_")
        else:
            filename_from_url = os.path.basename(url)

        if output is None:
            output = filename_from_url

        output_is_path = isinstance(output, six.string_types)
        if output_is_path and output.endswith(os.path.sep):
            if not os.path.exists(output):
                os.makedirs(output)
            output = os.path.join(output, filename_from_url)

        if output_is_path:
            existing_tmp_files = []
            for file in os.listdir(os.path.dirname(output) or "."):
                if file.startswith(os.path.basename(output)):
                    existing_tmp_files.append(os.path.join(os.path.dirname(output), file))
            if resume and existing_tmp_files:
                if len(existing_tmp_files) != 1:
                    print(
                        "There are multiple temporary files to resume:",
                        file=sys.stderr,
                    )
                    print("\n")
                    for file in existing_tmp_files:
                        print("\t", file, file=sys.stderr)
                    print("\n")
                    print(
                        "Please remove them except one to resume downloading.",
                        file=sys.stderr,
                    )
                    return
                tmp_file = existing_tmp_files[0]
            else:
                resume = False
                # mkstemp is preferred, but does not work on Windows
                # https://github.com/wkentaro/gdown/issues/153
                tmp_file = tempfile.mktemp(
                    suffix=tempfile.template,
                    prefix=os.path.basename(output),
                    dir=os.path.dirname(output),
                )
            f = open(tmp_file, "ab")
        else:
            tmp_file = None
            f = output

        if tmp_file is not None and f.tell() != 0:
            headers = {"Range": "bytes={}-".format(f.tell())}
            res = sess.get(url, headers=headers, stream=True, verify=verify)
        #
        # if not quiet:
        #     print("Downloading...", file=sys.stderr)
        #     if resume:
        #         print("Resume:", tmp_file, file=sys.stderr)
        #     print("From:", url_origin, file=sys.stderr)
        #     print(
        #         "To:",
        #         osp.abspath(output) if output_is_path else output,
        #         file=sys.stderr,
        #     )

        try:
            total = res.headers.get("Content-Length")
            if total is not None:
                self.total_chunk += int(int(total) / 1000)

            self.lb_status.setText("Đang tải dữ liệu")

            if not quiet:
                
                self.progess.show()
                self.progess.setRange(0, self.total_chunk)

                # self.thread_pool.resultChanged.emit("UPDATE_RANGE_PROGESS", "UPDATE_RANGE_PROGESS", self.total_chunk)
            # t_start = time.time()
            for chunk in res.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
                if not quiet:
                    self.chunk += int(len(chunk) / 1000)
                    if (self.chunk / self.total_chunk) * 100 >= 98.0:
                        self.chunk = self.total_chunk
                        
                    # widget = self.main_table.cellWidget(row_number, self.column_progress)
                    self.progess.show()
                    self.progess.setValue(self.chunk)
                    # self.thread_pool.progressChanged.emit("UPDATE_VALUE_PROGESS", "UPDATE_VALUE_PROGESS",self.chunk)
 
            if tmp_file:
                f.close()
                shutil.move(tmp_file, output)
        except IOError as e:
            print(e, file=sys.stderr)
            return
        finally:
            sess.close()

        return output

    def download_folder_drive(
            self,
            row_number,
            url=None,
            id=None,
            output=None,
            quiet=False,
            proxy=None,
            speed=None,
            use_cookies=True,
            remaining_ok=False,
            verify=True,
    ):
        """Downloads entire folder from URL.
        Returns
        -------
        filenames: list of str
            List of files downloaded, or None if failed.

        Example
        -------
        gdown.download_folder(
            "https://drive.google.com/drive/folders/" +
            "1ZXEhzbLRLU1giKKRJkjm8N04cO_JoYE2",
        )
        """
        if not (id is None) ^ (url is None):
            raise ValueError("Either url or id has to be specified")
        if id is not None:
            url = "https://drive.google.com/drive/folders/{id}".format(id=id)

        sess = _get_session(proxy=proxy, use_cookies=use_cookies)

        if not quiet:
            print("Retrieving folder list", file=sys.stderr)
        try:
            return_code, gdrive_file = _download_and_parse_google_drive_link(
                sess,
                url,
                quiet=quiet,
                remaining_ok=remaining_ok,
                verify=verify,
            )
        except RuntimeError as e:
            print("Failed to retrieve folder contents:", file=sys.stderr)
            error = "\n".join(textwrap.wrap(str(e)))
            error = indent(error, "\t")
            print("\n", error, "\n", file=sys.stderr)
            return

        if not return_code:
            return return_code
        if not quiet:
            print("Retrieving folder list completed", file=sys.stderr)
            print("Building directory structure", file=sys.stderr)
        if output is None:
            output = os.getcwd() + os.path.sep
        if output.endswith(os.path.sep):
            root_folder = os.path.join(output, gdrive_file.name)
        else:
            root_folder = output
        directory_structure = _get_directory_structure(gdrive_file, root_folder)
        if not os.path.exists(root_folder):
            os.makedirs(root_folder)

        if not quiet:
            print("Building directory structure completed")
        filenames = []
        for file_id, file_path in directory_structure:
            if file_id is None:  # folder
                if not os.path.exists(file_path):
                    os.makedirs(file_path)
                continue

            filename = self._download_file_drive(
                row_number,
                url="https://drive.google.com/uc?id=" + file_id,
                output=file_path,
                quiet=quiet,
                proxy=proxy,
                speed=speed,
                use_cookies=use_cookies,
                verify=verify,
            )

            if filename is None:
                if not quiet:
                    print("Download ended unsuccessfully", file=sys.stderr)
                return
            filenames.append(filename)
        if not quiet:
            print("Download completed", file=sys.stderr)
            self.lb_status.setText("Tải xong!")
        return filenames

    def extractall(self, path_file, id_type, row_number, tool_code):

        # dir_extract = os.path.dirname(path_file)

        if not which("7z.exe") is None:
            self.thread_pool.start(self.func_extract_file, id_type, EXTRACT_FILE_UPDATE, path_file=path_file,
                                   row_number=row_number, tool_code=tool_code)
        else:
            os.remove(path_file)
            QMessageBox().critical(self, "Lỗi",
                                   f'<p style="font-size:15px; font-weight:bold; color: #ff0000;">Thiếu file, Vui lòng liên hệ Admin!</p>')

    def func_extract_file(self, **kwargs):
        try:
            id_type = kwargs["id_worker"]
            path_file = kwargs["path_file"]
            dir_extract = os.path.dirname(path_file)
            row_number = kwargs["row_number"]
            tool_code = kwargs["tool_code"]

            cmd = f'{which("7z.exe")} x "{path_file}" -p"{self.pz.get(tool_code)}" -bsp1 -y -o"{dir_extract}"'
            
            self.progess.show()
            self.progess.setRange(0, 100)
            self.lb_status.setText("Đang cài đặt...")
            self.run_cmd_result(cmd, row_number)
            os.remove(path_file)  # xóa file tải về trước
            # print(dir_extract)
            if len(os.listdir(dir_extract)) > 1:
                self.count_update += 1
                version_new = self.main_table.item(row_number, self.column_verison_latest).text()
 
                self.progess.show()
                self.progess.setValue(100)
                column_verison_current = self.main_table.item(row_number, self.column_verison_current)
                column_verison_current.setText(version_new)

                self.lb_status.setText("UPDATE THÀNH CÔNG !")

        except:
            self.close()

    def run_cmd_result(self, command: str, row_number):
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            # creationflags=0x08000000,
            encoding='utf-8',
            errors='replace'
        )
        list_output_stdout = []
        while True:
            realtime_output = process.stdout.readline()
            if realtime_output == '' and process.poll() is not None:
                break
            if realtime_output:
                # print(realtime_output.strip())
                list_output_stdout.append(
                    realtime_output.strip().replace("\x1b[0m", "").replace("\n", ""))
                progress = progessPercentDetectSub(realtime_output.strip())

                if progress:
                
                    self.progess.show()
                    self.progess.setValue(progress)

 