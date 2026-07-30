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


# ============================================================
# MAIN STEMMER
# ============================================================

def stem(word):
    original = word.lower().strip().split()[0]
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

    # Keep word before suffix processing
    before_suffix = word

    word = strip_derivational_suffixes(word)
    debug_print("derivational suffixes", word)

    # If derivational processing already removed the final -a
    # from an -ia form, preserve the resulting -i.
    # Prevent double stripping after derivational processing
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

    if len(word) < 3:
        return original

    return word


    original = word.lower().strip().split()[0]
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

    word = strip_derivational_suffixes(word)
    debug_print("derivational suffixes", word)

    word = strip_final_vowel(word)
    debug_print("final vowel", word)

    if len(word) < 3:
        return original

    return word


# ============================================================
# STEMMER WITH TRACE
# ============================================================

def stem_with_trace(word):

    trace = {}

    word = word.lower().strip().split()[0]

    trace["original"] = word

    word = strip_compound_prefixes(word)
    trace["compound_prefixes"] = word

    word = strip_simple_prefixes(word)
    trace["simple_prefixes"] = word

    word = strip_tense_markers(word)
    trace["tense_markers"] = word

    word = strip_object_markers(word)
    trace["object_markers"] = word

    word = strip_derivational_suffixes(word)
    trace["derivational_suffixes"] = word

    word = strip_final_vowel(word)
    trace["final"] = word

    return trace


# ============================================================
# COMPOUND PREFIXES
# ============================================================

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


# ============================================================
# SIMPLE PREFIXES
# ============================================================

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

        r'^ku',

        r'^lili',

        r'^(ina|ita|ili|ime|inge)',

        r'^(zina|zita|zili|zime|zinge)',

        r'^(yana|yata|yali|yame|yange)',

        r'^(ni|tu|wa|mu)',
    ]

    for pattern in patterns:
        word = safe_sub(
            pattern,
            '',
            word
        )

    return word


# ============================================================
# TENSE MARKERS
# ============================================================

def strip_tense_markers(word):

    word = safe_sub(
        r'^ngali',
        '',
        word
    )

    word = safe_sub(
        r'^ngeli',
        '',
        word
    )

    word = safe_sub(
        r'^nge',
        '',
        word
    )

    # Past tense marker -li-
    temp = re.sub(
        r'^li(?=[aeiou])',
        '',
        word
    )

    if len(temp) >= 3:
        word = temp

    # Present tense marker -na-
    word = safe_sub(
        r'^na(?=.{3,})',
        '',
        word
    )

    # Future tense marker -ta-
    temp = re.sub(
        r'^ta(?=[aeiou].{2,})',
        '',
        word
    )

    if len(temp) >= 3:
        word = temp

    word = safe_sub(
        r'^ja',
        '',
        word
    )

    word = safe_sub(
        r'^yo',
        '',
        word
    )

    word = safe_sub(
        r'^ye',
        '',
        word
    )

    temp = re.sub(
        r'^cho(?=[aeiou])',
        '',
        word
    )

    if len(temp) >= 3:
        word = temp

    word = safe_sub(
        r'^vyo',
        '',
        word
    )

    word = safe_sub(
        r'^ka(?=.{3,})',
        '',
        word
    )

    return word


# ============================================================
# OBJECT MARKERS
# ============================================================

def strip_object_markers(word):

    word = safe_sub(
        r'^ji(?=[a-z]{3,})',
        '',
        word
    )

    word = safe_sub(
        r'^(mw|mu|ku|wa|ki|vi|zi|li|ya|pa|u)(?=[aeiou])',
        '',
        word
    )

    return word


# ============================================================
# DERIVATIONAL SUFFIXES
# ============================================================

def strip_derivational_suffixes(word):

    # Passive suffix
    if len(word) > 4 and re.search(r'[^aeio]wa$', word):
        result = re.sub(r'wa$', '', word)
        if len(result) >= 3:
            return result

    # Applicative extension -ilia
# ROOT + ilia -> ROOT
    if len(word) > 6 and re.search(r'ilia$', word):

      result = re.sub(
        r'ilia$',
        '',
        word
    )

    if len(result) >= 4:
        return result

    # Applicative -ia
    if re.search(r'ia$', word):
        result = word[:-1]
        if len(result) >= 3:
            return result

    # Applicative -ea
    if re.search(r'ea$', word):
        result = word[:-1]
        if len(result) >= 3:
            return result

    # Preserve -ika
    if re.search(r'ika$', word):
        result = word[:-1]
        if len(result) >= 3:
            return result

    # Preserve -eka
    if re.search(r'eka$', word):
        result = word[:-1]
        if len(result) >= 3:
            return result

    # Preserve -isha / -esha
    if re.search(r'(isha|esha)$', word):
        return word[:-1]

   # Reciprocal extension -an-
   # Remove -ana when a sufficiently long verbal base remains
    if re.search(r'ana$', word):
      return word[:-1]

    # Preserve -anisha / -anesha
    if re.search(r'(anisha|anesha)$', word):
        return word[:-1]

    return word


def strip_final_vowel(word):

    if len(word) <= 2:
        return word

    if word.endswith('a'):
        return word[:-1]

    if word.endswith('e') and len(word) > 3:
        return word[:-1]

    if word.endswith('i') and len(word) > 4:
        if (
            not word.endswith('ini')
            and not word.endswith('ai')
            and not word.endswith('ki')
            and not word.endswith('ni')
        ):
            return word[:-1]

    if word.endswith('u') and len(word) >= 4:
        return word[:-1]

    return word

    if len(word) <= 2:
        return word

    if word.endswith('a'):
        return word[:-1]

    if (
        word.endswith('u')
        and len(word) >= 4
    ):

        return word[:-1]

    return word