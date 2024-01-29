import base64
import datetime
import json
import os
import time

import requests

from gui.helpers.constants import USER_DATA, TOOL_CODE_MAIN
from gui.helpers.ect import mh_ae, cr_pc
from gui.helpers.func_helper import getValueSettings
from gui.helpers.get_data import URL_API_BASE
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request


class TTSTiengAnhTranslator(BaseTranslator):
	
	
	def __init__ (self, manage_thread_pool, file_json: str, request: Request = Request(), service_url: str = ""):
		self.manage_thread_pool = manage_thread_pool
		self.file_json = file_json
		self.session = request
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
	
	
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
	
	def check_balance (self):
		headers = {"Authorization": f"Bearer {self.user_data['token']}"}
		
		response = requests.get(url=URL_API_BASE + "/tts/private/check-balance?t=tieng_anh", headers=headers)
		# print(response.json())
		if response.status_code == 200:
			return True, response.json().get("data"), 1
		
		return False, "Hết ký tự !", 0
	
	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		# if source_language == "auto":
		source_language = self._language(text)
		
		payload = {
			"text": text,
			"gender": gender,
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		headers = {"Authorization": f"Bearer {self.user_data['token']}"}
		data_encrypt = mh_ae(payload, p_k=self.user_data['paes'])
		
		for i in range(5):
			response = requests.post(url=URL_API_BASE + "/tts/private/tieng-anh", headers=headers, json={
				"data": data_encrypt})
			if response.status_code == 200:
				decoded_bytes = base64.b64decode(response.json().get("data"))
				return source_language, decoded_bytes
		
		return source_language, None
	
	def name (self) -> str:
		return "TTS_Tieng_Anh"
	
	def __str__ (self) -> str:
		return "TTS_Tieng_Anh"


if __name__ == "__main__":
	t = b''
	print(t in ["", b"", None])
	# server = FPTTranslator(api_key="IIeLabQDiOLs7HXwdFdBwwrX2BCMgVAZ")
	# res = server.text_to_speech(gender="minhquangace", text="Phận con trai 12 bến nước, đi làm kiếm tiền vậy mà mụ vk đâu để yên, quét nhà, nấu cơm, Phận con trai 12 bến nước, ")
	#
	# if not res.result is None:
	# 	res.write_to_file("test.mp3")
	# gender = "male-female"
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
	'''
	
	vi-VN-Neural2-A|servicegoo #low
	
	"Nữ - vi-VN-Neural2-A"
	vi-VN-Neural2-D|servicegoo #low
	"Nam - vi-VN-Neural2-D"
	vi-VN-Standard-A|servicegoo
	"Nữ - vi-VN-Standard-A"
	vi-VN-Standard-B|servicegoo
	"Nam - vi-VN-Standard-B"
	vi-VN-Standard-C|servicegoo
	"Nữ - vi-VN-Standard-C"
	vi-VN-Standard-D|servicegoo
	"Nam - vi-VN-Standard-D"
	vi-VN-Wavenet-A|servicegoo
	"Nữ - vi-VN-Wavenet-A"
	vi-VN-Wavenet-B|servicegoo
	"Nam - vi-VN-Wavenet-B"
	vi-VN-Wavenet-C|servicegoo
	"Nữ - vi-VN-Wavenet-C"
	vi-VN-Wavenet-D|servicegoo
	"Nam - vi-VN-Wavenet-D
	'''
	payload = json.dumps({
		"text": 'Chúng tôi đã có ứng dụng ping không gian của chúng tôi và chúng tôi có thể tải xuống từ cửa hàng Android chính thức, nhưng',
		"voiceService": 'servicegoo',
		"voiceID": 'vi-VN-Wavenet-D',
		"voiceSpeed": "0",
		"voicePitch": 'high'
	})
	# headers = {
	# 	'Content-Type': 'application/json',
	# 	"apikey": data_token.get("api-key")
	# }
	# # print(payload)
	# # print(headers)
	# #
	# response = self.session.post("https://ttsfree.com/api/v1/tts", headers=headers, data=payload)
	# if response.json().get("status") == 'success':
	# 	decoded_bytes = base64.b64decode(response.json().get("audioData"))
