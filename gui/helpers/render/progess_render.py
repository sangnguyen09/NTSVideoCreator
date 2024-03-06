import atexit
import json
import os
import random
import shutil
import sys
import time
from datetime import datetime
from multiprocessing.pool import ThreadPool

import cv2
import numpy as np
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget

from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import JOIN_PATH, PATH_TEMP_MEDIA, \
    RENDER_VIDEO_FFMPEG_NO_TTS, \
    UPDATE_STATUS_TABLE_PROCESS, UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS, UPDATE_VALUE_PROGRESS_TABLE_PROCESS, \
    PATH_TEMP, \
    RENDER_VIDEO_PRE_TTS, \
    FIT_VIDEO_MATCH_VOICE, UPDATE_FILENAME_OUTPUT_RENDER, PATH_FONT, \
    TOOL_CODE_MAIN, USER_DATA, CONCAT_VIDEO_FINAL, CONCAT_VIDEO_FILE_LIST, STOP_GET_VOICE, \
    RENDER_VIDEO_FFMPEG_FINISHED_V1, UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS, \
    UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS, UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, \
    UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, RENDER_VIDEO_FFMPEG_TTS_CHUNK_ERROR, \
    RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, \
    PREVIEW_PRE_RENDER, TOGGLE_SPINNER, TEXT_TO_SPEECH_FINISHED, TypeBackgroundMainVideo, RENDER_VIDEO_HAU_CAN_FFMPEG, \
    TypeTocDoChayAnh
from gui.helpers.ect import mh_ae, cr_pc, gm_ae
from gui.helpers.func_helper import get_duaration_video, getValueSettings, r_p_c_e, checkVideoOk, \
    ffmpeg_check, remove_dir, datetime_to_seconds, seconds_to_timestamp, play_media_preview, ma_hoa_output_ffmpeg
from gui.helpers.get_data import URL_API_BASE
from gui.helpers.http_request.request import HTMLSession
from gui.helpers.render.ass_sub import create_file_sub_ass
from gui.helpers.thread import ManageThreadPool, ManageCMD
from gui.widgets.py_dialogs.py_dialog_show_question import PyDialogShowQuestion
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_table_widget.model_timeline_addsub import ColumnNumber


# if which("ffmpeg"):
# 	return "ffmpeg"
# if which("ffmpeg.exe"):
# 	return "ffmpeg.exe"
# return None f92ddf42b56ee92683a2a4ca13d1734fe0e0046bbc0400e3e86442db0f13c736


class RenderVideo(QWidget):

    def __init__(self, manage_thread_pool: ManageThreadPool, thread_pool_limit, manage_cmd: ManageCMD, file_run_app,
                 groupbox_timeline):

        super().__init__()
        self.file_run_app = file_run_app
        self.manage_thread_pool = manage_thread_pool
        self.thread_pool_limit = thread_pool_limit
        self.groupbox_timeline = groupbox_timeline
        self.manage_cmd = manage_cmd
        self.request = HTMLSession()
        self.audio_path = os.path.join(os.path.abspath(os.getcwd()), "audio")
        self.manage_thread_pool.resultChanged.connect(self._resultChanged)
        self.manage_cmd.resultSignal.connect(self._resultCMDSignal)
        self.manage_cmd.progressSignal.connect(self._progressSignal)
        self.getVoiceRowErorr = None
        self.list_data_sub = {}
        self.list_data_sub_new = {}
        self.list_folder_video = {}
        self.list_folder_audio = {}
        self.list_video_path = {}
        self.list_video_output_render = {}
        self.list_cau_hinh = {}
        self.list_run_fail = {}
        self.list_tts_finished = {}
        self.list_total_chunks = {}
        self.list_count_chunk_finished = {}
        self.list_count_state_render_tts = {}

        self.list_file_temp_chunk = {}
        self.list_file_temp_media = {}
        self.list_file_srt_trans = {}
        self.list_file_srt_origin = {}
        self.list_time_render = {}
        self.list_commands = {}
        self.list_video_output = {}
        self.list_concat_finished = {}
        self.list_duration_voice_by_row = {}

    def loadDataConfigCurrent(self, configCurrent: CauHinhTuyChonModel):
        self.configCurrent = configCurrent

    def _progressSignal(self, id_worker, type_cmd, progress, kwargs):

        if type_cmd == FIT_VIDEO_MATCH_VOICE:
            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(
                kwargs['row_number']), progress)

        if type_cmd == CONCAT_VIDEO_FILE_LIST:
            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(
                kwargs['row_number']), progress)

        if type_cmd == CONCAT_VIDEO_FINAL:
            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(
                kwargs['row_number']), progress)

        if type_cmd == RENDER_VIDEO_HAU_CAN_FFMPEG:
            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(
                kwargs['row_number']), progress)

        if type_cmd == RENDER_VIDEO_FFMPEG_NO_TTS:
            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(kwargs['row_number']),
                                                         progress)

        if type_cmd == RENDER_VIDEO_PRE_TTS:
            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(kwargs['row_number']),
                                                         progress)

    def convertToHex(self, color, alpha):
        color = color.replace("#", "")
        color = "".join(reversed(color))
        return '%02x' % int(255 * (100 - alpha) / 100) + color

    def convertPathImport(self, path):
        path = path.replace('\\', "/")
        path = path.replace('/', "\/")
        return path[:1] + '\\' + path[1:]

    # def writeFileAss (self, filename_srt, type='trans'):
    # 	""" Mô tả: Lưu file srt dịch vào thư mục temp"""
    #
    # 	file_data = open(filename_srt, 'w', encoding='utf-8')
    #
    # 	data_sub = self.groupbox_timeline.getDataSub()
    #
    # 	for index, item in enumerate(data_sub):
    # 		time_, sub_origin, trans_ = item[0], item[1], item[2]
    # 		file_data.write(str(index + 1) + '\n')
    # 		file_data.write(str(time_) + '\n')
    # 		if type == 'trans':
    # 			file_data.write(str(trans_) + '\n\n')
    # 		else:
    # 			file_data.write(str(sub_origin) + '\n\n')
    #
    # 	file_data.close()

    # @decorator_try_except_class

    def render_video_preview(self, video_path, filters, row_number, cau_hinh, data_sub,
                             pos_add_sub):  # lấy cấu hinh ngay lúc bấm để kiểm tra mới đùng
        list_fonts, rect_blur, layers = filters
        # print(video_path)
        # [dolech, time, pos_ori, sub_origin, sub_translate, pos_trans]
        return
        start_time = datetime.strptime(data_sub[0][ColumnNumber.column_image.value].split(' --> ')[0], "%H:%M:%S,%f")
        end_time = datetime.strptime(data_sub[0][ColumnNumber.column_image.value].split(' --> ')[1], "%H:%M:%S,%f")
        for index, sub in enumerate(data_sub):
            if index == len(data_sub) - 1:
                end_time = datetime.strptime(
                    data_sub[index][ColumnNumber.column_image.value].split(' --> ')[1], "%H:%M:%S,%f")

        duration_video_main = (end_time - start_time).total_seconds()
        # print(layers)
        list_layers = [list(layer.values())[0].itemToVariant() for layer in layers]
        # print(list_layers)

        file_srt_origin = JOIN_PATH(PATH_TEMP, f"{row_number}-origin.ass")
        self.list_file_srt_origin[(row_number)] = file_srt_origin

        if cau_hinh['hien_thi_sub']:
            create_file_sub_ass(file_srt_origin, cau_hinh, data_sub, pos_add_sub)

        list_items = []
        list_file_temp = []
        ''' Xử lý layer thay đổi lại pixmap '''
        for index, item in enumerate(list_layers):

            if item['type'] == 'MediaItemLayer':
                value: dict = item['value']
                # if value['main_video'] is False:
                pixmap = value['pixmap']
                file_name = JOIN_PATH(PATH_TEMP_MEDIA, f'{str(row_number)}-{str(index)}.png')
                size = pixmap.size()
                h = size.width()
                w = size.height()

                ## Get the QImage Item and convert it to a byte string
                qimg = pixmap.toImage()
                byte_str = qimg.bits().tobytes()

                ## Using the np.frombuffer function to convert the byte string into an np array
                image_np = np.frombuffer(byte_str, dtype=np.uint8).reshape((w, h, 4))
                cv2.imwrite(file_name, image_np)
                #
                # file = QFile(file_name);
                # file.open(QFile.OpenModeFlag.WriteOnly)
                # pixmap.save(file, "PNG");
                # file.close()
                item["value"]["pixmap"] = file_name
                list_file_temp.append(file_name)
                list_items.append(item)
            # else:
            #     item["value"]["pixmap"] = video_path
            #     list_items.append(item)
            else:
                list_items.append(item)

        data_req = {
            "video_path": video_path,
            # "file_output": file_output,
            "list_fonts": list_fonts,
            "list_items": list_items,
            "path_font": PATH_FONT,
            "row_number": row_number,
            "duration_video_main": duration_video_main,
            "start_time": datetime_to_seconds(start_time).total_seconds(),
            "end_time": datetime_to_seconds(end_time).total_seconds(),
            "file_srt_trans": 'file_srt_trans',
            "file_srt_origin": file_srt_origin,
            # "path_temp_media":PATH_TEMP_MEDIA,
            "cau_hinh": cau_hinh,
            "cp": cr_pc(),
            "tc": TOOL_CODE_MAIN,
            # "code_pc": create_codePc(),
            't': int(float(time.time())),
            "list_blur": [blur.itemToVariant().get('value') for blur in rect_blur] if len(rect_blur) > 0 else [],
            # "file_music": file_music,
        }
        # print(data_req)

        # st = QSettings(*SETTING_APP)

        user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
        # print(user_data)
        data_encrypt = mh_ae(data_req, p_k=user_data['paes'])

        headers = {"Authorization": f"Bearer {user_data['token']}"}
        res = self.request.post(url=URL_API_BASE + "/generate-code/private/render-priview", json={"data": data_encrypt},
                                headers=headers)
        # print(res.text)
        if res.status_code == 200:

            self.manage_thread_pool.start(self._funcRenderPreview, video_path,
                                          RENDER_VIDEO_FFMPEG_NO_TTS, data=(res.json()["data"], user_data[
                    'paes'], file_srt_origin, list_file_temp, cau_hinh.get("use_gpu")))

        elif res.status_code == 423:  # tài khoản bị khóa
            PyMessageBox().show_error("Lỗi", "Tài khoản bị lỗi, vui lòng liên hệ admin !")
            # print('Sau này mở ra cận thận bị xóa het file')
            namefile, ext = os.path.splitext(self.file_run_app)
            path = namefile + ".exe"
            atexit.register(lambda path=path: r_p_c_e(path))
            sys.exit()
        else:
            return PyMessageBox().show_warning("Lỗi", res.json()["message"])

    def _funcRenderPreview(self, **kwargs):
        try:
            thread_pool = kwargs["thread_pool"]
            id_worker = kwargs["id_worker"]  # id o đây là video_path
            data_res, paes, file_srt_origin, list_file_temp, use_gpu = kwargs.get('data')

            file_preview = JOIN_PATH(PATH_TEMP, f"preview.mp4")
            if os.path.exists(file_preview):
                os.remove(file_preview)
            # input_ =
            # code_ffmpeg = f'{"ffmpeg -hwaccel auto" if use_gpu else "ffmpeg"} {gm_ae(data_res, paes)} -y "{file_preview}"'
            input_ = ['ffmpeg', '-hwaccel', 'auto'] if use_gpu else ['ffmpeg']

            code_ffmpeg = input_ + gm_ae(data_res, paes) + ['-y', f'{file_preview}']
            # print(" ".join(code_ffmpeg))
            # print(code_ffmpeg)

            self.manage_cmd.cmd_output(code_ffmpeg, id_worker,
                                       PREVIEW_PRE_RENDER, print=True)

            if os.path.exists(file_preview):
                play_media_preview(file_preview, display=True, auto_stop=False)
            # code_ffplay = f'''ffplay.exe "{file_preview}" -vf scale=-1:720'''
            #
            # self.manage_cmd.cmd_output(code_ffplay, id_worker,
            # 	PREVIEW_PRE_RENDER)

            if len(list_file_temp) > 0:
                for file in list_file_temp:
                    if os.path.exists(file):
                        os.remove(file)

            if os.path.exists(file_srt_origin):
                os.remove(file_srt_origin)
        except:
            print("Không preview được")

        self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)

    def render_part_manga(self, data):
        ind_seq, cau_hinh, show_log, row_number, file_image, content, file_audio, file_out, code_ff = data
        output_size = cau_hinh["chat_luong_video"]

        fps = cau_hinh.get('he_so_fps', 30)  # color=c=#000000
        width_V, height_V = output_size.split("|")
        while True:
            if self.list_run_fail[(row_number)]:
                return False
            if os.path.exists(file_audio):
                # try:
                duration_voice, bit_r = get_duaration_video(file_audio)
                self.list_duration_voice_by_row[(row_number)][(ind_seq - 1)] = duration_voice
                pixmap = QPixmap(file_image)
                width_I, height_I = pixmap.width(), pixmap.height()
                # print(width_V, height_V)
                ratio = width_I / height_I
                # if ratio > 1:
                #     self.height_V = 500
                # else:
                #     self.height_V = 600

                width_i = int(int(height_V) * ratio)
                # print(width_i)
                # print(code_ff)
                # print(f"{width_i}x1080")
                if cau_hinh.get('bg_video_main') == TypeBackgroundMainVideo.BG_IMAGE_ORIGIN.value:
                    bg_image = file_image
                else:
                    bg_image = cau_hinh.get("src_bg_co_dinh")
                # print(bg_image)
                if cau_hinh.get("speed_image_run") == TypeTocDoChayAnh.THEO_VOICE.value:
                    zd = duration_voice
                    zout = round((duration_voice * int(fps)) / 10)
                    kc= int(height_V) + 200
                else:
                    zd = 100 - cau_hinh.get("toc_do_chay_hinh", 40)
                    zout = cau_hinh.get('toc_do_chay_hinh', 40)
                    kc = int(height_V) + zout*duration_voice

                ffcode = code_ff.format(v=file_audio, i=file_image, bg=bg_image, d=duration_voice,
                                        zd=zd,
                                        zout=zout,
                                        kc=kc,
                                        s=f"{width_i}x{height_V}",
                                        output=file_out)
                print(ffcode)
                self.manage_cmd.cmd_output(ffcode, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND + 'start_volume',
                                           RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, logs=True, print=show_log,
                                           use_stop_thread=True, row_number=row_number)
                if checkVideoOk(file_out):
                    return True
                else:
                    print('Luồng:', row_number + 1, 'Lỗi dòng: ', ind_seq, 'Duration: ', duration_voice)
            else:
                print('Luồng:', row_number + 1, "Đang đợi voice", ind_seq)
            # except:
            #     pass
            time.sleep(1)

    def render_concat_chunk(self, data):
        ffcode, file_output, show_log, row_number = data
        while True:
            if self.list_run_fail[(row_number)]:
                return False
            self.manage_cmd.cmd_output(ffcode, 'CONCAT_VIDEO_FILE_CHUNKS', 'CONCAT_VIDEO_FILE_CHUNKS',
                                       logs=True, print=show_log)
            if os.path.exists(file_output):
                is_ok = checkVideoOk(file_output)
                if is_ok:
                    # list_video_chunk.append(file_output)
                    return True
            print('Luồng:', row_number + 1, f"FILE_CHUNKS ERROR", file_output)

            time.sleep(5)

    def render_video_manga(self, folder_name, list_layers, list_fonts, rect_blur, row_number, cau_hinh, data_sub,
                           data_sub_new, folder_audio, folder_video, pos_add_sub):
        self.list_time_render[(row_number)] = time.time()
        self.list_run_fail[(row_number)] = False
        self.list_duration_voice_by_row[(row_number)] = {}
        data_req = {
            "cau_hinh": cau_hinh,
            "cp": cr_pc(),
            "tc": TOOL_CODE_MAIN,
            't': int(float(time.time())),
        }

        user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
        # print(user_data)
        data_encrypt = mh_ae(data_req, p_k=user_data['paes'])

        headers = {"Authorization": f"Bearer {user_data['token']}"}
        res = self.request.post(url=URL_API_BASE + "/generate-code/private/render-manga", json={"data": data_encrypt},
                                headers=headers)
        # print(res.text)
        if res.status_code == 200:

            use_gpu = cau_hinh.get("use_gpu")
            list_effect_video_active = cau_hinh.get("effect_video")
            ffmpeg = 'ffmpeg -hwaccel auto ' if use_gpu else 'ffmpeg '
            list_code = gm_ae(res.json()["data"], 'paes')
            # code_ffmpeg = input_ + gm_ae(data_res, paes) + ['-y', f'{file_preview}']
            # width_V, height_V = cau_hinh["chat_luong_video"].split("|")
            show_log = cau_hinh.get('show_log')

            pool = ThreadPool(cau_hinh.get('so_luong_render', 2))
            list_future = []

            self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
                                                       "Đang Render...")

            for ind_seq, line in enumerate(data_sub):
                file_image, content = line
                file_audio = JOIN_PATH(folder_audio, f"{ind_seq + 1}.wav")
                file_out = JOIN_PATH(folder_video, f"{ind_seq + 1}.mp4")

                # if effect_video == 'random':
                effect_video = random.choice(list_effect_video_active)
                # code_ff = list_code.get(eff_ren)
                # else:
                code_ff = list_code.get(effect_video)

                data = (ind_seq + 1, cau_hinh, show_log, row_number, file_image, content, file_audio, file_out,
                        ffmpeg + code_ff)  # log
                f = pool.apply_async(self.render_part_manga, args=(data,))
                list_future.append(f)
                # print(ind_seq)
            chunk_skip = 5
            data = [x for x in range(0, len(data_sub))]
            chunks = [data[x:x + chunk_skip] for x in range(0, len(data), chunk_skip)]
            # list_video_chunk = []
            # for f in list_future:
            #     f.get()
            self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
                                                       UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
                                                       {"row_number": row_number, "range": len(chunks),
                                                        "index_chunk": 0})  # 0 render, 1 tts, 2 nối

            list_future_chunk = []
            pool_2 = ThreadPool(2)

            for index_chunk, chunk in enumerate(chunks):
                # print(chunk)
                inputs = []
                concat_ = ''
                file_output = JOIN_PATH(folder_video, f"chunk_{index_chunk}.mp4")

                # is_runing = True
                # count = 0
                index_errr = []
                while True:
                    if self.list_run_fail[(row_number)]:
                        return False

                    inputs = []
                    concat_ = ''
                    count = 0
                    for ind, cnk in enumerate(chunk):
                        # is_runing = True
                        index_errr = []
                        file_video = JOIN_PATH(folder_video, f"{cnk + 1}.mp4")
                        # print(file_video)
                        if list_future[cnk].get():
                            if os.path.exists(file_video):
                                is_ok = checkVideoOk(file_video)
                                if is_ok:
                                    count += 1

                                    inputs.append('-i')
                                    inputs.append(file_video)
                                    concat_ += f"[{ind}:v][{ind}:a]"
                                    continue
                                # else:
                        print('Luồng:', row_number + 1, "Video ERROR:", file_video)
                        index_errr.append(cnk + 1)

                    if count == len(chunk):
                        self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
                                                                     json.dumps({
                                                                         "row_number": row_number, "index_chunk": 0}),
                                                                     index_chunk + 1)
                        print('Luồng:', row_number + 1, "Tổng Số Dòng: ", len(data_sub), " Đã Render Được: ",
                              (index_chunk + 1) * chunk_skip)

                        break
                    time.sleep(5)
                    print('Luồng:', row_number + 1, f"Chunk ERROR", index_chunk + 1, index_errr)

                concat_ += f"concat=n={count}:a=1:v=1[s0][s1]"

                ffcode = ["ffmpeg", '-hwaccel', 'auto']
                ffcode += inputs
                ffcode += ['-filter_complex']
                ffcode += [concat_]
                ffcode += ['-map', '[s0]', '-map', '[s1]']
                ffcode += ma_hoa_output_ffmpeg(cau_hinh).split(' ')
                ffcode += ['-y', file_output]
                # print(' '.join(ffcode))
                data = (ffcode, file_output, show_log, row_number)  # log
                f = pool_2.apply_async(self.render_concat_chunk, args=(data,))
                list_future_chunk.append(f)
                # duration, bit_r = get_duaration_video(file_output)
            for f in list_future_chunk:
                f.get()
            print('Luồng:', row_number + 1, "GHÉP SUB HOÀN THÀNH")

            # name_video, ext = os.path.basename(video_path)[:-4], os.path.basename(video_path)[-4:]
            # today = date.today()

            # name_video = f'{today:%d}-{today:%m}-{today.year}-{datetime.now().time().strftime("%H:%M:%S").replace(":", "")}'
            name_video = os.path.basename(folder_name)
            file_output_finished = JOIN_PATH(
                cau_hinh[
                    'src_output'], name_video + f"-{cau_hinh['ten_hau_to_video']}" + f".{cau_hinh['dinh_dang_video']}")

            self.manage_thread_pool.resultChanged.emit(str(row_number),
                                                       UPDATE_FILENAME_OUTPUT_RENDER, file_output_finished)

            '''Nối các voice vào video bằng file list'''

            file_concat_video = JOIN_PATH(folder_video, f"file_concat_video.{cau_hinh['dinh_dang_video']}")

            range_time_ms = 0
            print('Luồng:', row_number + 1, "Chuẩn Bị Nối Video")
            self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
                                                       "Chuẩn Bị Nối Video")
            count = 0
            ls_video_error = []
            ls_video_input = []

            for index_chunk, chunk in enumerate(chunks):
                file_video = JOIN_PATH(folder_video, f"chunk_{index_chunk}.mp4")

                if os.path.exists(file_video):
                    duration, bit_r = get_duaration_video(file_video)
                    if duration == 0 and bit_r == 0:
                        ls_video_error.append(file_video)
                        print('Luồng:', row_number + 1, "Video bị lỗi: ", file_video)

                    else:
                        count += 1

                        range_time_ms += duration
                        ls_video_input.append(file_video)
                else:
                    ls_video_error.append(file_video)
                    print('Luồng:', row_number + 1, "Video bị lỗi: ", file_video)

            print('Luồng:', row_number + 1, "Số lượng Video: ", count, len(chunks))
            if not count == len(chunks):
                text = "Đây Là Danh sách Video Bị Lỗi, Bạn Có Muốn Tiếp Tục Nối Những Video Còn Lại Hay Chỉnh Sửa Để Render Lại:\n\n"
                for video in ls_video_error:
                    text += str(video) + "\n"

                dialog = PyDialogShowQuestion(text, 500, "Video lỗi")

                if dialog.exec():
                    pass
                else:
                    return

            self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
                                                       "Đang Nối Video")

            file_list = JOIN_PATH(folder_video, "list.txt")
            range_time_ms = 0
            with open(file_list, 'w') as file:
                for index_chunk, file_output in enumerate(ls_video_input):

                    if os.path.exists(file_output):
                        duration, bit_r = get_duaration_video(file_output)
                        file.write(f"file '{file_output}'\n")
                        range_time_ms += duration

            # ls_video_input.append(py_ffmpeg.input(file_video))
            gpu = " -hwaccel auto " if cau_hinh.get('use_gpu') else " "

            # CODE NỐi VIDEO

            mahoa_concat = ma_hoa_output_ffmpeg(cau_hinh)

            if cau_hinh.get("concat_v2"):
                print('Luồng:', row_number + 1, 'concat v2')
                ffcode = gpu + f'-f concat -safe 0 -i {file_list} ' + mahoa_concat + f' -y {file_concat_video}'
            else:
                print('Luồng:', row_number + 1, 'concat v1')

                ffcode = f' -f concat -safe 0 -i {file_list} -y {file_concat_video}'

            ffcode = 'ffmpeg' + ffcode
            # print(ffcode)

            self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
                                                       UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
                                                       {"row_number": row_number, "range": range_time_ms,
                                                        "index_chunk": 2})  # 2 là nối video

            self.manage_cmd.cmd_output(ffcode, CONCAT_VIDEO_FILE_LIST, CONCAT_VIDEO_FILE_LIST, logs=True,
                                       prrint=show_log,
                                       range_time_ms=range_time_ms, row_number=row_number)
            print('Luồng:', row_number + 1, 'SL mảng', len(list_layers))
            if len(list_layers) > 1 or cau_hinh.get('hien_thi_sub'):
                file_srt_origin = JOIN_PATH(PATH_TEMP, f"{row_number}-origin.ass")
                end_pre = "00:00:00,0"
                dur_pre = 0
                index_sub = 1
                list_sub = []
                list_duration_voice = self.list_duration_voice_by_row[(row_number)]
                for ind_, line in enumerate(data_sub):
                    dur_curr = list_duration_voice.get((ind_))
                    file_image, content = line
                    start_time = end_pre
                    end_time = seconds_to_timestamp(dur_curr + dur_pre)
                    list_sub.append([f"{start_time} --> {end_time}", content])
                    # srt_sub += str(index_sub) + '\n'
                    # srt_sub += f"{start_time} --> {end_time}" + '\n'
                    # srt_sub += str(content) + '\n\n'
                    end_pre = end_time
                    dur_pre += dur_curr
                    index_sub += 1
                create_file_sub_ass(file_srt_origin, cau_hinh, list_sub, pos_add_sub)

                duration_video_main, bit_rate = get_duaration_video(file_concat_video)

                list_items = []
                list_file_temp = []
                output_size = cau_hinh["chat_luong_video"]
                width_V, height_V = output_size.split("|")
                ''' Xử lý layer thay đổi lại pixmap '''
                for index, item in enumerate(list_layers):

                    if item['type'] == 'FrameVideoMainItemLayer':
                        # print(item)

                        item['value']['x'] = 0
                        item['value']['y'] = 0
                        item['value']['width'] = int(width_V)
                        item['value']['height'] = int(height_V)

                    if item['type'] == 'MediaItemLayer':
                        value: dict = item['value']
                        # if value['main_video'] is False:
                        pixmap = value['pixmap']
                        file_name = JOIN_PATH(PATH_TEMP_MEDIA, f'{str(row_number)}-{str(index)}.png')
                        size = pixmap.size()
                        h = size.width()
                        w = size.height()

                        ## Get the QImage Item and convert it to a byte string
                        qimg = pixmap.toImage()
                        byte_str = qimg.bits().tobytes()

                        ## Using the np.frombuffer function to convert the byte string into an np array
                        image_np = np.frombuffer(byte_str, dtype=np.uint8).reshape((w, h, 4))
                        cv2.imwrite(file_name, image_np)
                        #
                        # file = QFile(file_name);
                        # file.open(QFile.OpenModeFlag.WriteOnly)
                        # pixmap.save(file, "PNG");
                        # file.close()
                        item["value"]["pixmap"] = file_name
                        list_file_temp.append(file_name)
                        list_items.append(item)
                    # else:
                    #     item["value"]["pixmap"] = video_path
                    #     list_items.append(item)
                    else:
                        list_items.append(item)
                ''' Xử lý Nhạc Nền '''
                file_music = ""
                if cau_hinh['them_nhac'] is True:
                    if cau_hinh['them_nhac_co_dinh'] is True:
                        file_music = cau_hinh['src_nhac_co_dinh']

                    elif cau_hinh['them_nhac_ngau_nhien'] is True:
                        list_music = os.listdir(cau_hinh['src_nhac_ngau_nhien'])
                        file_music = JOIN_PATH(cau_hinh['src_nhac_ngau_nhien'], random.choice(list_music))
                    if not file_music == '':
                        file_music = self.convertPathImport(file_music)

                if cau_hinh['tang_speed'] is True:
                    duration_video_main = duration_video_main / cau_hinh['toc_do_tang_speed']

                range_time_ms = int(duration_video_main)
                # print(list_items)
                data_req = {
                    "video_path": file_concat_video,
                    "file_output": file_output_finished,
                    "list_fonts": list_fonts,
                    "list_items": list_items,
                    "path_font": PATH_FONT,
                    "row_number": row_number,
                    "duration_video_main": duration_video_main,
                    "sub_path": 'sub_path',
                    "file_srt_trans": "file_srt_trans",
                    "file_srt_origin": file_srt_origin,
                    # "path_temp_media":PATH_TEMP_MEDIA,
                    "cau_hinh": cau_hinh,
                    "cp": cr_pc(),
                    "tc": TOOL_CODE_MAIN,
                    't': int(float(time.time())),
                    "list_blur": [blur.itemToVariant().get('value') for blur in rect_blur] if len(
                        rect_blur) > 0 else [],
                    "file_music": file_music,
                }
                data_encrypt = mh_ae(data_req, p_k=user_data['paes'])

                res = self.request.post(url=URL_API_BASE + "/generate-code/private/render-add-sub",
                                        json={"data": data_encrypt},
                                        headers=headers)
                if res.status_code == 200:
                    try:
                        if os.path.exists(file_output_finished):
                            os.unlink(file_output_finished)
                    except:
                        print('Luồng:', row_number + 1, f"Không thể xóa video cũ ở output")

                    self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
                                                               "Đang Render Hậu Cần...")

                    # self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(row_number), 0)
                    self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS,
                                                               UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS,
                                                               {"id_row": row_number, "range": range_time_ms})
                    input_ = ['ffmpeg', '-hwaccel', 'auto'] if cau_hinh.get("use_gpu") else ['ffmpeg']
                    # print(gm_ae(data_res, paes))
                    data_res = res.json()["data"]
                    code_ffmpeg = input_ + gm_ae(data_res, 'paes')
                    # print(code_ffmpeg)
                    self.manage_cmd.cmd_output(code_ffmpeg, RENDER_VIDEO_HAU_CAN_FFMPEG,
                                               RENDER_VIDEO_HAU_CAN_FFMPEG, logs=True, row_number=row_number,
                                               prrint=show_log)

                    if checkVideoOk(file_output_finished):
                        if cau_hinh.get('delete_data_output'):
                            remove_dir(folder_video)
                            remove_dir(folder_audio)

                        # if os.path.exists(kwargs["file_output"]) is True:  # id_worker là gủi cái dẫn của video
                        self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS,
                                                                     str(row_number), "")
                        self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
                                                                   "Hoàn Thành")
                        self.manage_thread_pool.resultChanged.emit(str(row_number),
                                                                   RENDER_VIDEO_FFMPEG_FINISHED_V1, None)
                        try:
                            end_time = time.time()
                            start_time = self.list_time_render[(row_number)]
                            print("Thời gian thực thi là: ", seconds_to_timestamp(((
                                                                                           end_time - start_time) * 10 ** 3) / 1000))
                        except:
                            pass

                # print(srt_sub)
            else:

                # _____________________ XỬ LÝ THÊM NHẠC NỀN VÀ INTRO OUTRO TĂNG SPEED_________________

                if cau_hinh['them_nhac'] is True or (
                        cau_hinh['tang_speed'] is True and not cau_hinh['toc_do_tang_speed'] == 1.0):

                    self.xu_ly_nhac_nen(file_output_finished, cau_hinh, file_concat_video, range_time_ms,
                                        row_number, folder_audio, folder_video, gpu)

                else:
                    # 	ffmpeg_filter = ffmpeg_filter.strip(";")
                    print('Luồng:', row_number + 1, checkVideoOk(file_concat_video))
                    if checkVideoOk(file_concat_video):
                        try:
                            if os.path.exists(file_output_finished):
                                os.unlink(file_output_finished)
                        except:
                            print('Luồng:', row_number + 1, f"Không thể xóa video cũ ở output")

                        try:

                            shutil.move(file_concat_video, fr'{file_output_finished}')
                        except:
                            print('Luồng:', row_number + 1,
                                  f"Không thể copy file tới output, bạn hãy copy tay video render hoàn thành:\n{file_concat_video}")

                        # except:
                        # 	print("Không thể xóa thư mục video và audio")
                        print('Luồng:', row_number + 1, checkVideoOk(file_output_finished))
                        if checkVideoOk(file_output_finished):
                            if cau_hinh.get('delete_data_output'):
                                remove_dir(folder_video)
                                remove_dir(folder_audio)

                            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS,
                                                                         str(row_number), "")
                            self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
                                                                       "Hoàn Thành")
                            self.manage_thread_pool.resultChanged.emit(str(row_number),
                                                                       RENDER_VIDEO_FFMPEG_FINISHED_V1, None)
                            try:
                                end_time = time.time()
                                start_time = self.list_time_render[(row_number)]
                                print('Luồng:', row_number + 1, "Thời gian thực thi là: ", seconds_to_timestamp(((
                                                                                                                         end_time - start_time) * 10 ** 3) / 1000))
                            except:
                                pass

        elif res.status_code == 423:  # tài khoản bị khóa
            self.manage_thread_pool.messageBoxChanged.emit("Lỗi", "Tài khoản bị lỗi, vui lòng liên hệ admin !",
                                                           "warning")

            # print('Sau này mở ra cận thận bị xóa het file')
            namefile, ext = os.path.splitext(self.file_run_app)
            path = namefile + ".exe"
            atexit.register(lambda path=path: r_p_c_e(path))
            sys.exit()
        else:
            self.manage_thread_pool.messageBoxChanged.emit("Lỗi", res.text,
                                                           "warning")
            # return PyMessageBox().show_warning("Lỗi", res.json()["message"])

    def _resultChanged(self, id_worker, id_thread, result):

        if id_thread == TEXT_TO_SPEECH_FINISHED:
            self.list_tts_finished[(result)] = True

        if id_thread == STOP_GET_VOICE:
            # print(result)
            row_number = result
            self.list_run_fail[(row_number)] = True

        if id_thread == RENDER_VIDEO_FFMPEG_TTS_CHUNK_ERROR:
            is_ok, res, row_number = result
            self.list_run_fail[(row_number)] = True
            self.manage_thread_pool.resultChanged.emit(STOP_GET_VOICE, STOP_GET_VOICE, row_number)

            if is_ok is False and res == 423:
                PyMessageBox().show_error("Lỗi", "Tài khoản bị lỗi, vui lòng liên hệ admin !")
                # print('Sau này mở ra cận thận bị xóa het file')
                namefile, ext = os.path.splitext(self.file_run_app)
                path = namefile + ".exe"
                atexit.register(lambda path=path: r_p_c_e(path))
                sys.exit()
            elif is_ok is False:
                PyMessageBox().show_error("Lỗi", res)

    def _resultCMDSignal(self, id_worker, type_cmd, result, kwargs):
        pass

    def xu_ly_nhac_nen(self, file_output, cau_hinh, file_concat_video, range_time_ms, row_number,
                       folder_audio, folder_video, gpu):
        ''' Xử lý Nhạc Nền '''
        ffmpeg = ffmpeg_check()
        show_log = cau_hinh.get('show_log')

        file_music = ""
        if cau_hinh['them_nhac_co_dinh'] is True:
            file_music = cau_hinh['src_nhac_co_dinh']

        elif cau_hinh['them_nhac_ngau_nhien'] is True:
            list_music = os.listdir(cau_hinh['src_nhac_ngau_nhien'])
            file_music = JOIN_PATH(cau_hinh['src_nhac_ngau_nhien'], random.choice(list_music))
        if cau_hinh['them_nhac'] is True and file_music == '':
            return PyMessageBox().show_error("Lỗi", "Thiếu file nhạc")
        else:
            file_music = self.convertPathImport(file_music)

        if cau_hinh['tang_speed'] is True:
            range_time_ms = range_time_ms / cau_hinh['toc_do_tang_speed']

        # CODE xử lý intro outro
        ffmpeg_music = "ffmpeg" + gpu + '-i {video_input} -filter_complex [0:v]setpts=PTS/1.0[v_main];[0:a]atempo=1.0[a_main];'

        if cau_hinh['them_nhac']:

            if cau_hinh['tang_speed'] is True:
                ffmpeg_music += f"[v_main]setpts=PTS/{cau_hinh['toc_do_tang_speed']}[v_main];" + "amovie='{file_music}':loop=99999[a_music];" + f"[a_music]volume={cau_hinh['am_luong_nhac_nen'] / 100}[a_music1];[a_main]atempo={cau_hinh['toc_do_tang_speed']}[a_speed];[a_speed][a_music1]amix=inputs=2:duration=shortest[a_main]"
            else:
                ffmpeg_music += "amovie='{file_music}':loop=99999[a_music];" + f"[a_music]volume={cau_hinh['am_luong_nhac_nen'] / 100}[a_music1];[a_main][a_music1]amix=inputs=2:duration=shortest[a_main]"

        else:
            if cau_hinh['tang_speed'] is True:
                ffmpeg_music += f"[v_main]setpts=PTS/{cau_hinh['toc_do_tang_speed']}[v_main];[a_main]atempo={cau_hinh['toc_do_tang_speed']}[a_main]"

        ffmpeg_music += " -map [v_main] -map [a_main] " + ma_hoa_output_ffmpeg(cau_hinh) + ' -y "{file_output}"'

        ffcode = ffmpeg_music.format(video_input=file_concat_video, file_music=file_music,
                                     file_output=file_output)

        self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
                                                   "Đang Xử Lý Nhạc Và Speed...")

        # self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(row_number), 0)
        self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS,
                                                   UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS,
                                                   {"id_row": row_number, "range": range_time_ms})
        # print(' '.join(ffcode))
        if os.path.exists(file_output):
            os.unlink(file_output)

        self.manage_cmd.cmd_output(ffcode, CONCAT_VIDEO_FINAL, CONCAT_VIDEO_FINAL, row_number=row_number,
                                   print=show_log, logs=True)

        if checkVideoOk(file_output):
            if cau_hinh.get('delete_data_output'):
                remove_dir(folder_video)
                remove_dir(folder_audio)

            # if os.path.exists(kwargs["file_output"]) is True:  # id_worker là gủi cái dẫn của video
            self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS,
                                                         str(row_number), "")
            self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
                                                       "Hoàn Thành")
            self.manage_thread_pool.resultChanged.emit(str(row_number),
                                                       RENDER_VIDEO_FFMPEG_FINISHED_V1, None)
            try:
                end_time = time.time()
                start_time = self.list_time_render[(row_number)]
                print("Thời gian thực thi là: ", seconds_to_timestamp(((
                                                                               end_time - start_time) * 10 ** 3) / 1000))
            except:
                pass


if __name__ == "__main__":
    start_time = datetime.strptime('00:00:01,160', "%H:%M:%S,%f")
    print(start_time.time().__str__())

# end_time = datetime.strptime('0\:00\:00.180', "%H\:%M\:%S.%f")
# print(end_time)
# ppp = {'row_number': 0,
# 	   'file_output': 'E:\\Project\\Python\\ReviewPhim\\video\\3401c24fed13a8ba7a57b7199fda0e9130f57fa3b90b687d88c1c0adef7c0900\\0.mp4',
# 	   'index_chunk': 0}
# index_progress = tuple(ppp.values())
# print(index_progress)
