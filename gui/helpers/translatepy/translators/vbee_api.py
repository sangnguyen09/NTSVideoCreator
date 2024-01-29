import os
import time

from gui.helpers.constants import STOP_GET_VOICE
from gui.helpers.func_helper import is_file_audio
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request
import requests
import json


class VBeeAPITranslator(BaseTranslator):
	
	
	def __init__ (self, manage_thread_pool, file_json: str):
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.tts_fail = {}
		self.file_json = file_json
		self.session = Request()
		self.is_stop = False
		
		self.row_number = False
	def _resultThread (self, id_worker, id_thread, result):
		if id_thread == STOP_GET_VOICE:
			# print(result)
			row_number = result
			self.tts_fail[row_number] = True
	
	def _language (self, text: str) -> str:
		params = {"client": "gtx", "dt": "t", "sl": "auto", "tl": "ja", "q": text}
		request = self.session.get("https://translate.googleapis.com/translate_a/single", params=params)
		response = request.json()
		if request.status_code < 400:
			return response[2]
		
		params = {"client": "dict-chrome-ex", "sl": "auto", "tl": "ja", "q": text}
		request = self.session.get("https://clients5.google.com/translate_a/t", params=params)
		response = request.json()
		if request.status_code < 400:
			return response['ld_result']["srclangs"][0]
	
	def _language_normalize (self, language: Language):
		if language.id == "zho":
			return "zh-CN"
		elif language.id == "och":
			return "zh-TW"
		return language.alpha2
	
	def _language_denormalize (self, language_code):
		if str(language_code).lower() == "zh-cn":
			return Language("zho")
		elif str(language_code).lower() == "zh-tw":
			return Language("och")
		return Language(language_code)
	
	def check_token (self):
		return True, "Ok"
	
	def save_config_json (self, data):
		# filename = JOIN_PATH(PATH_DB,"fpt.json")
		filename = self.file_json
		if not os.path.exists(filename):
			with open(filename, 'w') as openfile:
				openfile.write(json.dumps([]))
		with open(filename, 'w') as openfile:
			openfile.write(json.dumps(data))
	
	def check_balance (self):
		try:
			if os.path.exists(self.file_json):
				with open(self.file_json, "r") as file:
					token = json.load(file)
				# print(token)
				if not isinstance(token, dict):
					return False, "Bạn chưa nhập API vào file json", 0
				
				if token.get("token") is None and token.get("app_id") is None:
					return False, "File Json Không Đúng Định Dạng"
				
				self.list_token_active = token
				return True, -1, 1
			
			else:
				return False, "File Json Không Tồn Tại", 0
		except:
			return False, "File Token Sai Hoặc Hết Hạn", 0
	
	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		# self.row_number = kwargs.get('row_number')
		
		# if self.is_stop is False:
		# if source_language == "auto":
		# 	source_language = self._language(text)
		
		# print(text)
		token = self.list_token_active
		payload = {
			"app_id": token.get("app_id"),
			"response_type": "direct",
			"input_text": text,
			"voice_code": gender,
			"audio_type": "wav",
			# "bitrate": 128,
			# "speed_rate": "1.0"
		}
		
		url = "https://vbee.vn/api/v1/tts"
		headers = {
			'Authorization': f'Bearer {token.get("token")}',
			'Content-Type': 'application/json',
		}
		session = requests.Session()
		for i in range(0, 10):
			if self.tts_fail.get(kwargs.get('row_number', 0)):
				raise Exception
			response = session.post(url, headers=headers, json=payload)
			# print(response.content)
			if response.status_code == 200:
				# finished = False
				data = response.json()
				# print(data)
				if data.get('status') == 1:
					
					res = session.get(data.get('result').get('audio_link'))
					if res.status_code == 200:
						if is_file_audio(res.content):
							return source_language, res.content
			
			time.sleep(1)
		
		return source_language, None
		# else:
			# raise Exception
	
	def _resultThreadChanged (self, id_worker, id_thread, result):
		
		if id_thread == STOP_GET_VOICE and self.row_number == result:
			self.is_stop = True
	
	def name (self) -> str:
		return "VBEE"
	
	def __str__ (self) -> str:
		return "VBEE"


if __name__ == "__main__":
	# server = FPTTranslator(api_key="IIeLabQDiOLs7HXwdFdBwwrX2BCMgVAZ")
	# res = server.text_to_speech(gender="minhquangace", text="Phận con trai 12 bến nước, đi làm kiếm tiền vậy mà mụ vk đâu để yên, quét nhà, nấu cơm, Phận con trai 12 bến nước, ")
	#
	# if not res.result is None:
	# 	res.write_to_file("test.mp3")
	gender = "male-female"
	# region, model = gender.split("-")
	# with open('E:\Project\Python\ReviewPhim\\vnpt.json', "r") as file:
	# 	data_token = json.load(file)
	# ddd = {'message': 'IDG-00000000', 'object': {'ai_version': '1.0', 'code': 'success', 'playlist': [
	# 	{'audio_link': 'https://idg-obs.vnpt.vn/text-speech/20230514/tts/8488e881705c45b68e909a945468a904.wav',
	# 	 'idx': '0', 'text': 'We patch rooting detections, certificate pinning.', 'text_len': 49, 'total': '1'}],
	# 											 'r_audio_full': '', 'r_audio_full_finished': False,
	# 											 'text_id': '8c521911ea57b91a86464503db62d38e', 'text_len': 49,
	# 											 'version': '1.0.0'}}
	# print(ddd['object'])
	
	url = "https://vbee.vn/api/v1/synthesis"
	
	payload = json.dumps({
		"audioType": "wav",
		"bitrate": 128000,
		"backgroundMusic": {
			"volume": 80
		},
		"text": "Bôi đen cụm từ để nghe thử",
		"voiceCode": "hn_female_ngochuyen_full_48k-fhg",
		"speed": 1
	})
	headers = {
		'Accept': 'application/json, text/plain, */*',
		'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
		'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmRzE4X1Z1TGRTQ2tFbHlIS0g0NEY1WGNHd1dXUG1zbXRydnJBaXV2b2JzIn0.eyJleHAiOjE2ODcwODMxMDEsImlhdCI6MTY4Njk5NjcwMSwiYXV0aF90aW1lIjoxNjg2OTk2NjQ1LCJqdGkiOiI3OTYyZjg5NC02OTY1LTRkNGEtOTEyNi1iYTkwNzUyYTQ2NGYiLCJpc3MiOiJodHRwczovL2FjY291bnRzLnZiZWUudm4vYXV0aC9yZWFsbXMvdmJlZS1ob2xkaW5nIiwiYXVkIjoiYWNjb3VudCIsInN1YiI6ImQxN2I3ZDQ4LWQ1NTEtNDc0ZS04MWY1LTRjMDVjMDE2ZmFjZiIsInR5cCI6IkJlYXJlciIsImF6cCI6InZiZWUtdHRzLWNybSIsIm5vbmNlIjoiYjFhMzhkYmQtMmJhNS00YTkxLTg3M2YtYTJiZWY3NzJkNWMyIiwic2Vzc2lvbl9zdGF0ZSI6ImI3MmI5MzYwLTA5NDctNGVkNS1iNWJkLTNlMDc1YWIxNDliNyIsImFjciI6IjAiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly92YmVlLnZuIiwiaHR0cHM6Ly9ob21lLnZiZWUudm4iLCJodHRwczovL2FwaS52YmVlLnZuIiwiaHR0cHM6Ly9zdHVkaW8udmJlZS52biIsImh0dHBzOi8vd3d3LnZiZWUudm4iLCJodHRwOi8vbG9jYWxob3N0OjMwMDAiXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImRlZmF1bHQtcm9sZXMtdmJlZS1ob2xkaW5nIiwib2ZmbGluZV9hY2Nlc3MiLCJ1bWFfYXV0aG9yaXphdGlvbiJdfSwicmVzb3VyY2VfYWNjZXNzIjp7ImFjY291bnQiOnsicm9sZXMiOlsibWFuYWdlLWFjY291bnQiLCJtYW5hZ2UtYWNjb3VudC1saW5rcyIsInZpZXctcHJvZmlsZSJdfX0sInNjb3BlIjoib3BlbmlkIGVtYWlsIHByb2ZpbGUiLCJzaWQiOiJiNzJiOTM2MC0wOTQ3LTRlZDUtYjViZC0zZTA3NWFiMTQ5YjciLCJpZGVudGl0eV9wcm92aWRlciI6ImVtYWlsIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImlwIjoiMTcxLjIzNS45Mi4xNjMiLCJuYW1lIjoic2FuZ2N0YTg2IiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2FuZ2N0YTg2QGdtYWlsLmNvbSIsImdpdmVuX25hbWUiOiJzYW5nY3RhODYiLCJlbWFpbCI6InNhbmdjdGE4NkBnbWFpbC5jb20ifQ.bUnz_6U5UVhnrVwCUtQYBswZxfxH_0r8lAE_4clbDRWYwsy7TzANUZh0uXqzqTr6TaHn7D9POCVe5PSG-c4FYxaR1hCDQQsTeIr6divrL-DeYfjMAtq6co6NpflU8MWQAKZX6xqTQt49eErf2KqhyoKMVpLyktl0DjuruXWyACTyJWoCLL_jIlNpmw0Pj4w5PPpfK4pR9HL31dR50Y0DuWg-cqz6-AGpH5kjyKru56_qfL2W-yQkNbx-z5kX46ofxG5AuedrdJW1vfgKOlCRslEiQtctYvRzOE0YkKj05V9qQMUT5UXz2G0M5d-jYuvcGXWYKgWslbiVcysfu--NDg',
		'Connection': 'keep-alive',
		'Content-Type': 'application/json',
		'Origin': 'https://studio.vbee.vn',
		'Referer': 'https://studio.vbee.vn/',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-site',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
		'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"'
	}
	
	response = requests.request("POST", url, headers=headers, data=payload)
	
	print(response.text)
