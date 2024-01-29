from enum import Enum

from gui.helpers.handle_speech.speech_to_text import GoogleSpeechToText
from gui.helpers.selelium.get_token import get_token_fpt, get_token_viettelAI
from gui.helpers.translatepy.translators.fpt import FPTTranslator
from gui.helpers.translatepy.translators.tts_da_ngon_ngu import TTSDaNgonNguTranslator
from gui.helpers.translatepy.translators.tts_folder_voice import TTSVoiceCoSanTranslator
from gui.helpers.translatepy.translators.tts_online_free import TTSFreeOnlineTranslator
from gui.helpers.translatepy.translators.tts_tieng_viet import TTSTiengVietTranslator
from gui.helpers.translatepy.translators.vbee_api import VBeeAPITranslator
from gui.helpers.translatepy.translators.viettel_ai import ViettelAITranslator
from gui.widgets.py_groupbox.tab_con_tach_sub_tu_giong_noi import TabConTachSubTuGiongNoi
from gui.widgets.py_groupbox.tab_con_tach_sub_tu_hinh_anh import TabConTachSubTuHinhAnh
from gui.widgets.py_tab.py_tab_extract_sub_AI import PyTabExtractSubAI
from gui.widgets.py_tab.py_tab_extract_sub_capcut import PyTabExtractSubCapCut
from gui.widgets.py_tab.py_tab_extract_sub_use_youtube import PyTabExtractSubServerYoutube


# except:
# 	print("Lỗi server vui lòng liên hệ admin")



# class TabIndexTranslate(Enum):
# 	Baidu = 0
# 	ChatGPT_Pro = 1
# 	Translate_Pro1 = 2
# 	Translate_Pro2 = 3
# 	ChatGPT_API = 4
# 	ChatGPT_Thucong = 5
# 	Tencent = 6
# 	Alibaba = 7
# 	Google = 8
# 	Microsoft = 9
# 	File_TXT = 10


# SERVER_TRANSLATE_V2 = {
# 	"Baidu Free": {'server': 'baidu',
# 				   'url_check_proxy': 'https://fanyi.baidu.com',
# 				   "language_support": LANGUAGES_BAIDU},
#
# 	"AI Translate Pro": {'server': 'chatgpt_pro',
# 						 'url_check_proxy': 'https://www.google.com',
# 						 "language_support": LANGUAGES_TRANS},
#
# 	"Pro 1": {'server': 'translate_pro1',
# 			  'url_check_proxy': 'https://www.google.com',
# 			  "language_support": LANGUAGES_TRANS},
#
# 	"Pro 2": {'server': 'translate_pro2',
# 			  'url_check_proxy': 'https://www.google.com',
# 			  "language_support": LANGUAGES_TRANS},
#
# 	"OPEN AI API": {'server': 'chatgpt_api_key',
# 					'url_check_proxy': 'https://www.google.com', "language_support": LANGUAGES_TRANS},
#
# 	"Dịch AI Bằng Web": {'server': 'chatgpt_thu_cong',
# 						 'url_check_proxy': 'https://www.google.com',
# 						 "language_support": LANGUAGES_TRANS},
#
# 	"Tencent Free": {'server': 'sogou',
# 					 'url_check_proxy': 'https://fanyi.sogou.com',
# 					 "language_support": LANGUAGES_TRANS},
#
# 	"Alibaba Free": {'server': 'alibaba',
# 					 'url_check_proxy': 'https://translate.alibaba.com',
#
# 					 "language_support": LANGUAGES_TRANS},
#
#
# 	"Google Free": {'server': 'google',
# 					'url_check_proxy': 'https://www.google.com',
# 					"language_support": {**LANGUAGES_TRANS, "tl": "Philippine"}},
#
# 	"Microsoft Free": {'server': 'bing',
# 					   'url_check_proxy': 'https://www.bing.com',
# 					   "language_support": {**LANGUAGES_TRANS, "fil": "Philippine"}},
# 	# "Translate": {'server': 'translatecom',
# 	# 			  'url_check_proxy': 'https://www.bing.com',
# 	# 			  "language_support": {**LANGUAGES_TRANS, "fil": "Philippine"}},
#
# 	"Từ File TXT": {'server': 'txt_file',
# 					'url_check_proxy': 'https://www.google.com',
# 					"language_support": LANGUAGES_TRANS},
# }


# SERVER_API_TTS = {"apiFPT": "FPT AI"}
class TabIndexTTS(Enum):
	FreeTTS = 0
	TTSTiengViet = 1
	TTSDaNgonNgu = 2
	FPTAI = 3
	VIETTELAI = 4
	VbeeAPI = 5
	# Google = 6
	CoSan = 6


# VStudio = 8


TYPE_TTS_SUB = {
	"origin": "SUB GỐC",
	"trans": "SUB DỊCH",
}


class TypeSubEnum(Enum):
	origin = 0
	trans = 1


# print(MODE_RENDER_TTS)

# MODE_TTS = MODE_RENDER_TTS
# # print(GENDER_VOICE_TTSFREEAPI)
voice_co_san = 'cosan'

# print(GENDER_VOICE_COSAN)
SERVER_TAB_TTS = {
	
	"Free": {'server_trans': lambda *args, **kwargs: TTSFreeOnlineTranslator(*args, **kwargs),
			 "key_lang": 'language_tts_free', "gender": 'tts_free_v2',
	
			 "name_api_db": "apiFreeTTS", "file_account": None, "web": None, "check_balance": False},
	
	"Tiếng Việt Pro": {'server_trans': lambda *args, **kwargs: TTSTiengVietTranslator(*args, **kwargs),
					   "key_lang": 'language_vi', "gender": 'tieng_viet',
					   "name_api_db": "tieng_viet_paid", "file_account": None, "web": None, "check_balance": True},
	
	
	"Multilingual Natural Voice": {'server_trans': lambda *args, **kwargs: TTSDaNgonNguTranslator(*args, **kwargs),
								   "key_lang": 'language_tts_pro', "gender": 'tts_pro',
								   "name_api_db": "da_ngon_ngu_paid", "file_account": None, "web": None,
								   "check_balance": True},
	
	"FPT AI": {'server_trans': lambda *args, **kwargs: FPTTranslator(*args, **kwargs),
			   "key_lang": 'language_vi', "gender": 'fpt', "name_api_db": "apiFPT",
			   "file_account": "fpt-account.txt", 'get_token': get_token_fpt,
			   "web": "https://fpt.ai/vi", "check_balance": True},
	
	"VIETTEL AI": {'server_trans': lambda *args, **kwargs: ViettelAITranslator(*args, **kwargs),
				   "key_lang": 'language_vi', "gender": 'viettel',
				   "name_api_db": "apiViettelAi", "file_account": "viettelAI-account.txt",
				   'get_token': get_token_viettelAI, "web": "https://viettelai.vn", "check_balance": True},
	
	
	"Vbee API": {'server_trans': lambda *args, **kwargs: VBeeAPITranslator(*args, **kwargs),
				 "key_lang": 'language_vbee', "gender": 'vbee',
				 "name_api_db": "apiVbee", "file_account": None,
				 "web": "https://vbee.vn/?aff=ntstool", "check_balance": False},
	#
	# "Google": {'server_trans': lambda *args, **kwargs: GoogleTranslateV2(*args, **kwargs),
	# 		   "language_tts": LANGUAGES_TTS_GOOGLE, "gender": GENDER_VOICE_GOOGLE, "name_api_db": "apiGoogle",
	# 		   "file_account": None, "web": None, "check_balance": False},
	
	
	"Voice Có Sẵn": {'server_trans': lambda *args, **kwargs: TTSVoiceCoSanTranslator(*args, **kwargs),
					 "key_lang": 'language_tts_free', "gender": 'cosan',
					 "name_api_db": "apiVoiceCoSan",
					 "file_account": None, "web": None, "check_balance": False},
	
	# "Voice Cũ": {'server_trans': lambda *args, **kwargs: VBeeStudioTranslator(*args, **kwargs),
	# 		  "language_tts": LANGUAGES_TTS_VIETTNAM, "gender": GENDER_VOICE_VBEE_STUDIO,
	# 		  "name_api_db": "apiVStudio", 'get_token': get_token_vbee, "file_account": None,
	# 		  "web": None, "check_balance": True},
	
	
}
SERVER_SPEECHTOTEXT = {
	"Google Free": lambda *args, **kwargs: GoogleSpeechToText(*args, **kwargs)
}
CACH_LAY_SUB_YOUTUBE = {
	"C1": "Từ Video Nguồn",
	# "C2": "Từ Server Free",
	# "C3": "Từ Google Speech",
	
}


class CachLaySubYoutubeEnum(Enum):
	Nguon = 'C1'


NAME_AI_LOCAL = "AI local"

SERVER_EXTRACT_VOICE = {
	NAME_AI_LOCAL: lambda *args: PyTabExtractSubAI(*args),
	"CapCut": lambda *args: PyTabExtractSubCapCut(*args),
	"Youtube": lambda *args: PyTabExtractSubServerYoutube(*args, CACH_LAY_SUB_YOUTUBE, CachLaySubYoutubeEnum),
	# "Server Free": lambda *args: PyTabExtractSubServerSTT(*args, SERVER_SPEECHTOTEXT)
}

TYPE_EXTRACT_SUB = {
	"Giọng Nói": lambda *args, **kwargs: TabConTachSubTuGiongNoi(*args, SERVER_EXTRACT_VOICE, NAME_AI_LOCAL, **kwargs),
	"Hình Ảnh": lambda *args, **kwargs: TabConTachSubTuHinhAnh(*args, **kwargs)
}


class IndexExtractYoutube(Enum):
	AILOCAL = 0
	AIPAID = 1


SERVER_EXTRACT_YOUTUBE = ["AI Local", "AI Trả Phí"]
# print(1111)
# if __name__ == "__main__":
# 	print([1, 2, 4, 5, 6, 7, 8, 9][:2])
# 	# des_lang = Language('fr').as_dict().get('in_foreign_languages').get('en')
# 	# print(des_lang)  --> 00:00:31,350
