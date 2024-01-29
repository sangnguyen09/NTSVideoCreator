from datetime import datetime

from gui.helpers.translatepy.language import Language
from gui.helpers.translatepy.translators.base import BaseTranslator
from gui.helpers.translatepy.utils.annotations import Tuple
from gui.helpers.translatepy.utils.request import Request


class TranslateComTranslate(BaseTranslator):
    """
    translatepy's implementation of translate.com
    """

    def __init__(self, request: Request = Request()):
        self.session = request
        self.translate_url = "https://www.translate.com/translator/ajax_translate"
        self.langdetect_url = "https://www.translate.com/translator/ajax_lang_auto_detect"

    def _translate(self, text: str, destination_language: str, source_language: str) -> Tuple[str, str]:
        """
        This is the translating endpoint

        Must return a tuple with (detected_language, result)
        """
        if source_language == "auto":
            source_language = self._language(text)
        print(source_language)
        request = self.session.post(self.translate_url, data={"text_to_translate": text, "source_lang": source_language, "translated_lang": destination_language, "use_cache_only": "false"})
        # print(request.text)
        # print(request.status_code)
        if request.status_code < 400:
            result = request.json()["translated_text"]
            return source_language, result

    def _language(self, text: str) -> str:
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
    def _language_normalize(self, language: Language):
        if language.id == "zho":
            return "zh-CN"
        elif language.id == "och":
            return "zh-TW"
        return language.alpha2

    def _language_denormalize(self, language_code):
        if str(language_code).lower() == "zh-cn":
            return Language("zho")
        elif str(language_code).lower() == "zh-tw":
            return Language("och")
        return Language(language_code)

    def __str__(self) -> str:
        return "Translate.com"

if __name__ == "__main__":
    start_time = datetime.strptime('00:00:07,433' ,"%H:%M:%S,%f")
    end_time = datetime.strptime('00:00:07,133', "%H:%M:%S,%f")
    duration = 3/(end_time - start_time).total_seconds()
    print(duration)
    mmm =TranslateComTranslate()
    print(mmm.translate("山门顶竞有地球上早已火灭绝的绿植",'vi').result)