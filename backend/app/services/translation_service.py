# app/services/translation_service.py
from polyglot.detect import Detector
from libretranslate import LibreTranslateAPI

class TranslationService:
    def __init__(self):
        self.translator = LibreTranslateAPI("http://localhost:5000")  # Run LibreTranslate locally
    
    def detect_language(self, text: str) -> str:
        detector = Detector(text)
        return detector.language.code
    
    def translate_to_english(self, text: str, source_lang: str) -> str:
        if source_lang == 'en':
            return text
        return self.translator.translate(text, source_lang, 'en')
    
    def translate_from_english(self, text: str, target_lang: str) -> str:
        if target_lang == 'en':
            return text
        return self.translator.translate(text, 'en', target_lang)