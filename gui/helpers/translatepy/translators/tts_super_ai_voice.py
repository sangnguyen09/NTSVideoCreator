import base64
import time

import requests

from gui.helpers.constants import USER_DATA, TOOL_CODE_MAIN, STOP_GET_VOICE
from gui.helpers.ect import cr_pc, mh_ae
from gui.helpers.func_helper import getValueSettings
from gui.helpers.get_data import URL_API_BASE
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request


class TTSSuperAiVoice(BaseTranslator):
	
	
	def __init__ (self, manage_thread_pool, file_json: str, request: Request = Request(), service_url: str = ""):
		self.manage_thread_pool = manage_thread_pool
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.tts_fail = {}
		self.file_json = file_json
		self.session = request
		self.user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
	
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
	
	def check_balance (self):
		headers = {"Authorization": f"Bearer {self.user_data['token']}"}
		payload = {
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		response = requests.post(url=URL_API_BASE + "/tts/private/check-balance/super-ai-voice", headers=headers, json={
			"data": mh_ae(payload, p_k=self.user_data['paes'])})
		# print(response.json())
		if response.status_code == 200:
			return True, response.json().get("data"), 1
		
		return False, "Hết ký tự !", 0

	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		# if source_language == "auto":
		# source_language = self._language(text)
		payload = {
			"text": text,
			"gender": gender,
			"style": kwargs.get("style"),
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		# print(kwargs)
		
		headers = {"Authorization": f"Bearer {self.user_data['token']}"}
		
		for i in range(20):
			if self.tts_fail.get(kwargs.get('row_number', 0)):
				raise Exception
			try:
				response = requests.post(url=URL_API_BASE + "/tts/private/super-ai-voice", headers=headers, json={
					"data": mh_ae(payload, p_k=self.user_data['paes'])})
			except:
				continue
			if response.status_code == 200:
				# print(response.json())
				data = response.json().get('data')
				req_id = data.get('req_id')
				for i in range(60):
					if self.tts_fail.get(kwargs.get('row_number', 0)):
						raise Exception
					# print('Request',i)
					try:
						res = requests.get(url=URL_API_BASE + f"/tts/public/check-task/{req_id}", headers=headers)
						if res.status_code == 200:
							decoded_bytes = base64.b64decode(res.json().get("data"))
							# if decoded_bytes == "server_busy":
							# 	return source_language, None
							# print(decoded_bytes)
							
							return source_language, decoded_bytes
					except:
						pass
					time.sleep(1)
			elif response.status_code == 429:
				self.manage_thread_pool.resultChanged.emit(STOP_GET_VOICE, STOP_GET_VOICE, kwargs.get('row_number', 0))
				# return source_language, "Quá nhiều request"
				return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", "Quá nhiều request", "warning")
			time.sleep(1)
		return source_language, None
	
	def name (self) -> str:
		return "TTS_DaNgonNgu"
	
	def __str__ (self) -> str:
		return "TTS_DaNgonNgu"


if __name__ == "__main__":
	pass
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
