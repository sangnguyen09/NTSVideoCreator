import json
import os
import random
import string
import time

from gui.helpers.constants import STOP_GET_VOICE
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request


class ViettelGroupTranslator(BaseTranslator):
	
	
	def __init__ (self, manage_thread_pool, file_json: str, request: Request = Request(), service_url: str = ""):
		self.manage_thread_pool = manage_thread_pool
		self.file_json = file_json
		self.api_key = None
		self.session = request
		self.list_api_key=[]
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
	
	def check_token (self):
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
					if data_token.get("api-key") is None or data_token.get("user-agent") is None or data_token.get("access-token") is None or data_token.get("cookies") is None or data_token.get("user_id") is None:
						
						return False, "File Json Không Đúng Định Dạng"
					list_api_key.append(data_token.get("api-key"))
					url = "https://viettelgroup.ai/api/token/list"
					
					headers = {
						'Accept': '*/*',
						'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
						'Connection': 'keep-alive',
						'Content-Length': '0',
						'Cookie': data_token.get("cookies"),
						'Origin': 'https://viettelgroup.ai',
						'Referer': 'https://viettelgroup.ai/dashboard',
						'Sec-Fetch-Dest': 'empty',
						'Sec-Fetch-Mode': 'cors',
						'Sec-Fetch-Site': 'same-origin',
						'User-Agent': data_token.get("user-agent"),
						'X-XSRF-TOKEN': data_token.get("access-token"),
						'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
						'sec-ch-ua-mobile': '?0',
						'sec-ch-ua-platform': '"Windows"'
					}
					
					response = self.session.post(url, headers=headers, json={"user_id":data_token.get("user_id")})
					
					if response.status_code > 200:
						continue
					else:
						token_active.append(data_token)
				
				self.list_api_key = list_api_key
				# total_token += 1
				if len(token_active) == 0:
					return False, "Tất cả token đã hết hạn! Bấm nút LẤY TOKEN để lấy lại"
				self.save_config_json(token_active)
				return True, "ok"
			
			else:
				return False, "File Json không tồn tại !"
		except:
			return False, "File Json không đúng định dạng !"
	
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
				if len(list_data_token) == 0:
					return False, "Bạn chưa lấy token, hãy bấm nút LẤY TOKEN", ""
				token_active = []
				total_character = 0
				for data_token in list_data_token:
					if data_token.get("api-key") is None or data_token.get("user-agent") is None or data_token.get("access-token") is None or data_token.get("cookies") is None or data_token.get("user_id") is None:
						return False, "File Json Không Đúng Định Dạng", ""
					
					headers = {
						'Accept': '*/*',
						'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
						'Connection': 'keep-alive',
						'Content-Length': '0',
						'Cookie': data_token.get("cookies"),
						'Origin': 'https://viettelgroup.ai',
						'Referer': 'https://viettelgroup.ai/dashboard',
						'Sec-Fetch-Dest': 'empty',
						'Sec-Fetch-Mode': 'cors',
						'Sec-Fetch-Site': 'same-origin',
						'User-Agent': data_token.get("user-agent"),
						'X-XSRF-TOKEN': data_token.get("access-token"),
						'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
						'sec-ch-ua-mobile': '?0',
						'sec-ch-ua-platform': '"Windows"'
					}
					
					response = self.session.post('https://viettelgroup.ai/api/user/info', headers=headers)
					
					if response.status_code > 200:
						continue
					else:
						token_active.append(data_token)
						for value in response.json().get('data').get("remains"):
							if value.get("service_categories_id") == 1:
								total_character += value.get('remain')
				self.save_config_json(token_active)
				return True, total_character, len(token_active)
			else:
				return False, "File Json Không Tồn Tại", 0
		except:
			return False, "File Token Sai Hoặc Hết Hạn", 0
	
	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		self.row_number = kwargs.get('row_number')
		if self.is_stop is False:
			if source_language == "auto":
				source_language = self._language(text)
			while True:
				payload = json.dumps({
					"text": text,
					"voice": gender,
					"speed": 1,
					"id": ''.join(random.choices(string.ascii_uppercase + string.digits, k=8)),
					"tts_return_option": 2,
					"without_filter": False
				})
				headers = {
					'Content-Type': 'application/json',
					"token": random.choice(self.list_api_key),
				}
				
				response = self.session.post("https://viettelgroup.ai/voice/api/tts/v1/rest/syn", headers=headers, data=payload)
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
	
	def _resultThreadChanged (self, id_worker, id_thread, result):
		
		if id_thread == STOP_GET_VOICE and self.row_number == result:
			self.is_stop = True
	
	
	def name (self) -> str:
		return "VIETTEL_GROUP"
	
	def __str__ (self) -> str:
		return "VIETTEL_GROUP"


if __name__ == "__main__":
	pass
# server = FPTTranslator(api_key="IIeLabQDiOLs7HXwdFdBwwrX2BCMgVAZ")
# res = server.text_to_speech(gender="minhquangace", text="Phận con trai 12 bến nước, đi làm kiếm tiền vậy mà mụ vk đâu để yên, quét nhà, nấu cơm, Phận con trai 12 bến nước, ")

# if not res.result is None:
# 	res.write_to_file("test.mp3")
