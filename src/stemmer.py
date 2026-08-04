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

# ============================================================
# MAIN STEMMER
# ============================================================

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


# ============================================================
# STEMMER WITH TRACE
# ============================================================

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

    trace["final"] = final_word
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

    # Protect lexical words whose beginnings resemble full
    # subject/tense prefixes.
    if word.startswith(("itabir", "hudum")):
        return word

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

        # ku is stripped only before a vowel.
        r'^ku(?=[aeiou])',

        r'^lili',
        r'^(ina|ita|ili|ime|inge)',
        r'^(zina|zita|zili|zime|zinge)',
        r'^(yana|yata|yali|yame|yange)',

        # Short subject markers are removed only before a vowel.
        r'^(ni|tu|wa|mu)(?=[aeiou])',
    ]

    for pattern in patterns:
        word = safe_sub(pattern, '', word)

    return word


# ============================================================
# TENSE MARKERS
# ============================================================

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

    # These markers are stripped only before a vowel. This avoids
    # cutting lexical beginnings such as ja-, yo-, ye- and ka-
    # when they are followed by a consonant.
    word = safe_sub(r'^ja(?=[aeiou])', '', word)
    word = safe_sub(r'^yo(?=[aeiou])', '', word)
    word = safe_sub(r'^ye(?=[aeiou])', '', word)

    temp = re.sub(r'^cho(?=[aeiou])', '', word)
    if len(temp) >= 3:
        word = temp

    word = safe_sub(r'^vyo', '', word)
    word = safe_sub(r'^ka(?=[aeiou].{2,})', '', word)

    return word


# ============================================================
# OBJECT MARKERS
# ============================================================

def strip_object_markers(word):

    # In kiuka, ki belongs to the lexical form.
    if word.startswith("kiuka"):
        return word

    # Reflexive ji- before this consonant pattern is removed.
    if word.startswith("jikoko"):
        result = word[2:]

        if len(result) >= 3:
            return result

    # ji- is treated as a marker only before a vowel.
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


# ============================================================
# DERIVATIONAL SUFFIXES
# ============================================================

def strip_derivational_suffixes(word):

    # Narrow rules derived from repeated morphological patterns.
    if word.endswith(("hirika", "mirika")):
        result = word[:-2]
        if len(result) >= 3:
            return result

    if word.endswith("chilia"):
        result = word[:-4]
        if len(result) >= 3:
            return result

    if word.endswith(("nzia", "hia", "hamia", "gumia", "salia")):
        result = word[:-2]
        if len(result) >= 2:
            return result

    if word.endswith("agaza"):
        result = word[:-3]
        if len(result) >= 3:
            return result

    if word.endswith("nanisha"):
        result = word[:-4]
        if len(result) >= 3:
            return result

    if word.endswith("jibu"):
        result = word[:-1]
        if len(result) >= 3:
            return result

    if word.endswith("gizia"):
        result = re.sub(r"ngizia$", "ndikiz", word)
        if result != word:
            return result

    if word.endswith("nana"):
        result = word[:-3]
        if len(result) >= 2:
            return result


    # Passive form -uliwa
    if word.endswith("uliwa"):
        result = word[:-2]

        if len(result) >= 3:
            return result

    # Passive suffix -wa
    if (
        len(word) > 4
        and re.search(r"[^aeio]wa$", word)
    ):
        result = re.sub(r"wa$", "", word)

        if len(result) >= 3:
            return result

    # Root + mkia
    if word.endswith("mkia"):
        result = word[:-3]

        if len(result) >= 3:
            return result

    # Root + ulia
    if word.endswith("ulia"):
        result = word[:-3]

        if len(result) >= 3:
            return result

    # Root + ukiza
    if word.endswith("ukiza"):
        result = word[:-2]

        if len(result) >= 3:
            return result

    # Root + ofisha
    if word.endswith("ofisha"):
        result = word[:-4]

        if len(result) >= 3:
            return result

    # Root ending in vowel + isha
    if word.endswith("aisha"):
        result = word[:-3]

        if len(result) >= 3:
            return result

    # Reciprocal forms
    if word.endswith("jana"):
        result = word[:-3]

        if len(result) >= 2:
            return result

    if word.endswith("tana"):
        result = word[:-3]

        if len(result) >= 2:
            return result

    # Stative forms
    if word.endswith("fuka"):
        result = word[:-2]

        if len(result) >= 3:
            return result

    if word.endswith("aika"):
        result = word[:-2]

        if len(result) >= 3:
            return result

    # Reciprocal-applicative form -iana
    if word.endswith("iana"):
        result = word[:-4]

        if len(result) >= 3:
            return result

    # Narrow causative patterns
    if word.endswith("msha"):
        result = word[:-3]

        if len(result) >= 3:
            return result

    if word.endswith("vusha"):
        result = word[:-3]

        if len(result) >= 3:
            return result

    if word.endswith("mbeza"):
        result = word[:-3]

        if len(result) >= 3:
            return result

    # Applicative extension -ilia
    if (
        len(word) > 6
        and word.endswith("ilia")
    ):
        result = word[:-4]

        if len(result) >= 4:
            return result

    # Applicative ending -ia
    if word.endswith("ia"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    # Applicative ending -ea
    if word.endswith("ea"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    # Preserve -ik and remove final a only.
    if word.endswith("ika"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    # Preserve -ek and remove final a only.
    if word.endswith("eka"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    # Preserve -ish/-esh and remove final a only.
    if word.endswith(("isha", "esha")):
        result = word[:-1]

        if len(result) >= 3:
            return result

    # Preserve -an and remove final a only.
    if word.endswith("ana"):
        result = word[:-1]

        if len(result) >= 3:
            return result

    return word


# ============================================================
# FINAL VOWEL
# ============================================================

def strip_final_vowel(word):

    if len(word) <= 2:
        return word

    # Narrow final-vowel rules supported by recurring patterns.
    if word.endswith(("lisi", "kari", "riri", "nuku", "hui")):
        result = word[:-1]

        if len(result) >= 2:
            return result

    # Preserve other words ending with e, i, o or u.
    if word.endswith(("e", "i", "o", "u")):
        return word

    # Preserve lexical forms ending in -aana.
    if word.endswith("aana"):
        return word

    # Remove final a.
    if word.endswith("a"):
        result = word[:-1]

        if len(result) >= 2:
            return result

    return word

