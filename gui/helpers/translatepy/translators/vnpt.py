import datetime
import json
import os

from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request


class VNPTTranslator(BaseTranslator):
	
	
	def __init__ (self,manage_thread_pool, file_json: str, request: Request = Request(), service_url: str = "https://api.idg.vnpt.vn"):
		self.manage_thread_pool = manage_thread_pool
		self.file_json = file_json
		self.session = request
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
					data_token = json.load(file)
	
				if data_token.get("token-id") is None or data_token.get("token-key") is None or data_token.get("access-token") is None:
					return False, "File Json Không Đúng Định Dạng"
	 
				headers = {
					'Content-Type': 'application/json',
					'Authorization': data_token.get("access-token"),
					'Token-id': data_token.get("token-id"),
					'Token-key': data_token.get("token-key")
				}
				
				now = datetime.datetime.now()
				url = f"https://api.idg.vnpt.vn/report-service/v1/characters/status?tokenId={data_token.get('token-id')}&fromDate={now.day}/{now.month}/{now.year}&toDate={now.day}/{now.month}/{now.year}"
				response = self.session.get(url, headers=headers)
				
				if response.status_code > 200:
					return False, "Token không đúng hoặc hết hạn !"
				else:
					return True, "Ok"
			else:
				return False, "File Json VNPT không tồn tại !"
		except:
			return False, "File Json VNPT không đúng định dạng !"
		
	def check_balance (self):
		try:
			if os.path.exists(self.file_json):
				with open(self.file_json, "r") as file:
					data_token = json.load(file)
				if data_token.get("token-id") is None or data_token.get("token-key") is None or data_token.get("access-token") is None:
					return False, "Bạn chưa lấy token", ""
				headers = {
					'Accept': 'application/json, text/plain, */*',
					'Content-Type': 'application/json',
					'Authorization': data_token.get("access-token"),
					'Token-id': data_token.get("token-id"),
					'Token-key': data_token.get("token-key")
				}
				now = datetime.datetime.now()
				url = f"https://api.idg.vnpt.vn/report-service/v1/characters/status?tokenId={data_token.get('token-id')}&fromDate={now.day}/{now.month}/{now.year}&toDate={now.day}/{now.month}/{now.year}"
				response = self.session.get(url, headers=headers)
				
				if response.status_code > 200:
					return False, 0,0
				else:
					return True, response.json().get('object').get('available'),1
		
			else:
				return False, "File Json Không Tồn Tại", 0
		except:
			return False, "File Token Sai Hoặc Hết Hạn", 0
	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		if source_language == "auto":
			source_language = self._language(text)
		
		with open(self.file_json, "r") as file:
			data_token = json.load(file)
		
		region, model = gender.split("-")
		# print(region , model )
		payload = json.dumps({
			"text": text,
			"text_split": False,
			"model": model,
			"speed": "1",
			"region": region
		})
		headers = {
			'Content-Type': 'application/json',
			'Authorization': data_token.get("access-token"),
			'Token-id': data_token.get("token-id"),
			'Token-key': data_token.get("token-key")
		}
		
		response = self.session.post(self.service_url + "/tts-service/v1/standard", headers=headers, data=payload)
		if response.status_code == 200:
			# finished = False
			text_id = response.json().get("object").get("text_id")
			# print(text_id)
			payload = json.dumps({
				"text_id": text_id
			})
			content = ''
			while True:
				res = self.session.post(self.service_url + "/tts-service/v1/check-status", headers=headers, data=payload)
				
				if res.status_code == 200:
					# print(res.json())
					
					link_audio = res.json().get("object").get("playlist")[0].get("audio_link")
					
					res = self.session.get(link_audio)
					content = res.content
					break
			# print("link_audio")
			
			return source_language, content
		
		return source_language, None
	
	def name (self) -> str:
		return "VNPT"
	def __str__ (self) -> str:
		return "VNPT"


if __name__ == "__main__":
	# server = FPTTranslator(api_key="IIeLabQDiOLs7HXwdFdBwwrX2BCMgVAZ")
	# res = server.text_to_speech(gender="minhquangace", text="Phận con trai 12 bến nước, đi làm kiếm tiền vậy mà mụ vk đâu để yên, quét nhà, nấu cơm, Phận con trai 12 bến nước, ")
	#
	# if not res.result is None:
	# 	res.write_to_file("test.mp3")
	gender = "male-female"
	region, model = gender.split("-")
	with open('E:\Project\Python\ReviewPhim\\vnpt.json', "r") as file:
		data_token = json.load(file)
	ddd = {'message': 'IDG-00000000', 'object': {'ai_version': '1.0', 'code': 'success', 'playlist': [
		{'audio_link': 'https://idg-obs.vnpt.vn/text-speech/20230514/tts/8488e881705c45b68e909a945468a904.wav',
		 'idx': '0', 'text': 'We patch rooting detections, certificate pinning.', 'text_len': 49, 'total': '1'}],
												 'r_audio_full': '', 'r_audio_full_finished': False,
												 'text_id': '8c521911ea57b91a86464503db62d38e', 'text_len': 49,
												 'version': '1.0.0'}}
	print(ddd['object'])
