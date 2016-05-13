# coding: utf-8
import re
import six
import chardet
import logging
from unicodedata import category
import unicodedata
from datetime import datetime, date
from unidecode import unidecode

log = logging.getLogger(__name__)
COLLAPSE = re.compile(r'\s+')
WS = ' '

# Unicode character classes, see:
# http://www.fileformat.info/info/unicode/category/index.htm
CATEGORIES = {
    'C': None,
    'M': None,
    'Z': WS,
    'P': '',
    'S': WS
}


def latinize_text(text):
    if not isinstance(text, six.text_type):
        return text
    text = text.lower()
    text = text.replace(u'ə', 'a')
    return unicode(unidecode(text))


def normalize_strong(text):
    if not isinstance(text, six.string_types):
        return

    if six.PY2 and not isinstance(text, six.text_type):
        text = text.decode('utf-8')

    text = latinize_text(text.lower())
    text = unicodedata.normalize('NFKD', text)
    characters = []
    for character in text:
        category = unicodedata.category(character)[0]
        character = CATEGORIES.get(category, character)
        if character is None:
            continue
        characters.append(character)
    text = u''.join(characters)
    return COLLAPSE.sub(WS, text).strip(WS)


def string_value(value):
    if value is None:
        return
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    elif isinstance(value, float):
        if value.is_integer():
            return int(value)
        return unicode(value)
    elif isinstance(value, six.string_types):
        if not isinstance(value, six.text_type):
            enc = chardet.detect(value) or 'utf-8'
            value = value.decode(enc)
            value = ''.join(ch for ch in value if category(ch)[0] != 'C')
            value = value.replace(u'\xfe\xff', '')  # remove BOM
        if not len(value.strip()):
            return
        return value
    else:
        value = unicode(value)
    return value