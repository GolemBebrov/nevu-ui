from dataclasses import dataclass
import string

def connect(text):
    return "".join(set(text))

@dataclass(frozen=True)
class _Letters:
    ENG = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    RUS = "йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
    UKR = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    BEL = "абвгдеёжзійклмнопрстуўфхцчшыьэюяАБВГДЕЁЖЗІЙКЛМНОПРСТУЎФХЦЧШЫЬЭЮЯ"
    
    GER = f"{ENG}äöüÄÖÜß"
    FR = f"{ENG}àâçéèêëîïôûüÿæœÀÂÇÉÈÊËÎÏÔÛÜŸÆŒ"
    ES = f"{ENG}áéíóúüñÁÉÍÓÚÜÑ"
    IT = f"{ENG}àèéìòóùÀÈÉÌÒÓÙ"
    PL = f"{ENG}ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
    PT = f"{ENG}àáâãçéêíóôõúüÀÁÂÃÇÉÊÍÓÔÕÚÜ"
    
    GR = "αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    AR = "ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوي"
    HE = "אבגדהוזחטיכךלמםנןסעפףצץקרשת"
    JP_KANA = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロワヲンーぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをん"
    CN_COMMON = "的一是不了人我在有他这为之大来以个中上们"
    KR_HANGUL = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
    HI_DEVANAGARI = "अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"

    ALL_CYRILLIC = connect(RUS +  UKR + BEL)
    ALL_LATIN_EXT = connect(GER + FR + ES + IT + PL + PT)
    ALL = connect(ALL_CYRILLIC + ALL_LATIN_EXT + GR + AR + HE + JP_KANA + CN_COMMON + KR_HANGUL + HI_DEVANAGARI)

letters = _Letters()

@dataclass(frozen=True)
class InputType:
    NUMBERS = string.digits
    HEX_DIGITS = string.hexdigits
    
    WHITESPACE = string.whitespace
    CONTROL_CHARS = "".join(chr(i) for i in range(32))

    PUNCTUATION = string.punctuation
    DASHES = "-—‒–"
    QUOTES = "\"'`«»"
    BRACKETS = "()[]{}"
    APOSTROPHE = "'"
    
    LETTERS = letters
    
    MATH_BASIC = "+-*/="
    MATH_ADVANCED = "><≤≥≠≈±√∑∫"
    CURRENCY = "€£¥₽$"
    MATH_GREEK = "πΩΣΔΘΛΞΦΨΓ"
    
    URL_SYMBOLS = f"{letters.ENG}{NUMBERS}-._~:/?#[]@!$&'()*+,;=%"
    EMAIL_SYMBOLS = f"{letters.ENG}{NUMBERS}-._%+"
    
    MARKDOWN = "*_`~>#+![]()="
    EMOJIS_BASIC = "😀😂😍🤔👍👎❤️💔"
    SPECIAL_SYMBOLS = "©®™°№§"
    BOX_DRAWING = "─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"

    ALL_PUNCTUATION = connect(PUNCTUATION + DASHES + QUOTES + BRACKETS + APOSTROPHE)
    ALL_MATH = connect(MATH_BASIC + MATH_ADVANCED + CURRENCY + MATH_GREEK)
    ALL_SYMBOLS = connect(ALL_PUNCTUATION + ALL_MATH + MARKDOWN + EMOJIS_BASIC + SPECIAL_SYMBOLS + BOX_DRAWING)
    
    ALPHANUMERIC_ENG = letters.ENG + NUMBERS
    ALPHANUMERIC_RUS = letters.RUS + NUMBERS

    PRINTABLE = letters.ALL + NUMBERS + ALL_SYMBOLS + WHITESPACE
