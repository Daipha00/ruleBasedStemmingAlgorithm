import re


DEBUG = False


def debug_print(stage, word):
    if DEBUG:
        print(f"  {stage:<30}: {word}")


def safe_sub(pattern, repl, word, min_len=3):
    new_word = re.sub(pattern, repl, word)
    return new_word if len(new_word) >= min_len else word


def _run_stemmer(word):
    if not isinstance(word, str) or not word.strip():
        return "", {}

    original = word.lower().split()[0]
    trace = {"original": original}

    if (
    original.endswith(("i", "o", "u"))
    and not original.endswith("mu")
    and strip_compound_prefixes(original) == original
    and strip_simple_prefixes(original) == original
):
        trace["non_bantu_word"] = original
        return original, trace

    word = original
    for stage, strip in (
        ("compound_prefixes", strip_compound_prefixes),
        ("simple_prefixes", strip_simple_prefixes),
        ("tense_markers", strip_tense_markers),
        ("object_markers", strip_object_markers),
        ("derivational_suffixes", strip_derivational_suffixes),
    ):
        if stage == "simple_prefixes":
         word = strip_simple_prefixes(word, allow_hu=(word == original))
        else:
         word = strip(word)
        trace[stage] = word

    before_suffix = trace["object_markers"]
    preserve_ending = (
        before_suffix.endswith("ia")
        and not before_suffix.endswith("ilia")
        and word.endswith("i")
    ) or (before_suffix.endswith("ea") and word.endswith("e"))

    if not preserve_ending:
        word = strip_final_vowel(word)

    trace["final_vowel"] = word
    result = original if len(word) < 2 else word
    trace["final_stem"] = result
    return result, trace


def stem(word):
    result, trace = _run_stemmer(word)
    if DEBUG and trace and "non_bantu_word" not in trace:
        for stage, value in trace.items():
            if stage != "final_stem":
                debug_print(stage.replace("_", " "), value)
    return result


def stem_with_trace(word):
    return _run_stemmer(word)[1]


def strip_compound_prefixes(word):
    patterns = [
        r"^(nisingali|usingali|asingali|tusingali|msingali|wasingali)",
        r"^(nisingeli|usingeli|asingeli|tusingeli|msingeli|wasingeli)",
        r"^(nisinge|usinge|asinge|tusinge|msinge|wasinge)",
        r"^(isingali|zisingali|yasingali)",
        r"^(isingeli|zisingeli|yasingeli)",
        r"^(isinge|zisinge|yasinge)",
        r"^(ningali|tungali|wangali|ungali|angali|mngali)",
        r"^(yangali|zingali|ingali)",
        r"^(ningeli|tungeli|wangeli|ungeli|angeli|mngeli)",
        r"^(yangeli|zingeli|ingeli)",
        r"^lililo",
        r"^liliyo",
        r"^liliye",
        r"^lilicho",
        r"^lilipo",
        r"^lilio",
        r"^zilizo",
        r"^ziliyo",
        r"^ziliye",
        r"^zilicho",
        r"^zilipo",
        r"^zilio",
        r"^ilicho",
        r"^(niliye|uliye|aliye|tuliye|mliye|waliye)",
        r"^(niliya|uliya|aliya|tuliya|mliya|waliya)",
        r"^(niliyo|uliyo|aliyo|tuliyo|mliyo|waliyo)",
        r"^(yaliyo|iliyo|kiliyo|liliyo)",
        r"^(yaliye|iliye|kiliye)",
        r"^(nilicho|ulicho|alicho|tulicho|mlicho|walicho|kilicho)",
        r"^(nilipo|ulipo|alipo|tulipo|mlipo|walipo)",
        r"^(yalipo|ilipo)",
        r"^(nilio|ulio|alio|tulio|mlio|walio)",
        r"^(yalio|ilio)",
        r"^(nijapo|ujapo|ajapo|tujapo|mjapo|wajapo)",
        r"^(nisipo|usipo|asipo|tusipo|msipo|wasipo)",
        r"^(ninaye|unaye|anaye|tunaye|mnaye|wanaye)",
        r"^(nitaye|utaye|ataye|tutaye|mtaye|wataye)",
        r"^(niki|uki|aki|tuki|mki|waki|ziki|yaki|iki)",
        r"^(ninge|unge|ange|tunge|mnge|wange)",
        r"^(kumu|kuwa|kum|kuw)",
    ]

    for pattern in patterns:
        word = safe_sub(pattern, "", word)

    return word


def strip_simple_prefixes(word , allow_hu=True):
    original_form = word
    patterns = [
        r"^(nina|nime|nita)",
        r"^(una|ume|uta)",
        r"^(ana|ame|ata)",
        r"^(tuna|tume|tuta)",
        r"^(mna|mme|mta)",
        r"^(wana|wame|wata)",
        r"^(nili|tuli|mli|wali)",
        r"^(uli|ali)",
        r"^hu",
        r"^ku(?=[aeiou])",
        r"^lili",
        r"^(ina|ita|ili|ime|inge)",
        r"^(zina|zita|zili|zime|zinge)",
        r"^(yana|yata|yali|yame|yange)",
        r"^(ni|tu|wa|mu)(?=[aeiou])",
    ]

    for pattern in patterns:
         if pattern == r"^hu" and (not allow_hu or word != original_form):
            continue

         word = safe_sub(pattern, "", word)

    return word

    


def strip_tense_markers(word):
    patterns = [
        r"^ngali",
        r"^ngeli",
        r"^nge",
        r"^li(?=[aeiou])",
        r"^na(?=.{3,})",
        r"^ta(?=[aeiou].{2,})",
        r"^ja(?=[aeiou])",
        r"^yo(?=[aeiou])",
        r"^ye(?=[aeiou])",
        r"^cho(?=[aeiou])",
        r"^vyo",
        r"^ka(?=[aeiou].{2,})",
    ]

    for pattern in patterns:
        word = safe_sub(pattern, "", word)

    return word


def strip_object_markers(word):
    word = safe_sub(r"^ji(?=[aeiou])", "", word)
    return safe_sub(r"^(mw|mu|ku|wa|ki|vi|zi|li|ya|pa|u)(?=[aeiou])", "", word)


def strip_derivational_suffixes(word):
    endings = ("ia", "ea", "ika", "eka", "isha", "esha", "ana")
    if len(word) >= 4 and word.endswith(endings):
        return word[:-1]

    return word


def strip_final_vowel(word):
    if len(word) <= 2 or word.endswith("aana"):
        return word
    
    if word.endswith(("mu")):
     return word[:-1]

    if word.endswith("a"):
        return word[:-1]

    return word
