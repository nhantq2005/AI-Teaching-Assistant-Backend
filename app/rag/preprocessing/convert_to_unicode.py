import re

TCVN3_CHARS = "µ¸¶·¹¨»¾¼½Æ©ÇÊÈÉË®ÌÐÎÏÑªÒÕÓÔÖ×ÝØÜÞßãáâä«åèæçé¬êíëìîïóñòô\xadõøö÷ùúýûüþ"
UNICODE_CHARS = "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵ"
TCVN3_MAP = str.maketrans(TCVN3_CHARS, UNICODE_CHARS)
STD_VN_CHARS = set(
    "àáảãạăằắẳẵặâầấẩẫậđèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬĐÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴ")
TCVN3_SIGNATURES = set(TCVN3_CHARS) - STD_VN_CHARS


def convert_tcvn3_to_unicode(text: str) -> str:
    text = text.replace("¤", "ô")
    text = re.sub(r'[-−]([¬êíëìî])', r'ư\1', text)
    text = re.sub(r'[-−]([õøö÷ù])', r'ư\1', text)
    if any(c in TCVN3_SIGNATURES for c in text):
        return text.translate(TCVN3_MAP)

    return text