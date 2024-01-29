import atexit
import json
import os
import random
import shutil
import sys
import time
from datetime import datetime

import cv2
import numpy as np
from PySide6.QtWidgets import QWidget

from gui.db.sqlite import CauHinhTuyChonModel
from gui.helpers.constants import JOIN_PATH, PATH_TEMP_MEDIA, \
	RENDER_VIDEO_FFMPEG_NO_TTS, \
	UPDATE_STATUS_TABLE_PROCESS, UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS, UPDATE_VALUE_PROGRESS_TABLE_PROCESS, \
	PATH_TEMP, \
	RENDER_VIDEO_FFMPEG_NO_TTS_FINISHED, RENDER_VIDEO_PRE_TTS, \
	FIT_VIDEO_MATCH_VOICE, UPDATE_FILENAME_OUTPUT_RENDER, PATH_FONT, \
	TOOL_CODE_MAIN, USER_DATA, CONCAT_VIDEO_FINAL, CONCAT_VIDEO_FILE_LIST, STOP_GET_VOICE, \
	RENDER_VIDEO_FFMPEG_FINISHED_V1, UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS, \
	UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS, UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, \
	UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, RENDER_VIDEO_FINISHED, \
	RENDER_VIDEOPRE_FINISHED, RENDER_VIDEO_FFMPEG_TTS_CHUNK_ERROR, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, \
	RESULT_CMD_RENDER_VIDEO_PRE_TTS, PREVIEW_PRE_RENDER, TOGGLE_SPINNER, Noi_Video_theo_chunk, TEXT_TO_SPEECH_FINISHED, \
	SMART_CUT_VIDEO, CMD_SMART_CUT_VIDEO, RESET_VALUE_PROGRESS_TABLE_PROCESS, SMART_CUT_VIDEO_HAS_MUSIC
from gui.helpers.ect import mh_ae, cr_pc, gm_ae, mh_ae_w
from gui.helpers.func_helper import get_duaration_video, getValueSettings, r_p_c_e, checkVideoOk, \
	ffmpeg_check, remove_dir, datetime_to_seconds, seconds_to_timestamp, play_media_preview, ma_hoa_output_ffmpeg
from gui.helpers.get_data import URL_API_BASE, PATH_FFCUT
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
	
	def __init__ (self, manage_thread_pool: ManageThreadPool, thread_pool_limit, manage_cmd: ManageCMD, file_run_app, groupbox_timeline):
		
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
	
	def loadDataConfigCurrent (self, configCurrent: CauHinhTuyChonModel):
		self.configCurrent = configCurrent
	
	def _progressSignal (self, id_worker, type_cmd, progress, kwargs):
		
		if type_cmd == FIT_VIDEO_MATCH_VOICE:
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(
				kwargs['row_number']), progress)
		
		if type_cmd == CONCAT_VIDEO_FILE_LIST:
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(
				kwargs['row_number']), progress)
		
		if type_cmd == CONCAT_VIDEO_FINAL:
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(
				kwargs['row_number']), progress)
		
		if type_cmd == RENDER_VIDEO_FFMPEG_NO_TTS:
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(kwargs['row_number']),
				progress)
		
		if type_cmd == RENDER_VIDEO_PRE_TTS:
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(kwargs['row_number']),
				progress)
	
	def convertToHex (self, color, alpha):
		color = color.replace("#", "")
		color = "".join(reversed(color))
		return '%02x' % int(255 * (100 - alpha) / 100) + color
	
	def convertPathImport (self, path):
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
	
	def render_video_preview (self, video_path, filters, row_number, cau_hinh, data_sub, pos_add_sub):  # lấy cấu hinh ngay lúc bấm để kiểm tra mới đùng
		list_fonts, rect_blur, layers = filters
		# print(video_path)
		# [dolech, time, pos_ori, sub_origin, sub_translate, pos_trans]
		
		start_time = datetime.strptime(data_sub[0][ColumnNumber.column_time.value].split(' --> ')[0], "%H:%M:%S,%f")
		end_time = datetime.strptime(data_sub[0][ColumnNumber.column_time.value].split(' --> ')[1], "%H:%M:%S,%f")
		for index, sub in enumerate(data_sub):
			if index == len(data_sub) - 1:
				end_time = datetime.strptime(
					data_sub[index][ColumnNumber.column_time.value].split(' --> ')[1], "%H:%M:%S,%f")
		
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
	
	def _funcRenderPreview (self, **kwargs):
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
	
	# thread_pool.finishSingleThread(id_worker, limit_thread=True)
	# return row_number if done is True else None
	
	def render_video_no_tts (self, video_path, filters, row_number, sub_path, cau_hinh, data_sub, pos_add_sub):  # lấy cấu hinh ngay lúc bấm để kiểm tra mới đùng
		list_fonts, rect_blur, layers = filters
		# print(video_path)
		duration_video_main, bit_rate = get_duaration_video(video_path)
		# cau_hinh['bit_rate_value_origin'] = bit_rate
		duration_intro = 0
		duration_outro = 0
		self.list_data_sub[(row_number)] = data_sub
		self.list_time_render[(row_number)] = time.time()
		# cau_hinh: dict = json.loads(self.configCurrent.value)
		# list_layers = [list(layer.values())[0].itemToVariant() for layer in layers]
		# print(layers)
		
		list_layers = [list(layer.values())[0].itemToVariant() for layer in layers]
		
		# file_srt_trans = JOIN_PATH(PATH_TEMP, f"{row_number}-trans.ass")
		file_srt_origin = JOIN_PATH(PATH_TEMP, f"{row_number}-origin.ass")
		self.list_file_srt_origin[(row_number)] = file_srt_origin
		if cau_hinh['hien_thi_sub']:
			# if cau_hinh['sub_hien_thi'] == 'origin' or cau_hinh['sub_hien_thi'] == 'all':
			create_file_sub_ass(file_srt_origin, cau_hinh, data_sub, pos_add_sub)
		
		name_video = os.path.basename(video_path)[:-4]
		
		file_output = JOIN_PATH(
			cau_hinh['src_output'], name_video + f"-{cau_hinh['ten_hau_to_video']}" + f".{cau_hinh['dinh_dang_video']}")
		
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
		
		range_time_ms = int(duration_video_main + duration_intro + duration_outro)
		# print(list_items)
		data_req = {
			"video_path": video_path,
			"file_output": file_output,
			"list_fonts": list_fonts,
			"list_items": list_items,
			"path_font": PATH_FONT,
			"row_number": row_number,
			"duration_video_main": duration_video_main,
			"sub_path": sub_path,
			"file_srt_trans": "file_srt_trans",
			"file_srt_origin": file_srt_origin,
			# "path_temp_media":PATH_TEMP_MEDIA,
			"cau_hinh": cau_hinh,
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
			"list_blur": [blur.itemToVariant().get('value') for blur in rect_blur] if len(rect_blur) > 0 else [],
			"file_music": file_music,
		}
		
		# st = QSettings(*SETTING_APP)
		
		user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		data_encrypt = mh_ae(data_req, p_k=user_data['paes'])
		
		headers = {"Authorization": f"Bearer {user_data['token']}"}
		res = self.request.post(url=URL_API_BASE + "/generate-code/private/render-add-sub", json={"data": data_encrypt},
			headers=headers)
		if res.status_code == 200:
			
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(row_number), 0)
			self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS,
				UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS,
				{"id_row": row_number, "range": range_time_ms})
			self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
				"Đang Đợi...")
			self.manage_thread_pool.resultChanged.emit(str(row_number),
				UPDATE_FILENAME_OUTPUT_RENDER, file_output)
			
			self.thread_pool_limit.start(self._funcRenderNoTTS, video_path,
				RENDER_VIDEO_FFMPEG_NO_TTS, limit_thread=True, data_res=res.json()["data"], paes=user_data[
					'paes'], row_number=row_number, total_seconds=range_time_ms,
				file_srt_origin=file_srt_origin, file_output=file_output, cau_hinh=cau_hinh, list_file_temp=list_file_temp)
		
		elif res.status_code == 423:  # tài khoản bị khóa
			self.manage_thread_pool.messageBoxChanged.emit("Lỗi", "Tài khoản bị lỗi, vui lòng liên hệ admin !", "error")
			
			# PyMessageBox().show_error("Lỗi", "Tài khoản bị lỗi, vui lòng liên hệ admin !")
			# print('Sau này mở ra cận thận bị xóa het file')
			namefile, ext = os.path.splitext(self.file_run_app)
			path = namefile + ".exe"
			atexit.register(lambda path=path: r_p_c_e(path))
			sys.exit()
		else:
			self.manage_thread_pool.messageBoxChanged.emit("Lỗi", res.text, "warning")
		return
	
	# return PyMessageBox().show_warning()
	
	def _funcRenderNoTTS (self, **kwargs):
		# try:
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]  # id o đây là video_path
		row_number = kwargs["row_number"]
		total_seconds = kwargs["total_seconds"]
		# file_srt_trans = kwargs["file_srt_trans"]
		file_srt_origin = kwargs["file_srt_origin"]
		file_output = kwargs["file_output"]
		data_res = kwargs["data_res"]
		paes = kwargs["paes"]
		cau_hinh = kwargs["cau_hinh"]
		list_file_temp = kwargs["list_file_temp"]
		
		ffmpeg = ffmpeg_check()
		
		input_ = [ffmpeg, '-hwaccel', 'auto'] if cau_hinh.get("use_gpu") else [ffmpeg]
		# print(gm_ae(data_res, paes))
		code_ffmpeg = input_ + gm_ae(data_res, paes)
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
			"Đang Render Video...")
		
		done = self.manage_cmd.cmd_output(code_ffmpeg, id_worker,
			RENDER_VIDEO_FFMPEG_NO_TTS, logs=True, use_stop_thread=True, row_number=row_number, total_seconds=total_seconds,
			file_srt_origin=file_srt_origin, file_output=file_output, cau_hinh=cau_hinh)
		
		# if len(list_file_temp) > 0:
		# 	for file in list_file_temp:
		# 		if os.path.exists(file):
		# 			os.remove(file)
		
		thread_pool.finishSingleThread(id_worker, limit_thread=True)
		return row_number if done is True else None
	
	# @decorator_try_except_class
	def render_video_TTS_split (self, video_path, list_layers, list_fonts, rect_blur, file_output, row_number, sub_path, cau_hinh, data_sub, data_sub_new, folder_audio, folder_video, pos_add_sub):  # lấy cấu hinh ngay lúc bấm để kiểm tra mới đùng
		# Khớp hình vào voice render trước rồi moi ghep voice
		self.manage_thread_pool.resultChanged.emit(UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS,
			UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS,
			{"row_number": row_number, "percent_range": 25})
		
		self.list_count_state_render_tts[(row_number)] = 0
		
		self.list_video_path[(row_number)] = video_path
		self.list_video_output_render[(row_number)] = file_output
		self.list_folder_audio[(row_number)] = folder_audio
		self.list_folder_video[(row_number)] = folder_video
		self.list_data_sub[(row_number)] = data_sub
		self.list_data_sub_new[(row_number)] = data_sub_new
		self.list_cau_hinh[(row_number)] = cau_hinh
		self.list_run_fail[(row_number)] = False
		self.list_tts_finished[(row_number)] = False
		self.list_file_temp_chunk[(row_number)] = {}
		self.list_count_chunk_finished[(row_number)] = 0
		self.list_file_temp_media[(row_number)] = []
		self.list_time_render[(row_number)] = time.time()
		
		duration_video_main, bit_rate = get_duaration_video(video_path)
		
		self.list_cau_hinh[(row_number)] = cau_hinh
		
		# cau_hinh: dict = json.loads(self.configCurrent.value)
		# list_layers = [list(layer.values())[0].itemToVariant() for layer in layers]
		name_video, ext = os.path.basename(video_path)[:-4], os.path.basename(video_path)[-4:]
		
		if cau_hinh.get("use_video_origin"):
			self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
				UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
				{"row_number": row_number, "range": 1,
				 "index_chunk": 0})  # 0 render, 1 tts,2 là ghép, 3 nối
			shutil.copy2(video_path, file_output)
			if checkVideoOk(file_output):  # id_worker là gủi cái dẫn của video
				self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, json.dumps({
					"row_number": row_number, "index_chunk": 0}),
					1)
				
				self.manage_thread_pool.resultChanged.emit(RENDER_VIDEOPRE_FINISHED, RENDER_VIDEOPRE_FINISHED,
					row_number)
				
				self.manage_thread_pool.resultChanged.emit(str(row_number), RENDER_VIDEO_FINISHED, "")
		else:
			file_srt_origin = JOIN_PATH(PATH_TEMP, f"{row_number}-origin.ass")
			self.list_file_srt_origin[(row_number)] = file_srt_origin
			
			if cau_hinh['hien_thi_sub']:
				create_file_sub_ass(file_srt_origin, cau_hinh, data_sub, pos_add_sub)
			
			list_items = []
			list_file_temp = []
			''' Xử lý layer thay đổi lại pixmap '''
			for index, item in enumerate(list_layers.copy()):
				
				if item['type'] == 'MediaItemLayer':
					try:
						value: dict = item['value']
						# if value['main_video'] is False:
						pixmap = value['pixmap']
						file_name = JOIN_PATH(PATH_TEMP_MEDIA, f'{row_number}_overlay_{str(index)}.png')
						try:
							if os.path.exists(file_name):
								os.remove(file_name)
						except:
							file_name = JOIN_PATH(PATH_TEMP_MEDIA, f'{row_number}_overlayfix_{str(index)}.png')
						
						size = pixmap.size()
						h = size.width()
						w = size.height()
						
						## Get the QImage Item and convert it to a byte string
						qimg = pixmap.toImage()
						byte_str = qimg.bits().tobytes()
						
						## Using the np.frombuffer function to convert the byte string into an np array
						image_np = np.frombuffer(byte_str, dtype=np.uint8).reshape((w, h, 4))
						cv2.imwrite(file_name, image_np)
						
						item["value"]["pixmap"] = file_name
						list_items.append(item)
						list_file_temp.append(file_name)
					except:
						pass
				
				else:
					list_items.append(item)
			
			data_config = cau_hinh.copy()
			''' Xử lý Nhạc Nền '''
			data_config['them_nhac'] = False
			
			data_config['tang_speed'] = False
			
			range_time_ms = int(duration_video_main)
			# print(list_items)
			
			
			data_req = {
				"video_path": video_path,
				"file_output": file_output,
				"list_fonts": list_fonts,
				"path_font": PATH_FONT,
				"list_items": list_items,
				"row_number": row_number,
				"duration_video_main": duration_video_main,
				"sub_path": sub_path,
				"file_srt_trans": 'file_srt_trans',
				"file_srt_origin": file_srt_origin,
				# "path_temp_media":PATH_TEMP_MEDIA,
				"cau_hinh": data_config,
				"cp": cr_pc(),
				"tc": TOOL_CODE_MAIN,
				't': int(float(time.time())),
				"list_blur": [blur.itemToVariant().get('value') for blur in rect_blur] if len(rect_blur) > 0 else [],
				# "file_music": file_music,
			}
			# print(data_req)
			
			# st = QSettings(*SETTING_APP)
			# settings = getValueSettings (SETTING_APP_DATA, TOOL_CODE_MAIN)
			user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
			data_encrypt = mh_ae(data_req, p_k=user_data['paes'])
			
			headers = {"Authorization": f"Bearer {user_data['token']}"}
			res = self.request.post(url=URL_API_BASE + "/generate-code/private/render-add-sub", json={
				"data": data_encrypt},
				headers=headers)
			# print(res.json())
			
			if res.json()["status_code"] == 200:
				
				self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
					UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
					{"row_number": row_number, "range": range_time_ms,
					 "index_chunk": 0})  # 0 render, 1 tts,2 là ghép, 3 nối
				
				self.thread_pool_limit.start(self._funcRenderPreTTS, video_path,
					RENDER_VIDEO_PRE_TTS, limit_thread=True, data_res=res.json()["data"], paes=user_data[
						'paes'], row_number=row_number, total_seconds=range_time_ms,
					file_srt_origin=file_srt_origin, file_output=file_output, list_file_temp=list_file_temp, name_video=name_video, cau_hinh=cau_hinh)
			
			elif res.json()["status_code"] == 423:  # tài khoản bị khóa
				self.manage_thread_pool.messageBoxChanged.emit("Lỗi", "Tài khoản bị lỗi, vui lòng liên hệ admin !", "warning")
				
				# PyMessageBox().show_error("Lỗi", "Tài khoản bị lỗi, vui lòng liên hệ admin !")
				# print('Sau này mở ra cận thận bị xóa het file')
				namefile, ext = os.path.splitext(self.file_run_app)
				path = namefile + ".exe"
				atexit.register(lambda path=path: r_p_c_e(path))
				sys.exit()
			else:
				self.manage_thread_pool.messageBoxChanged.emit("Lỗi", res.text, "warning")
	
	# PyMessageBox().show_warning("Lỗi", res.json()["message"])
	
	def _funcRenderPreTTS (self, **kwargs):
		# Khớp hình vào voice render trước rồi moi ghep voice
		# try:
		
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]  # id o đây là video_path
		row_number = kwargs["row_number"]
		total_seconds = kwargs["total_seconds"]
		
		file_srt_origin = kwargs["file_srt_origin"]
		file_output = kwargs["file_output"]
		data_res = kwargs["data_res"]
		paes = kwargs["paes"]
		list_file_temp = kwargs["list_file_temp"]
		name_video = kwargs["name_video"]
		
		cau_hinh = kwargs["cau_hinh"]
		
		ffmpeg = ffmpeg_check()
		# code_ffmpeg = f"{ffmpeg + ' -hwaccel auto' if cau_hinh.get('use_gpu') else ffmpeg} {gm_ae(data_res, paes)}"
		
		input_ = [ffmpeg, '-hwaccel', 'auto'] if cau_hinh.get("use_gpu") else [ffmpeg]
		
		code_ffmpeg = input_ + gm_ae(data_res, paes)
		# print(" ".join(code_ffmpeg))
		# while True:
		# 	pass
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
			"Đang Render Video...")
		try:
			if os.path.exists(file_output):
				os.remove(file_output)
		except:
			pass
		show_log = cau_hinh.get('show_log')
		done = self.manage_cmd.cmd_output(code_ffmpeg, id_worker,
			RESULT_CMD_RENDER_VIDEO_PRE_TTS, logs=True, print=show_log, use_stop_thread=True, row_number=row_number, total_seconds=total_seconds,
			file_srt_origin=file_srt_origin, file_output=file_output, name_video=name_video)
		
		for file in list_file_temp:
			try:
				if os.path.exists(file):
					os.remove(file)
			except:
				continue
		
		# thread_pool.finishSingleThread(id_worker, limit_thread=True)
		return row_number if done is True else None
	
	
	def func_r_v_l (self, **kwargs):
		
		start_time, video_path, mode_tts, folder_audio, folder_video, row_number, ind_seq, second_start, seconds_sub, end_time_sub, cau_hinh, sub_tss = \
			kwargs[
				'data_thread']
		show_log = cau_hinh.get('show_log')
		try:
			if self.list_run_fail[(row_number)]:
				return False, row_number, ''
		# raise ValueError
		except:
			pass
		file_strim = JOIN_PATH(folder_video, f"{ind_seq + 1}_strim.mp4")
		file_audio = JOIN_PATH(folder_audio, f"{ind_seq + 1}.wav")
		
		file_output = JOIN_PATH(folder_video, f"{ind_seq + 1}.mp4")
		
		# file_merge = JOIN_PATH(folder_video, f"{ind_seq}.mkv")
		file_start_temp = JOIN_PATH(folder_video, f"start_temp.mp4")
		file_start = JOIN_PATH(folder_video, f"start.mp4")
		list_commands = self.list_commands[(row_number)]
		list_video_output = self.list_video_output[(row_number)]
		
		try:
			
			if ind_seq == 0 and second_start > 0.3:
				
				if checkVideoOk(file_start) is False:
					ff_code = list_commands.get("start").format(video_path=video_path, second_start=second_start, file_start_temp=file_start_temp)
				else:
					ff_code = f'ffmpeg -version'
				self.manage_cmd.cmd_output(ff_code, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND + 'start',
					RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, logs=True, print=show_log, use_stop_thread=True, row_number=row_number)
				
				if list_commands.get('start_volume') is not None:
					ff_code = list_commands.get("start_volume").format(file_start_temp=file_start_temp, file_start=file_start)
					
					self.manage_cmd.cmd_output(ff_code, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND + 'start_volume',
						RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, logs=True, print=show_log, use_stop_thread=True, row_number=row_number)
				list_video_output = [file_start] + list_video_output
				
				if os.path.exists(file_start_temp):
					os.unlink(file_start_temp)
			
			# XỬ lý Cắt VIDEO
			# print(file_output)
			while True:
				if self.list_run_fail[(row_number)]:
					return False, row_number, ''
				if checkVideoOk(file_output) is False:
					# Cắt video
					ff_code = list_commands.get(f"strim").format(start_time=start_time, video_path=video_path, seconds_sub=seconds_sub, file_strim=file_strim)
				else:
					ff_code = f'ffmpeg -version'
				# print(ff_code)
				self.manage_cmd.cmd_output(ff_code, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND + f'_strim_{ind_seq + 1}',
					RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, logs=True, print=show_log, use_stop_thread=True, row_number=row_number)
				# print()
				if checkVideoOk(file_strim):
					break
				time.sleep(5)
			ff_code = ""
			
			if checkVideoOk(file_output) is False:
				# thêm voice vào video
				count_time = 0
				while True:
					if self.list_run_fail[(row_number)]:
						return False, row_number, ''
					# file_voice = JOIN_PATH(folder_audio, str(ind_seq) + ".wav")
					
					if os.path.exists(file_audio):
						try:
							duration_voice, bit_r = get_duaration_video(file_audio)
							if duration_voice > 0:
								if seconds_sub == 0:
									tempo = 0
									atempo_ = 0
								else:
									tempo = duration_voice / seconds_sub
									if tempo == 0:
										print("Không get được voice")
										self.manage_thread_pool.resultChanged.emit(STOP_GET_VOICE, STOP_GET_VOICE, row_number)
										self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", f"Dòng sub {ind_seq + 1} không get được voice", "warning")
										return False, row_number, ''
									
									atempo_ = tempo if mode_tts == 'v2' else 1 / tempo  # v2 Khớp với hình
								# atempo = f"atempo=1"
								#
								# if atempo_ < 0.5:
								# 	# atempo = f"atempo=1"
								# 	hs_tempo = 1
								# 	n = 0
								# 	for i in range(5):
								# 		hs_t = (atempo_ * 2) * hs_tempo
								# 		if hs_t >= 0.5:
								# 			n += 1
								# 			atempo = f"atempo={hs_t}{',atempo=0.5' * n}"
								# 			break
								# 		hs_tempo += 1
								atempo = f"atempo=1"
								if atempo_ < 0.5:
									# atempo = f"atempo=1"
									hs_tempo = 1
									# n = 1
									for i in range(5):
										hs_t = (atempo_ * 2) * hs_tempo
										# print(hs_t)
										if hs_t >= 0.5:
											atempo = f"atempo={hs_t}{',atempo=0.5' * hs_tempo}"
											break
										# n += 1
										hs_tempo += 1
								# atempo = f"atempo={atempo_ * 2},atempo=0.5"
								elif 4 >= atempo_ > 2:
									atempo = f"atempo={atempo_ / 2},atempo=2"
								else:
									atempo = f"atempo={atempo_}"
								
								# print(atempo)
								
								# if tempo > 4:
								# 	self.manage_thread_pool.resultChanged.emit(STOP_GET_VOICE, STOP_GET_VOICE, row_number)
								
								if tempo < 1:
									if mode_tts == 'v3':
										print(end_time_sub)
										print(duration_voice)
										tempo = end_time_sub / duration_voice
										atempo__ = 1 / tempo
										if atempo__ < 0.68:
											atempo = f"atempo=1"
										else:
											atempo = f"atempo={atempo__}"
										# atempo = f"atempo={atempo * 2},atempo=0.5"
										# elif 4 >= atempo__ > 2:
										# 	atempo = f"atempo={atempo__ / 2},atempo=2"
										# else:
										# 	atempo = f"atempo={atempo__}"
										# print(atempo)
										ff_code = list_commands.get(f"mix_<1").format(atempo=atempo, tempo=str(tempo), file_strim=file_strim, file_audio=file_audio, seconds_sub=seconds_sub, file_output=file_output, end_time=duration_voice)
									
									else:
										ff_code = list_commands.get(f"mix_<1").format(atempo=atempo, tempo=str(tempo), file_strim=file_strim, file_audio=file_audio, seconds_sub=seconds_sub,  end_time_sub=end_time_sub,file_output=file_output)
								else:
									ff_code = list_commands.get(f"mix_>=1").format(atempo=atempo, tempo=str(tempo), file_strim=file_strim, file_audio=file_audio, seconds_sub=seconds_sub, end_time_sub=duration_voice,file_output=file_output)
								# print(atempo)
								# print(ff_code)
								self.manage_cmd.cmd_output(ff_code, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND + f'_addsub_{ind_seq + 1}',
									RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, logs=True, print=show_log, row_number=row_number)
								
								if checkVideoOk(file_output):
									break
								else:
									time.sleep(5)
									
									print("Lỗi Ghép Video: ", file_output)
						
						except Exception as err:
							print(f"Lỗi Dòng SUb SỐ: {ind_seq + 1}", str(err))
					
					else:
						print("Đang đợi voice: ", ind_seq + 1)
						if count_time > 60 or self.list_tts_finished.get((row_number)):
							try:
								if self.getVoiceRowErorr:
									self.getVoiceRowErorr(cau_hinh, sub_tss, ind_seq, row_number, folder_audio)
							except:
								print("Không Get Được voice: ", ind_seq + 1)
					
					count_time += 1
					time.sleep(3)
			
			else:  # bo qua luôn
				ff_code = f'ffmpeg -version'
		# self.manage_cmd.cmd_output(ff_code, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND + f'_addsub_{ind_seq + 1}',
		# 	RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, logs=True, use_stop_thread=True, row_number=row_number)
		# không cần phải load tien trinh vì render mới up range
		# print()
		
		
		except:
			print("Lỗi render video: ", file_output)
		
		if self.list_run_fail[(row_number)]:
			return False, row_number, ''
		# vì thread limit ko bắt được sự kiện nên cần dùng cái này
		self.manage_thread_pool.resultChanged.emit(RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND,
			RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, (True, row_number, list_video_output))
		
		try:
			if os.path.exists(file_strim):
				os.unlink(file_strim)
		except:
			
			print("Lỗi xóa file: ", file_strim)
		# thread_pool.finishSingleThread(id_worker, limit_thread=True)
		return True, row_number, list_video_output
	
	def _resultChanged (self, id_worker, id_thread, result):
		
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
		
		if id_thread == RENDER_VIDEOPRE_FINISHED:
			
			row_number = result
			# self.list_count_state_render_tts[(row_number)] += 1
			
			# if self.list_count_state_render_tts[(row_number)] == 2:
			print("RENDER HOÀN THÀNH")
			file_video_input = self.list_video_output_render[(row_number)]
			folder_audio = self.list_folder_audio[(row_number)]
			folder_video = self.list_folder_video[(row_number)]
			data_sub = self.list_data_sub[(row_number)]
			data_sub_new = self.list_data_sub_new[(row_number)]
			cau_hinh = self.list_cau_hinh[(row_number)]
			
			duration_video_main, bit_rate = get_duaration_video(file_video_input)
			
			# self.thread_limit_tts_chunk = ManageThreadPool()
			# self.thread_limit_tts_chunk.setMaxThread(cau_hinh.get('so_luong_render'))
			if data_sub_new is not None:
				data_sub = data_sub_new
			# sequences = [sub[:2] for sub in data_sub]
			# print(sequences)
			data_req = {
				"cp": cr_pc(),
				"tc": TOOL_CODE_MAIN,
				't': int(float(time.time())),
				"cau_hinh": cau_hinh,
			}
			self.thread_limit_tts_chunk = ManageThreadPool()
			self.thread_limit_tts_chunk.setMaxThread(cau_hinh.get('so_luong_render'))
			
			user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
			
			headers = {"Authorization": f"Bearer {user_data['token']}"}
			
			paes = user_data['paes']
			data_encrypt = mh_ae(data_req, p_k=paes)
			
			res = self.request.post(url=URL_API_BASE + "/generate-code/private/render-list-split", json={
				"data": data_encrypt},
				headers=headers)
			if res.status_code == 200:
				data_res = gm_ae(res.json()["data"], paes)
				# list_video_output = data_res.get('list_video_output')
				self.list_commands[(row_number)] = data_res.get('list_commands')
				# list_seconds_sub = data_res.get('list_seconds_sub')
				
				self.list_total_chunks[(row_number)] = len(data_sub)
				self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
					UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
					{"row_number": row_number, "range": len(data_sub), "index_chunk": 3})
				
				# self.manage_thread_pool.resultChanged.emit(UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS,
				# 	UPDATE_PECENT_RANGE_TTS_CHUNK_TABLE_PROCESS,
				# 	{"row_number": row_number, "percent_range": 100})
				
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
					"Đang Ghép Voice Vào Video...")
				
				self.list_video_output[(row_number)] = []
				
				for ind_seq, sub in enumerate(data_sub):
					file_output = JOIN_PATH(folder_video, f"{ind_seq + 1}.mp4")
					self.list_video_output[(row_number)].append(file_output)
				
				# tạo 1 thread để kiem tra video nếu trong chunk thì render ra
				chunk_skip = 5
				lengt_sub = len(self.list_video_output[(row_number)])
				
				sec_start = data_sub[0][ColumnNumber.column_time.value].split(' --> ')[0]
				isHasStart = False
				if datetime_to_seconds(datetime.strptime(sec_start, "%H:%M:%S,%f")).total_seconds() > 0.3:
					isHasStart = True
				
				# if cau_hinh.get("mode_fast"):
				data = [x for x in range(0, lengt_sub)]
				chunks = [data[x:x + chunk_skip] for x in range(0, len(data), chunk_skip)]
				self.manage_thread_pool.start(self.fn_concat_video_chunks, Noi_Video_theo_chunk, Noi_Video_theo_chunk,
					data_thread=(chunks, folder_video, row_number, isHasStart, cau_hinh))
				
				for ind_seq, sub in enumerate(data_sub):
					start, end = sub[ColumnNumber.column_time.value].split(' --> ')
					second_start = datetime_to_seconds(datetime.strptime(start, "%H:%M:%S,%f")).total_seconds()
					
					# start = sub[1].split(' --> ')[0]
					
					start_time = datetime.strptime(start, "%H:%M:%S,%f")
					end_time = datetime.strptime(end, "%H:%M:%S,%f")
					
					if ind_seq < len(data_sub) - 1:
						start_sub_next = datetime.strptime(
							data_sub[ind_seq + 1][ColumnNumber.column_time.value].split(' --> ')[0], "%H:%M:%S,%f")
					else:
						dur_main_time = datetime.strptime(seconds_to_timestamp(duration_video_main, ","), "%H:%M:%S,%f")
						if (dur_main_time - end_time).total_seconds() > 1:
							start_sub_next = dur_main_time
						else:
							start_sub_next = end_time
					
					delta = start_sub_next - start_time
					delta_end = end_time - start_time
					# 00:29:36,266 --> 00:29:38,000
					seconds_sub = delta.total_seconds()
					print(f"Thời gian sub {ind_seq + 1}: {seconds_sub}")
					end_time_sub = delta_end.total_seconds()
					
					sub_tss = sub[ColumnNumber.column_sub_text.value]
					
					self.thread_limit_tts_chunk.start(self.func_r_v_l, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND, RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND,
						data_thread=(
							
							start_time.time().__str__(),
							
							file_video_input,
							cau_hinh["servers_tts"]["mode"], folder_audio, folder_video,
							row_number,
							# list_video_output,
							# list_commands, list_seconds_sub,
							ind_seq,
							second_start, seconds_sub, end_time_sub, cau_hinh, sub_tss))
			
			elif res.status_code == 423:  # tài khoản bị khóa
				
				self.manage_thread_pool.resultChanged.emit(RENDER_VIDEO_FFMPEG_TTS_CHUNK_ERROR,
					RENDER_VIDEO_FFMPEG_TTS_CHUNK_ERROR, (False, 423, row_number))
			
			else:
				print("Trạng thái lỗi: ", res.status_code)
				
				try:
					message = res.json().get("message")
				except:
					message = "Lỗi server"
				self.manage_thread_pool.resultChanged.emit(RENDER_VIDEO_FFMPEG_TTS_CHUNK_ERROR,
					RENDER_VIDEO_FFMPEG_TTS_CHUNK_ERROR, (False, message, row_number))
		
		if id_thread == RENDER_VIDEO_TTS_GHEP_VOICE_COMMAND:
			# print("Nối video")
			is_ok, row_number, list_video_output = result
			
			self.list_count_chunk_finished[(row_number)] += 1
			
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, json.dumps({
				"row_number": row_number, "index_chunk": 3}),
				self.list_count_chunk_finished[(row_number)])  # index_chunk 3 là ghép voice
			
			print("Tổng Sub: ",
				self.list_total_chunks[(row_number)], " Đã Render Được: ", self.list_count_chunk_finished[(row_number)])
			
			if self.list_count_chunk_finished[(row_number)] == self.list_total_chunks[(row_number)]:
				print("GHÉP SUB HOÀN THÀNH")
				self.list_concat_finished[(row_number)] = True
		# cau_hinh = self.list_cau_hinh[(row_number)]
		
		if id_thread == Noi_Video_theo_chunk:
			
			row_number, list_video_output = result
			if row_number is False and list_video_output == "STOP":
				return
			folder_video = self.list_folder_video[(row_number)]
			folder_audio = self.list_folder_audio[(row_number)]
			video_path = self.list_video_path[(row_number)]
			cau_hinh = self.list_cau_hinh[(row_number)]
			list_commands = self.list_commands[(row_number)]
			
			# total_chunks = self.list_total_chunks[(row_number)]
			
			for file in self.list_file_temp_media[(row_number)]:
				try:
					if os.path.exists(file):
						os.remove(file)
				except:
					continue
			
			file_list = JOIN_PATH(folder_video, "list.txt")
			
			name_video, ext = os.path.basename(video_path)[:-4], os.path.basename(video_path)[-4:]
			
			file_output_finished = JOIN_PATH(
				cau_hinh[
					'src_output'], name_video + f"-{cau_hinh['ten_hau_to_video']}" + f".{cau_hinh['dinh_dang_video']}")
			
			self.manage_thread_pool.resultChanged.emit(str(row_number),
				UPDATE_FILENAME_OUTPUT_RENDER, file_output_finished)
			
			'''Nối các voice vào video bằng file list'''
			# row_number, file_list, file_output_finished, folder_audio, folder_video, cau_hinh = res
			
			file_concat_video = JOIN_PATH(folder_video, f"file_concat_video.{cau_hinh['dinh_dang_video']}")
			
			range_time_ms = 0
			print("Chuẩn Bị Nối Video")
			self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
				"Chuẩn Bị Nối Video")
			count = 0
			ls_video_error = []
			ls_video_input = []
			
			# with open(file_list, 'w') as file:
			for file_video in list_video_output:
				# if file_video is not None:
				if os.path.exists(file_video):
					duration, bit_r = get_duaration_video(file_video)
					if duration == 0 and bit_r == 0:
						ls_video_error.append(file_video)
					# return PyMessageBox().show_error("Lỗi", f"Video {file_video} bị lỗi")
					else:
						count += 1
						# file.write(f"file '{file_video}'\n")
						range_time_ms += duration
						ls_video_input.append(file_video)
				else:
					ls_video_error.append(file_video)
					print("Video bị lỗi: ", file_video)
			print("Số lượng Video: ", count, len(list_video_output))
			if not count == len(list_video_output):
				text = "Đây Là Danh sách Video Bị Lỗi, Bạn Có Muốn Tiếp Tục Nối Những Video Còn Lại Hay Chỉnh Sửa Để Render Lại:\n\n"
				for video in ls_video_error:
					text += str(video) + "\n"
				
				dialog = PyDialogShowQuestion(text, 500, "Video lỗi")
				
				if dialog.exec():
					pass
				else:
					return
			
			self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
				UPDATE_RANGE_PROGRESS_TTS_CHUNK_TABLE_PROCESS,
				{"row_number": row_number, "range": range_time_ms * 2,
				 "index_chunk": 4})  # 4 là nối video
			
			# self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_PROCESS,
			# 	UPDATE_RANGE_PROGRESS_TABLE_PROCESS,
			# 	{"id_row": row_number, "range": range_time_ms})
			
			self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
				"Đang Nối Video")
			self.manage_thread_pool.start(self.func_concat_list, 'CONCAT_VIDEO_FILE_LIST1',
				'CONCAT_VIDEO_FILE_LIST1', data=(ls_video_input,
												 row_number, folder_video, folder_audio, file_concat_video,
												 file_output_finished,
												 cau_hinh, list_commands))
		
		# self.manage_thread_pool.start(self.fn_concat_video_chunks, 'CONCAT_VIDEO_FILE_LIST1',
		# 	'CONCAT_VIDEO_FILE_LIST1', data=(ls_video_input,
		# 									 row_number, chunks, folder_video, folder_audio, file_concat_video,
		# 									 file_output_finished,
		# 									 cau_hinh, list_commands))
		if id_thread == SMART_CUT_VIDEO_HAS_MUSIC:
			if result and isinstance(result, tuple):
				self.xu_ly_nhac_nen(*result)
	
	def fn_concat_video_chunks (self, **kwargs):
		(chunks, folder_video, row_number, isHasStart, cau_hinh) = kwargs.get('data_thread')
		list_video_output = self.list_video_output[(row_number)]
		
		file_start = JOIN_PATH(folder_video, f"start.mp4")
		
		list_video_chunk = []
		for index_chunk, chunk in enumerate(chunks):
			# print(chunk)
			inputs = []
			concat_ = ''
			file_output = JOIN_PATH(folder_video, f"chunk_{index_chunk}.mp4")
			
			# is_runing = True
			count = 0
			index_errr = []
			while True:
				if self.list_run_fail[(row_number)]:
					return False, "STOP"
				
				inputs = []
				concat_ = ''
				count = 0
				for ind, cnk in enumerate(chunk):
					# is_runing = True
					index_errr = []
					file_video = list_video_output[cnk]
					if os.path.exists(file_video):
						is_ok = checkVideoOk(file_video)
						if is_ok:
							count += 1
							
							inputs.append('-i')
							inputs.append(file_video)
							concat_ += f"[{ind}:v][{ind}:a]"
							continue
					index_errr.append(cnk + 1)
					if self.list_concat_finished.get((row_number)):
						print("Video ERROR:", file_video)
				if count == len(chunk):
					break
				# time.sleep(5)
				print(f"Chunk ERROR", index_chunk + 1, index_errr)
			if isHasStart and index_chunk == 0:
				inputs = inputs + ['-i', file_start]
				concat_ = f"[{count}:v][{count}:a]" + concat_
				count += 1
			# break
			concat_ += f"concat=n={count}:a=1:v=1[s0][s1]"
			
			ffcode = ["ffmpeg", '-hwaccel', 'auto']
			ffcode += inputs
			ffcode += ['-filter_complex']
			ffcode += [concat_]
			ffcode += ['-map', '[s0]', '-map', '[s1]']
			ffcode += ma_hoa_output_ffmpeg(cau_hinh).split(' ')
			ffcode += ['-y', file_output]
			
			self.manage_cmd.cmd_output(ffcode, 'CONCAT_VIDEO_FILE_CHUNKS', 'CONCAT_VIDEO_FILE_CHUNKS', logs=True)
			duration = 0
			if os.path.exists(file_output):
				list_video_chunk.append(file_output)
				duration, bit_r = get_duaration_video(file_output)
			
			# if cau_hinh.get("mode_fast", False):
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, json.dumps({
				"row_number": row_number, "index_chunk": 4}),  # 4 nối
				duration)
		return row_number, list_video_chunk
	
	def func_concat_list (self, **kwargs):
		ls_video_input, row_number, folder_video, folder_audio, file_concat_video, file_output_finished, cau_hinh, list_commands = kwargs.get('data')
		# print(ls_video_input)
		list_file_concat_chunk = []
		file_list = JOIN_PATH(folder_video, "list.txt")
		range_time_ms = 0
		with open(file_list, 'w') as file:
			for index_chunk, file_output in enumerate(ls_video_input):
				
				if os.path.exists(file_output):
					duration, bit_r = get_duaration_video(file_output)
					file.write(f"file '{file_output}'\n")
					range_time_ms += duration
		
		# ls_video_input.append(py_ffmpeg.input(file_video))
		
		ffcode = list_commands.get('concat').format(file_list=file_list, file_concat_video=file_concat_video).split('|')
		ffcode = ['ffmpeg'] + ffcode
		# print(ffcode)
		self.manage_cmd.cmd_output(ffcode, CONCAT_VIDEO_FILE_LIST, CONCAT_VIDEO_FILE_LIST, logs=True, folder_audio=folder_audio, folder_video=folder_video, file_output=file_output_finished, file_concat_video=file_concat_video, range_time_ms=range_time_ms, row_number=row_number, cau_hinh=cau_hinh)
	
	def _resultCMDSignal (self, id_worker, type_cmd, result, kwargs):
		
		if type_cmd == RENDER_VIDEO_FFMPEG_NO_TTS:
			video_path = id_worker
			
			if "file_srt_origin" in kwargs.keys():
				if os.path.exists(kwargs['file_srt_origin']) is True:
					os.remove(kwargs['file_srt_origin'])
			
			if "file_output" in kwargs.keys():
				if os.path.exists(kwargs["file_output"]) is True:  # id_worker là gủi cái dẫn của video
					self.manage_thread_pool.statusChanged.emit(str(kwargs['row_number']), UPDATE_STATUS_TABLE_PROCESS,
						"Hoàn Thành")
					self.manage_thread_pool.resultChanged.emit(str(
						kwargs['row_number']), RENDER_VIDEO_FFMPEG_NO_TTS_FINISHED, None)
					
					self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS, str(
						kwargs['row_number']), "")
					try:
						end_time = time.time()
						start_time = self.list_time_render[(kwargs['row_number'])]
						print("Thời gian thực thi là: ", seconds_to_timestamp(((
																					   end_time - start_time) * 10 ** 3) / 1000))
					except:
						pass
					play_media_preview(kwargs["file_output"], display=True)
		
		if type_cmd == RESULT_CMD_RENDER_VIDEO_PRE_TTS:
			
			if "file_srt_origin" in kwargs.keys():
				if os.path.exists(kwargs['file_srt_origin']) is True:
					os.remove(kwargs['file_srt_origin'])
			# print(result)
			if result is not False:
				if "file_output" in kwargs.keys():
					if checkVideoOk(kwargs["file_output"]):  # id_worker là gủi cái dẫn của video
						self.manage_thread_pool.resultChanged.emit(RENDER_VIDEOPRE_FINISHED, RENDER_VIDEOPRE_FINISHED,
							kwargs['row_number'])
						
						self.manage_thread_pool.resultChanged.emit(str(kwargs['row_number']), RENDER_VIDEO_FINISHED, "")
		
		if type_cmd == CONCAT_VIDEO_FILE_LIST:
			row_number = kwargs['row_number']
			cau_hinh = kwargs['cau_hinh']
			range_time_ms = kwargs['range_time_ms']
			file_concat_video = kwargs['file_concat_video']
			file_output = kwargs['file_output']
			folder_video = kwargs['folder_video']
			folder_audio = kwargs['folder_audio']
			list_commands = self.list_commands[(row_number)]
			
			# _____________________ XỬ LÝ THÊM NHẠC NỀN VÀ INTRO OUTRO TĂNG SPEED_________________
			
			if cau_hinh['them_nhac'] is True or (
					cau_hinh['tang_speed'] is True and not cau_hinh['toc_do_tang_speed'] == 1.0):
				
				if cau_hinh.get("smart_cut"):
					smart_cut_audio = cau_hinh.get('smart_cut_audio', 8)
					smart_cut_video = cau_hinh.get('smart_cut_video', 0)
					self.manage_thread_pool.start(self.fn_smart_cut, SMART_CUT_VIDEO_HAS_MUSIC, SMART_CUT_VIDEO_HAS_MUSIC, data=(
						file_output, smart_cut_audio, smart_cut_video, row_number), data_return=(
						cau_hinh, file_concat_video, range_time_ms, list_commands, row_number, folder_audio,
						folder_video))
				else:
					self.xu_ly_nhac_nen(file_output, cau_hinh, file_concat_video, range_time_ms, list_commands, row_number, folder_audio, folder_video)
			
			else:
				# 	ffmpeg_filter = ffmpeg_filter.strip(";")
				print(checkVideoOk(file_concat_video))
				if checkVideoOk(file_concat_video):
					try:
						if os.path.exists(file_output):
							os.unlink(file_output)
					except:
						print(f"Không thể xóa video cũ ở output")
					
					try:
						
						shutil.move(file_concat_video, fr'{file_output}')
					except:
						print(f"Không thể copy file tới output, bạn hãy copy tay video render hoàn thành:\n{file_concat_video}")
					
					# except:
					# 	print("Không thể xóa thư mục video và audio")
					print(checkVideoOk(file_output)
					)
					if checkVideoOk(file_output):
						if cau_hinh.get('delete_data_output'):
							# try:
							file_video_input = self.list_video_output_render[(row_number)]
							
							if os.path.exists(file_video_input) is True:
								os.unlink(file_video_input)
							file_srt_origin = self.list_file_srt_origin[(row_number)]
							if os.path.exists(file_srt_origin) is True:
								os.remove(file_srt_origin)
							
							remove_dir(folder_video)
							remove_dir(folder_audio)
						# print(cau_hinh)
						if cau_hinh.get("smart_cut"):
							smart_cut_audio = cau_hinh.get('smart_cut_audio', 8)
							smart_cut_video = cau_hinh.get('smart_cut_video', 0)
							self.manage_thread_pool.start(self.fn_smart_cut, SMART_CUT_VIDEO, SMART_CUT_VIDEO, data=(
								file_output, smart_cut_audio, smart_cut_video, row_number))
						
						else:
							self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS, str(row_number), "")
							self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
								"Hoàn Thành")
							self.manage_thread_pool.resultChanged.emit(str(row_number),
								RENDER_VIDEO_FFMPEG_FINISHED_V1, None)
							try:
								end_time = time.time()
								start_time = self.list_time_render[(kwargs['row_number'])]
								print("Thời gian thực thi là: ", seconds_to_timestamp(((
																							   end_time - start_time) * 10 ** 3) / 1000))
							except:
								pass
		# play_media_preview(file_output, display=True)
		
		if type_cmd == CONCAT_VIDEO_FINAL:
			row_number = kwargs['row_number']
			range_time_ms = kwargs['range_time_ms']
			folder_video = kwargs['folder_video']
			file_output = kwargs['file_output']
			folder_audio = kwargs['folder_audio']
			
			cau_hinh = self.list_cau_hinh[(row_number)]
			
			# except:
			# 	pass
			print(checkVideoOk(file_output))
			
			if checkVideoOk(file_output):
				if cau_hinh.get('delete_data_output'):
					# try:
					file_video_input = self.list_video_output_render[(row_number)]
					
					if os.path.exists(file_video_input) is True:
						os.unlink(file_video_input)
					
					file_srt_origin = self.list_file_srt_origin[(row_number)]
					if os.path.exists(file_srt_origin) is True:
						os.unlink(file_srt_origin)
					remove_dir(folder_video)
					remove_dir(folder_audio)
				
				# if os.path.exists(kwargs["file_output"]) is True:  # id_worker là gủi cái dẫn của video
				self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS, str(row_number), "")
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
					"Hoàn Thành")
				self.manage_thread_pool.resultChanged.emit(str(row_number),
					RENDER_VIDEO_FFMPEG_FINISHED_V1, None)
				try:
					end_time = time.time()
					start_time = self.list_time_render[(kwargs['row_number'])]
					print("Thời gian thực thi là: ", seconds_to_timestamp(((
																				   end_time - start_time) * 10 ** 3) / 1000))
				except:
					pass
		
		if type_cmd == CMD_SMART_CUT_VIDEO:
			video_ouput = kwargs.get("video_ouput")
			row_number = kwargs.get("row_number")
			
			if checkVideoOk(video_ouput):
				self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_FINISHED_TABLE_PROCESS, str(row_number), "")
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
					"Hoàn Thành")
				self.manage_thread_pool.resultChanged.emit(str(row_number),
					RENDER_VIDEO_FFMPEG_FINISHED_V1, None)
				try:
					end_time = time.time()
					start_time = self.list_time_render[(kwargs['row_number'])]
					print("Thời gian thực thi là: ", seconds_to_timestamp(((
																				   end_time - start_time) * 10 ** 3) / 1000))
				except:
					pass
	
	# play_media_preview(kwargs["file_output"], display=True)
	
	def fn_smart_cut (self, **kwargs):
		
		file_output, smart_cut_audio, smart_cut_video, row_number = kwargs.get('data')
		file_output_cut = file_output[:-4] + "_smart_cut" + file_output[-4:]
		
		if smart_cut_audio == 0 and smart_cut_video == 0:
			return
		edit_based_on = f'(or audio:{smart_cut_audio}% motion:{smart_cut_video}%)'
		
		if smart_cut_audio == 0:
			edit_based_on = f'motion:{smart_cut_video}%'
		if smart_cut_video == 0:
			edit_based_on = f'audio:{smart_cut_audio}%'
		# print(edit_based_on)
		
		try:
			if self.list_run_fail[(row_number)]:
				return False
		except:
			pass
		# # print(path_tool)cwd="/"
		user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		# print(mh_ae({"cp":cr_pc(),"tc":TOOL_CODE_AUTOSUB,'t': int(float(time.time()))}))
		cmd = f'"{PATH_FFCUT}"  -v "{file_output}" -e "{edit_based_on}"  -a {URL_API_BASE} -t {user_data.get("token")} -c {mh_ae_w({"cp": cr_pc("tool_code"), "tc": TOOL_CODE_MAIN, "t": int(float(time.time()))})}'
		# print(cmd)
		self.manage_thread_pool.resultChanged.emit(RESET_VALUE_PROGRESS_TABLE_PROCESS, RESET_VALUE_PROGRESS_TABLE_PROCESS, row_number)
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
			"Chuẩn Bị Cắt Thông Minh")
		self.manage_cmd.cmd_output(cmd, CMD_SMART_CUT_VIDEO, CMD_SMART_CUT_VIDEO, print=False, video_ouput=file_output_cut, row_number=row_number)
		if checkVideoOk(file_output_cut):
			return file_output_cut, *kwargs.get('data_return', ())
	
	def xu_ly_nhac_nen (self, file_output, cau_hinh, file_concat_video, range_time_ms, list_commands, row_number, folder_audio, folder_video):
		''' Xử lý Nhạc Nền '''
		ffmpeg = ffmpeg_check()
		
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
		
		ffcode = list_commands.get("music").format(video_input=file_concat_video, file_music=file_music, file_output=file_output).split('|')
		
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_PROCESS,
			"Đang Xử Lý Nhạc Và Speed...")
		
		# self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_PROCESS, str(row_number), 0)
		self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS,
			UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS,
			{"id_row": row_number, "range": range_time_ms})
		# print(' '.join(ffcode))
		if os.path.exists(file_output):
			os.unlink(file_output)
		
		self.manage_cmd.execute(ffmpeg, ffcode, CONCAT_VIDEO_FINAL, CONCAT_VIDEO_FINAL, logs=True, folder_audio=folder_audio, folder_video=folder_video, row_number=row_number, file_output=file_output, range_time_ms=range_time_ms)


# smart_cut(file_output,file_output_cut, edit_based_on)


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
