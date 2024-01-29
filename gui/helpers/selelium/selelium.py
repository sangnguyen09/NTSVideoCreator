import atexit
import os
import random
import shutil
import subprocess
import tempfile
import time

# import undetected_chromedriver as uc
from selenium.common.exceptions import ElementNotVisibleException, NoSuchElementException, WebDriverException
from selenium.webdriver import ActionChains, DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.chrome.service import Service as ChromeService
import seleniumwire.undetected_chromedriver as uc

from subprocess import CREATE_NO_WINDOW

RELATIVE_PATH = lambda path: os.path.join(os.path.abspath(os.getcwd()), str(path))

FOLDER_PROFILE = RELATIVE_PATH("profile")


def remove_dir (path):
	file_scipt_delete = os.path.join(FOLDER_PROFILE, os.path.basename(path)) + '.vbs'
	# print(file_scipt_delete)
	delcode = f'''
    folderRemove ="{path}"
    WScript.Sleep 3000
    Set fso = CreateObject("Scripting.FileSystemObject")
    
        If fso.FolderExists(folderRemove) Then
            fso.DeleteFolder folderRemove, True
        Else
        End If

    Set oFso = CreateObject("Scripting.FileSystemObject") : oFso.DeleteFile Wscript.ScriptFullName, True
    '''
	with open(file_scipt_delete, "w+") as delete:
		delete.write(delcode)
	os.startfile(file_scipt_delete)
	
	# try:
	#     shutil.rmtree(path)
	# except:
	#     subprocess.check_output(['cmd', '/C', 'rmdir', '/S', '/Q', path])


class Auto_Selenium():
	
	def __init__ (self, profile_name="", executable_path="chromedriver", browserName="chrome",
				  **configs):
		self.driver = None
		
		self.folder_profile_current = os.path.join(FOLDER_PROFILE, profile_name)
		if profile_name == "":
			self.folder_profile_current = tempfile.mkdtemp(dir=FOLDER_PROFILE)
			profile_name = os.path.basename(self.folder_profile_current)
		
		print(profile_name)
		
		if browserName == "chrome":
			chrome_options = uc.ChromeOptions()
			# chrome_options.add_argument(
			#     f"user-data-dir={self.folder_profile_current}")  # profile là thư muc trong tep chay chính
			# chrome_options.add_argument(f"--profile-directory={profile_name}")
			
			if "isHeadless" in configs.keys() and configs["isHeadless"] is True:  # chế độ ẩn
				chrome_options.headless = True
				chrome_options.add_argument('--headless')
				# chrome_options.add_argument("--headless=new")
			# chrome_options.headless = configs["isHeadless"]
			
			if "proxy" in configs.keys():  # thêm proxy
				chrome_options.add_argument(f'--proxy-server={configs["proxy"]}')
			
			if "downloadFolder" in configs.keys():  # cấu hình folder download
				self.folder_download = tempfile.TemporaryDirectory(dir=RELATIVE_PATH(configs.get('downloadFolder')))
				# print(self.folder_download.name)
				prefs = {
					'download.default_directory': self.folder_download.name,
					'download.prompt_for_download': False,
					'safebrowsing_for_trusted_sources_enabled': False,
					'download.directory_upgrade': True,
					'safebrowsing.enabled': False
				}
				chrome_options.add_experimental_option("prefs", prefs)
			
			if "hideImage" in configs.keys() and configs["hideImage"] is True:  # tắt ảnh
				prefs = {"profile.managed_default_content_settings.images": 2}
				chrome_options.add_experimental_option("prefs", prefs)
			
			if "hideNotification" in configs.keys() and configs["hideNotification"] is True:  # tắt thông báo
				prefs = {"profile.default_content_setting_values.notifications": 2}
				chrome_options.add_experimental_option("prefs", prefs)
			
			if "userAgent" in configs.keys():  # Sử dụng user-agent:
				print(configs["userAgent"])
				chrome_options.add_argument(f'user-agent={configs["userAgent"]}')
			
			if "incognito" in configs.keys() and configs["incognito"] is True:  # Chế độ ẩn danh:
				chrome_options.add_argument('--incognito')
			# driverService = Service
			# chrome_options.add_argument('--ignore-certificate-errors')
			# chrome_options.add_argument('--disable-gpu')
			# chrome_options.add_argument('--allow-running-insecure-content')
			# chrome_options.add_argument('--disable-web-security')
			caps = DesiredCapabilities.CHROME.copy()
			caps['acceptInsecureCerts'] = True
			self.driver = uc.Chrome(options=chrome_options, desired_capabilities=caps, user_data_dir=self.folder_profile_current,
				driver_executable_path=executable_path, version_main=113, seleniumwire_options={
					'request_storage_base_dir': 'storage'})
	
	def getLocatorType (self, locatorType):
		locatorType = locatorType.lower()
		if locatorType == "id":
			return By.ID
		elif locatorType == "name":
			return By.NAME
		elif locatorType == "class":
			return By.CLASS_NAME
		elif locatorType == "xpath":
			return By.XPATH
		elif locatorType == "css":
			return By.CSS_SELECTOR
		elif locatorType == "tag":
			return By.TAG_NAME
		elif locatorType == "link":
			return By.LINK_TEXT
		elif locatorType == "plink":
			return By.PARTIAL_LINK_TEXT
		
		return False
	
	def get_element (self, locatorValue, locatorType="id"):
		webElement = None
		try:
			locatorType = locatorType.lower()
			locatorByType = self.getLocatorType(locatorType)
			webElement = self.driver.find_element(locatorByType, locatorValue)
		
		except Exception as e:
			print("Lỗi ", e)
		
		return webElement
	
	def get_elements (self, locatorValue, locatorType="id"):
		webElement = None
		try:
			locatorType = locatorType.lower()
			locatorByType = self.getLocatorType(locatorType)
			webElement = self.driver.find_elements(locatorByType, locatorValue)
		
		except Exception as e:
			print("Lỗi ", e)
		
		return webElement
	
	def wait_element (self, locatorValue, locatorType="id", time_out=20) -> WebElement:
		webElement = None
		try:
			locatorType = locatorType.lower()
			locatorByType = self.getLocatorType(locatorType)
			wait = WebDriverWait(self.driver, time_out, poll_frequency=1,
				ignored_exceptions=[ElementNotVisibleException, NoSuchElementException])
			webElement = wait.until(ec.presence_of_element_located((locatorByType, locatorValue)))
			# webElement = wait.until(ec.)
		except Exception as e:
			print("Lỗi ", e)
		return webElement
		
	def wait_page_loaded (self,time_out=20):
		try:
			wait = WebDriverWait(self.driver, time_out, poll_frequency=1,
				ignored_exceptions=[ElementNotVisibleException, NoSuchElementException])
			wait.until(lambda d: d.execute_script('return document.readyState') == 'complete')
			# webElement = wait.until(ec.)
		except Exception as e:
			print("Lỗi ", e)
	
	def click_element (self, locatorValue, locatorType="id", time_out=20):
		try:
			locatorType = locatorType.lower()
			webElement = self.wait_element(locatorValue, locatorType, time_out)
			# print(webElement)
			webElement.click()
		except Exception as e:
			print("Lỗi ", e)
	
	def wait_time (self, wait_seconds):
		self.driver.implicitly_wait(wait_seconds)
	
	def send_text (self, text, locatorValue, locatorType="id", wait=1):
		try:
			locatorType = locatorType.lower()
			webElement = self.wait_element(locatorValue, locatorType)
			self.driver.implicitly_wait(wait)
			webElement.clear()
			webElement.send_keys(text)
		except Exception as e:
			print("Lỗi ", e)
			# try:
			#     locatorType = locatorType.lower()
			#     webElement = self.wait_element(locatorValue, locatorType)
			#     self.driver.implicitly_wait(1)
			#     webElement.clear()
			#     webElement.send_keys(text)
			# except Exception as e:
			#     print("Lỗi ", e)
	
	def get_text (self, locatorValue, locatorType="id"):
		elementText = None
		try:
			locatorType = locatorType.lower()
			webElement = self.wait_element(locatorValue, locatorType)
			elementText = webElement.text
		except Exception as e:
			print("Lỗi ", e)
		return elementText
	
	def is_element_displayed (self, locatorValue, locatorType="id"):
		elementDisplayed = None
		try:
			locatorType = locatorType.lower()
			webElement = self.wait_element(locatorValue, locatorType)
			# print(webElement.get_attribute('class'))
			
			elementDisplayed = webElement.is_displayed()
		
		except Exception as e:
			print("Lỗi ", e)
		return elementDisplayed
	
	def scroll_to (self, locatorValue, locatorType="id"):
		actions = ActionChains(self.driver)
		try:
			locatorType = locatorType.lower()
			webElement = self.wait_element(locatorValue, locatorType)
			actions.move_to_element(webElement).perform()
		
		except Exception as e:
			print("Lỗi ", e)
	
	def check_curent_ip (self, driver):
		self.driver.get('https://api6.ipify.org?format=json')
		text = self.driver.find_element_by_css_selector('body').text
		# print(text)
		return text
	
	def run_js (self):
		try:
			return self.driver.execute_script("")
		
		except Exception as e:
			print("Lỗi ", e)
	
	def select_option (self, locatorValue, locatorType, value_select, type_value="index"):
		try:
			locatorType = locatorType.lower()
			webElement = self.wait_element(locatorValue, locatorType)
			# webElement.click()
			opt_select = Select(webElement)
			if type_value == "index":
				opt_select.select_by_index(value_select)
			elif type_value == "value":
				opt_select.select_by_value(value_select)
			elif type_value == "text":
				opt_select.select_by_visible_text(value_select)
		
		except Exception as e:
			print("Lỗi ", e)
	
	def choose_radio_button (self):
		self.click_element("//input[@name='sex' and @value='" + str(random.randint(1, 2)) + "']", "xpath")
	
	def get_cookies (self):
		try:
			return self.driver.get_cookies()
		
		except Exception as e:
			print("Lỗi ", e)
	
	def set_cookies (self, cookie):
		try:
			self.driver.add_cookie(cookie)
		
		except Exception as e:
			print("Lỗi ", e)
	
	def go_to_url (self, url):
		try:
			self.driver.get(url)
		
		except Exception as e:
			print("Lỗi ", e)
	
	def pause (self):
		try:
			while 1:
				pass
		
		except Exception as e:
			print("Lỗi ", e)
	
	def get_source_url (self, url):
		try:
			self.driver.get(url)
			return self.driver.page_source
		
		except Exception as e:
			print("Lỗi ", e)
	
	def upload_file (self, file_path, locatorValue, locatorType="id"):
		try:
			locatorType = locatorType.lower()
			webElement = self.wait_element(locatorValue, locatorType)
			webElement.send_keys(file_path)
		
		except Exception as e:
			print("Lỗi ", e)
	
	def dowload_file_event_click (self, locatorValue, locatorType="id"):
		try:
			if hasattr(self, "folder_download"):
				locatorType = locatorType.lower()
				webElement = self.wait_element(locatorValue, locatorType)
				webElement.click()
				
				def get_last_downloaded_file_path ():
					while not os.listdir(self.folder_download.name):
						time.sleep(0.5)
					return max(
						[os.path.join(self.folder_download.name, f) for f in os.listdir(self.folder_download.name)],
						key=os.path.getctime)
				
				while '.part' in get_last_downloaded_file_path():
					time.sleep(0.5)
				file = get_last_downloaded_file_path()
				print(file)
				with open(file, "rb") as file_handle:
					file_stream = file_handle.read()
				self.folder_download.cleanup()
				del self.folder_download
				return file_stream
				# shutil.move(get_last_downloaded_file_path(dummy_dir), os.path.join(destination_dir, new_file_name))
			else:
				self.folder_download.cleanup()
				del self.folder_download
				print("Chưa cấu hình thư mục download chrome")
		except Exception as e:
			print("Lỗi ", e)
	
	def action_chains (self):
		action = ActionChains(self.driver)  # có thêm nhiều dạng hành động kéo thả nữa
	
	def open_new_tab (self, url=""):
		try:
			self.driver.execute_script(f"window.open({url});")
		
		except Exception as e:
			print("Lỗi ", e)
	
	def switch_tab (self, index_tab):
		try:
			self.driver.switch_to.window(self.driver.window_handles[index_tab])
		
		except Exception as e:
			print("Lỗi ", e)
	
	def switch_to_frame (self, frame):
		try:
			self.driver.switch_to.frame(frame)
		
		except Exception as e:
			print("Lỗi ", e)
	
	def switch_to_main_page (self):
		try:
			self.driver.switch_to.default_content()
		
		except Exception as e:
			print("Lỗi ", e)
	
	def reload_page (self):
		self.driver.refresh()
	
	def is_opening (self):
		try:
			self.driver.get("google.com")
			return True
		except WebDriverException:
			print("webdriver closed by user")
			return False
	
	def close_chrome (self, remove_profile=True):
		try:
			if self.is_opening:
				print("Closing chrome")
				if hasattr(self, "folder_download"):
					self.folder_download.cleanup()
				self.driver.close()
				self.driver.quit()
			if remove_profile and os.path.isdir(self.folder_profile_current):
				print("Removing profile")
				atexit.register(lambda: remove_dir(self.folder_profile_current))
				# time.sleep(1)
				# remove_dir(self.folder_profile_current)
		except:
			atexit.register(lambda remove_profile=remove_profile: self.close_chrome(remove_profile))


class ContextAutoSelenium():
	def __init__ (self, profile_name="", executable_path="chromedriver", browserName="chrome", remove_profile=True,
				  **configs):
		self.profile_name = profile_name
		self.executable_path = executable_path
		self.browserName = browserName
		self.configs = configs
		self.remove_profile = remove_profile
	
	def __enter__ (self):
		self.auto = Auto_Selenium(profile_name=self.profile_name, executable_path=self.executable_path,
			browserName=self.browserName, **self.configs)
		if self.auto.is_opening is False:
			raise IOError('Chrome chưa được mở')
		return self.auto
	
	def __exit__ (self, exc_type, exc_value, traceback):
		self.auto.close_chrome(self.remove_profile)


if __name__ == '__main__':
	auto = Auto_Selenium("chrome")
	auto.go_to_url("http://www.dummypoint.com/seleniumtemplate.html")
	# auto.clickOnElement("gLFyf", "class")
	auto.send_text("phim hay", "gLFyf", "class")
	auto.get_element("gLFyf", "class").submit()
	# auto.sendText(Keys.RETURN,"gLFyf", "class")
