import os


RELATIVE_PATH = lambda path: os.path.join(os.path.abspath(os.getcwd()), str(path))
PATH_TOOL_FFSUB = RELATIVE_PATH("ffsub")
# PATH_TOOL_FFSUB = r'E:\Project\Python\_APP\ffsub\dist\ffsub'
URL_API_BASE = "http://127.0.0.1:8000/api/v1"
# URL_API_BASE = "https://app.ntstool.com/api/v1"
VERSION_CURRENT = "1.0"  #
# git branch -M v4.4
PATH_FFCUT = RELATIVE_PATH('ffcut.exe')



LANGUAGES_TTS_VIETTNAM = {
	"vi": "Vietnamese",
}

LANGUAGES_TTS_ENGLISH = {
	"en": "English",
}

LANGUAGES_SUPPORT_TRANSPRO1 = {
	
	"zh": [
		"en", "ja", "ko", "fr", "es", "it", "de", "id", "th", "vi"
	]
	
	
	, "en": [
		"zh", "ja", "ko", "fr", "es", "it", "de", "id", "th", "vi", "hi"
	]
	,
	
	"ja": [
		"zh", "en", "ko"
	],
	
	"ko": [
		"zh", "ja", "en"
	],
	"fr": [
		"zh", "en", "es", "it", "de"
	],
	
	"es": [
		"zh", "en", "fr", "it", "de"
	],
	
	"it": [
		"zh", "en", "fr", "es", "de"
	],
	
	"de": [
		"zh", "en", "fr", "it", "es"
	],
	"vi": [
		"zh", "en"
	],
	
	"th": [
		"zh", "en"
	],
	
	"id": [
		"zh", "en"
	],
	
	
}

if __name__ == "__main__":
	#
	# response = requests.head(
	# 	"https://ntstool.com/wp-content/uploads/2024/01/z45.7z",  # Example file
	# 	allow_redirects=True
	# )
	#
	# URL = "https://ntstool.com/wp-content/uploads/2024/01/z45.7z"
	# filename = os.path.basename(URL)
	#
	# response = requests.get(URL, stream=True)
	#
	# if response.status_code == 200:
	# 	with open(filename, 'wb') as out:
	# 		out.write(response.content)

	# atempo = f"atempo=1"
	# atempo_ =0.15
	# if atempo_ < 0.5:
	# 	# atempo = f"atempo=1"
	# 	hs_tempo = 1
	# 	# n = 1
	# 	for i in range(5):
	# 		hs_t = (atempo_ * 2) * hs_tempo
	# 		# print(hs_t)
	# 		if hs_t >= 0.5:
	# 			atempo = f"atempo={hs_t}{',atempo=0.5' * hs_tempo}"
	# 			break
	# 		# n += 1
	# 		hs_tempo += 1
	# print(atempo)
	# print(',atempo=0.5' * 2)
	# url_download= "https://ntstool.com/wp-content/uploads/2023/07/banmai.mp3"
	# content = requests.get(url_download).content
	# print(content)
	# filenam = "file_temp.mp3"
	# with open(filenam, "wb") as file:
	# 	file.write(content)
	# os.startfile(filenam)
	ttt = "vn"
	# print(ttt[:2])
	# chunk_skip = 3
	# sub_tran = re.sub(r'bro', 'Anh trai', 'Bro anh ơi',flags=re.IGNORECASE)
	# print(sub_tran)
