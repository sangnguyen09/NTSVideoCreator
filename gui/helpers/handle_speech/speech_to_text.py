import json
import random
import time

import pyuseragents

from gui.helpers.translatepy.utils.request import Request


GOOGLE_SPEECH_API_KEY = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
GOOGLE_SPEECH_API_URL = "http://www.google.com/speech-api/v2/recognize?client=chromium&lang={lang}&key={key}"  # pylint: disable=line-too-long


class GoogleSpeechToText(object):
	def __init__ (self, request, language="en", rate=16000, retries=15, api_key=GOOGLE_SPEECH_API_KEY):
		self.language = language
		self.rate = rate
		self.request: Request = request
		self.api_key = api_key
		self.retries = retries
	
	def speechToText (self, file_flac_temp):
		# try:
		print(file_flac_temp)
		for i in range(self.retries):
		# while True:
			time.sleep(1)
			url = GOOGLE_SPEECH_API_URL.format(lang=self.language, key=self.api_key)
			headers = {
				# "User-Agent": pyuseragents.random(),
				"Content-Type": "audio/x-flac; rate=%d" % self.rate
			}
			
			try:
				with open(file_flac_temp, "rb") as file:
					resp = self.request.post(url, data=file.read(), headers=headers)
			except Exception as e:
				print(e)
				continue
			for line in resp.content.decode('utf-8').split("\n"):
				try:
					line = json.loads(line)
					line = line['result'][0]['alternative'][0]['transcript']
					print(line)
					
					return line[:1].upper() + line[1:]
				except:
					# no result
					continue
		# return False
		# except KeyboardInterrupt:
		# return "Đoạn này chưa lấy được text"
		return


class GladiaSpeechToText(object):
	def __init__ (self, request, language="en", rate=16000,retries=15, api_key='e9e25b39-f86b-4287-a2cf-5b3e652e558b'):
		self.request: Request = request
		self.api_key = api_key
		self.url = 'https://api.gladia.io/audio/text/audio-transcription/'
		self.retries = retries
	
	def speechToText (self, file_music):
		# try:
		for i in range(self.retries):
			#
			headers = {
				'accept': 'application/json',
				'x-gladia-key': self.api_key,
				# requests won't add a boundary if this header is set when you pass files=
				# 'Content-Type': 'multipart/form-data',
			}
			time.sleep(1)
			files = {
				'audio': (file_music, open(file_music, 'rb'), 'audio/flac'),
				'diarization_max_speakers': (None, '2'),
				'language': (None, 'english'),
				'language_behaviour': (None, 'automatic single language'),
				'output_format': (None, 'json'),
				'target_translation_language': (None, 'english'),
				'toggle_noise_reduction': (None, 'true'),
				'toggle_text_emotion_recognition': (None, 'false'),
			}
			
			try:
				response = self.request.post(self.url, headers=headers, files=files)
				print(response.status_code)
				print(response.text)
			except Exception as e:
				print(e)
				time.sleep(random.randrange(2,4))
				
				continue
			
			try:
				line = str(response.text)
				if line == '' or line == 'Too many requests, please try again later.':
					time.sleep(random.randrange(2, 4))
					continue
				# return line[:1].upper() + line[1:]
				return response.json().get("prediction")
			except:
				# no result
				continue
 
		return
