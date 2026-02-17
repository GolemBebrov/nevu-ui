class InputType:
    NUMBERS = "0123456789"
    HEX_DIGITS = f"{NUMBERS}abcdefABCDEF"

    LETTERS_ENG = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    LETTERS_RUS = "йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
    LETTERS_UKR = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюяАБВГҐДЕЄЖЗИІЇЙКЛМНОПРСТУФХЦЧШЩЬЮЯ"
    LETTERS_BEL = "абвгдеёжзійклмнопрстуўфхцчшыьэюяАБВГДЕЁЖЗІЙКЛМНОПРСТУЎФХЦЧШЫЬЭЮЯ"
    
    LETTERS_GER = f"{LETTERS_ENG}äöüÄÖÜß"
    LETTERS_FR = f"{LETTERS_ENG}àâçéèêëîïôûüÿæœÀÂÇÉÈÊËÎÏÔÛÜŸÆŒ"
    LETTERS_ES = f"{LETTERS_ENG}áéíóúüñÁÉÍÓÚÜÑ"
    LETTERS_IT = f"{LETTERS_ENG}àèéìòóùÀÈÉÌÒÓÙ"
    LETTERS_PL = f"{LETTERS_ENG}ąćęłńóśźżĄĆĘŁŃÓŚŹŻ"
    LETTERS_PT = f"{LETTERS_ENG}àáâãçéêíóôõúüÀÁÂÃÇÉÊÍÓÔÕÚÜ"
    
    LETTERS_GR = "αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    LETTERS_AR = "ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوي"
    LETTERS_HE = "אבגדהוזחטיכךלמםנןסעפףצץקרשת"
    LETTERS_JP_KANA = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロワヲンーぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをん"
    LETTERS_CN_COMMON = "的一是不了人我在有他这为之大来以个中上们"
    LETTERS_KR_HANGUL = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
    LETTERS_HI_DEVANAGARI = "अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"

    WHITESPACE = " \t\n\r\f\v"
    CONTROL_CHARS = "".join(chr(i) for i in range(32))

    PUNCTUATION = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    DASHES = "-—‒–"
    QUOTES = "\"'`«»"
    BRACKETS = "()[]{}"
    APOSTROPHE = "'"
    
    MATH_BASIC = "+-*/="
    MATH_ADVANCED = "><≤≥≠≈±√∑∫"
    CURRENCY = "€£¥₽$"
    MATH_GREEK = "πΩΣΔΘΛΞΦΨΓ"
    
    URL_SYMBOLS = f"{LETTERS_ENG}{NUMBERS}-._~:/?#[]@!$&'()*+,;=%"
    EMAIL_SYMBOLS = f"{LETTERS_ENG}{NUMBERS}-._%+"
    
    MARKDOWN = "*_`~>#+![]()="
    EMOJIS_BASIC = "😀😂😍🤔👍👎❤️💔"
    SPECIAL_SYMBOLS = "©®™°№§"
    BOX_DRAWING = "─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"

    ALL_CYRILLIC_LETTERS = "".join(set(LETTERS_RUS + LETTERS_UKR + LETTERS_BEL))
    ALL_LATIN_EXT_LETTERS = "".join(set(LETTERS_GER + LETTERS_FR + LETTERS_ES + LETTERS_IT + LETTERS_PL + LETTERS_PT))
    ALL_LETTERS = "".join(set(ALL_CYRILLIC_LETTERS + ALL_LATIN_EXT_LETTERS + LETTERS_GR + LETTERS_AR + LETTERS_HE + LETTERS_JP_KANA + LETTERS_CN_COMMON + LETTERS_KR_HANGUL + LETTERS_HI_DEVANAGARI))

    ALL_PUNCTUATION = "".join(set(PUNCTUATION + DASHES + QUOTES + BRACKETS + APOSTROPHE))
    ALL_MATH = "".join(set(MATH_BASIC + MATH_ADVANCED + CURRENCY + MATH_GREEK))
    ALL_SYMBOLS = "".join(set(ALL_PUNCTUATION + ALL_MATH + MARKDOWN + EMOJIS_BASIC + SPECIAL_SYMBOLS + BOX_DRAWING))
    
    ALPHANUMERIC_ENG = LETTERS_ENG + NUMBERS
    ALPHANUMERIC_RUS = LETTERS_RUS + NUMBERS

    PRINTABLE = ALL_LETTERS + NUMBERS + ALL_SYMBOLS + WHITESPACE
