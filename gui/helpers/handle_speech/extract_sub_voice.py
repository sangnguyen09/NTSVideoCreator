# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import audioop
import json
import math
import os
import re
import subprocess
import tempfile
import time
import uuid
import wave
from typing import TextIO

from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter

from gui.helpers.custom_logger import decorator_try_except_class
from gui.helpers.ect import cr_pc
from gui.helpers.func_helper import which
from gui.helpers.handle_speech.speech_to_text import GoogleSpeechToText, GladiaSpeechToText
# from gui.helpers.server import CachLaySubYoutubeEnum
from gui.helpers.thread import ManageThreadPool, ManageCMD
from gui.helpers.constants import UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS, UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, PATH_TEMP, FILE_FFSUB, \
	RUN_CMD_AISUB, EXTRACT_SUB_FINISHED, JOIN_PATH, \
	EXTRACT_SUB_SPEECH_TO_TEXT, EXTRACT_SUB_YOUTUBE_BY_GOOGLE
from gui.helpers.translatepy.utils.request import Request
from gui.helpers.get_data import URL_API_BASE
try:
	from json.decoder import JSONDecodeError
except ImportError:
	JSONDecodeError = ValueError

import pysrt
import six

GOOGLE_SPEECH_API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
GOOGLE_SPEECH_API_URL = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang={lang}&key={key}"  # pylint: disable=line-too-long


def srt_formatter (subtitles, padding_before=0, padding_after=0):
	"""
	Serialize a list of subtitles according to the SRT format, with optional time padding.
	"""
	sub_rip_file = pysrt.SubRipFile()
	
	for i, ((start, end), text) in enumerate(subtitles, start=1):
		item = pysrt.SubRipItem()
		item.index = i
		item.text = six.text_type(text)
		item.start.seconds = max(0, start - padding_before)
		item.end.seconds = end + padding_after
		sub_rip_file.append(item)
	return '\n'.join(six.text_type(item) for item in sub_rip_file)


def vtt_formatter (subtitles, padding_before=0, padding_after=0):
	"""
	Serialize a list of subtitles according to the VTT format, with optional time padding.
	"""
	text = srt_formatter(subtitles, padding_before, padding_after)
	text = 'WEBVTT\n\n' + text.replace(',', '.')
	return text


def json_formatter (subtitles):
	"""
	Serialize a list of subtitles as a JSON blob.
	"""
	subtitle_dicts = [
		{
			'start': start,
			'end': end,
			'content': text,
		}
		for ((start, end), text)
		in subtitles
	]
	return json.dumps(subtitle_dicts)


def raw_formatter (subtitles):
	"""
	Serialize a list of subtitles as a newline-delimited string.
	"""
	return ' '.join(text for (_rng, text) in subtitles)


FORMATTERS = {
	'srt': srt_formatter,
	'vtt': vtt_formatter,
	'json': json_formatter,
	'raw': raw_formatter,
}

DEFAULT_SUBTITLE_FORMAT = 'srt'
DEFAULT_CONCURRENCY = 10
DEFAULT_SRC_LANGUAGE = 'en'


def percentile (arr, percent):
	arr = sorted(arr)
	k = (len(arr) - 1) * percent
	f = math.floor(k)
	c = math.ceil(k)
	if f == c: return arr[int(k)]
	d0 = arr[int(f)] * (c - k)
	d1 = arr[int(c)] * (k - f)
	return d0 + d1


def is_same_language (lang1, lang2):
	return lang1.split("-")[0] == lang2.split("-")[0]


def get_folder_music_temp (row_number):
	path = JOIN_PATH(PATH_TEMP, "flac-" + str(row_number))
	if not os.path.exists(path):
		os.mkdir(path)
	return path


def remove_folder_music_temp (row_number):
	path = JOIN_PATH(PATH_TEMP, "flac-" + str(row_number))
	if os.path.isdir(path):
		if os.name == 'nt':
			subprocess.check_output(['cmd', '/C', 'rmdir', '/S', '/Q', path])
		else:
			subprocess.check_output(['rm', '-rf', path])


def ffmpeg_check ():
	"""
	Return the ffmpeg executable name. "None" returned when no executable exists.
	"""
	if which("ffmpeg"):
		return "ffmpeg"
	if which("ffmpeg.exe"):
		return "ffmpeg.exe"
	return None


def extract_audio (filename, channels=1, rate=16000):
	temp = tempfile.NamedTemporaryFile(dir=PATH_TEMP, suffix='.wav', delete=False)
	if not os.path.isfile(filename):
		raise Exception("Invalid filepath: {0}".format(filename))
	if not ffmpeg_check():
		raise Exception("Dependency not found: ffmpeg")
	command = ["ffmpeg", "-y", "-i", filename, "-ac", str(channels), "-ar", str(rate), "-loglevel", "error", temp.name]
	subprocess.check_output(command, stdin=open(os.devnull), creationflags=0x08000000)
	return temp.name, rate


# def find_speech_regions(filename, frame_width=4096, min_region_size=0.5, max_region_size=6):
def find_speech_regions (filename, frame_width=4096, min_region_size=0.3, max_region_size=8):
	reader = wave.open(filename)
	sample_width = reader.getsampwidth()
	rate = reader.getframerate()
	n_channels = reader.getnchannels()
	
	total_duration = reader.getnframes() / rate
	chunk_duration = float(frame_width) / rate
	
	n_chunks = int(total_duration / chunk_duration)
	energies = []
	
	for i in range(n_chunks):
		chunk = reader.readframes(frame_width)
		energies.append(audioop.rms(chunk, sample_width * n_channels))
	
	threshold = percentile(energies, 0.2)
	
	elapsed_time = 0
	
	regions = []
	region_start = None
	
	for energy in energies:
		is_silence = energy <= threshold
		max_exceeded = region_start and elapsed_time - region_start >= max_region_size
		
		if (max_exceeded or is_silence) and region_start:
			if elapsed_time - region_start >= min_region_size:
				regions.append((region_start, elapsed_time))
				region_start = None
		
		elif (not region_start) and (not is_silence):
			region_start = elapsed_time
		elapsed_time += chunk_duration
	return regions


def CountEntries (subtitle_file):
	e = 0
	with open(subtitle_file, 'r', encoding='utf-8') as srt:
		while True:
			e += 1
			# read lines in order
			number_in_sequence = srt.readline()
			timecode = srt.readline()
			# whether it's the end of the file.
			if not number_in_sequence:
				break
			# put all subtitles seperated by newline into a list.
			subtitles = []
			while True:
				subtitle = srt.readline()
				# whether it's the end of a entry.
				if subtitle == '\n':
					break
				subtitles.append(subtitle)
	total_entries = e - 1
	# print('Total Entries', total_entries)
	return total_entries


def entries_generator (subtitle_file):
	"""Generate a entries queue.

	input:
		subtitle_file: The original filename. [*.srt]

	output:
		entries: A queue generator.
	"""
	with open(subtitle_file, 'r', encoding='utf-8') as srt:
		while True:
			# read lines in order
			number_in_sequence = srt.readline()
			timecode = srt.readline()
			# whether it's the end of the file.
			if not number_in_sequence:
				break
			# put all subtitles seperated by newline into a list.
			subtitles = []
			while True:
				subtitle = srt.readline()
				# whether it's the end of a entry.
				if subtitle == '\n':
					break
				subtitles.append(subtitle)
			yield number_in_sequence, timecode, subtitles


def format_timestamp (seconds: float, always_include_hours: bool = False, decimal_marker: str = '.'):
	assert seconds >= 0, "non-negative timestamp expected"
	milliseconds = round(seconds * 1000.0)
	
	hours = milliseconds // 3_600_000
	milliseconds -= hours * 3_600_000
	
	minutes = milliseconds // 60_000
	milliseconds -= minutes * 60_000
	
	seconds = milliseconds // 1_000
	milliseconds -= seconds * 1_000
	
	hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
	return f"{hours_marker}{minutes:02d}:{seconds:02d}{decimal_marker}{milliseconds:03d}"


def write_srt (result: dict, file: TextIO):
	for i, segment in enumerate(result["segments"], start=1):
		# write srt lines
		file.write(f"{i}\n")
		file.write(f"{format_timestamp(segment['start'], always_include_hours=True, decimal_marker=',')} --> ")
		file.write(f"{format_timestamp(segment['end'], always_include_hours=True, decimal_marker=',')}\n")
		file.write(f"{segment['text'].strip().replace('-->', '->')}\n\n")


class FLACConverter(object):
	def __init__ (self, source_path, row_number, include_before=0.25, include_after=0.25):
		self.source_path = source_path
		self.include_before = include_before
		self.include_after = include_after
		self.row_number = row_number
	
	def split_region (self, region, index):
		# try:
		start, end = region
		start = max(0, start - self.include_before)
		end += self.include_after
		folder_temp = get_folder_music_temp(self.row_number)
		temp_file = JOIN_PATH(folder_temp, str(index) + ".flac")
		if os.path.exists(temp_file):
			os.unlink(temp_file)
		command = ["ffmpeg", "-ss", str(start), "-t", str(end - start), "-y", "-i", self.source_path, "-loglevel",
				   "error", "-y", temp_file]
		subprocess.check_output(command, stdin=open(os.devnull), creationflags=0x08000000)
		# data = temp.read()
		# temp.close()
		return temp_file


class ExtractSubVoice():
	
	def __init__ (self, manage_thread_pool: ManageThreadPool, manage_cmd: ManageCMD, request: Request = None):
		self.manage_thread_pool = manage_thread_pool
		self.manage_cmd = manage_cmd
		
		self.list_origin_language = {}
		self.list_audio_filename = {}
		self.list_source_path = {}
		self.list_regions = {}
		self.list_converter = {}
		self.list_recognizer = {}
		self.list_transcripts = {}
		self.count_result_convert = {}
		self.count_result = 0
		self.total_region = {}
		self.request = request
		
		self.manage_thread_pool.resultChanged.connect(self._resultThreadChanged)
		self.manage_cmd.resultSignal.connect(self._resultCMDSignal)
		self.manage_cmd.progressSignal.connect(self._progressSignal)
	
	def _resultThreadChanged (self, id_worker, id_thread, result):
		pass
	
	def _resultCMDSignal (self, id_worker, type_cmd, result, kwargs):
		if type_cmd == RUN_CMD_AISUB:
			self.manage_thread_pool.statusChanged.emit(str(kwargs['row_number']), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
				"Hoàn Thành")
			base, ext = os.path.splitext(kwargs.get('source_path'))
			srt_path = "{base}.{format}".format(base=base, format='srt')
			self.manage_thread_pool.resultChanged.emit(str(kwargs['row_number']), EXTRACT_SUB_FINISHED, srt_path)
	
	
	def _progressSignal (self, id_worker, type_cmd, progress, kwargs):
		if type_cmd == RUN_CMD_AISUB:
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS,
				str(kwargs['row_number']), progress)
	
	@decorator_try_except_class
	def extractSrtServerSTT (self, source_path, request, origin_language, row_number, server_stt, thread_pool_limit_convert):
		audio_filename, audio_rate = extract_audio(source_path)
		regions = find_speech_regions(audio_filename)
		print(regions)
		# pool = multiprocessing.Pool(concurrency)
		converter = FLACConverter(source_path=audio_filename, row_number=row_number)
		
		recognizer = server_stt(request, language=origin_language, rate=audio_rate)
		
		# SpeechRecognizer(request, language=origin_language, rate=audio_rate, api_key=GOOGLE_SPEECH_API_KEY)
		self.count_result_convert[(row_number)] = 0
		self.total_region[(row_number)] = len(regions)
		self.list_origin_language[(row_number)] = origin_language
		self.list_audio_filename[(row_number)] = audio_filename
		self.list_source_path[(row_number)] = source_path
		self.list_regions[(row_number)] = regions
		self.list_converter[(row_number)] = converter
		self.list_recognizer[(row_number)] = recognizer
		
		if regions:
			
			self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
				"Đang trích xuất sub...")
			self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS,
				UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS,
				{"id_row": row_number, "range": len(regions)})
			
			for i, region in enumerate(regions):
				thread_pool_limit_convert.start(self._funcExtractSrtServerSTT, "extractVoiceServerSTT" + uuid.uuid4().__str__(), EXTRACT_SUB_SPEECH_TO_TEXT, index=i, region=region, row_number=row_number)
	
	
	def _funcExtractSrtServerSTT (self, **kwargs):
		# print(111)
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		index = kwargs["index"]
		row_number = kwargs["row_number"]
		region = kwargs["region"]
		converter = self.list_converter[(row_number)]
		recognizer = self.list_recognizer[(row_number)]
		time.sleep(3)
		
		file_temp = converter.split_region(region, index)
		
		transcript = recognizer.speechToText(file_temp)
		
		thread_pool.finishSingleThread(id_worker)
		
		self.list_transcripts[(row_number, index)] = transcript
		
		return {'row_number': row_number}
	
	# @decorator_try_except_class
	def extractSrtAILocal (self, source_path, mode_whisper, model_whisper, row_number, token,language_origin):
		
		# if which(FILE_FFOCR):
		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, str(row_number),
			0)
		self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS,
			UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS,
			{"id_row": row_number, "range": 100})
		
		command = f'"{FILE_FFSUB}" -a {URL_API_BASE} -l {language_origin} -p {cr_pc()} -t {token} -v "{source_path}" -m {model_whisper} -md {mode_whisper} -ty ai'
		# print(command)
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Đang khởi tạo...")
		
		self.manage_cmd.cmd_output(command, RUN_CMD_AISUB,
			RUN_CMD_AISUB, row_number=row_number,detect_sub=True, source_path=source_path)
		
		return True
	def parseYoutubeURL (self, url: str) -> str:
		data = re.findall(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
		if data:
			return data[0]
		return ""
	def extractSrtFromYoutube (self, url_video, language, filename, row_number, cach_lay,thread_pool_limit_convert,CachLaySubYoutubeEnum):
		ID_video = self.parseYoutubeURL(url_video)
		transcript = YouTubeTranscriptApi.get_transcript(ID_video, [language])
		
		if cach_lay == CachLaySubYoutubeEnum.Nguon.value:
			try:
				format = SRTFormatter()
				data = format.format_transcript(transcript)
				
				with open(filename, 'w', encoding='utf-8') as json_file:
					json_file.write(data)
				
				return True
			except:
				return False
		elif cach_lay == CachLaySubYoutubeEnum.Google.value:
			#tải mp3 về
			yt = YouTube(url_video)
			audio_temp = tempfile.mktemp(dir=PATH_TEMP,suffix='.wav')
			yt.streams.get_audio_only().download(filename=audio_temp)
			audio_filename, audio_rate = extract_audio(audio_temp)
			if os.path.exists(audio_filename):
				os.unlink(audio_temp)
			# audio_rate = 16000
			regions = []

			for i, seg in enumerate(transcript):
				end = seg['start'] + seg['duration']
				endd = transcript[i + 1]['start'] if i < len(transcript) - 1 and transcript[i + 1]['start'] < end else end
				print(end)
				print(endd)
				regions.append((seg.get('start'),endd))
			
			print(regions)
			# return
			# pool = multiprocessing.Pool(concurrency)
			converter = FLACConverter(source_path=audio_filename, row_number=row_number,include_before=0,include_after=0)
			request =Request()
			# recognizer = GoogleSpeechToText(request, language=language, rate=audio_rate)
			recognizer = GladiaSpeechToText(request, language=language, rate=audio_rate)
			
			# SpeechRecognizer(request, language=origin_language, rate=audio_rate, api_key=GOOGLE_SPEECH_API_KEY)
			self.count_result_convert[(row_number)] = 0
			self.total_region[(row_number)] = len(regions)
			self.list_origin_language[(row_number)] = language
			self.list_audio_filename[(row_number)] = audio_filename
			self.list_source_path[(row_number)] = filename
			self.list_regions[(row_number)] = regions
			self.list_converter[(row_number)] = converter
			self.list_recognizer[(row_number)] = recognizer
			
			if regions:
				
				self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
					"Đang trích xuất sub...")
				self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS,
					UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS,
					{"id_row": row_number, "range": len(regions)})
				
				for i, region in enumerate(regions):
					thread_pool_limit_convert.start(self._funcExtractSrtServerSTT, "extractVoiceServerSTT" + uuid.uuid4().__str__(), EXTRACT_SUB_YOUTUBE_BY_GOOGLE, index=i, region=region, row_number=row_number)
			return False


