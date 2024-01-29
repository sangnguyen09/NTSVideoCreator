import base64
import os
import time

import requests

from gui.helpers.constants import USER_DATA, TOOL_CODE_MAIN, STOP_GET_VOICE, JOIN_PATH
from gui.helpers.ect import cr_pc, mh_ae
from gui.helpers.func_helper import getValueSettings
from gui.helpers.get_data import URL_API_BASE
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request


class TTSVoiceCoSanTranslator(BaseTranslator):
	
	
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
		return True, -1, 1
	
	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		# if source_language == "auto":
		folder_src_voice = kwargs.get('folder_src_voice', '')
		if folder_src_voice != '':
			if os.path.exists(folder_src_voice):
				path_voice = ''
				voice_wav = JOIN_PATH(folder_src_voice, f"{kwargs.get('line_sub', '1')}.wav")
				voice_mp3 = JOIN_PATH(folder_src_voice, f"{kwargs.get('line_sub', '1')}.mp3")
				if os.path.isfile(voice_wav):
					path_voice = voice_wav
				elif os.path.isfile(voice_mp3):
					path_voice = voice_wav
				if path_voice != '':
					with open(path_voice, 'rb') as file_v:
						return source_language, file_v.read()
		return source_language, None

	def name (self) -> str:
		return "TTS_VoiceCoSan"
	
	def __str__ (self) -> str:
		return "TTS_VoiceCoSan"


if __name__ == "__main__":
	pass
