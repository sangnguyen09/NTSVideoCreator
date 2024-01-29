from gui.helpers.translatepy.language import Language
from gui.helpers.translatepy.translators.base import BaseTranslateException, BaseTranslator
from gui.helpers.translatepy.utils.annotations import Tuple
from gui.helpers.translatepy.utils.request import Request


class MyMemoryException(BaseTranslateException):
    error_codes = {
        "NO_MATCH": "There is no match to the translation"
    }


class MyMemoryTranslate(BaseTranslator):
    """
    translatepy's implementation of MyMemory
    """

    def __init__(self, request: Request = Request()):
        self.session = request
        self.base_url = "https://api.mymemory.translated.net/get"

    def _translate(self, text: str, destination_language: str, source_language: str,**kwargs) -> Tuple[str, str]:
        """
        This is the translating endpoint

        Must return a tuple with (detected_language, result)
        """
        request = self.session.get(self.base_url, params={"q": text, "langpair": source_language + "|" + destination_language})
        
        if request.json()['responseData']['translatedText'] =="PLEASE SELECT TWO DISTINCT LANGUAGES":
           raise MyMemoryException("NO_MATCH")

        if int(request.json()['responseStatus']) == 200:
            try:
                result = request.json()["matches"][0]
            except IndexError:
                raise MyMemoryException("NO_MATCH")
            try:
                _detected_language = request.json()["responseData"]['detectedLanguage']
            except Exception:
                _detected_language = source_language
            return _detected_language, result["translation"]

    def _language(self, text: str) -> str:
        """
        This is the language detection endpoint

        Must return a string with the language code
        """
        # You could use `self.session` to make a request to the endpoint, with all of the parameters
        request = self.session.get(self.base_url, params={"q": text, "langpair": "autodetect|en"})
        
        if request.json()['responseData']['translatedText'] =="PLEASE SELECT TWO DISTINCT LANGUAGES":
            return "en"

        if int(request.json()['responseStatus']) == 200:
            try:
                result = request.json()
                _detected_language = result["responseData"]['detectedLanguage']
                return _detected_language
            except IndexError:
                raise MyMemoryException("NO_MATCH")

    def _language_normalize(self, language: Language) -> str:
        """
        This is the language validation function
        It receives a "translatepy.language.Language" object and returns the correct language code

        Must return a string with the correct language code
        """
        if language.id == "auto":
            return "autodetect"
        return language.alpha2

    def _language_denormalize(self, language_code) -> str:
        """
        This is the language denormalization function
        It receives a string with the translator language code and returns a "translatepy.language.Language" object

        Must return a string with the correct language code
        """
        language_code = str(language_code).split("-")[0]
        if language_code == "autodetect":
            return Language("auto")
        elif str(language_code).lower() in {"zh-cn", "zh"}:
            return Language("zho")
        return Language(language_code)

    def __str__(self) -> str:
        return "MyMemory"


if __name__ == "__main__":
    serr = MyMemoryTranslate()
    res = serr.language("Phận con trai 12 bến nước")
    print(res.result.as_dict())
    # rr =serr.language()