import glob
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timedelta, date

import budoux

from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.audiostretchy.stretch import stretch_audio
from gui.helpers.constants import PATH_AUDIO, JOIN_PATH, PATH_VIDEO, CHECK_LIVE_PROXY_ON_TTS, \
    PATH_TEMP, TRIM_AUDIO_SLICE, UPDATE_BALANCE_API_TTS, STOP_GET_VOICE, TEXT_TO_SPEECH_CHUNK, \
    UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, \
    UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, \
    TEXT_TO_SPEECH_FINISHED, GET_VOICE_PREVIEW, TTS_GET_VOICE_FINISHED, LANGUAGE_CODE_SPLIT_NO_SPACE, TOGGLE_SPINNER
from gui.helpers.func_helper import ffmpeg_check, pitch_shift
from gui.helpers.http_request.check_proxy import ProxyChecker
from gui.helpers.server import SERVER_TAB_TTS
from gui.helpers.thread import ManageThreadPool, ManageCMD
from gui.helpers.translatepy.translators import BaseTranslator, GoogleTranslateV2
from gui.helpers.translatepy.utils.request import Request
from gui.widgets.py_messagebox.py_massagebox import PyMessageBox
from gui.widgets.py_table_widget.model_timeline_addsub import ColumnNumber


def replace_time(time):
    return time.__str__().replace(":", "\:")


class TextToSpeech():

    def __init__(self, manage_thread_pool: ManageThreadPool, manage_cmd: ManageCMD,
                 configCurrent: CauHinhTuyChonModel, check_render_tts_finished):

        self.checker = ProxyChecker(manage_thread_pool)
        self.checker.finishedCheckLiveProxySignal.connect(self._finishedCheckLiveProxySignal)
        self.configCurrent = configCurrent
        self.manage_thread_pool = manage_thread_pool
        self.thread_pool_limit = ManageThreadPool()
        self.thread_pool_limit.setMaxThread(8)
        self.manage_cmd = manage_cmd
        # self.video_render = video_render
        self.check_render_tts_finished = check_render_tts_finished

        self.list_seconds_sub = {}
        self.list_folder_video = {}
        self.list_start_time = {}
        self.list_end_time = {}
        self.list_end_sub_pre = {}
        self.list_sub_end_time = {}  # danh sách time của dòng sub cuối cùng để kiểm tra voi thời lượng video xem còn đoạn cuối ko
        self.list_duaration_time_video = {}  # ds thười lượng video ,ddoojo dài video
        self.list_duaration_voice_sub = {}  # thời lượng vủa voice từng sub
        self.list_delay_seconds_sub = {}
        self.list_seconds_start = {}
        self.total_sub = {}
        self.count_result_tts = {}
        self.count_result_fit_voice = {}
        self.end_sub_pre = {}
        self.path_video_render = {}
        self.name_video_origin = {}
        self.list_cau_hinh = {}
        self.list_data_sub = {}
        self.total_chunk = {}
        self.count_result_add_voice_chunk = {}
        self.list_file_temp_chunk = {}

        # self.ouput_src = {}
        self.filters_ = {}
        self.src_subtitle_ = {}
        self.finished = False
        self.run_fail = False
        self.tts_fail = {}

        self.manage_thread_pool.resultChanged.connect(self._resultThread)
        self.thread_pool_limit.resultChanged.connect(self._resultThread)
        self.max_length_word = 100
        self.max_length_character = 490

    # self.manage_cmd.resultSignal.connect(self._resultCMDSignal)

    def removeAllVoices(self, row_number):
        """ Mô tả: Xóa toàn bộ hình ảnh trong frames folder """
        folder_audio = JOIN_PATH(PATH_AUDIO, str(row_number))
        folder_video = JOIN_PATH(PATH_VIDEO, str(row_number))

        if os.path.exists(folder_audio) is False:
            os.makedirs(folder_audio)
        else:
            self.remove_dir(folder_audio)
            os.makedirs(folder_audio)

        if os.path.exists(folder_video) is False:
            os.makedirs(folder_video)
        else:
            self.remove_dir(folder_video)
            os.makedirs(folder_video)

    def remove_dir(self, path):
        try:
            if os.name == 'nt':
                subprocess.check_output(['cmd', '/C', 'rmdir', '/S', '/Q', path])
            else:
                subprocess.check_output(['rm', '-rf', path])
        except:
            pass

    def _finishedCheckLiveProxySignal(self, id_thread, result):

        if id_thread == CHECK_LIVE_PROXY_ON_TTS:
            ''' kết quả kiểm tra live proxy'''
            request = Request(proxy_urls=["http://" + item for item in result['proxy_live']])
            if 'row_number' in result['kwargs'].keys():  # đã thêm type chuyển đổi o đây
                print("Ko cần proxy")

    # self._convertTTS(request, result['kwargs']['row_number'])

    def getVoiceRow(self, cau_hinh, sub_tss, index, row_number, folder_audio):
        print(f"GET voice {index + 1} again")

        gender, language_tts, pitch, style = cau_hinh["servers_tts"][
            "gender"], cau_hinh["servers_tts"]["language_tts"], cau_hinh[
            "servers_tts"].get("pitch"), cau_hinh[
            "servers_tts"].get("style")

        api_server = SERVER_TAB_TTS.get(
            list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("name_api_db")

        lamda_server_trans = SERVER_TAB_TTS.get(
            list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("server_trans")
        server_trans = lamda_server_trans(manage_thread_pool=self.manage_thread_pool, file_json=cau_hinh["servers_tts"][
            api_server])
        self._funcTextToSpeechChunk(server_trans=server_trans, row_number=row_number, get_voice=True,
                                    index=index, text=sub_tss, gender=gender, style=style, language_tts=language_tts,
                                    pitch=pitch, folder_audio=folder_audio, cau_hinh=cau_hinh)
        print(f"DONE voice {index + 1}")

    def convertTextToSpeechChunk(self, row_number, cau_hinh, data_sub, folder_audio, get_voice=False, list_rows=None):
        # Khớp voice vào hình
        self.count_result_tts[(row_number)] = 0

        gender, language_tts, pitch, style = cau_hinh["servers_tts"][
            "gender"], cau_hinh["servers_tts"]["language_tts"], cau_hinh[
            "servers_tts"].get("pitch"), cau_hinh[
            "servers_tts"].get("style")

        api_server = SERVER_TAB_TTS.get(
            list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("name_api_db")

        lamda_server_trans = SERVER_TAB_TTS.get(
            list(SERVER_TAB_TTS.keys())[cau_hinh["tab_tts_active"]]).get("server_trans")
        server_trans = lamda_server_trans(manage_thread_pool=self.manage_thread_pool, file_json=cau_hinh["servers_tts"][
            api_server])

        check_ok, mes = server_trans.check_token()
        if check_ok is False:
            self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)

            return PyMessageBox().show_warning("Thông báo", mes)

        check_ok, balance, total_token = server_trans.check_balance()


        if check_ok is False:
            self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)

            return PyMessageBox().show_warning("Thông báo", "Token API của bạn bị sai hoặc đã hết hạn")
        if isinstance(balance, dict):
            balance = -1 if isinstance(balance.get('characters'), str) else balance.get('characters')

        if not balance == -1:
            if int(balance) < 100:
                self.manage_thread_pool.resultChanged.emit(TOGGLE_SPINNER, TOGGLE_SPINNER, False)

                return PyMessageBox().show_warning("Thông báo", "Số ký tự còn lại trong tài khoản không đủ !")

        if not get_voice:
            self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
                                                       UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
                                                       {"row_number": row_number, "range": len(data_sub),
                                                        "index_chunk": 1})

        self.total_sub[(row_number)] = len(data_sub)
        today = date.today()
        folder_name = f'{today:%d}{today:%m}{today.year}{datetime.now().time().strftime("%H:%M:%S").replace(":", "")}'
        folder_temp = JOIN_PATH(PATH_AUDIO, str(folder_name))
        if os.path.exists(folder_temp) is False:
            os.mkdir(folder_temp)
        for index, sub in enumerate(data_sub):

            self.tts_fail[row_number] = False
            self.run_fail = False

            sub_tss = sub[ColumnNumber.column_sub_text.value]
            # print(sub_tss)
            if get_voice:
                index = list_rows[index]
            self.thread_pool_limit.start(self._funcTextToSpeechChunk, "text_to_speech_" + str(index + 1),
                                         TEXT_TO_SPEECH_CHUNK, limit_thread=True,
                                         server_trans=server_trans, row_number=row_number, get_voice=get_voice,
                                         index=index, text=sub_tss, gender=gender, style=style,
                                         language_tts=language_tts, pitch=pitch, folder_audio=folder_audio,
                                         folder_temp=folder_temp, cau_hinh=cau_hinh)

    def _funcTextToSpeechChunk(self, **kwargs):
        # typeVersion là typeTHread trả về result
        # try:
        thread_pool = kwargs.get('thread_pool')
        id_worker = kwargs.get('id_worker')

        row_number = kwargs["row_number"]
        text = kwargs.get('text').replace('\n', ' ')
        gender = kwargs["gender"]
        language_tts = kwargs["language_tts"]
        index = kwargs["index"]
        folder_audio = kwargs["folder_audio"]
        folder_temp = kwargs["folder_temp"]
        style = kwargs["style"]

        pitch = kwargs["pitch"]
        cau_hinh = kwargs["cau_hinh"]
        speed_giong_doc = cau_hinh["speed_giong_doc"]
        get_voice = kwargs["get_voice"]

        ffmpeg = ffmpeg_check(gpu=cau_hinh.get("use_gpu"))

        if self.tts_fail[row_number]:
            return "STOP", row_number, None, None, get_voice

        if "server_trans" in kwargs.keys():

            server_trans: BaseTranslator = kwargs["server_trans"]

            file_out = JOIN_PATH(folder_audio, str(index + 1) + ".wav")

            file_temp = JOIN_PATH(folder_temp, f"{index + 1}_temp.wav")
            file_temp2 = JOIN_PATH(folder_temp, f"{index + 1}_temp2.wav")
            file_speed = JOIN_PATH(folder_temp, f"{index + 1}_speed.wav")
            file_pitch = JOIN_PATH(folder_temp, f"{index + 1}_pitch.wav")
            # file_fix = JOIN_PATH(folder_audio, "_fix.wav")

            if not os.path.exists(file_out) or get_voice:
                if text == '':
                    time_no_text = cau_hinh.get("time_no_text",1)
                    code_ff = f'{ffmpeg} -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -t {time_no_text} {file_out}'
                    self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index + 1),
                                               TRIM_AUDIO_SLICE)
                else:
                    if len(text) > self.max_length_character:
                        acode = '-acodec pcm_s16le -ac 1'

                        list_chunk = self.split_text(text)
                        audio_chunks = []
                        file_list = JOIN_PATH(folder_temp, f"{index + 1}-list.txt")
                        with open(file_list, 'w') as file:
                            for idx, txt in enumerate(list_chunk):
                                # print(txt)
                                file_chunk = JOIN_PATH(folder_temp, f"{index + 1}-{idx + 1}_chunk.wav")
                                file_chunk_temp = JOIN_PATH(folder_temp, f"{index + 1}-{idx + 1}_chunk_temp.wav")

                                text_trans = server_trans.text_to_speech(txt, 100, gender, language_tts,
                                                                         row_number=row_number,
                                                                         style=style, folder_src_voice=cau_hinh.get(
                                        "folder_src_voice", ""), line_sub=str(index + 1))
                                if text_trans.result is False:
                                    return False, row_number, None, None, get_voice
                                if text_trans.result is None:
                                    return False, row_number, None, None, get_voice
                                text_trans.write_to_file(file_chunk)

                                if os.path.exists(file_chunk):
                                    code_ff = f'{ffmpeg} -i "{file_chunk}" {acode} -ar 48000 -y "{file_chunk_temp}"'
                                    self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index),
                                                               TRIM_AUDIO_SLICE)
                                    if os.path.exists(file_chunk_temp):
                                        audio_chunks.append(file_chunk_temp)
                                        file.write(f"file '{file_chunk_temp}'\n")

                        if len(audio_chunks) > 0:
                            code_ff = f'{ffmpeg} -f concat -safe 0 -i "{file_list}" {acode} -ar 48000 -y "{file_temp}"'
                            self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index),
                                                       TRIM_AUDIO_SLICE)
                    else:
                        text_trans = server_trans.text_to_speech(text, 100, gender, language_tts, row_number=row_number,
                                                                 style=style,
                                                                 folder_src_voice=cau_hinh.get("folder_src_voice", ""),
                                                                 line_sub=str(index + 1))
                        if text_trans.result is None:
                            return False, row_number, None, None, get_voice
                        # elif isinstance(text_trans.result,str):
                        # 	return False, row_number, text_trans.result, None, None
                        text_trans.write_to_file(file_temp)

                    try:  # loại bỏ khoảng lạng đầu và cuối
                        code_ff = f'{ffmpeg} -i "{file_temp}" -af silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse -acodec pcm_s16le -ac 1 -ar 48000 -y "{file_temp2}"'
                        # code_ff = f' -i "{file_temp.name}" -af silenceremove=start_periods=1:stop_periods=1:detection=peak -y "{file_out}"'
                        self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index + 1),
                                                   TRIM_AUDIO_SLICE)
                        if not os.path.exists(file_temp2):
                            code_ff = f'{ffmpeg} -i "{file_temp}" -acodec pcm_s16le -ac 1 -ar 48000 -y "{file_temp2}"'
                            self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index + 1),
                                                       TRIM_AUDIO_SLICE)
                            if not os.path.exists(file_temp2):
                                shutil.copy(file_temp, file_temp2)

                    except:
                        try:
                            # file_temp.close()
                            code_ff = f'{ffmpeg} -i "{file_temp}" -acodec pcm_s16le -ac 1 -ar 48000 -y "{file_temp2}"'
                            self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index + 1),
                                                       TRIM_AUDIO_SLICE)
                            if not os.path.exists(file_temp2):
                                shutil.copy(file_temp, file_temp2)
                        except:
                            pass

                    sp = (speed_giong_doc / 10)

                    # try:
                    if not sp == 1:
                        stretch_audio(file_temp2, file_speed, ratio=(1 / sp))
                        shutil.move(file_speed, file_temp2)

                    if not pitch == 0:
                        # print(1)
                        pitch_shift(file_temp2, file_pitch, (pitch / 10), folder_audio, index + 1)
                        shutil.move(file_pitch, file_temp2)
                    # except:
                    # 	pass
                    channel_audio = cau_hinh.get("channel_audio", 1)
                    try:  # loại bỏ khoảng lạng đầu và cuối
                        code_ff = f'{ffmpeg} -i "{file_temp2}" -af volume={cau_hinh.get("volume_giong_doc") / 100},silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB,areverse -acodec pcm_s16le -ac {channel_audio} -ar 48000 -y "{file_out}"'
                        self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index + 1),
                                                   TRIM_AUDIO_SLICE)

                        if not os.path.exists(file_out):
                            code_ff = f'{ffmpeg} -i "{file_temp2}" -af volume={cau_hinh.get("volume_giong_doc") / 100} -acodec pcm_s16le -ac {channel_audio} -ar 48000 -y "{file_out}"'
                            self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index + 1),
                                                       TRIM_AUDIO_SLICE)
                            if not os.path.exists(file_out):
                                shutil.move(file_temp2, file_out)
                    except:
                        # file_temp.close()
                        try:
                            code_ff = f'{ffmpeg} -i "{file_temp2}" -af volume={cau_hinh.get("volume_giong_doc") / 100} -acodec pcm_s16le -ac {channel_audio} -ar 48000 -y "{file_out}"'
                            self.manage_cmd.cmd_output(code_ff, str(row_number) + TRIM_AUDIO_SLICE + str(index + 1),
                                                       TRIM_AUDIO_SLICE)
                            if not os.path.exists(file_out):
                                shutil.move(file_temp2, file_out)
                        except:
                            pass
                    finally:

                        if os.path.exists(file_temp2):
                            os.remove(file_temp2)

            try:
                if os.path.exists(file_speed):
                    os.unlink(file_speed)
            except:
                pass
            try:
                if os.path.exists(file_pitch):
                    os.unlink(file_pitch)
            except:
                pass

            if thread_pool:
                thread_pool.finishSingleThread(id_worker, limit_thread=True)

            return True, row_number, file_out, folder_audio, get_voice

    def _resultThread(self, id_worker, id_thread, result):
        if id_thread == GET_VOICE_PREVIEW:
            data_sub, cau_hinh, list_rows = result
            # print(data_sub)
            self.convertTextToSpeechChunk(1000, cau_hinh, data_sub, PATH_TEMP, get_voice=True, list_rows=list_rows)

        if id_thread == STOP_GET_VOICE:
            # print(result)
            row_number = result
            self.tts_fail[row_number] = True

        if id_thread == TEXT_TO_SPEECH_CHUNK:
            is_ok, row_number, file_out, folder_audio, get_voice = result

            if self.tts_fail[row_number]:
                return

            if is_ok is False:
                self.tts_fail[row_number] = True
                self.manage_thread_pool.resultChanged.emit(STOP_GET_VOICE, STOP_GET_VOICE, row_number)

                PyMessageBox().show_warning("Thông báo",
                                            "Server lấy giọng đọc hiện tại đang chậm hoặc bị quá tải không lấy được voice")
            elif is_ok == 'STOP':
                print('stop')
                return
            else:
                self.count_result_tts[(row_number)] += 1
                if not get_voice:
                    self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
                                                                 json.dumps({
                                                                     "row_number": row_number, "index_chunk": 1}),
                                                                 self.count_result_tts[(row_number)])
                # self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_PLUS_TABLE_PROCESS, str(row_number), 1)

                print("Số voice đã get được: " + str(self.count_result_tts[(row_number)]))
                if self.count_result_tts[(row_number)] == self.total_sub[(row_number)]:
                    self.count_result_tts[(row_number)] = 0
                    self.manage_thread_pool.resultChanged.emit(UPDATE_BALANCE_API_TTS, UPDATE_BALANCE_API_TTS, "")
                    print("TTS HOÀN THÀNH")
                    # if self.check_render_tts_finished(row_number):
                    self.manage_thread_pool.resultChanged.emit(TEXT_TO_SPEECH_FINISHED, TEXT_TO_SPEECH_FINISHED,
                                                               row_number)
                    if get_voice:
                        self.manage_thread_pool.resultChanged.emit(TTS_GET_VOICE_FINISHED, TTS_GET_VOICE_FINISHED,
                                                                   file_out)

    # else:
    # 	self.manage_thread_pool.resultChanged.emit(TEXT_TO_SPEECH_PUSH_PATH_AUDIO, TEXT_TO_SPEECH_PUSH_PATH_AUDIO, (
    # 		row_number, folder_audio))

    # self.check_render_tts_finished(row_number, return_value=False, value=True)

    # def _resultCMDSignal (self, id_worker, type_cmd, result, kwargs):  # file_temp idworker được truyền vào ở hàm run cmd
    #
    # 	if type_cmd == ADD_VOICE_TO_VIDEO_THREAD:
    # 		is_ok, row_number = result
    # 		if result is False:
    # 			self.run_fail = True
    # 			self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
    # 				"Không thể thêm voice vào video")
    # 			PyMessageBox().show_warning("Thông báo", "Không thể thêm voice vào video")

    def getFolderAudioRow(self, folder_name):
        # namevideo = os.path.basename(self.path_video[(row_number)])[:-4]
        path = JOIN_PATH(PATH_AUDIO, str(folder_name))
        path_video = JOIN_PATH(PATH_VIDEO, str(folder_name))

        if os.path.isdir(path):
            is_ok = PyMessageBox().show_question("Thông báo",
                                                 "Đã tồn tại trạng thái chuyển thành voice trước đó với video này. Bạn có muốn chuyển lại voice không ? Chuyển lại sẽ làm lãng phí ký tự của bạn.")
            if is_ok:
                self.remove_dir(path)
                self.remove_dir(path_video)
            else:
                return path

        if os.path.exists(path) is False:
            os.mkdir(path)

        return path

    def getFolderVideoRow(self, folder_name):
        # namevideo = os.path.basename(self.path_video[(row_number)])[:-4]
        path = JOIN_PATH(PATH_VIDEO, str(folder_name))

        if os.path.exists(path) is False:
            os.mkdir(path)

        return path

    #
    # def getFolderVideoRow (self, row_number):  # đã tạo lúc đầu
    #
    # 	return JOIN_PATH(PATH_VIDEO, str(row_number))

    def getListVideoRow(self, folder_video) -> list:  # đã tạo lúc đầu
        digits = re.compile(r'(\d+)')

        def tokenize(filename):
            return tuple(int(token) if match else token
                         for token, match in
                         ((fragment, digits.search(fragment))
                          for fragment in digits.split(filename)))

        liss = glob.glob(folder_video + '**/*.mp4', recursive=True)
        # Now you can sort your PDF file names like so:
        liss.sort(key=tokenize)
        return liss

    def datetime_to_seconds(self, time) -> timedelta:  #
        a = datetime.strptime('00:0:00,000', '%H:%M:%S,%f')
        return (time - a)

    # return (time - a).total_seconds()

    def get_timestamp(self, seconds):
        td = timedelta(seconds=seconds)
        ms = td.microseconds // 1000
        m, s = divmod(td.seconds, 60)
        h, m = divmod(m, 60)
        return datetime.strptime('{:02d}:{:02d}:{:02d},{:03d}'.format(h, m, s, ms), "%H:%M:%S,%f")

    def split_text(self, content_):
        translator_server = GoogleTranslateV2(self.manage_thread_pool)

        lang_source = translator_server.language(content_[:100])
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

            if str(lang_source.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
                if len(text_c) + len(text_) > self.max_length_word:
                    list_text.append(text_c.strip() + "\n")
                    text_c = ''
                text_c += text_
            else:
                if len(text_c.strip().split()) + 1 > self.max_length_word:
                    list_text.append(text_c.strip() + "\n")
                    text_c = ''
                elif not text_c == '':
                    if len(text_c.strip().split()) > self.max_length_word / 2 and text_c.strip()[
                        -1] in '''.,!;?'"]:)>/\\}''':
                        list_text.append(text_c.strip() + "\n")
                        text_c = ''
                text_c += text_ + " "
            if index == len(list_content) - 1:
                list_text.append(text_c.strip() + "\n")
        return list_text


if __name__ == '__main__':
    # end_sub_pre = datetime.strptime(f"00:00:00,500", "%H:%M:%S,%f")
    # end_time = datetime.strptime("00:00:06,220", "%H:%M:%S,%f")

    print(1)
