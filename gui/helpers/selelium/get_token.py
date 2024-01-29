import json
import random
import string
import time

import requests
from requests import Session
from seleniumwire.utils import decode

from gui.helpers.selelium.selelium import ContextAutoSelenium


def get_token_vbee (username, password):
	try:
		with ContextAutoSelenium(profile_name=username, browserName="chrome", downloadFolder="temp",
				isHeadless=False, remove_profile=False) as auto:
			auto.go_to_url("https://vbee.vn/")
			
			auto.click_element("//button[text()='Đăng nhập']", "xpath")
			# time.sleep(4)
			auto.wait_element("username", "id", time_out=20)
			auto.send_text(username, "username", "id")
			auto.send_text(password, "password", "id")
			
			while not "https://studio.vbee.vn/studio/text-to-speech" in auto.driver.current_url:
				pass
			time.sleep(2)
			access_token = ''
			user_agent = ''
			# print(auto.driver.current_url)
			for request in auto.driver.requests:
				if request.url == 'https://vbee.vn/api/v1/me':
					# print(request.headers)
					user_agent = request.headers.get('user-agent',
						'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36')
					access_token = request.headers.get('Authorization', '')
			# print(access_token)
			# auto.pause()
			return {"access-token": access_token, "user-agent": user_agent}
	except:
		return None


def get_token_viettelAI (username, password):
	try:
		with ContextAutoSelenium(profile_name=username, browserName="chrome", downloadFolder="temp",
				isHeadless=False, remove_profile=False) as auto:
			# auto = Auto_Selenium(browserName="chrome", downloadFolder="temp", isHeadless=True)
			
			# auto.go_to_url("https://www.text-to-speech.online")
			auto.go_to_url("https://viettelai.vn/auth/login")
			auto.click_element('//*[@id="__layout"]/div/div[1]/div[1]/div/div[1]/a', "xpath")
			time.sleep(1)
			auto.send_text(username, "Số điện thoại/Email")
			auto.send_text(password, "Mật khẩu")
			del auto.driver.requests
			time.sleep(1)
			
			auto.click_element("button-login", "class")
			time.sleep(4)
			authorization = ''
			user_agent = ''
			api_key = ''
			name_test = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
			for i in range(1, 20):
				for request in auto.driver.requests:
					
					if request.url == 'https://viettelai.vn/_backend/api/application/list' or request.url == 'https://viettelai.vn/api/application/list' or request.url == 'https://viettelai.vn/api/auth/me' or request.url == 'https://viettelai.vn/_backend/api/auth/me':
						authorization = request.headers.get('Authorization', '')
						if authorization == '':
							break
						user_agent = request.headers.get('user-agent',
							'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36')
						
						break
				if not authorization == '':
					break
				time.sleep(1)
				
			headers = {
				'Accept': 'application/json, text/plain, */*',
				'Accept-Language': 'vi',
				'Authorization': authorization,
				'Connection': 'keep-alive',
				'Referer': 'https://viettelai.vn/dashboard/my-service',
				'Sec-Fetch-Dest': 'empty',
				'Sec-Fetch-Mode': 'cors',
				'Sec-Fetch-Site': 'same-origin',
				'User-Agent': user_agent,
				'X-KL-Ajax-Request': 'Ajax_Request',
				'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
				'sec-ch-ua-mobile': '?0',
				'sec-ch-ua-platform': '"Windows"'
			}
			
			session = Session()
			session.headers = headers
			
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
			response = session.post(f"https://viettelai.vn/_backend/api/token/listing", data=payload)
			
			if len(response.json().get("data")) > 0:
				for item in response.json().get("data"):
					token_id = item.get('id')
					session.delete(f"https://viettelai.vn/_backend/api/token/{token_id}")
			
			res = session.post("https://viettelai.vn/_backend/api/token",
				json={"name": name_test})
			api_key = res.json().get('data').get("token")
			
			return {"api-key": api_key, "access-token": authorization,
					"user-agent": user_agent}
	except:
		return None


def get_token_viettelGroup (username, password):
	try:
		with ContextAutoSelenium(profile_name=username, browserName="chrome", downloadFolder="temp",
				isHeadless=False, remove_profile=False) as auto:
			
			auto.go_to_url("https://viettelgroup.ai/login")
			
			if not auto.driver.current_url == 'https://viettelgroup.ai/dashboard':
				
				auto.send_text(username, "//input[@name='account']", "xpath")
				auto.send_text(password, "//input[@name='password']", "xpath")
				del auto.driver.requests
				time.sleep(1)
				
				auto.click_element("//button[@type='submit']", "xpath")
				time.sleep(4)
			else:
				time.sleep(4)
			authorization = ''
			user_agent = ''
			cookies = ''
			api_key = ''
			user_id = ''
			name_test = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
			
			for i in range(1, 20):
				for request in auto.driver.requests:
					
					if request.url == 'https://viettelgroup.ai/api/user/info':
						# print(request.headers)
						# print(request.response.body)
						# print(request.response.headers)
						#
						authorization = request.headers.get('X-XSRF-TOKEN', '')
						if authorization == '':
							break
						user_agent = request.headers.get('user-agent',
							'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36')
						cookies = request.headers.get('Cookie')
						# print(cookies)
						body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
						info_user = json.loads(body)
						user_id = info_user.get('data').get('id')
				 
						break
				if not authorization == '':
					break
				time.sleep(1)
				
			# auto.pause()
			headers = {
				'Accept': '*/*',
				'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
				'Connection': 'keep-alive',
				'Content-Length': '0',
				'Cookie': cookies,
				'Origin': 'https://viettelgroup.ai',
				'Referer': 'https://viettelgroup.ai/dashboard',
				'Sec-Fetch-Dest': 'empty',
				'Sec-Fetch-Mode': 'cors',
				'Sec-Fetch-Site': 'same-origin',
				'User-Agent': user_agent,
				'X-XSRF-TOKEN': authorization,
				'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
				'sec-ch-ua-mobile': '?0',
				'sec-ch-ua-platform': '"Windows"'
			}
			session = Session()
			session.headers = headers
			
			response = session.post(f"https://viettelgroup.ai/api/token/list", json={"user_id": user_id})
			# print(response.json())
			
			if response.json().get("data").get("total") > 0:
				for token in response.json().get("data").get("list"):
					token_id = token.get("id")
					session.post(f"https://viettelgroup.ai/api/token/delete", json={"user_id": user_id,
																					"token_id": token_id})
			
			session.post("https://viettelgroup.ai/api/token/store",
				json={"user_id": user_id, "name": name_test})
			
			response = session.post(f"https://viettelgroup.ai/api/token/list", json={"user_id": user_id})
			
			api_key = response.json().get('data').get("list")[0].get("token")
			
			return {"api-key": api_key, "access-token": authorization, "user-agent": user_agent, 'cookies': cookies,
					"user_id": user_id}
	
	except:
		return None


# auto.pause()

def get_token_fpt (username, password):
	try:
		with ContextAutoSelenium(profile_name=username, browserName="chrome", downloadFolder="temp",
				isHeadless=False, remove_profile=False) as auto:
			# auto = Auto_Selenium(browserName="chrome", downloadFolder="temp", isHeadless=True)
			
			auto.go_to_url(
				"https://id.fptcloud.com/auth/realms/FptSmartCloud/protocol/openid-connect/auth?client_id=fptai_console&redirect_uri=https://console.fpt.ai/home&state=gyi2p564vm&response_type=code&scope=openid+profile+email+phone")
			auto.send_text(username, "username")
			auto.send_text(password, "password")
			time.sleep(1)
			auto.click_element("kc-login-button")
			time.sleep(4)
			# print(auto.driver.requests)
			list_project = []
			project_id = ''
			authorization = ''
			user_agent = ''
			api_key = ''
			email = ''
			name_test = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
			for request in auto.driver.requests:
				
				if request.url == 'https://backend.fpt.ai/api/projects/?project_type=':
					# print(request.headers)
					authorization = request.headers.get('Authorization', '')
					user_agent = request.headers.get('user-agent',
						'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36')
					
					body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
					list_project = json.loads(body)
			# print(list_project)
			# break
			
			headers = {
				'authority': 'backend.fpt.ai',
				'accept': '*/*',
				'accept-language': 'en-US',
				'authorization': authorization,
				'origin': 'https://console.fpt.ai',
				'referer': 'https://console.fpt.ai/',
				'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
				'sec-ch-ua-platform': '"Windows"',
				'user-agent': user_agent
			}
			
			session = Session()
			session.headers = headers
			
			if len(list_project) == 0:  # tạo project mới#
				# print("chưa có")
				response = session.post(f"https://backend.fpt.ai/api/projects", json={"name": name_test})
				project_id = response.json().get("id")
			
			else:  # chọn project đâu tiên
				project_id = list_project[0].get("id")
			
			response = session.get(f"https://backend.fpt.ai/api/projects/{project_id}/categories/")
			# print(response.json())

			list_apis = response.json()[0].get('apis')
			enabled_ips = None
			for apis in list_apis:
				if apis.get("name") == 'Text to Speech':
					enabled_ips = apis.get("enable")
			
			# lấy key api
			response = session.get(f"https://backend.fpt.ai/api/projects/{project_id}/credentials/")
			# print(response.json())
			if len(response.json()) == 0:
				# res = session.delete(f"https://backend.fpt.ai/api/projects/{project_id}/credentials/{response.json()[0].get('id')}")
				
				res = session.post(f"https://backend.fpt.ai/api/projects/{project_id}/credentials/",
					json={"name": name_test})
				api_key = res.json().get('key')
			else:
				api_key = response.json()[0].get('key')
				
			if enabled_ips is False:
				session.put(
					f"https://backend.fpt.ai/api/projects/{project_id}/enable-api/646f356f-d470-43f6-b8ca-84056cb40f62/")
			# email =
			del auto.driver.requests
			auto.go_to_url("https://voicemaker.fpt.ai/")
			# auto.pause()
			# auto.wait_page_loaded()
			authorization = ""
			for i in range(1,20):
				for request in auto.driver.requests:
					if request.url == 'https://voicemaker.fpt.ai/api/user':
						authorization = request.headers.get('Authorization', '')
						if authorization == '':
							break
						body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
						email = json.loads(body).get("email")
						break
				if not authorization == '':
					break
				time.sleep(1)
				
			return {"api-key": api_key, "project-id": project_id, "access-token": authorization,
					"user-agent": user_agent, "email": email}
	except:
		return None
