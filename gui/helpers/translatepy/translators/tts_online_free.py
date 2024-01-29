import asyncio
import os
import random

# from playwright.sync_api import sync_playwright

from gui.helpers import edge_tts
from gui.helpers.constants import PATH_BROWSERS_CHROMIUM, STOP_GET_VOICE
from gui.helpers.translatepy import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.request import Request


class TTSFreeOnlineTranslator(BaseTranslator):
	
	def __init__ (self, manage_thread_pool, request: Request = Request(), service_url: str = "https://www.text-to-speech.online/", file_json=''):
		self.manage_thread_pool = manage_thread_pool
		self.request = request
		self.service_url = service_url
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
		self.tts_fail = {}
		self.is_stop = False
	def _resultThread (self, id_worker, id_thread, result):
		if id_thread == STOP_GET_VOICE:
			# print(result)
			row_number = result
			self.tts_fail[row_number] = True
	def _text_to_speech_playwright (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		
		pitch = kwargs.get("pitch")
		content = '<speak  xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="en-US">'
		content += f'<voice  name="{gender}"> <prosody  rate="0%" pitch="{pitch}%">{text}</prosody> </voice> </speak>'
		
		# if os.path.exists(PATH_BROWSERS_CHROMIUM):
		# with sync_playwright() as p:
		# 	browser = p.chromium.launch(headless=False, executable_path=PATH_BROWSERS_CHROMIUM, args=["--disable-gpu"])
		#
		# 	page = browser.new_page()
		# 	file_stream = None
		#
		# 	while True:
		# 		try:
		# 			page.goto("https://www.text-to-speech.online/", wait_until="load")
		#
		# 			# page.get_by_role("tab", name="TEXT").click()
		# 			page.wait_for_selector("#locale", state="attached")
		# 			page.locator("#locale").select_option(source_language)
		# 			page.wait_for_selector("#voice", state="attached")
		# 			page.locator("#voice").select_option(gender)
		# 			page.wait_for_selector("#nav_ssml_tab", state="attached")
		# 			page.locator("#nav_ssml_tab").click()
		# 			# page.pause()
		# 			# page.get_by_placeholder("Please enter text").fill(content)
		# 			page.locator("#text").fill(content)
		#
		# 			with page.expect_download() as download_info:
		# 				# Perform the action that initiates download
		# 				page.wait_for_selector("#download", state="attached")
		# 				page.locator("#download").click()
		# 			# # Wait for the download to start
		# 			download = download_info.value
		# 			if os.path.exists(download.path()):
		# 				with open(download.path(), "rb") as file_handle:
		# 					file_stream = file_handle.read()
		# 				break
		# 		except:
		# 			continue
		#
		# 	browser.close()
		#
		# 	return source_language, file_stream
		#
	def check_token (self):
		return True, "Ok"
	
	def check_balance (self):
		return True, -1, 1
	
	def _text_to_speech (self, text: str, speed: int, gender: str, source_language: str, **kwargs):
		
		pitch = 0
		# print(pitch)
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
		# loop = asyncio.get_event_loop()
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		try:
			done = loop.run_until_complete(self.get_voice(text, gender, pitch,kwargs.get('row_number', 0)))
			return source_language, done
		except:
			return source_language, None
		finally:
			loop.close()
	
	async def get_voice (self, text, gender, pitch,row_number, retries=5):
		for i in range(retries):
			if self.tts_fail.get(row_number):
				raise Exception
			try:
				if not self.request.proxies == [None]:
					# self.proxies[self._proxies_index]
					proxy = random.choice(self.request.proxies)
					communicate = edge_tts.Communicate(text, gender, pitch=f"{pitch}%", proxy=proxy)
				
				else:
					communicate = edge_tts.Communicate(text, gender, pitch=f"{pitch}%")
				# file_temp = JOIN_PATH(folder_temp.name,"tts_voice.mp3")
				return await communicate.get_byte()
			
			except Exception as e:
				print(e)
				continue
		return None
	
	def check_excutable_path (self) -> bool:
		if os.path.exists(PATH_BROWSERS_CHROMIUM):
			return True
		return False
	
	def _language (self, text: str) -> str:
		# print(2)
		
		params = {"client": "gtx", "dt": "t", "sl": "auto", "tl": "ja", "q": text}
		res = self.request.get("https://translate.googleapis.com/translate_a/single", params=params)
		response = res.json()
		if res.status_code < 400:
			return response[2]
		
		params = {"client": "dict-chrome-ex", "sl": "auto", "tl": "ja", "q": text}
		res = self.request.get("https://clients5.google.com/translate_a/t", params=params)
		response = res.json()
		if res.status_code < 400:
			return response['ld_result']["srclangs"][0]
	
	def _language_normalize (self, language: Language):
		if language.id == "zho":
			return "zh-CN"
		elif language.id == "och":
			return "zh-TW"
		return language.alpha2
	
	def _language_denormalize (self, language_code):
		return Language(language_code.split("-")[0])
	
	
	def name (self) -> str:
		return "TTSFree"
	
	def __str__ (self) -> str:
		return "TTSFree"


def get_voice_text_to_speech (content, file_save, locale, voicer):
	exec_path = "E:/Project/Python/ReviewPhim/browsers/chromium-1055/chrome-win/chrome.exe"
	# if os.path.exists(exec_path):
	# 	with sync_playwright() as p:
	# 		browser = p.chromium.launch(executable_path=exec_path, args=["--disable-gpu"])
	# 		# print(browser)
	# 		page = browser.new_page()
	# 		page.goto("https://www.text-to-speech.online/")
	# 		# page.get_by_role("tab", name="TEXT").click()
	# 		page.locator("#locale").select_option("vi-VN")
	# 		page.locator("#voice").select_option("vi-VN-NamMinhNeural")
	# 		page.get_by_role("tab", name="SSML").click()
	# 		# page.get_by_placeholder("Please enter text").fill(content)
	# 		page.get_by_placeholder("SSML content").fill(content)
	#
	# 		with page.expect_download() as download_info:
	# 			# Perform the action that initiates download
	# 			page.locator("#download").click()
	# 		# Wait for the download to start
	# 		download = download_info.value
	# 		download.save_as(file_save)
	#
	# 		browser.close()
	#

# page.pause()
if __name__ == "__main__":
	#
	# proxy = "user49102:ilvY8LihiQ@103.121.89.112:49102"
	# proxy = "103.121.89.112:49102"
	# Request = TTSFreeOnlineTranslator()
	# print("@" in proxy)
	# a = proxy.split("@")[0]
	get_voice_text_to_speech("Hôm nay trên chương trình Ben Shapiro, Trump bắt đầu một cơn bão lửa bằng một cái tên đánh rơi Elizabeth Warren và Pocahontas", "dsds.mp3", "vi-VN", "vi-vn-hoaimyneural")
