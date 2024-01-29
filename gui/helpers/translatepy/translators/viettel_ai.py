import datetime
import json
import os
import random
import time

from gui.helpers.constants import STOP_GET_VOICE
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request


class ViettelAITranslator(BaseTranslator):
	
	
	def __init__ (self, manage_thread_pool, file_json: str, request: Request = Request(), service_url: str = ""):
		self.manage_thread_pool = manage_thread_pool
		self.file_json = file_json
		self.api_key = None
		self.session = request
		self.is_stop = False
		self.row_number = False
		self.service_url = service_url
	
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
		# try:
			if os.path.exists(self.file_json):
				with open(self.file_json, "r") as file:
					list_data_token = json.load(file)
				if len(list_data_token) == 0:
					return False, "Bạn chưa lấy token, hãy bấm nút LẤY TOKEN"
				# total_token = 0
				token_active = []
				list_api_key = []
				for data_token in list_data_token:
					if data_token.get("api-key") is None or data_token.get("user-agent") is None or data_token.get("access-token") is None:
						return False, "File Json Không Đúng Định Dạng"
					list_api_key.append(data_token.get("api-key"))
					url = "https://viettelai.vn/_backend/api/token/listing"
					
					payload = json.dumps({
						"page": 1,
						"itemsPerPage": 10,
						"sortBy": [
							"created_at"
						],
						"sortDesc": [
							True
						],
						"groupBy": [],
						"groupDesc": [],
						"mustSort": False,
						"multiSort": False,
						"word": None
					})
					headers = {
						'Accept': 'application/json, text/plain, */*',
						'Accept-Language': 'vi',
						'Authorization': data_token.get("access-token"),
						'Connection': 'keep-alive',
						'Referer': 'https://viettelai.vn/dashboard/my-service',
						'Sec-Fetch-Dest': 'empty',
						'Sec-Fetch-Mode': 'cors',
						'Sec-Fetch-Site': 'same-origin',
						'User-Agent': data_token.get("user-agent"),
						'X-KL-Ajax-Request': 'Ajax_Request',
						'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
						'sec-ch-ua-mobile': '?0',
						'sec-ch-ua-platform': '"Windows"'
					}
					
					response = self.session.post(url, headers=headers, data=payload)
					
					if response.status_code > 200:
						continue
					else:
						token_active.append(data_token)
				
				self.list_api_key = list_api_key
				# total_token += 1
				if len(token_active) == 0:
					return False, "Tài khoản hoặc token đã hết hạn"
				self.save_config_json(token_active)
				return True, "ok"
			
			else:
				return False, "File Json không tồn tại !"
		# except:
		# 	return False, "File Json không đúng định dạng !"
	
	def save_config_json (self, data):
		# filename = JOIN_PATH(PATH_DB,"fpt.json")
		filename = self.file_json
		if not os.path.exists(filename):
			with open(filename, 'w') as openfile:
				openfile.write(json.dumps([]))
		with open(filename, 'w') as openfile:
			openfile.write(json.dumps(data))
	
	
	def check_balancev1 (self):
		try:
			if os.path.exists(self.file_json):
				with open(self.file_json, "r") as file:
					list_data_token = json.load(file)
				if len(list_data_token) == 0:
					return False, "Bạn chưa lấy token, hãy bấm nút LẤY TOKEN", ""
				token_active = []
				total_character = 0
				# print(list_data_token)

				for data_token in list_data_token:
					if data_token.get("user-agent") is None or data_token.get("api-key") is None or data_token.get("access-token") is None:
						return False, "File Json Không Đúng Định Dạng", ""
					
					url = f"https://viettelai.vn/_backend/api/auth/me"
					headers = {
						'Accept': 'application/json, text/plain, */*',
						'Accept-Language': 'vi',
						'Authorization': data_token.get("access-token"),
						'Connection': 'keep-alive',
						'Referer': 'https://viettelai.vn/dashboard/my-service',
						'Sec-Fetch-Dest': 'empty',
						'Sec-Fetch-Mode': 'cors',
						'Sec-Fetch-Site': 'same-origin',
						'User-Agent': data_token.get("user-agent"),
						'X-KL-Ajax-Request': 'Ajax_Request',
						'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
						'sec-ch-ua-mobile': '?0',
						'sec-ch-ua-platform': '"Windows"'
					}
					response = self.session.get(url, headers=headers)
					# print(response.json())
					if response.status_code > 200:
						continue
					else:
						for value in response.json().get('user').get("using_limit"):
							if value.get('package').get('service_category').get('name') == "TTS":

								if int(value.get("expired_at")) < time.time() * 1000:
									continue
								total_character += value.get('remaining_units')
								token_active.append(data_token)
				
				self.save_config_json(token_active)
				# if len(token_active) == 0:
				# 	return False, "Tài khoản hoặc token đã hết hạn"
				return True, total_character, len(token_active)
			else:
				return False, "File Json Không Tồn Tại", 0
		except:
			return False, "File Token Sai Hoặc Hết Hạn", 0
	
	def _text_to_speechv1 (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		self.row_number = kwargs.get('row_number')
		if self.is_stop is False:
			if source_language == "auto":
				source_language = self._language(text)
			while True:
				payload = json.dumps({
					"text": text,
					"voice": gender,
					"speed": 1,
					"tts_return_option": 2,
					"token": random.choice(self.list_api_key),
					"without_filter": False
				})
				headers = {
					'accept': '*/*',
					'Content-Type': 'application/json'
				}
				
				response = self.session.post("https://viettelai.vn/tts/speech_synthesis", headers=headers, data=payload)
				# print(response.content)
				if response.status_code == 403:
					return source_language, None
				
				if response.status_code > 200:
					time.sleep(1)
					continue
				#
				# elif response.json().get('code')>200:
				# 	time.sleep(1)
				# 	continue
				elif response.content == b'':
					time.sleep(1)
					continue
				
				return source_language, response.content
			
			return source_language, None
		else:
			raise Exception
		
	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		self.row_number = kwargs.get('row_number')
		if self.is_stop is False:
			# if source_language == "auto":
			# 	source_language = self._language(text)
			for i in range(5):
				payload = json.dumps({
					"text": text,
					"voice": gender,
					"speed": 1,
					"tts_return_option": 2,
					"token": random.choice(self.list_api_key),
					"without_filter": False
				})
				headers = {
					'accept': '*/*',
					'Content-Type': 'application/json'
				}
				
				response = self.session.post("https://viettelai.vn/tts/speech_synthesis", headers=headers, data=payload)
				# print(response.content)
				if response.status_code == 403:
					return source_language, None
				
				if response.status_code > 200:
					time.sleep(1)
					continue
	 
				elif response.content == b'':
					time.sleep(1)
					continue
				
				return source_language, response.content
			
			return source_language, None
		else:
			raise Exception
	def check_token (self):
		return True, "Ok"
	
	def check_balance (self):
		try:
			if os.path.exists(self.file_json):
				with open(self.file_json, "r") as file:
					list_data_token = json.load(file)
				if len(list_data_token) < 1:
					return False, "Bạn chưa nhập API vào file json", 0
				
				self.list_api_key = list_data_token
				return True, -1, 1
			
			else:
				return False, "File Json Không Tồn Tại", 0
		except:
			return False, "File Token Sai Hoặc Hết Hạn", 0
	def _resultThreadChanged (self, id_worker, id_thread, result):
		
		if id_thread == STOP_GET_VOICE and self.row_number == result:
			self.is_stop = True
	
	
	def name (self) -> str:
		return "VIETTEL_AI"
	
	def __str__ (self) -> str:
		return "VIETTEL_AI"


if __name__ == "__main__":
	# pass
	print(datetime.datetime.fromtimestamp(1687447264258 / 1000))
	
	'1687856470.602868'
	print()
	token =  [{'api-key': '73aa1651d8b1f5331a4c714e584d7ef5', 'access-token': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC92aWV0dGVsYWkudm5cL2FwaVwvYXV0aFwvbG9naW4iLCJpYXQiOjE2ODc4NTU1MjcsImV4cCI6MTY4Nzk0MTkyNywibmJmIjoxNjg3ODU1NTI3LCJqdGkiOiJHOWowOHNNbEtkaGt6VjFSIiwic3ViIjoyODQ2MiwicHJ2IjoiODdlMGFmMWVmOWZkMTU4MTJmZGVjOTcxNTNhMTRlMGIwNDc1NDZhYSJ9.5iXviKpeA_3hSUR9kURn2fpKMpMiDFd7W6HAikWfigo', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}]
	
	# for data_token in token:
		
		# if data_token.get("api-key") is None or data_token.get("user-agent") is None or data_token.get("access-token") is None:
		

# server = FPTTranslator(api_key="IIeLabQDiOLs7HXwdFdBwwrX2BCMgVAZ")
# res = server.text_to_speech(gender="minhquangace", text="Phận con trai 12 bến nước, đi làm kiếm tiền vậy mà mụ vk đâu để yên, quét nhà, nấu cơm, Phận con trai 12 bến nước, ")

# if not res.result is None:
# 	res.write_to_file("test.mp3")
