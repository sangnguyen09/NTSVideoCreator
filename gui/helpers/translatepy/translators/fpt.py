import json
import os
import random
import time

import requests

from gui.helpers.constants import STOP_GET_VOICE
from gui.helpers.func_helper import is_file_audio
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request


class FPTTranslator(BaseTranslator):
	
	def __init__ (self, manage_thread_pool, file_json: str, request: Request = Request(),
				  service_url: str = "https://api.fpt.ai/hmi/tts/v5", ):
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.tts_fail = {}
		self.request_429 = {}
		self.file_json = file_json
		self.list_token_active = None
		self.is_stop = False
		self.row_number = False
		self.session = request
		self.service_url = service_url
	
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
	
	def check_tokenv1 (self):
		try:
			if os.path.exists(self.file_json):
				with open(self.file_json, "r") as file:
					list_data_token = json.load(file)
				if len(list_data_token) == 0:
					return False, "Bạn chưa lấy token, hãy bấm nút LẤY TOKEN"
				# total_token = 0
				token_active = []
				list_api_key = []
				for data_token in list_data_token:
					if data_token.get("email") is None or data_token.get("project-id") is None or data_token.get(
							"user-agent") is None or data_token.get("api-key") is None or data_token.get(
						"access-token") is None:
						return False, "File Json Không Đúng Định Dạng"
					list_api_key.append(data_token.get("api-key"))
					
					# url = f"https://backend.fpt.ai/api/projects/{}/credentials"
					url = f"https://voicemaker.fpt.ai/api/tts-info"
					token = data_token.get("access-token")
					cookie = token.replace("Bearer ", "")
					user_agent = data_token.get("user-agent")
					project_id = data_token.get("project-id")
					data = {'projectID': project_id}
					headers = {
						'authority': 'voicemaker.fpt.ai',
						'accept': 'application/json, text/plain, */*',
						'accept-language': 'vi,fr-FR;q=0.9,fr;q=0.8,en-US;q=0.7,en;q=0.6',
						'authorization': token,
						'content-type': 'application/json;charset=UTF-8',
						'cookie': f'jwToken={cookie}',
						'origin': 'https://voicemaker.fpt.ai',
						'referer': 'https://voicemaker.fpt.ai/',
						'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
						'sec-ch-ua-mobile': '?0',
						'sec-ch-ua-platform': '"Windows"',
						'sec-fetch-dest': 'empty',
						'sec-fetch-mode': 'cors',
						'sec-fetch-site': 'same-origin',
						'user-agent': user_agent
					}
					
					response = self.session.post(url, headers=headers, json=data)
					if response.status_code > 200:
						continue
					else:
						token_active.append(data_token)
				# total_token += 1
				if len(token_active) == 0:
					return False, "Tất cả token đã hết hạn! Bấm nút LẤY TOKEN để lấy lại"
				self.list_token_active = token_active
				
				self.save_config_json(token_active)
				return True, "ok"
			else:
				return False, "File Json FPT không tồn tại !"
		except:
			return False, "File Json FPT không đúng định dạng !"
	
	def check_balancev1 (self):
		try:
			if os.path.exists(self.file_json):
				with open(self.file_json, "r") as file:
					list_data_token = json.load(file)
				if len(list_data_token) == 0:
					return False, "Bạn chưa lấy token, hãy bấm nút LẤY TOKEN", ""
				token_active = []
				total_character = 0
				for data_token in list_data_token:
					if data_token.get("email") is None or data_token.get("project-id") is None or data_token.get(
							"user-agent") is None or data_token.get("api-key") is None or data_token.get(
						"access-token") is None:
						return False, "File Json Không Đúng Định Dạng", ""
					
					# url = f"https://backend.fpt.ai/api/projects/{data_token.get('project-id')}/api-remaining/646f356f-d470-43f6-b8ca-84056cb40f62"
					url = f"https://voicemaker.fpt.ai/api/tts-info"
					token = data_token.get("access-token")
					cookie = token.replace("Bearer ", "")
					user_agent = data_token.get("user-agent")
					project_id = data_token.get("project-id")
					data = {'projectID': project_id}
					headers = {
						'authority': 'voicemaker.fpt.ai',
						'accept': 'application/json, text/plain, */*',
						'accept-language': 'vi,fr-FR;q=0.9,fr;q=0.8,en-US;q=0.7,en;q=0.6',
						'authorization': token,
						'content-type': 'application/json;charset=UTF-8',
						'cookie': f'jwToken={cookie}',
						'origin': 'https://voicemaker.fpt.ai',
						'referer': 'https://voicemaker.fpt.ai/',
						'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
						'sec-ch-ua-mobile': '?0',
						'sec-ch-ua-platform': '"Windows"',
						'sec-fetch-dest': 'empty',
						'sec-fetch-mode': 'cors',
						'sec-fetch-site': 'same-origin',
						'user-agent': user_agent
					}
					
					response = self.session.post(url, headers=headers, json=data)
					
					if response.status_code > 200:
						continue
					else:
						token_active.append(data_token)
						for value in response.json().get('remain').values():
							total_character += value.get('remaining')
				
				self.list_token_active = token_active
				self.save_config_json(token_active)
				return True, total_character, len(token_active)
			
			else:
				return False, "File Json Không Tồn Tại", 0
		except:
			return False, "File Token Sai Hoặc Hết Hạn", 0
	
	def _text_to_speech1 (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		self.row_number = kwargs.get('row_number')
		if self.is_stop is False:
			if source_language == "auto":
				source_language = self._language(text)
			for i in range(5):
				# headers = {'api-key': random.choice(self.list_api_key),
				# 		   'speed': '0',
				# 		   'voice': gender}
				# print(headers)
				# print(text)
				acc_random = random.choice(self.list_token_active)
				token = acc_random.get("access-token")
				cookie = token.replace("Bearer ", "")
				user_agent = acc_random.get("user-agent")
				project_id = acc_random.get("project-id")
				email = acc_random.get("email")
				
				time.sleep(random.randrange(3, 8))
				headers = {
					'authority': 'voicemaker.fpt.ai',
					'accept': 'application/json, text/plain, */*',
					'accept-language': 'vi,fr-FR;q=0.9,fr;q=0.8,en-US;q=0.7,en;q=0.6',
					'authorization': token,
					'content-type': 'application/json;charset=UTF-8',
					'cookie': f'jwToken={cookie}',
					'origin': 'https://voicemaker.fpt.ai',
					'referer': 'https://voicemaker.fpt.ai/',
					'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
					'sec-ch-ua-mobile': '?0',
					'sec-ch-ua-platform': '"Windows"',
					'sec-fetch-dest': 'empty',
					'sec-fetch-mode': 'cors',
					'sec-fetch-site': 'same-origin',
					'user-agent': user_agent
				}
				# print(headers)
				# print(text)
				# time.sleep(random.randrange(3, 8))
				json_data = {
					"voices": [
						gender
					],
					"speed": "0",
					"content": [
						{
							"type": "paragraph",
							"content": [
								{
									"type": "text",
									"text": text
								}
							]
						}
					],
					"modelName": email,
					"projectID": project_id
				}
				response = self.session.post("https://voicemaker.fpt.ai/api/tts-plus/generate-audio", headers=headers,
					json=json_data)
				# response = self.session.post("https://api.fpt.ai/hmi/tts/v5", headers=headers, data=(text.encode('utf-8')))
				# print(response.json())
				data = response.json()
				if not data.get('message') == "success":
					continue
				# finished = False
				content = ""
				while True:
					res = self.session.get(data.get('links')[0])
					if res.status_code == 200 and not res.content == b'':
						# print("get ok")
						return source_language, res.content
					time.sleep(5)
			
			return source_language, None
		else:
			raise Exception
	
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
					list_data_token = json.load(file)
				if len(list_data_token) < 1:
					return False, "Bạn chưa nhập API vào file json", 0
				
				self.list_token_active = list_data_token
				return True, -1, 1
			
			else:
				return False, "File Json Không Tồn Tại", 0
		except:
			return False, "File Token Sai Hoặc Hết Hạn", 0
	
	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		
		row_number = kwargs.get('row_number', 0)
		for i in range(15):
			if self.tts_fail.get(row_number):
				raise Exception
			if self.request_429.get(row_number):
				time.sleep(random.randrange(3, 8))
			
			headers = {'api-key': random.choice(self.list_token_active),
					   'speed': '0',
					   'voice': gender}
			try:
				response = requests.post("https://api.fpt.ai/hmi/tts/v5", headers=headers, data=(
					text.encode('utf-8')))
				if response.status_code == 429:
					self.request_429[row_number] = True
				# time.sleep(random.randrange(3, 8))
				if response.status_code == 200:
					if response.json().get('error') == 0:
						for i in range(300):
							if self.tts_fail.get(row_number):
								raise Exception
							res = requests.get(response.json()['async'])
							if res.status_code == 200:
								if self.request_429.get(row_number):
									self.request_429[row_number] = False
								if is_file_audio(res.content):
									return source_language, res.content
							time.sleep(1)
				
				time.sleep(random.randrange(3, 8))
			except:
				time.sleep(1)
		
		return source_language, None
	
	def _resultThreadChanged (self, id_worker, id_thread, result):
		
		if id_thread == STOP_GET_VOICE and self.row_number == result:
			self.is_stop = True
	
	def name (self) -> str:
		return "FPT"
	
	def __str__ (self) -> str:
		return "FPT"


