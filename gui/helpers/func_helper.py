import asyncio
import base64
import hashlib
import json
import os
import random
import re
import string
import subprocess
import sys
import time
from datetime import datetime, timedelta
from difflib import SequenceMatcher

import aiohttp
import cv2
import numpy as np
import pendulum
import pysrt
import requests
import six
import wordsegment
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from PIL import ImageGrab
from PySide6 import QtGui
from PySide6.QtCore import QSettings, QByteArray

from platformdirs import user_data_dir, user_data_path


from gui.helpers.constants import JOIN_PATH, APP_PATH, FILE_FFSUB_MAIN_REPLACE, FILE_PYTRAN_MAIN_REPLACE, \
	FILE_PYTRAN_FAKE_REPLACE, FILE_FFSUB_FAKE_REPLACE, SETTING_APP, TOOL_CODE_MAIN, \
	USER_DATA, LANGUAGE_CODE_SPLIT_NO_SPACE

from gui.helpers.pymediainfo import MediaInfo
from gui.helpers.translatepy import Language
import soundfile as sf


def reformat (path):
	# fix "RecursionError: maximum recursion depth exceeded in comparison" in wordsegment.segment call
	if sys.getrecursionlimit() < 100000:
		sys.setrecursionlimit(100000)
	wordsegment.load()
	subs = pysrt.open(path)
	verb_forms = ["I'm", "you're", "he's", "she's", "we're", "it's", "isn't", "aren't", "they're", "there's", "wasn't",
				  "weren't", "I've", "you've", "we've", "they've", "hasn't", "haven't", "I'd", "you'd", "he'd", "she'd",
				  "it'd", "we'd", "they'd", "doesn't", "don't", "didn't", "I'll", "you'll", "he'll", "she'll", "we'll",
				  "they'll", "there'll", "there'd", "can't", "couldn't", "daren't", "hadn't", "mightn't", "mustn't",
				  "needn't", "oughtn't", "shan't", "shouldn't", "usedn't", "won't", "wouldn't", "that's", "what's",
				  "it'll"]
	verb_form_map = {}
	
	typo_map = {
		"l'm": "I'm",
		"l just": "I just",
		"Let'sqo": "Let's go",
		"Iife": "life",
		"威筋": "威胁"
	}
	
	for verb in verb_forms:
		verb_form_map[verb.replace("'", "").lower()] = verb
	
	def format_seg_list (seg_list):
		new_seg = []
		for seg in seg_list:
			if seg in verb_form_map:
				new_seg.append([seg, verb_form_map[seg]])
			else:
				new_seg.append([seg])
		return new_seg
	
	def typo_fix (text):
		for k, v in typo_map.items():
			text = re.sub(re.compile(k, re.I), v, text)
		return text
	
	# 逆向过滤seg
	def remove_invalid_segment (seg, text):
		seg_len = len(seg)
		span = None
		new_seg = []
		for i in range(seg_len - 1, -1, -1):
			s = seg[i]
			if len(s) > 1:
				regex = re.compile(f"({s[0]}|{s[1]})", re.I)
			else:
				regex = re.compile(f"({s[0]})", re.I)
			try:
				ss = [(i) for i in re.finditer(regex, text)][-1]
			except IndexError:
				ss = None
			if ss is None:
				continue
			text = text[:ss.span()[0]]
			if span is None:
				span = ss.span()
				new_seg.append(s)
				continue
			if span > ss.span():
				new_seg.append(s)
				span = ss.span()
		return list(reversed(new_seg))
	
	for sub in subs:
		sub.text = typo_fix(sub.text)
		seg = wordsegment.segment(sub.text)
		if len(seg) == 1:
			seg = wordsegment.segment(re.sub(re.compile(f"(\ni)([^\\s])", re.I), "\\1 \\2", sub.text))
		seg = format_seg_list(seg)
		
		# 替换中文前的多个空格成单个空格, 避免中英文分行出错
		sub.text = re.sub(' +([\\u4e00-\\u9fa5])', ' \\1', sub.text)
		# 中英文分行
		sub.text = sub.text.replace("  ", "\n")
		lines = []
		remain = sub.text
		seg = remove_invalid_segment(seg, sub.text)
		seg_len = len(seg)
		for i in range(0, seg_len):
			s = seg[i]
			global regex
			if len(s) > 1:
				regex = re.compile(f"(.*?)({s[0]}|{s[1]})", re.I)
			else:
				regex = re.compile(f"(.*?)({s[0]})", re.I)
			ss = re.search(regex, remain)
			if ss is None:
				if i == seg_len - 1:
					lines.append(remain.strip())
				continue
			
			lines.append(remain[:ss.span()[1]].strip())
			remain = remain[ss.span()[1]:].strip()
			if i == seg_len - 1:
				lines.append(remain)
		if seg_len > 0:
			ss = " ".join(lines)
		else:
			ss = remain
		# again
		ss = typo_fix(ss)
		# 非大写字母的大写字母前加空格
		ss = re.sub("([^\\sA-Z\\-])([A-Z])", "\\1 \\2", ss)
		# 删除重复空格
		ss = ss.replace("  ", " ")
		ss = ss.replace("。", ".")
		# 删除,?!,前的多个空格
		ss = re.sub(" *([\\.\\?\\!\\,])", "\\1", ss)
		# 删除'的前后多个空格
		ss = re.sub(" *([\\']) *", "\\1", ss)
		# 删除换行后的多个空格, 通常时第二行的开始的多个空格
		ss = re.sub('\n\\s*', '\n', ss)
		# 删除开始的多个空格
		ss = re.sub('^\\s*', '', ss)
		# 删除-左侧空格
		ss = re.sub("([A-Za-z0-9]) (\\-[A-Za-z0-9])", '\\1\\2', ss)
		# 删除%左侧空格
		ss = re.sub("([A-Za-z0-9]) %", '\\1%', ss)
		# 结尾·改成.
		ss = re.sub('·$', '.', ss)
		# 移除Dr.后的空格
		ss = re.sub(r'\bDr\. *\b', "Dr.", ss)
		ss = ss.replace("\n\n", "\n")
		sub.text = ss.strip()
	subs.save(path, encoding='utf-8')


class VideoCapture:
	def __init__ (self, video_path):
		self.path = video_path
	
	def __enter__ (self):
		self.cap = cv2.VideoCapture(self.path)
		if not self.cap.isOpened():
			raise IOError('Can not open video {}.'.format(self.path))
		return self.cap
	
	def __exit__ (self, exc_type, exc_value, traceback):
		self.cap.release()


FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')


def open_and_select_file (path):
	# explorer would choke on forward slashes
	path = os.path.normpath(path)
	
	if os.path.isdir(path):
		subprocess.run([FILEBROWSER_PATH, path])
	elif os.path.isfile(path):
		subprocess.run([FILEBROWSER_PATH, '/select,', path])


def play_media_preview (path, display=False, auto_stop=True):
	try:
		height = ImageGrab.grab().height - 150
		# print(width,height)
		show = f'-vf scale=-1:{height}' if display else '-nodisp'
		stop = f'-autoexit ' if auto_stop else ''
		ffmpeg = f'''ffplay.exe "{path}" {stop}{show}'''
		# print(ffmpeg)
		
		process = subprocess.Popen(
			ffmpeg,
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT,
			shell=True,
			creationflags=0x08000000,
			encoding='utf-8',
			errors='replace'
		)
	except:
		print("Không thể preview")


def ffmpeg_check (gpu=False):
	"""
	Return the ffmpeg executable name. "None" returned when no executable exists.
	"""
	
	# if gpu:
	# 	return "ffmpeggpu"
	# else:
	return "ffmpeg"


def similar (a, b):
	return SequenceMatcher(None, a, b).ratio()


def string_time_to_seconds (time_string, format="%H:%M:%S,%f"):
	date_time = datetime.strptime(time_string, format)
	et = datetime(1900, 1, 1)
	return (date_time - et).total_seconds()


def seconds_to_timestamp (seconds, delimiter=','):
	td = timedelta(seconds=seconds)
	ms = td.microseconds // 1000
	m, s = divmod(td.seconds, 60)
	h, m = divmod(m, 60)
	return '{:02d}:{:02d}:{:02d}{}{:03d}'.format(h, m, s, delimiter, ms)


def datetime_to_seconds (time) -> timedelta:  #
	a = datetime.strptime('00:0:00,000', '%H:%M:%S,%f')
	return (time - a)


def get_timestamp (seconds):
	td = timedelta(seconds=seconds)
	ms = td.microseconds // 1000
	m, s = divmod(td.seconds, 60)
	h, m = divmod(m, 60)
	return datetime.strptime('{:02d}:{:02d}:{:02d},{:03d}'.format(h, m, s, ms), "%H:%M:%S,%f")


def filter_sequence_srt (path_srt, path_video) -> list:
	# sequences = list(map(list, re.findall(r"(\d+)\n+(\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+)\n+(.+(?:\n.+)?)\n+", content)))
	# sequences = [list(filter(None, sequence)) for sequence in sequences]
	# print(1)
	# sequences = []
	# i = 1
	# for id, seq in enumerate(re.findall(r"(\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+.?)\n+(.+)\n+", content)):
	# 	if len(seq) == 2:
	# 		sequences.append([str(i), seq[0], seq[1]])
	# 		i += 1
	# print(sequences)
	sequences = pysrt.open(path_srt, encoding='utf-8')
	
	total_seconds, fps = get_duaration_video(path_video)
	duaration_time_video = get_timestamp(total_seconds)
	
	lang_source = Language(language(random.choice(sequences).text))
	score_similar = 0.9
	if lang_source.alpha3 in LANGUAGE_CODE_SPLIT_NO_SPACE:
		score_similar = 0.65
	text_pre = ""
	start_pre = ""
	end_pre = "00:00:00,0"
	list_new_seg = []
	text_same = ''
	start_same = ''
	end_same = ''
	# print(2)
	
	for seq in sequences:
		# start = seq[1].split(' --> ')[0].strip()
		# end = seq[1].split(' --> ')[1].strip()
		start = str(seq.start)
		# print(seq.time)
		end = str(seq.end)
		# print(seq)
		# print(end)
		end_time = datetime.strptime(end, "%H:%M:%S,%f")
		text_sub = seq.text
		if (duaration_time_video - end_time).total_seconds() < 0:
			break
		if start == end:
			continue
		text_sub = re.sub(r"\[.+", "", text_sub)
		# regex = re.compile(r"\[.+\]", re.M)
		# mmm = regex.search(seq[-1])
		# if mmm:
		# 	continue
		
		if text_sub == '':
			continue
		# print(1)
		
		start_time = datetime.strptime(start, "%H:%M:%S,%f")
		end_time_pre = datetime.strptime(end_pre, "%H:%M:%S,%f")
		# print((start_time - end_time_pre).total_seconds())
		if similar(text_sub, text_pre) > score_similar and (start_time - end_time_pre).total_seconds() < 0.2:
			if start_same == '':
				start_same = start_pre
			if len(text_same) < len(text_sub):
				text_same = text_sub
			end_same = end
		
		else:
			if not text_same == '' and not start_same == '' and not end_same == '':
				del list_new_seg[-1]
				list_new_seg.append([str(len(list_new_seg) + 1), f"{start_same} --> {end_same}", text_same])
				text_same = ''
				start_same = ''
				end_same = ''
			list_new_seg.append([str(len(list_new_seg) + 1), f"{seq.start} --> {seq.end}", seq.text])
		
		text_pre = text_sub
		start_pre = start
		end_pre = end
	# print(3)
	return list_new_seg


def writeFileSrt (filename_srt, data_sub, type_srt):
	""" Mô tả: Lưu file srt dịch vào thư mục temp"""
	if os.path.isfile(filename_srt):
		os.remove(filename_srt)
	origin_lag = Language(language(data_sub[0]))
	
	with open(filename_srt, "w", encoding='utf-8') as file_data:
		for index, item in enumerate(data_sub):
			# TODO: time,sub_origin, sub_translate
			time,sub_origin, sub_translate = item
			file_data.write(str(index + 1) + '\n')
			file_data.write(str(time) + '\n')
			if type_srt == 0:
				content = str(sub_origin)
			else:
				content = str(sub_translate)
			
			if origin_lag.alpha3 in LANGUAGE_CODE_SPLIT_NO_SPACE:
				content = content.strip().replace("\n", "")
			else:
				content = content.strip().replace("\n", " ")
			
			file_data.write(str(content) + '\n\n')


def writeFileTXT (filename_srt, data_sub, type_srt):
	""" Mô tả: Lưu file srt dịch vào thư mục temp"""
	if os.path.isfile(filename_srt):
		os.remove(filename_srt)
	
	origin_lag = Language(language(data_sub[0]))
	with open(filename_srt, "w", encoding='utf-8') as file_data:
		for index, item in enumerate(data_sub):
			# TODO: time,sub_origin, sub_translate
			time,sub_origin, sub_translate = item
			if type_srt == 0:
				
				content = str(sub_origin)
			else:
				content = str(sub_translate)
			
			if origin_lag.alpha3 in LANGUAGE_CODE_SPLIT_NO_SPACE:
				content = content.strip().replace("\n", "")
			else:
				content = content.strip().replace("\n", " ")
			if index == len(data_sub) - 1:
				file_data.write(str(content))
			else:
				file_data.write(str(content) + '\n')


def exportSRTCapCut (file_data) -> (bool, str):
	""" Mô tả: Xuất file srt capcut"""
	if os.path.exists(file_data):
		with open(file_data, "r", encoding="utf-8") as file:
			# try:
			data = json.loads(file.read())
			# print(data)
			tracks = data.get('tracks')
			data_sub = ""
			index_seg = 0
			for track in tracks:
				if track.get("type") == "text":
					index_seg += 1
					segments = track.get("segments")
					for index, segment in enumerate(segments):
						target_timerange = segment.get('target_timerange')
						start_time = seconds_to_timestamp(target_timerange.get('start') / 1000000)
						end_time = seconds_to_timestamp((
																target_timerange.get('start') + target_timerange.get('duration')) / 1000000)
						
						for text_it in data.get("materials").get('texts'):
							# words = text_it.get('words')
							text_id = text_it.get('id')
							if segment.get('material_id') == text_id:
								content = json.loads(text_it.get('content'))
								# l_text = re.findall("\[(.+)\]", text_it.get('content'))
								# if len(l_text) > 0:
								# 	text = l_text[0]
								# else:
								# 	text = ""
								text = content.get('text')
								data_sub += str(index_seg * (index + 1)) + '\n'
								data_sub += f"{start_time} --> {end_time}" + '\n'
								data_sub += str(text.capitalize()) + '\n\n'
								break
			
			if data_sub == '':
				return False, "Project Hiện Tại Không Có Sub"
			
			return True, data_sub
	# except Exception as e:
	# 	return False, e.__str__()
	else:
		return False, "File Data Không Tồn Tại"


def check_server_ffsub (url):
	try:
		res = requests.get(url)
		if res.status_code == 200:
			return True
	except:
		return False
	return False


def language (text: str) -> str:
	params = {"client": "gtx", "dt": "t", "sl": "auto", "tl": "ja", "q": text}
	session = requests.Session()
	request = session.get("https://translate.googleapis.com/translate_a/single", params=params)
	response = request.json()
	if request.status_code < 400:
		return response[2]
	
	params = {"client": "dict-chrome-ex", "sl": "auto", "tl": "ja", "q": text}
	request = session.get("https://clients5.google.com/translate_a/t", params=params)
	response = request.json()
	if request.status_code < 400:
		return response['ld_result']["srclangs"][0]


def iconFromBase64 (base64):
	pixmap = QtGui.QPixmap()
	pixmap.loadFromData(QByteArray.fromBase64(base64))
	icon = QtGui.QIcon(pixmap)
	
	return icon


def normalize (wave, is_normalize=False):
	"""Save output music files"""
	maxv = np.abs(wave).max()
	if maxv > 1.0:
		print(f"\nNormalization Set {is_normalize}: Input above threshold for clipping. Max:{maxv}")
		if is_normalize:
			print(f"The result was normalized.")
			wave /= maxv
		else:
			print(f"The result was not normalized.")
	else:
		print(f"\nNormalization Set {is_normalize}: Input not above threshold for clipping. Max:{maxv}")
	
	return wave


def to_shape (x, target_shape):
	padding_list = []
	for x_dim, target_dim in zip(x.shape, target_shape):
		pad_value = (target_dim - x_dim)
		pad_tuple = ((0, pad_value))
		padding_list.append(pad_tuple)
	
	return np.pad(x, tuple(padding_list), mode='constant')


def pitch_shift (input_path, output_path, pitch, folder_temp, index):
	WAV_TYPE = ('PCM_U8', 'PCM_16', 'PCM_24', 'PCM_32', '32-bit Float', '64-bit Float')
	
	wav1, sr = sf.read(input_path)
	
	outfile = JOIN_PATH(folder_temp, f"{index}outfile.wav")
	
	try:
		# Execute rubberban
		arguments = f'rubberband -q --pitch {pitch} {input_path} {outfile}'
		
		# print(arguments)
		subprocess.check_call(
			arguments.split(' '),
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL,
			creationflags=0x08000000,
		)
		# subprocess.check_call(arguments, stdout=DEVNULL, stderr=DEVNULL,creationflags=0x08000000)
		
		# Load the processed audio.
		y_out, _ = sf.read(outfile, always_2d=True)
		
		# make sure that output dimensions matches input
		if wav1.ndim == 1:
			y_out = np.squeeze(y_out)
		sf.write(output_path, y_out, sr, WAV_TYPE[2])
	
	except OSError as exc:
		six.raise_from(RuntimeError('Failed to execute rubberband. '
									'Please verify that rubberband-cli '
									'is installed.'),
			exc)
	except Exception as ess:
		print(ess)
	finally:
		# Remove temp files
		# os.unlink(infile)
		try:
			os.unlink(outfile)
		except:
			pass

# return y_out
#
# sf.write(output_path, y_stretch, sr, WAV_TYPE[2])

# print(1)
# wav, sr = librosa.load(input_path, sr=44100, mono=False)
# # tempo = 5
# print(1)
# if wav.ndim == 1:
# 	wav = np.asfortranarray([wav, wav])
# wav_1 = pyrubberband.pitch_shift(wav[0], sr, pitch, rbargs=None)
# wav_2 = pyrubberband.pitch_shift(wav[1], sr, pitch, rbargs=None)
#
# if wav_1.shape > wav_2.shape:
# 	wav_2 = to_shape(wav_2, wav_1.shape)
# if wav_1.shape < wav_2.shape:
# 	wav_1 = to_shape(wav_1, wav_2.shape)
# print(2)
#
# wav_mix = np.asfortranarray([wav_1, wav_2])
# is_normalization = True
# print(2)
#
# sf.write(output_path, normalize(wav_mix.T, is_normalization), int(sr), subtype=WAV_TYPE[2])
# print(2)

def checkVideoOk (filename):
	if not os.path.exists(filename):
		return False
	try:
		lib_file = JOIN_PATH(APP_PATH, "MediaInfo.dll")
		media_info = MediaInfo.parse(filename, library_file=lib_file)
		bit_rate = int(media_info.tracks[1].to_data()['bit_rate'] / 1000)
		duration_in_ms = media_info.tracks[1].to_data()["duration"]
		return True
	except:
		try:
			with VideoCapture(filename) as video_cap:
				fps = video_cap.get(cv2.CAP_PROP_FPS)
				frame_count = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
			# print(frame_count)
			return True
		except:
			return False


def count_file_in_folder (folder):
	i = 1
	for f in os.scandir(folder):
		if f.is_file():
			i += 1
	return i


def get_duaration_video_cv2 (filename):
	with VideoCapture(filename) as video_cap:
		fps = video_cap.get(cv2.CAP_PROP_FPS)
		frame_count = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
	return frame_count / fps, fps


def is_file_audio (file_bytes: bytes, return_type=False):
	first_char = file_bytes[:10]
	# print(first_char)
	
	if b'RIFF' in first_char:
		if return_type:
			return True, 'wav'
		else:
			return True
	
	elif b'ID3' in first_char:
		if return_type:
			return True, 'mp3'
		else:
			return True
	elif b'\xff\xf3D\xc4' in first_char or b'\xff\xf3\xa4' in first_char:
		if return_type:
			return True, 'wav'
		else:
			return True
	
	if return_type:
		return False, ''
	else:
		return False


# return "server_busy"


def has_audio (filename):
	lib_file = JOIN_PATH(APP_PATH, "MediaInfo.dll")
	media_info = MediaInfo.parse(filename, library_file=lib_file)
	try:
		has_audio = any([track.track_type == 'Audio' for track in media_info.tracks])
	except:
		result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
								 "format=nb_streams", "-of",
								 "default=noprint_wrappers=1:nokey=1", filename],
			stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT)
		has_audio = (int(result.stdout) - 1)
	
	return has_audio


def get_duaration_video (filename):
	lib_file = JOIN_PATH(APP_PATH, "MediaInfo.dll")
	media_info = MediaInfo.parse(filename, library_file=lib_file)
	
	# fps = media_info.tracks[1].to_data().get("frame_rate")
	# bit_rate = media_info.tracks[1].to_data().get('other_bit_rate')[0].strip(" b/s")
	# print(media_info.tracks[1].to_data())
	bit_rate = 2400
	try:
		bit_rate = int(media_info.tracks[1].to_data()['bit_rate'] / 1000)
		duration_in_ms = media_info.tracks[1].to_data()["duration"]
		duration = duration_in_ms / 1000
		return duration, bit_rate
	except:
		pass
	try:
		metadata = subprocess.check_output(f'ffprobe -i "{filename}" -v quiet -print_format json -show_format -hide_banner')
		format = json.loads(metadata)['format']
		bit_rate = format['bit_rate']
		return format['duration'], format['bit_rate'] / 1000
	except:
		pass
	try:
		with VideoCapture(filename) as video_cap:
			fps = video_cap.get(cv2.CAP_PROP_FPS)
			frame_count = video_cap.get(cv2.CAP_PROP_FRAME_COUNT)
		duration = frame_count / fps
		return duration, bit_rate
	except:
		pass
	return 0, 0


def ma_hoa_output_ffmpeg (cau_hinh):
	if cau_hinh.get('bit_rate_video') is None:
		bit_rate_video = '-b:v 10000k'
	else:
		bit_rate_video = f'-b:v {cau_hinh.get("bit_rate_video")}k'
	
	if cau_hinh.get('bit_rate_audio') is None:
		bit_rate_audio = '-b:a 10000k'
	else:
		bit_rate_audio = f'-b:a {cau_hinh.get("bit_rate_audio")}k'
	
	if cau_hinh.get('he_so_crf') is None:
		he_so_crf = 20
		he_so_preset = "veryfast"
		he_so_fps = 30
	else:
		he_so_crf = cau_hinh.get('he_so_crf')
		he_so_fps = cau_hinh.get('he_so_fps')
		he_so_preset = cau_hinh.get('he_so_preset')
	
	use_gpu = f'-vcodec libx264 -preset {he_so_preset} -r {he_so_fps}' if \
		cau_hinh['use_gpu'] is False else f'-vcodec h264_nvenc -r {he_so_fps}'
	
	return f'{use_gpu} {bit_rate_video} {bit_rate_audio} -ar 48000 -c:a aac -crf {he_so_crf}'


# return f'{use_gpu} {bit_rate_video} {bit_rate_audio} -ar 32000 -acodec libmp3lame -crf {he_so_crf}'


def remove_dir (path):
	try:
		if os.name == 'nt':
			subprocess.check_output(['cmd', '/C', 'rmdir', '/S', '/Q', path])
		else:
			subprocess.check_output(['rm', '-rf', path])
	except:
		pass


def PrintLog (msg=None):
	# print()
	# backslash_char = "\\"
	print(f"Debug line {sys._getframe().f_back.f_lineno} {' at class: ' + sys._getframe(1).f_locals['self'].__class__.__name__ + ' method: ' + sys._getframe().f_back.f_code.co_name} \n {msg if msg is not None else ''}")


# print(f"Debug line {sys._getframe().f_back.f_lineno} file {__file__.split(backslash_char)[-2]}/{__file__.split(backslash_char)[-1]}{' at ' + func if func is not None else ''}: \n {msg if msg is not None else ''}")

def which (program):
	"""
	Return the path for a given executable.
	"""
	
	def is_exe (file_path):
		"""
		Checks whether a file is executable.
		"""
		return os.path.isfile(file_path) and os.access(file_path, os.X_OK)
	
	fpath, _ = os.path.split(program)
	if fpath:
		if is_exe(program):
			return program
	else:
		for path in os.environ["PATH"].split(os.pathsep):
			path = path.strip('"')
			exe_file = os.path.join(path, program)
			if is_exe(exe_file):
				return exe_file
	return None


def rp_f ():
	if os.path.exists(FILE_PYTRAN_FAKE_REPLACE):
		try:
			pass
		# print("ok")
		
		# file_temp = os.path.join(FOLDER_REPLACE_PADDLE, FILE_NAME_PYTRAN_DLL)
		# des = shutil.copy2(FILE_PYTRAN_FAKE_REPLACE, FILE_PYTRAN)
		# print(des)
		# if os.path.exists(des):
		# 	shutil.move(des, FILE_PYTRAN)
		except:
			pass
	if os.path.exists(FILE_FFSUB_FAKE_REPLACE):
		try:
			pass
		# print("ok")
		# # file_temp = os.path.join(FOLDER_REPLACE_TORCH, FILE_NAME_FFSUB_EXE)
		# des = shutil.copy2(FILE_FFSUB_FAKE_REPLACE, FILE_FFSUB)
		# # print(des)
		# # if os.path.exists(des):
		# # 	shutil.move(des, FILE_FFSUB)
		except:
			pass


def rp_m ():
	try:
		if os.path.exists(FILE_PYTRAN_MAIN_REPLACE):
			print("ok")
		# des = shutil.copy2(FILE_PYTRAN_MAIN_REPLACE, FILE_PYTRAN)
		
		if os.path.exists(FILE_FFSUB_MAIN_REPLACE):
			print("ok")
	# des = shutil.copy2(FILE_FFSUB_MAIN_REPLACE, FILE_FFSUB)
	except:
		pass


def setValueSettings (SETTING_VALUE, TOOL_CODE, value):
	settings = QSettings(*SETTING_APP)
	st_value = settings.value(SETTING_VALUE)
	# print(st_value)
	if st_value is None:
		settings.setValue(SETTING_VALUE, {TOOL_CODE: value})
	else:
		# dd.update({'install_tool': {'password': '555', 'username': '555'}})
		st_value.update({TOOL_CODE: value})
		settings.setValue(SETTING_VALUE, st_value)


# print("Sau khi lưu\n", settings.value(SETTING_VALUE))


def getValueSettings (SETTING_VALUE, TOOL_CODE):
	settings = QSettings(*SETTING_APP)
	st_value = settings.value(SETTING_VALUE)
	# print(st_value)
	if st_value is None:
		return None
	
	elif st_value.get(TOOL_CODE) is None:
		return None
	
	elif st_value.get(TOOL_CODE) == '':
		return None
	else:
		return st_value.get(TOOL_CODE)


def get_expired (timestamp):
	expire_date_current = datetime.fromtimestamp(timestamp)
	today = datetime.now()
	so_ngay_con_lai = (expire_date_current - today).days
	# print(datetime.fromtimestamp(1706424186))
	tz = pendulum.timezone('Asia/Ho_Chi_Minh')
	date = pendulum.from_timestamp(timestamp, tz=tz)
	now = pendulum.now('Asia/Ho_Chi_Minh')
	return f"{date.diff_for_humans(now, locale='vi')} - {so_ngay_con_lai} Ngày"


def run_cmd_result (command: str):
	proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
		creationflags=0x08000000)
	return proc.communicate()[0].decode('ascii').split('\r\n')


list_app = [
	# 'debuggers.e',
	'disassembler.exe',
	'x64dbg',
	'qira.exe',
	'ghidra.exe',
	'dnspy.exe',
	'fiddler',
	'tcpview',
	'wireshark',
	'exeinfope',
	'detect it easy',
	'resource hacker',
	# 'HxD',
	'pydc',
	'ltfviewr5u',
	'sandboxie.exe',
	'processexplorer',
	'regshot.exe',
	'scylla.exe',
	'sysiternalssuite',
	'windbg.exe',
	'radare.exe',
	'pe-bear.exe',
	'fakenet-ng',
]


def check_exsist_app (folder_temp):
	for app in list_app:
		if app in folder_temp.lower():
			return True
		else:
			return False


def r_f_s (dir, ext):  # dir: str, ext: list run_fast_scan
	# https://stackoverflow.com/a/59803793/2441026
	subfolders = []
	for f in os.scandir(dir):
		
		try:
			if f.is_dir():
				# print(f.path)
				try:
					if "$recycle.bin" in f.path.lower() or 'system volume information' in f.path.lower() or 'documents and settings' in f.path.lower() or 'perflogs' in f.path.lower() or 'program files' in f.path.lower():
						continue
					if 'HxD' in f.path.lower():
						return True, f.path
					
					for app in list_app:
						if app in f.path.lower():
							return True, f.path
					
					subfolders.append(f.path)
				except:
					continue
			
			if f.is_file():
				# if os.path.splitext(f.name)[1].lower() in ext:
				
				if "uncompyle6" in f.path.lower():
					# print(f.path)
					return True, f.path
				
				elif "decompyle3" in f.path.lower():
					# print(f.path)
					return True, f.path
				
				elif "pydumpck" in f.path.lower() or "pydc" in f.path.lower() or "pyinstxtractor" in f.path.lower():
					# print(f.path)
					return True, f.path
				
				elif "de4dot.exe" in f.path.lower() or "dnspy.exe" in f.path.lower():
					# print(f.path)
					return True, f.path
				elif "die.exe" in f.path.lower():
					return True, f.path
				
				for app in list_app:
					if app in f.path.lower():
						return True, f.path
		#
		# elif "crack" in f.path.lower():
		#     print(f.path)
		#     return True
		except:
			# print(1111)
			continue
	
	if len(subfolders) > 0:
		for dir in list(subfolders):
			ck, path = r_f_s(dir, ext)
			if ck is True:
				return True, path
	# print(ck)
	# check=ck
	return False, ""


def s_d_u ():  # scan o dia user
	return False, ''  # khi test thi mở file này ra
	# ______________Kiểm tra python tren he thong____________________
	python_paths = run_cmd_result("where python")
	# check = []
	if len(python_paths) > 1:
		for python in python_paths:
			# print(python)
			
			if python == "":
				continue
			folder_python = os.path.dirname(python)
			check, path = r_f_s(folder_python, [".py"])
			if check is True:
				return True, path
	# ______________Kiểm tra conda____________________
	conda_paths = run_cmd_result("where conda")
	if len(conda_paths) > 1:
		for conda in conda_paths:
			if "conda.exe" in conda:
				site = conda.replace("\\", "/").split("/")
				folder_conda = ''
				for p in site:
					folder_conda += p + "/"
					if "anaconda" in p:
						break
				folder_conda = os.path.dirname(conda)
				check, path = r_f_s(folder_conda, [".conda"])
				if check is True:
					return True, path
	try:
		desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
		check, path = r_f_s(desktop, [".py"])
		if check is True:
			return True, path
	except:
		pass
	available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
	for disk in available_drives:
		if not disk == "C:":
			try:
				check, path = r_f_s(f"{disk}/", [".py"])
				if check is True:
					return True, path
			except:
				continue
	return False, ""


def r_p_c_e (path):
	# print(path)
	if not os.path.exists(path):
		return
	size = os.path.getsize(path)
	with open(path, 'rb') as f:
		bt_main = f.read()
	
	mid = int(size / 2)
	byte1 = bt_main[:mid]
	random_bytes = random.randbytes(size - mid)
	
	appname = "Windows"
	appauthor = "Microsoft"
	folder_temp = user_data_dir(appname, appauthor)
	
	file_scipt_delete = folder_temp + "\\" + "dll.vbs"
	file_name = path.replace("\\", "/").split("/")[-1]
	# print(file_name)
	file_err = folder_temp + "\\" + file_name
	
	with open(file_err, 'wb') as fb:
		fb.write(byte1 + random_bytes)
	basdd = '"{impersonationLevel=impersonate}!\\\\"'
	delcode = f'''
fileErr ="{file_err}"
outFile ="{path}"

Const TypeBinary = 1
Const ForReading = 1, ForWriting = 2, ForAppending = 8
WScript.Sleep 3000
Sub KillAll(ProcessName)
    Dim objWMIService, colProcess
    Dim strComputer, strList, p
    strComputer = "."
    Set objWMIService = GetObject("winmgmts:" & {basdd} & strComputer & "\\root\cimv2")
    Set colProcess = objWMIService.ExecQuery ("Select * from Win32_Process Where Name like '" & ProcessName & "'")
    For Each p in colProcess
        p.Terminate
    Next
End Sub
Call KillAll("{file_name}")
Function readBytes(file)
    Dim inStream: Set inStream = WScript.CreateObject("ADODB.Stream")
    inStream.Open
    inStream.type= TypeBinary
    inStream.LoadFromFile(file)
    readBytes = inStream.Read()

End Function
Function writeBytes(file, bytes)
    Dim binaryStream: Set binaryStream = CreateObject("ADODB.Stream")
    binaryStream.Type = TypeBinary
    binaryStream.Open
    binaryStream.Write bytes
    binaryStream.SaveToFile file, ForWriting
End Function

Call writeBytes(outFile,readBytes(fileErr))

Set fso = CreateObject("Scripting.FileSystemObject")
    If fso.FileExists(fileErr) Then
        Set fs = CreateObject("Scripting.Filesystemobject")
        fs.DeleteFile(fileErr)
    Else
    End If

Set oFso = CreateObject("Scripting.FileSystemObject") : oFso.DeleteFile Wscript.ScriptFullName, True
'''
	# setValueSettings(REMEMBER_ME, TOOL_CODE_MAIN, {"username": "", "password": ""})
	# setValueSettings(PATH_INSTALL_TOOL, TOOL_CODE_AUTOSUB, '')
	# setValueSettings(PATH_INSTALL_TOOL, TOOL_CODE_FFSUB, '')
	# setValueSettings(SETTING_VERSION_APP, TOOL_CODE_AUTOSUB, '')
	# setValueSettings(SETTING_VERSION_APP, TOOL_CODE_FFSUB, '')
	# setValueSettings(SETTING_APP_DATA, TOOL_CODE_AUTOSUB, '')
	setValueSettings(USER_DATA, TOOL_CODE_MAIN, '')
	
	with open(file_scipt_delete, "w+") as delete:
		delete.write(delcode)
	os.startfile(file_scipt_delete)


def convertPathImportFFmpeg (path):
	path = path.replace('\\', "/")
	path = path.replace('/', "\/")
	return path[:1] + '\\' + path[1:]


def _read_sequence (content, chunk_):
	# sequences = list(map(list, re.findall(r"(\d+:\d+:\d+,\d+ -+> \d+:\d+:\d+,\d+)\n+(.+(?:\n.+)?)\n?", content)))
	
	sequences = []
	
	for seq in [re.findall(r"\d+:\d+:\d+,\d+\s+-+>\s+\d+:\d+:\d+,\d+.?\n+(.+)\n?", content),
				re.findall(r"\d+:\d+:\d+,\d+\s+-+>\s+\d+:\d+:\d+,\d+.?\n+(.+)\n+", content),
				re.findall(r"\d+:\d+:\d+,\d+\s+-+>\s+\d+:\d+:\d+,\d+.?\n?(.+)\n?", content)]:
		if len(seq) == chunk_:
			sequences = seq
			break
	# print(sequences)
	
	# if len(sequences) == chunk_:
	# 	liss = []
	# 	for text in sequences:
	# 		try:
	# 			if text == '':
	# 				continue
	# 			reg = re.compile(r"\"(.+)\"", re.M)
	# 			m = reg.search(text)
	# 			if m:
	# 				text = m.group(1)
	# 			text = text.split('\n')[0]
	# 			liss.append(text)
	# 		except:
	# 			pass
	#
	# 	return liss
	# else:
	return sequences
def is_chinese_char ( char):
	return re.match(r'[\u4e00-\u9fff]', char)

if __name__ == '__main__':
	# print('{:02d}:{:02d}:{:02d}{}{:03d}'.format(33, 33, 33, '.', 55))
	# appname = "User Data"
	# args = Args()
	# args.input = paths
	# args.progress = 'classic'
	# # args.debug = True
	# # args.quiet = True

	# print()
	data = [x for x in range(0, 100)]
	chunks = [data[x:x + 5] for x in range(0, len(data), 5)]
	print(data)
	print(chunks)
	pass
