from __future__ import annotations

import asyncio
import base64
import datetime
import hashlib
import os
import re
import sys

import aiohttp
import certifi
import pysrt
import websockets
import wordsegment
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes

from gui.helpers.custom_logger import decorator_try_except_class
from gui.helpers.ect import cr_pc
from gui.helpers.thread import ManageThreadPool
from gui.helpers.get_data import URL_API_BASE
from gui.helpers.constants import UPDATE_STATUS_TABLE_EXTRACT_PROCESS, \
	UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS, UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, LANGUAGES_FORMAT, \
	FILE_FFSUB, RUN_CMD_DETECT_SUB, RUN_CMD_DETECT_SUB_DEMO, MODE_DETECT, EXTRACT_SUB_FINISHED


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


# convert frame index into SRT timestamp
def get_srt_timestamp (frame_index: int, fps: float):
	td = datetime.timedelta(seconds=frame_index / fps)
	ms = td.microseconds // 1000
	m, s = divmod(td.seconds, 60)
	h, m = divmod(m, 60)
	return '{:02d}:{:02d}:{:02d},{:03d}'.format(h, m, s, ms)


class DetectSubImage():
	
	def __init__ (self, manage_thread_pool: ManageThreadPool, manage_cmd):
		self.manage_thread_pool = manage_thread_pool
		self.manage_cmd = manage_cmd
		self.manage_cmd.resultSignal.connect(self._resultCMDSignal)
		self.manage_cmd.progressSignal.connect(self._progressSignal)
	
	# self.manage_thread_pool.resultChanged.connect(self._resultThread)
	
	# @decorator_try_except_class
	def detectSubOCR (self, row_number, video_path, language_origin, brightness_value,
					  contrast_value, conf_threshold, use_sharpen, mode,
					  crop_x, crop_y, crop_width, crop_height, token):
		
		
		# if which(FILE_FFOCR):
		self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS, str(row_number), 0)
		
		self.manage_thread_pool.resultChanged.emit(UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS,
			UPDATE_RANGE_PROGRESS_TABLE_EXTRACT_PROCESS,
			{"id_row": row_number, "range": 100})
		_use_sharpen = f" -sh {use_sharpen}" if use_sharpen else ""
		# python main.py  -p 6b329393eda58e6d49b15a43e65dec2c -t  -b 0 -c 100 -l ch -cf 10 -s 50 790 1340 270
		
		command = f'"E:\Project\Python\_APP\\autosub\\ffsub/ffsub.exe" -ty ocr -md {list(MODE_DETECT.keys())[mode]} -a {URL_API_BASE} -p {cr_pc()} -t {token} -l {language_origin} -v "{video_path}" -b {brightness_value} -c {contrast_value} -cf {conf_threshold}{_use_sharpen} -s {crop_x} {crop_y} {crop_width} {crop_height}'
		# print(command)
		self.manage_thread_pool.statusChanged.emit(str(row_number), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
			"Đang khởi tạo server...")
		
		self.manage_cmd.cmd_output(command.strip(), video_path,
			RUN_CMD_DETECT_SUB, detect_sub=True, row_number=row_number, origin_language=language_origin)
		
		return True
	
	# else:
	# 	return PyMessageBox().show_error("Lỗi", "Tool Tách Sub Chưa Được Cài Đặt, Vui Lòng Liên Hệ Admin")
	
	@decorator_try_except_class
	def detectSubDemoOCR (self, video_path, frame_number, language_origin, brightness_value,
						  contrast_value, conf_threshold, use_sharpen,
						  crop_x, crop_y, crop_width, crop_height, token):
		
		# if which(FILE_FFOCR):
		_use_sharpen = f" -sh {use_sharpen}" if use_sharpen else ""
		
		command = f'"{FILE_FFSUB}" -ty ocr -md fast -dm {frame_number} -a {URL_API_BASE} -p {cr_pc()} -t {token} -l {language_origin} -v "{video_path}" -b {brightness_value} -c {contrast_value} -cf {conf_threshold}{_use_sharpen} -s {crop_x} {crop_y} {crop_width} {crop_height}'
		self.manage_cmd.cmd_output(command.strip(), RUN_CMD_DETECT_SUB_DEMO,
			RUN_CMD_DETECT_SUB_DEMO, origin_language=language_origin, detect_sub=True)
		
		return True
	
	def _resultCMDSignal (self, id_worker, type_cmd, result, kwargs):
		if type_cmd == RUN_CMD_DETECT_SUB:
			base, ext = os.path.splitext(id_worker)
			subtitle_file = "{base}.{format}".format(base=base, format='srt')
			if "origin_language" in kwargs.keys():
				if kwargs.get("origin_language") in LANGUAGES_FORMAT:
					reformat(subtitle_file)
			
			self.manage_thread_pool.statusChanged.emit(str(kwargs['row_number']), UPDATE_STATUS_TABLE_EXTRACT_PROCESS,
				"Hoàn Thành")
			
			self.manage_thread_pool.resultChanged.emit(str(kwargs['row_number']), EXTRACT_SUB_FINISHED, subtitle_file)
	
	def _progressSignal (self, id_worker, type_cmd, progress, kwargs):
		if type_cmd == RUN_CMD_DETECT_SUB:
			self.manage_thread_pool.progressChanged.emit(UPDATE_VALUE_PROGRESS_TABLE_EXTRACT_PROCESS,
				str(kwargs['row_number']), progress)


if __name__ == "__main__":
	import requests
	import json
	
	url = "http://127.0.0.1:9292"
	
	payload = json.dumps({
		"id": "111111111111",
		"a": "https://app.ntstool.com/api/v1",
		"p": "cbcfa3ce6d7eb00db47efca4f85640f2",
		"t": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiYXBpX2tleSI6IlUyRnNkR1ZrWDE4cXoxeklJeEI3RURWU0ExYk53ZnJKd0xZUXo3QXlCNE09IiwidXNlcm5hbWUiOiJBZG1pblNhbmciLCJleHAiOjE3OTI3Mzg5MjZ9.VNHYJdhqGOnzkqmc9cm2AgbxV5eQiRZM89sjv_p8gjw",
		"l": "vi",
		"v": "E:/Project/Python/TachSubVideo/viet_ocr/hoat-hinh.mp4",
		"b": 0,
		"dm": 1005,
		"c": 100,
		"cf": 85,
		"s": [
			51,
			520,
			1103,
			122
		]
	})
	
	payload1 = json.dumps({
		"id": "111111111111",
		"a": "https://app.ntstool.com/api/v1",
		"p": "cbcfa3ce6d7eb00db47efca4f85640f2",
		"t": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MSwiYXBpX2tleSI6IlUyRnNkR1ZrWDE4cXoxeklJeEI3RURWU0ExYk53ZnJKd0xZUXo3QXlCNE09IiwidXNlcm5hbWUiOiJBZG1pblNhbmciLCJleHAiOjE3OTI3Mzg5MjZ9.VNHYJdhqGOnzkqmc9cm2AgbxV5eQiRZM89sjv_p8gjw",
		"l": "zh",
		"v": "E:/Project/Python/TachSubVideo/viet_ocr/11.mp4",
		# "v": "E:\Project\Python\TTSfree/vocals.wav",
		"m": 'medium',
		# "md": 'n',
		"md": 'f',
		# "md": 'e',
		# "sp": True,
		# "mw": 8,
		
	})
	
	__key__ = hashlib.sha256(b'33333').digest()
	
	
	def encrypt (raw, key):
		BS = AES.block_size
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
		
		raw = base64.b64encode(pad(raw).encode('utf8'))
		iv = get_random_bytes(AES.block_size)
		cipher = AES.new(key=key, mode=AES.MODE_CFB, iv=iv)
		# print(base64.b64encode(iv + cipher.encrypt(raw)))
		return base64.b64encode(iv + cipher.encrypt(raw))
	
	
	async def ws ():
		async with aiohttp.ClientSession(
				raise_for_status=True
		) as session, session.ws_connect(
			f"ws://localhost:8686/ws/ocr",
			# f"ws://localhost:8686/ws/ai",
			compress=15,
			autoclose=True,
			# autoping=True,
			# proxy=self.proxy,
			# headers=headers,
		) as websocket:
			# print(base64.b64encode(__key__).decode())
			# print(encrypt(payload, __key__).decode())
			
			await websocket.send_json([encrypt(payload, __key__).decode(), base64.b64encode(__key__).decode()])
			async for received in websocket:
				
				if received.type == aiohttp.WSMsgType.TEXT:
					print(json.loads(received.data))
				
				
				elif received.type == aiohttp.WSMsgType.ERROR:
					print(
						"WSMsgType.ERROR", received.data if received.data else "Unknown error"
					)
					await websocket.close()
	
	
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_until_complete(ws())
	