import logging
import gettext
from pathlib import Path

logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.INFO)
lang = None

def set_locale(locale_code):
    global lang
    locales_dir = Path(__file__).resolve().parent / 'locales'
    lang = gettext.translation('art-timelapse', localedir=locales_dir, languages=[locale_code], fallback=locale_code == 'en')

set_locale('en')

def _(text):
    return lang.gettext(text)
