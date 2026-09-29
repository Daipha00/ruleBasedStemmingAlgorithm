import re

DEBUG = False


def debug_print(stage, word):
    if DEBUG:
        print(f"  {stage:<30}: {word}")


def safe_sub(pattern, repl, word, min_len=3):
    new_word = re.sub(pattern, repl, word)

    if len(new_word) >= min_len:
        return new_word

    return word


def stem(word):

    if not isinstance(word, str):
        return ""

    word = word.lower().strip()

    if not word:
        return ""

    original = word.split()[0]
    word = original

    debug_print("original", word)

    word = strip_compound_prefixes(word)
    debug_print("compound prefixes", word)

    word = strip_simple_prefixes(word)
    debug_print("simple prefixes", word)

    word = strip_tense_markers(word)
    debug_print("tense markers", word)

    word = strip_object_markers(word)
    debug_print("object markers", word)

    before_suffix = word

    word = strip_derivational_suffixes(word)
    debug_print("derivational suffixes", word)

    if (
        (
            before_suffix.endswith("ia")
            and not before_suffix.endswith("ilia")
            and word.endswith("i")
        )
        or
        (
            before_suffix.endswith("ea")
            and word.endswith("e")
        )
    ):
        final_word = word
    else:
        final_word = strip_final_vowel(word)

    word = final_word
    debug_print("final vowel", word)

    if len(word) < 2:
        return original

    return word

def stem_with_trace(word):

    if not isinstance(word, str):
        return {}

    word = word.lower().strip()

    if not word:
        return {}

    word = word.split()[0]
    trace = {"original": word}

    word = strip_compound_prefixes(word)
    trace["compound_prefixes"] = word

    word = strip_simple_prefixes(word)
    trace["simple_prefixes"] = word

    word = strip_tense_markers(word)
    trace["tense_markers"] = word

    word = strip_object_markers(word)
    trace["object_markers"] = word

    before_suffix = word

    word = strip_derivational_suffixes(word)
    trace["derivational_suffixes"] = word

    if (
        (
            before_suffix.endswith("ia")
            and not before_suffix.endswith("ilia")
            and word.endswith("i")
        )
        or
        (
            before_suffix.endswith("ea")
            and word.endswith("e")
        )
    ):
        final_word = word
    else:
        final_word = strip_final_vowel(word)

    return trace




def strip_compound_prefixes(word):

    patterns = [

        r'^(nisingali|usingali|asingali|tusingali|msingali|wasingali)',

        r'^(nisingeli|usingeli|asingeli|tusingeli|msingeli|wasingeli)',

        r'^(nisinge|usinge|asinge|tusinge|msinge|wasinge)',

        r'^(isingali|zisingali|yasingali)',

        r'^(isingeli|zisingeli|yasingeli)',

        r'^(isinge|zisinge|yasinge)',

        r'^(ningali|tungali|wangali|ungali|angali|mngali)',

        r'^(yangali|zingali|ingali)',

        r'^(ningeli|tungeli|wangeli|ungeli|angeli|mngeli)',

        r'^(yangeli|zingeli|ingeli)',

        r'^lililo',
        r'^liliyo',
        r'^liliye',
        r'^lilicho',
        r'^lilipo',
        r'^lilio',

        r'^zilizo',
        r'^ziliyo',
        r'^ziliye',
        r'^zilicho',
        r'^zilipo',
        r'^zilio',

        r'^ilicho',

        r'^(niliye|uliye|aliye|tuliye|mliye|waliye)',

        r'^(niliya|uliya|aliya|tuliya|mliya|waliya)',

        r'^(niliyo|uliyo|aliyo|tuliyo|mliyo|waliyo)',

        r'^(yaliyo|iliyo|kiliyo|liliyo)',

        r'^(yaliye|iliye|kiliye)',

        r'^(nilicho|ulicho|alicho|tulicho|mlicho|walicho|kilicho)',

        r'^(nilipo|ulipo|alipo|tulipo|mlipo|walipo)',

        r'^(yalipo|ilipo)',

        r'^(nilio|ulio|alio|tulio|mlio|walio)',

        r'^(yalio|ilio)',

        r'^(nijapo|ujapo|ajapo|tujapo|mjapo|wajapo)',

        r'^(nisipo|usipo|asipo|tusipo|msipo|wasipo)',

        r'^(ninaye|unaye|anaye|tunaye|mnaye|wanaye)',

        r'^(nitaye|utaye|ataye|tutaye|mtaye|wataye)',

        r'^(niki|uki|aki|tuki|mki|waki|ziki|yaki|iki)',

        r'^(ninge|unge|ange|tunge|mnge|wange)',

        r'^(kumu|kuwa|kum|kuw)',
    ]

    for pattern in patterns:
        word = safe_sub(
            pattern,
            '',
            word
        )

    return word


def strip_simple_prefixes(word):

    patterns = [
        r'^(nina|nime|nita)',
        r'^(una|ume|uta)',
        r'^(ana|ame|ata)',
        r'^(tuna|tume|tuta)',
        r'^(mna|mme|mta)',
        r'^(wana|wame|wata)',
        r'^(nili|tuli|mli|wali)',
        r'^(uli|ali)',
        r'^hu',

        r'^ku(?=[aeiou])',

        r'^lili',
        r'^(ina|ita|ili|ime|inge)',
        r'^(zina|zita|zili|zime|zinge)',
        r'^(yana|yata|yali|yame|yange)',

        r'^(ni|tu|wa|mu)(?=[aeiou])',
    ]

    for pattern in patterns:
        word = safe_sub(pattern, '', word)

    return word


def strip_tense_markers(word):

    word = safe_sub(r'^ngali', '', word)
    word = safe_sub(r'^ngeli', '', word)
    word = safe_sub(r'^nge', '', word)

    temp = re.sub(r'^li(?=[aeiou])', '', word)
    if len(temp) >= 3:
        word = temp

    word = safe_sub(r'^na(?=.{3,})', '', word)

    temp = re.sub(r'^ta(?=[aeiou].{2,})', '', word)
    if len(temp) >= 3:
        word = temp

   
    word = safe_sub(r'^ja(?=[aeiou])', '', word)
    word = safe_sub(r'^yo(?=[aeiou])', '', word)
    word = safe_sub(r'^ye(?=[aeiou])', '', word)

    temp = re.sub(r'^cho(?=[aeiou])', '', word)
    if len(temp) >= 3:
        word = temp

    word = safe_sub(r'^vyo', '', word)
    word = safe_sub(r'^ka(?=[aeiou].{2,})', '', word)

    return word



def strip_object_markers(word):
    word = safe_sub(
        r'^ji(?=[aeiou])',
        '',
        word
    )

    word = safe_sub(
        r'^(mw|mu|ku|wa|ki|vi|zi|li|ya|pa|u)(?=[aeiou])',
        '',
        word
    )

    return word



def strip_derivational_suffixes(word):
  
    if word.endswith("ia"):
        result = word[:-1]

        if len(result) >= 3:
            return result

  
    if word.endswith("ea"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    if word.endswith("ika"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    
    if word.endswith("eka"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    if word.endswith(("isha", "esha")):
        result = word[:-1]

        if len(result) >= 3:
            return result

    if word.endswith("ana"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    return word



def strip_final_vowel(word):

    if len(word) <= 2:
        return word

    if word.endswith(("e", "i", "o", "u")):
        return word

  
    if word.endswith("aana"):
        return word

    # Remove final a.
    if word.endswith("a"):
        result = word[:-1]

        if len(result) >= 2:
            return result

    return word

