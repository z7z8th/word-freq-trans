import argostranslate.package
import argostranslate.translate

from_code = "en"
to_code = "zh"

# Translate
installed_languages = argostranslate.translate.get_installed_languages()
from_lang = list(filter(
        lambda x: x.code == from_code,
        installed_languages))[0]
to_lang = list(filter(
        lambda x: x.code == to_code,
        installed_languages))[0]
translation = from_lang.get_translation(to_lang)
translatedText = translation.translate("Hello World!")
print(translatedText)