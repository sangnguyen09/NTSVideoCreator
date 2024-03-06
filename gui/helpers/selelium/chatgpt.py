import random
import re
import time

import requests

from gui.helpers.get_data import URL_API_BASE
from gui.helpers.constants import TEXT_INFO_CHATGPT, LANGUAGE_CODE_SPLIT_NO_SPACE, USER_DATA, TOOL_CODE_MAIN, \
	SETTING_APP_DATA, STOP_THREAD_TRANSLATE
from gui.helpers.ect import mh_ae, gm_ae, cr_pc
from gui.helpers.func_helper import getValueSettings
from gui.helpers.thread import ManageThreadPool
from gui.helpers.translatepy import Language
from gui.widgets.py_dialogs.py_dialog_get_int import PyDialogGetInt
from gui.widgets.py_dialogs.py_dialog_show_chatgpt_translate import PyDialogShowGPTTranslate


class TranslaterServer():
	def __init__ (self, manage_thread_pool):
		self.is_error = False
		self.thread_pool_limit = ManageThreadPool()
		self.thread_pool_limit.setMaxThread(6)
		self.manage_thread_pool = manage_thread_pool
		
		self.manage_thread_pool.resultChanged.connect(self._resultThread)
	
	def _resultThread (self, id_worker, id_thread, result):
		
		if id_thread == STOP_THREAD_TRANSLATE:
			self.is_error = True
	
	def translateSubServerPro (self, server_trans, type_thread_chatgpt, sequences, source_lang, des_lang, lang_result, model, resetStatus, translate_cache):
		url = URL_API_BASE + "/translate/private/pro"
		chunk_split = 5
		self.is_error = False

		if server_trans == 'chatgpt_pro':
			source_lang = Language(source_lang).in_foreign_languages.get('en')
			des_lang = Language(des_lang).in_foreign_languages.get('en')
			url = URL_API_BASE + "/translate/private/chatgpt"
			chunk_split = getValueSettings(SETTING_APP_DATA, TOOL_CODE_MAIN).get('data_setting').get('chunk_split', 5)
		
		user_data = getValueSettings(USER_DATA, TOOL_CODE_MAIN)
		
		# print(chunk_split)
		dataTrans = {
			"text": "CHECK_ACCOUNT_ACCEPT_PRO",
			"source_lang": source_lang,
			"des_lang": des_lang,
			"model": model,
			"cp": cr_pc(),
			't': int(float(time.time())),
			"tc": TOOL_CODE_MAIN,
		}
		print(dataTrans)
		data_encrypt = mh_ae(dataTrans, user_data['paes'])
		
		headers = {"Authorization": f"Bearer {user_data['token']}"}
		
		res = requests.post(url=url,
			json={"data": data_encrypt}, headers=headers)
		
		if res.status_code >200:
			resetStatus()
			return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", res.json().get("message"), "warning")
		
		chunks = [sequences[x:x + chunk_split] for x in
				  range(0, len(sequences), chunk_split)]
		# print(chunks)
		for ind_ch, chunk in enumerate(chunks):
			self.thread_pool_limit.start(self._funcConvertLanguage, type_thread_chatgpt, 'type_thread_chatgpt', url=url, server_trans=server_trans, limit_thread=True, type_thread_chatgpt=type_thread_chatgpt,
				chunk=chunk, ind_chunk=ind_ch, user_data=user_data, source_lang=source_lang, lang_result=lang_result,
				des_lang=des_lang, model=model, translate_cache=translate_cache, resetStatus=resetStatus, chunk_split=chunk_split)
	
	
	def _funcConvertLanguage (self, **kwargs):
		
		if self.is_error:
			return
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		chunk = kwargs.get('chunk')
		ind_chunk = kwargs.get('ind_chunk')
		lang_result = kwargs.get('lang_result')
		source_lang = kwargs.get('source_lang')
		type_thread_chatgpt = kwargs.get('type_thread_chatgpt')
		des_lang = kwargs.get('des_lang')
		model = kwargs.get('model')
		
		user_data = kwargs.get('user_data')
		translate_cache = kwargs.get('translate_cache')
		resetStatus = kwargs.get('resetStatus')
		server_trans = kwargs.get('server_trans')
		url = kwargs.get('url')
		chunk_split = kwargs.get('chunk_split')
		
		query_text = ''
		for index_, seq in enumerate(chunk):
			# print(seq)
			file_image, sub_origin, sub_translate = seq
			
			if str(lang_result.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
				content = sub_origin.strip().replace("\n", "")
			else:
				content = sub_origin.strip().replace("\n", " ")
			if server_trans == 'chatgpt_pro':
				query_text += f'00:00:0{index_},00 --> 00:00:0{index_+1},00' + '\n'
				query_text += content + "\n\n"
			else:
				query_text += content + "\n"
		
		dataTrans = {
			"text": query_text,
			"source_lang": source_lang,
			"des_lang": des_lang,
			"model": model,
			"cp": cr_pc(),
			"tc": TOOL_CODE_MAIN,
			't': int(float(time.time())),
		}
		# print(dataTrans)
		data_encrypt = mh_ae(dataTrans, user_data['paes'])
		
		headers = {"Authorization": f"Bearer {user_data['token']}"}
		dataCache = {
			"text": query_text,
			"source_lang": source_lang,
			"des_lang": des_lang,
			'model': model,
			"server": server_trans
		}
		_cache_key = str(dataCache)
		# print(_cache_key)
		# print(translate_cache)
		if _cache_key in translate_cache:
			text_res = translate_cache[_cache_key]
			if len(text_res) == len(chunk):
				# data_res = [item[-1] for item in text_res]
				self.manage_thread_pool.resultChanged.emit(type_thread_chatgpt, type_thread_chatgpt, (
					ind_chunk, text_res, chunk_split))
				thread_pool.finishSingleThread(id_worker)
		# return True
		else:
			# return
			for i in range(10):
				if self.is_error:
					return
				response = requests.post(url=url,
					json={"data": data_encrypt}, headers=headers)
				# print(response.status_code)
				if response.status_code == 200:
					data = response.json().get('data')
					req_id = data.get('req_id')
					for i in range(60):
						if self.is_error:
							return
						try:
							res = requests.get(url=URL_API_BASE + f"/translate/public/check-task/{req_id}", headers=headers)
							# print(res.text)

							if res.status_code == 200:
								try:
									text_res = gm_ae(res.json()["data"], user_data['paes'])
									# print(text_res)
									
									if len(text_res) == len(chunk):
										# print(data_res)
										translate_cache[_cache_key] = text_res
										
										self.manage_thread_pool.resultChanged.emit(type_thread_chatgpt, type_thread_chatgpt, (
											ind_chunk, text_res, chunk_split))
										
										thread_pool.finishSingleThread(id_worker)
										
										return True
								except:
									print("Lỗi dịch")
							
							elif res.status_code == 429:
								# self.is_error = True
								# resetStatus()
								print(response.text)
								time.sleep(1)
								continue
						
						except:
							pass
						time.sleep(1)
				
				elif response.status_code == 429:
					# self.is_error = True
					# resetStatus()
					print(response.text)
				# return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", "Quá nhiều request", "warning")
				elif response.status_code == 402:
					# print('dddd')
					# self.is_error = True
					# resetStatus()
					# return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", response.text, "warning")
					print(response.text)
				time.sleep(1)
			
			# self.is_error = True
			resetStatus()
			return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", f"Chưa dịch được nội dung {query_text}", "warning")
	
	
	def translateGPTApiKey (self, type_thread_chatgpt, sequences, source_lang, des_lang, lang_result,
							model, list_api_key, text_prompt, line_break, resetStatus, translate_cache):
		
		source_lang = Language(source_lang).in_foreign_languages.get('en')
		des_lang = Language(des_lang).in_foreign_languages.get('en')
		
		chunk_split = line_break if line_break else 5
		
		type_ = 'subtitle'
		if isinstance(sequences, str):

			chunks = [[ "", sequences, ""]]
			type_ = 'text'
		
		else:
			chunks = [sequences[x:x + chunk_split] for x in
					  range(0, len(sequences), chunk_split)]
		# print(chunks)
		self.is_error = False
		for ind_ch, chunk in enumerate(chunks):
			self.thread_pool_limit.start(self._funcGPTKey, type_thread_chatgpt, 'type_thread_chatgpt',
				limit_thread=True,
				type_thread_chatgpt=type_thread_chatgpt,
				chunk=chunk, ind_chunk=ind_ch, source_lang=source_lang,
				lang_result=lang_result, type_=type_, list_api_key=list_api_key,
				text_prompt=text_prompt,
				des_lang=des_lang, model=model, translate_cache=translate_cache,
				resetStatus=resetStatus, chunk_split=chunk_split)
	
	def _funcGPTKey (self, **kwargs):
		
		if self.is_error:
			return
		thread_pool = kwargs["thread_pool"]
		id_worker = kwargs["id_worker"]
		chunk = kwargs.get('chunk')
		ind_chunk = kwargs.get('ind_chunk')
		lang_result = kwargs.get('lang_result')
		source_lang = kwargs.get('source_lang')
		type_thread_chatgpt = kwargs.get('type_thread_chatgpt')
		des_lang = kwargs.get('des_lang')
		type_ = kwargs.get('type_')
		model = kwargs.get('model')
		list_api_key = kwargs.get('list_api_key')
		
		translate_cache = kwargs.get('translate_cache')
		resetStatus = kwargs.get('resetStatus')
		
		chunk_split = kwargs.get('chunk_split')
		text_prompt = kwargs.get('text_prompt')
		
		query_text = ''
		for index_,seq in enumerate(chunk):
			# dolech, time_, pos_ori, sub_origin, sub_translate, pos_trans = seq
			# time_, sub_origin, translate = seq
			file_image, sub_origin, sub_translate = seq

			if str(lang_result.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
				content = sub_origin.strip().replace("\n", "")
			else:
				content = sub_origin.strip().replace("\n", " ")
			
			if type_ == 'subtitle':
				# query_text += str(time_) + '\n'
				query_text += f'00:00:0{index_},00 --> 00:00:0{index_+1},00' + '\n'

				query_text += content + "\n\n"
			else:
				query_text += content + "\n"
		
		dataCache = {
			"text": query_text,
			"source_lang": source_lang,
			"des_lang": des_lang,
			'model': model,
			"server": 'chatgpt_api_key'
		}
		_cache_key = str(dataCache)
		
		if _cache_key in translate_cache:
			text_res = translate_cache[_cache_key]
			if len(text_res) == len(chunk):
				# data_res = [item[-1] for item in text_res]
				self.manage_thread_pool.resultChanged.emit(type_thread_chatgpt, type_thread_chatgpt, (
					ind_chunk, text_res, chunk_split))
				thread_pool.finishSingleThread(id_worker)
		# return True
		else:
			# return
			url = 'https://api.openai.com/v1/chat/completions'
			
			list_model = {
				"gpt-3.5-turbo": 'gpt-3.5-turbo-1106',
				"gpt-4-turbo": 'gpt-4-1106-preview',
			}
			text_ = f'''
	        {query_text}
	        '''
			
			prompt = [
				{
					"role": "system",
					"content": text_prompt
				},
				
				{
					"role": "user",
					"content": text_,
				},
			]
			data = {
				"model": list_model.get(model),
				"messages": prompt
			}
			# print(prompt)
			status = ''
			for i in range(20):
				if self.is_error:
					return
				api_key = random.choice(list_api_key)
				headers = {
					"Content-Type": "application/json",
					"Authorization": f"Bearer {api_key}"
				}
				response = requests.post(url, headers=headers, json=data)
				# print(response.text)
				# print(response.status_code)
				if response.status_code == 200:
					data = response.json()
					content = data["choices"][0]["message"]["content"]
					if type_ == 'text':
						text_res = [content]
					else:
						text_res = self._read_sequence(content, len(chunk))
					if len(text_res) == len(chunk):
						# data_res = [item[-1] for item in text_res]
						# print(data_res)
						translate_cache[_cache_key] = text_res
						
						self.manage_thread_pool.resultChanged.emit(type_thread_chatgpt,
							type_thread_chatgpt, (
								ind_chunk, text_res,
								chunk_split))
						
						thread_pool.finishSingleThread(id_worker)
						return True
				# time.sleep(1)
				
				elif response.status_code >= 400:
					print(response.text)
				
				time.sleep(1)
			
			# self.is_error = True
			resetStatus()
			return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", f"Chưa dịch được nội dung {query_text}", "warning")
		
		# return self.manage_thread_pool.messageBoxChanged.emit("Cảnh báo", status, "warning")
	
	def _read_sequence (self, content, chunk_):
		# sequences = list(map(list, re.findall(r"(\d+:\d+:\d+,\d+ -+> \d+:\d+:\d+,\d+)\n+(.+(?:\n.+)?)\n?", content)))
		
		sequences = []
		
		for seq in [re.findall(r"\d+:\d+:\d+,\d+\s+-+>\s+\d+:\d+:\d+,\d+.?\n+(.+)\n?", content),
					re.findall(r"\d+:\d+:\d+,\d+\s+-+>\s+\d+:\d+:\d+,\d+.?\n+(.+)\n+", content),
					re.findall(r"\d+:\d+:\d+,\d+\s+-+>\s+\d+:\d+:\d+,\d+.?\n?(.+)\n?", content),
					re.findall(r"\[?\d+:\d+:\d+,\d+\]?\s+-+>\s+\[?\d+:\d+:\d+,\d+\]?.?\n+(.+)\n?", content),
					content.strip("\n").split("\n")
					]:
			if len(seq) == chunk_:
				sequences = seq
				break
		# print(sequences)
		
		if len(sequences) == chunk_:
			liss = []
			for text in sequences:
				try:
					if text == '':
						continue
					reg = re.compile(r"\"(.+)\"", re.M)
					m = reg.search(text)
					if m:
						text = m.group(1)
					text = text.strip('"').strip("'").strip('\n')
					# text = text.split('\n')[0]
					liss.append(text)
				except:
					pass
			
			return liss
		else:
			return sequences


def translateSubChatGPTThuCong (manage_thread_pool, type_thread_chatgpt, sequences, lang_source, des_lang, lang_result, resetStatus):
	chunks = []
	sequence_temp = ''
	text_cur = ""
	index_curr = 0
	origin_lang = Language(lang_source).in_foreign_languages.get('en')
	# print(lang_des)
	des_lang = Language(des_lang).in_foreign_languages.get('en')
	
	dial = PyDialogGetInt(TEXT_INFO_CHATGPT, "Nhập Ký Tự Giới Hạn Để Tách Sub Thành Nhiều Đoạn", "Nhập Số Ký Tự Giới Hạn:", 100, 30000, width=600, height=450)
	if dial.exec():
		pass
	# print(dial.getValue())
	else:
		resetStatus()
		
		return False
	limit_char = dial.getValue()
	
	for index, seq in enumerate(sequences):
		file_image, sub_origin, sub_translate = seq
		
		if len(sequence_temp) > limit_char:
			chunks.append(sequence_temp)
			sequence_temp = ''
		
		if str(lang_result.result) in LANGUAGE_CODE_SPLIT_NO_SPACE:
			content = sub_origin.strip().replace("\n", "")
		else:
			content = sub_origin.strip().replace("\n", " ")
		# sequence_temp += str(index+1) + '\n'
		# sequence_temp += str(time_) + '\n'
		sequence_temp += content + "\n"
	# text_cur += content + "\n"
	# print(len(sequence_temp))
	if not sequence_temp == '':
		chunks.append(sequence_temp)
	
	# print(len(chunks))
	# return
	for ind_ch, chunk in enumerate(chunks):
		dialog = PyDialogShowGPTTranslate(origin_lang, des_lang, chunk, f"Sẽ Có {len(chunks)} Đoạn Dịch. Đây Là Đoạn Dịch ({ind_ch + 1}/{len(chunks)})")
		if dialog.exec():
			# if type_trans == "all":
			# 	self.manage_thread_pool.resultChanged.emit(LOAD_SUB_TRANSLATE_CHATGPT, LOAD_SUB_TRANSLATE_CHATGPT, dialog.getTextTranslate())
			# else:
			manage_thread_pool.resultChanged.emit(type_thread_chatgpt, type_thread_chatgpt, (
				-1, dialog.getTextTranslate(), 0))
		# print(dialog.getTextTranslate())
		else:
			resetStatus()
			return False
