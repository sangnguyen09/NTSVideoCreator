import json
import random
import re
import subprocess
import uuid
from datetime import timedelta, datetime
from typing import Union

from PySide6.QtCore import (
	QProcess,
	Signal, QObject,
)

from gui.helpers.constants import RENDER_VIDEO_FFMPEG_NO_TTS, RUN_CMD_AISUB, RUN_CMD_DETECT_SUB, \
	RESULT_CMD_RENDER_VIDEO_PRE_TTS, FIT_VIDEO_MATCH_VOICE, DETECT_LANGUAGE_AISUB, UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	ADD_VOICE_TO_VIDEO_CHUNK, RUN_CMD_DETECT_SUB_DEMO, CONCAT_VIDEO_FINAL, CONCAT_VIDEO_FILE_LIST, \
	RENDER_VIDEO_FFMPEG_TTS_CHUNK, UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, STOP_GET_VOICE, CMD_SMART_CUT_VIDEO, \
	UPDATE_STATUS_TABLE_RENDER, UPDATE_RANGE_PROGRESS_TABLE_PROCESS_ADD_PLUS, UPDATE_RANGE_PROGRESS_TABLE_PROCESS, \
	RENDER_VIDEO_HAU_CAN_FFMPEG
from gui.helpers.custom_logger import customFfmpegLogger

STATES = {
	QProcess.ProcessState.NotRunning: "Not running",
	QProcess.ProcessState.Starting: "Starting...",
	QProcess.ProcessState.Running: "Running...",
}
DEFAULT_STATE = {"progress": 0, "status": QProcess.ProcessState.Starting}

TIME_REGEX = re.compile(
	r"time=(?P<hour>\d{2}):(?P<min>\d{2}):(?P<sec>\d{2})\.(?P<ms>\d{2})"
)
PROGRESS_AISUB = re.compile("(\d+)%.+(\d+)/(\d+)", re.M)

DETECT_LANGUAGE_AI = re.compile(r"Detected language: (.+)", re.M)

DETECT_TEXT_DEMO = re.compile(r"Text Demo: (.+)", re.M)

SPEED_FFMPEG = re.compile(r"speed=(.+)", re.M)

PROGRESS_DOWLOAD_MODEL_AI = re.compile(r"(\d+)%.+\/(\d\.?\d+G|\d\.?\d+M)", re.M)
PROGRESS_DETECTSUB = re.compile(r"Progress (\d+)%", re.M)

PROGRESS_FFCUT = re.compile(r"(.*?)(\d+.\d)%.+\s(\d+:\d+\s?..)", re.M)


def progessFFcut (output):
	m = PROGRESS_FFCUT.match(output)
	if m:
		# print(m.groups())
		
		pc_complete = m.group(1)
		status = ''
		for it in pc_complete.split(" "):
			if it.replace('⏳',"").isalpha():
				status += it.replace('⏳',"") + " "
		progress = m.group(2)
		time_new = m.group(3)
		return status, progress, time_new


def progessSpeedFfmpeg (output):
	"""
	Matches lines using the progress_re regex,
	returning a single integer for the % progress.
	"""
	progress_time = SPEED_FFMPEG.search(output)
	
	if progress_time:
		return progress_time.group(1)


def progessPercentFfmpeg (output):
	"""
	Matches lines using the progress_re regex,
	returning a single integer for the % progress.
	"""
	progress_time = TIME_REGEX.search(output)
	
	if progress_time:
		elapsed_time = to_ms(**progress_time.groupdict())
		return int(elapsed_time)


def progessTimeFfmpeg (output):
	"""
	Matches lines using the progress_re regex,
	returning a single integer for the % progress.
	"""
	progress_time = TIME_REGEX.search(output)
	
	if progress_time:
		return to_timetemp(**progress_time.groupdict())


def progessPercentAISUB (output):
	"""
	Matches lines using the progress_re regex,
	returning a single integer for the % progress.
	"""
	m = PROGRESS_AISUB.search(output)
	if m:
		pc_complete = m.group(1)
		return int(pc_complete)


def progessPercenDowloadModelAI (output):
	m = PROGRESS_DOWLOAD_MODEL_AI.search(output)
	if m:
		return int(m.group(1)), m.group(2)  # m.group(3)  # dung lượng
	return None, None


def detectLanguageAI (output):
	m = DETECT_LANGUAGE_AI.search(output)
	if m:
		return m.group(1)


def detectTextDemo (output):
	m = DETECT_TEXT_DEMO.search(output)
	if m:
		return m.group(1)


def progessPercentDetectSub (output):
	"""
	Matches lines using the progress_re regex,
	returning a single integer for the % progress.
	"""
	m = PROGRESS_DETECTSUB.search(output)
	if m:
		pc_complete = m.group(1)
		return int(pc_complete)


def to_ms (**kwargs: Union[float, int, str]) -> int:
	hour = int(kwargs.get("hour", 0))
	minute = int(kwargs.get("min", 0))
	sec = int(kwargs.get("sec", 0))
	# ms = int(kwargs.get("ms", 0))
	
	return (hour * 60 * 60) + (minute * 60) + sec


def to_timetemp (**kwargs: Union[float, int, str]) -> str:
	hour = int(kwargs.get("hour", 0))
	minute = int(kwargs.get("min", 0))
	sec = int(kwargs.get("sec", 0))
	# ms = int(kwargs.get("ms", 0))
	td = timedelta(seconds=(hour * 60 * 60) + (minute * 60) + sec)
	ms = td.microseconds // 1000
	m, s = divmod(td.seconds, 60)
	h, m = divmod(m, 60)
	return '{:02d}:{:02d}:{:02d}{}{:03d}'.format(h, m, s, '.', ms)


# return f"{(hour * 60 * 60)}:{(minute * 60)}:{sec}"


class ManageCMD(QObject):
	_jobs = {}
	_state = {}
	
	statusSignal = Signal(str, str, str)  # type,id, status
	readErrorSignal = Signal(str, str, object)  # type,id, object
	readOutputSignal = Signal(str, str, object)  # type,id, object
	resultSignal = Signal(str, str, object, dict)  # type,id, object
	progressSignal = Signal(str, str, int, dict)
	
	def __init__ (self, manage_thread_pool):
		super().__init__()
		self.list_output_stdout = {}
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self._resultChanged)
		
		self.list_stop_thread = {}
		self.list_thread = {}
		self.list_status_smart_cut = {}
	
	def _resultChanged (self, id_worker, id_thread, result):
		
		if id_thread == STOP_GET_VOICE:
			# print(result)
			row_number = result
			self.list_stop_thread[(row_number)] = True
			if self.list_thread[(row_number)]:
				try:
					self.list_thread[(row_number)].kill()
					self.list_thread[(row_number)].terminate()
				except:
					pass
	
	def cmd_output (self, command, id_worker, type_cmd, **kwargs):
		"""hàm này nó sẽ không chạy trong 1 thread khác dùng để lấy được tín hiện trả về thread chính"""
		# print(" ".join(command))
		# print(command)
		self.list_output_stdout[str(id_worker)] = []
		
		process = subprocess.Popen(
			command,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			shell=True,
			creationflags=0x08000000,
			encoding='utf-8',
			errors='replace'
		)
		is_loaded = False
		output_std = ''
		if type_cmd == RESULT_CMD_RENDER_VIDEO_PRE_TTS:
			self.list_thread[(kwargs.get("row_number"))] = process
		
		while True:
			# if kwargs.get('fn_check_stop'):
			# 	print("dds")
			# 	if kwargs.get('fn_check_stop')():
			# 		print("stoppp")
			# 		return
			
			realtime_output = process.stdout.readline()
			if realtime_output == '' and process.poll() is not None:
				break
			if kwargs.get('use_stop_thread'):
				# try:
				stop = self.list_stop_thread.get((kwargs.get("row_number")))
				if stop:
					# process()
					process.kill()
					process.terminate()
					# del self.list_output_stdout[str(id_worker)]
					self.resultSignal.emit(id_worker, type_cmd, False, kwargs)
					return False
			# break
			# except:
			# 	pass
			
			if realtime_output:
				output_std = realtime_output.strip()
				# print(realtime_output.strip())
				# if not realtime_output.strip() == '' and kwargs.get("detect_sub"):
				# 	print(realtime_output.strip())
				# try:
				# print(self.list_output_stdout.keys())
				# self.list_output_stdout[str(id_worker)].append(realtime_output.strip())
				# except:
				# 	print("Không thêm đươc vào màng ffmpeg render")
				info = ""
				
				pro_time = progessTimeFfmpeg(realtime_output.strip())
				if pro_time:
					info += "Time: " + pro_time
				
				speed = progessSpeedFfmpeg(realtime_output.strip())
				if speed:
					info += " - Speed: " + speed
				if not info == '' and kwargs.get("logs"):
					# print(info)
					print(info)
				# pass
				if kwargs.get('print'):
					print(realtime_output.strip())
				
				if type_cmd == CMD_SMART_CUT_VIDEO:
					result = progessFFcut(realtime_output.strip())
					if result and len(result) == 3:
						row_number = kwargs.get("row_number")
						status, progress, time_new = result
						if status != self.list_status_smart_cut.get((row_number)):
							self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_PROCESS,
								UPDATE_RANGE_PROGRESS_TABLE_PROCESS,
								{"id_row": row_number, "range": 100})
							self.list_status_smart_cut[(row_number)] = status
						self.manage_thread_pool.resultChanged.emit(UPDATE_STATUS_TABLE_RENDER, UPDATE_STATUS_TABLE_RENDER, (
							row_number, status, progress, time_new))
				
				if type_cmd == RUN_CMD_DETECT_SUB_DEMO:
					text_demo = detectTextDemo(realtime_output.strip())
					# print(text_demo)
					if text_demo:
						text_demo = text_demo.replace("\x1b[0m", "").replace("\n", "")
						text_demo = text_demo[:1].upper() + text_demo[1:]
						return self.resultSignal.emit(id_worker, type_cmd, [text_demo], kwargs)
				
				if type_cmd == RUN_CMD_DETECT_SUB:
					progress = progessPercentDetectSub(realtime_output.strip())
					if progress:
						self.progressSignal.emit(id_worker, type_cmd, progress, kwargs)
					
					progress_D, size = progessPercenDowloadModelAI(realtime_output.strip())
					if progress_D:
						if is_loaded is False:
							self.manage_thread_pool.statusChanged.emit(str(kwargs.get("row_number")), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
								f"Đang tải mô hình ngôn ngữ (chỉ tải 1 lần, cần {size} dung lượng ổ C)")
							self.progressSignal.emit(id_worker, type_cmd, 0, kwargs)
						
						is_loaded = True
						self.progressSignal.emit(id_worker, type_cmd, progress_D, kwargs)
					elif progress_D == 100:
						self.progressSignal.emit(id_worker, type_cmd, 0, kwargs)
						self.manage_thread_pool.statusChanged.emit(str(kwargs.get("row_number")), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
							"Đang trích xuất...")
					else:
						if is_loaded is False:
							self.manage_thread_pool.statusChanged.emit(str(kwargs.get("row_number")), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
								"Đang trích xuất...")
						is_loaded = True
				
				if type_cmd == RUN_CMD_AISUB:
					
					dt_lang = detectLanguageAI(realtime_output.strip())
					
					if dt_lang:
						self.manage_thread_pool.statusChanged.emit(str(kwargs.get("row_number")), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
							"Đang trích xuất...")
						dt_lang = dt_lang[:1].upper() + dt_lang[1:]
						self.manage_thread_pool.resultChanged.emit(str(kwargs.get("row_number")), DETECT_LANGUAGE_AISUB, dt_lang)
					
					progress_D, size = progessPercenDowloadModelAI(realtime_output.strip())
					if progress_D:
						if is_loaded is False:
							self.manage_thread_pool.statusChanged.emit(str(kwargs.get("row_number")), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
								f"Đang tải mô hình AI (chỉ tải 1 lần, cần {size} dung lượng ổ C)")
							self.progressSignal.emit(id_worker, type_cmd, 0, kwargs)
						
						is_loaded = True
						self.progressSignal.emit(id_worker, type_cmd, progress_D, kwargs)
					
					progress = progessPercentAISUB(realtime_output.strip())
					if progress:
						self.progressSignal.emit(id_worker, type_cmd, progress, kwargs)
				
				if type_cmd == RENDER_VIDEO_FFMPEG_NO_TTS:
					progress_time = progessPercentFfmpeg(realtime_output.strip())
					if progress_time:
						self.progressSignal.emit(id_worker, type_cmd, progress_time, kwargs)
				
				# if type_cmd == RESULT_CMD_RENDER_VIDEO_PRE_TTS:
				# 	progress_time = progessPercentFfmpeg(realtime_output.strip())
				# 	if progress_time:
				# 		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, json.dumps({
				# 			"row_number": kwargs.get("row_number"), "index_chunk": 0}),
				# 			progress_time)
				# self.progressSignal.emit(id_worker, type_cmd, progress_time, kwargs)
				
				if type_cmd == FIT_VIDEO_MATCH_VOICE:
					progress_time = progessPercentFfmpeg(realtime_output.strip())
					if progress_time:
						self.progressSignal.emit(id_worker, type_cmd, progress_time, kwargs)
				
				# if type_cmd == RENDER_VIDEO_FFMPEG_TTS_CHUNK:
				# 	progress_time = progessPercentFfmpeg(realtime_output.strip())
				# 	if progress_time:
				# 		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, json.dumps({
				# 			"row_number": kwargs.get("row_number"), "index_chunk": kwargs.get("index_chunk") + 1}),
				# 			progress_time)


				if type_cmd == CONCAT_VIDEO_FILE_LIST:
					progress_time = progessPercentFfmpeg(realtime_output.strip())
					if progress_time:
						self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, json.dumps({
							"row_number": kwargs.get("row_number"), "index_chunk": 2}),  # 2 là ghép nối
							progress_time)

				if type_cmd == CONCAT_VIDEO_FINAL:
					progress_time = progessPercentFfmpeg(realtime_output.strip())
					# print(progress_time)
					if progress_time:
						self.progressSignal.emit(id_worker, type_cmd, progress_time, kwargs)

				if type_cmd == RENDER_VIDEO_HAU_CAN_FFMPEG:
					progress_time = progessPercentFfmpeg(realtime_output.strip())
					# print(progress_time)
					if progress_time:
						self.progressSignal.emit(id_worker, type_cmd, progress_time, kwargs)
		try:
			process.kill()
			process.terminate()
		except:
			pass
		
		try:
			if self.list_thread[(kwargs.get("row_number"))]:
				del self.list_thread[(kwargs.get("row_number"))]
		except:
			pass
		
		# try:
		# 	if kwargs.get("logs"):
		# 		now = datetime.now().__str__().replace(':', '-')
		# 		content = self.list_output_stdout[str(id_worker)]
		# 		if len(content) > 2:
		# 			# mid = int(len(content) / 3)
		# 			# byte1 = content[mid:]
		# 			name = now + str(random.randrange(1000, 100000))  + str(type_cmd)
		# 			# print(name)
		# 			customFfmpegLogger(name).info(content[-2:])
		#
		# 			# chạy xong
		# except:
		# 	print("Không lưu được file log")
		
		# self.resultSignal.emit(id_worker, type_cmd, output_std, kwargs)
		
		self.resultSignal.emit(id_worker, type_cmd, output_std, kwargs)
		# try:
		# 	del self.list_output_stdout[str(id_worker)]
		# except:
		# 	pass
		return True
	
	
	def execute (self, command, arguments: list, id_worker, type_cmd, **kwargs):
		"""
		#hàm này nó sẽ chạy trong 1 thread khác nên sẽ không lấy lấy được tín hiện trả về khi nó được gọi trong thread khác
		"""
		job_id = uuid.uuid4().hex
		
		# if manage_thread_pool is not None:
		# ffmpeg -f concat -safe 0 -i E:\Project\Python\ReviewPhim\video\fb8218f298802d111378e51da1e300e454689b3fb5494a8cdbae3b8d370de7b2\list.txt -c:v copy -movflags +faststart -y E:\Project\Python\ReviewPhim\video\fb8218f298802d111378e51da1e300e454689b3fb5494a8cdbae3b8d370de7b2\file_concat_video.mp4
		#
		# list_args = []
		# for arg in arguments:
		# 	list_args.append(arg.strip(";")) -c:v copy
		#
		# arguments = list_args
		# print(" ".join(arguments))
		
		#
		def fwd_signal (target):
			return lambda *args: target(id_worker, type_cmd, job_id, kwargs, *args)
		
		# Set default status to waiting, 0 progress.
		self._state[job_id] = DEFAULT_STATE.copy()
		
		p = QProcess()
		p.readyReadStandardOutput.connect(
			fwd_signal(self.handle_output)
		)
		p.readyReadStandardError.connect(fwd_signal(self.handle_output))
		p.stateChanged.connect(fwd_signal(self.handle_state))
		p.finished.connect(fwd_signal(self.done))
		
		self._jobs[job_id] = p
		# print(111)
		self.list_output_stdout[str(id_worker)] = []
		p.start(command, arguments)
	
	def handle_output (self, id_worker, type_cmd, job_id, kwargs):
		p = self._jobs[job_id]
		stderr = bytes(p.readAllStandardError()).decode("utf8")
		stdout = bytes(p.readAllStandardOutput()).decode("utf8")
		output = stderr + stdout
		# print(output)
		self.list_output_stdout[str(id_worker)].append(output)
		
		info = ""
		
		pro_time = progessTimeFfmpeg(output.strip())
		if pro_time:
			info += "Time: " + pro_time
		
		speed = progessSpeedFfmpeg(output.strip())
		if speed:
			info += " - Speed: " + speed
		
		if not info == '' and kwargs.get("logs"):
			print(info)
		
		if type_cmd == RENDER_VIDEO_FFMPEG_NO_TTS:
			progress_time = progessPercentFfmpeg(output)
			if progress_time:
				self.progressSignal.emit(id_worker, type_cmd, progress_time, kwargs)
		
		if type_cmd == FIT_VIDEO_MATCH_VOICE:
			progress_time = progessPercentFfmpeg(output)
			if progress_time:
				self.progressSignal.emit(id_worker, type_cmd, progress_time, kwargs)
		

		
		if type_cmd == ADD_VOICE_TO_VIDEO_CHUNK:
			progress_time = progessPercentFfmpeg(output)
			if progress_time:
				self.manage_thread_pool.resultChanged.emit(id_worker, type_cmd, {
					"row_number": kwargs.get("row_number"),
					"progress_time": progress_time,
					"index_chunk": kwargs.get("index_chunk")})
		
		# if type_cmd == RENDER_VIDEO_FFMPEG_TTS_CHUNK:
		# 	progress_time = progessPercentFfmpeg(output)
		#
		# 	if progress_time:
		# 		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TTS_CHUNK_TABLE_PROCESS, json.dumps({
		# 			"row_number": kwargs.get("row_number"), "index_chunk": kwargs.get("index_chunk") + 1}),
		# 			progress_time)
	
	def handle_state (self, id_worker, type_cmd, job_id, kwargs, state, *args):
		# print(state)
		self._state[job_id]["status"] = state
	
	def done (self, id_worker, type_cmd, job_id, kwargs, *args):
		"""Sau khi chạy xong thì push output ra ngoài thay vì đọc từng dòng như signal"""
		# p = self._jobs[job_id]
		# kwargs['output'] = kwargs
		# self.manage_thread_pool.resultChanged.emit(id_worker,type_cmd,kwargs)
		self.resultSignal.emit(id_worker, type_cmd, self.list_output_stdout[str(id_worker)], kwargs)
		del self._jobs[job_id]
		
		if kwargs.get("logs"):
			now = datetime.now().__str__().replace(':', '-')
			content = self.list_output_stdout[str(id_worker)]
			if len(content) > 2:
				# mid = int(len(content) / 3)
				# byte1 = content[mid:]
				# print(now)
				name = now + str(random.randrange(1000, 100000)) + str(type_cmd)
				# print(name)
				customFfmpegLogger(name).info(content[-2:])
				customFfmpegLogger(now).info(content[-1])
		
		del self.list_output_stdout[str(id_worker)]
	
	def cleanup (self):
		"""
		Remove any complete/failed workers from worker_state.
		"""
		for job_id, s in list(self._state.items()):
			if s["status"] == QProcess.NotRunning:
				del self._state[job_id]


# if __name__ == "__main__":
# print(check_cuda_version())
