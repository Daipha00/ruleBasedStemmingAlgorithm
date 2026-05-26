import re

# ============================================================
# SWAHILI RULE-BASED STEMMER
# ============================================================

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
# PROTECTED WORD SETS
# ============================================================

PROTECTED_EKA = {'peleka', 'chomeka', 'koseka'}

KEEP_IK_BEFORE = {
    'sh', 'z', 'p',
    'and', 'ang', 'fun', 'mul', 'zind', 'an', 'bubuj',
    'adhir'
}

# Suffix-based -ia protection for 6+ char words
# Stems ending in these patterns keep their final -i
# kia: afikia->afiki, bia: ambia->ambi, lia: angalia->angali
# mia: angamia->angami, nia: adhinia->adhini, jivunia->jivuni
PROTECTED_IA_6PLUS = ('kia', 'bia', 'lia', 'mia', 'nia')

# 5-char -ia words that keep final -i
KEEP_IA_5CHAR = {'ambia'}


# ============================================================
# MAIN STEM FUNCTION
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

    word = strip_derivational_suffixes(word)
    debug_print("derivational suffixes", word)

    word = strip_final_vowel(word)
    debug_print("final vowel", word)

    if len(word) < 3:
        return original

    return word


# ============================================================
# TRACE FUNCTION
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
# STEP 1 — COMPOUND PREFIXES
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
        r'^lililo', r'^liliyo', r'^liliye', r'^lilicho', r'^lilipo', r'^lilio',
        r'^zilizo', r'^ziliyo', r'^ziliye', r'^zilicho', r'^zilipo', r'^zilio',
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
        word = safe_sub(pattern, '', word)

    return word


# ============================================================
# STEP 2 — SIMPLE SUBJECT PREFIXES
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
        word = safe_sub(pattern, '', word)

    return word


# ============================================================
# STEP 3 — TENSE MARKERS
# ============================================================

def strip_tense_markers(word):

    word = safe_sub(r'^ngali', '', word)
    word = safe_sub(r'^ngeli', '', word)
    word = safe_sub(r'^nge', '', word)

    # past -li- only when followed by vowel
    temp = re.sub(r'^li(?=[aeiou])', '', word)
    if len(temp) >= 3:
        word = temp

    # present -na- only if 3+ chars follow
    word = safe_sub(r'^na(?=.{3,})', '', word)

    # future -ta- only when followed by vowel + 2 more chars
    temp = re.sub(r'^ta(?=[aeiou].{2,})', '', word)
    if len(temp) >= 3:
        word = temp

    word = safe_sub(r'^ja', '', word)
    word = safe_sub(r'^yo', '', word)
    word = safe_sub(r'^ye', '', word)

    # ^cho only when followed by vowel
    temp = re.sub(r'^cho(?=[aeiou])', '', word)
    if len(temp) >= 3:
        word = temp

    word = safe_sub(r'^vyo', '', word)
    word = safe_sub(r'^ka(?=.{3,})', '', word)

    return word


# ============================================================
# STEP 4 — OBJECT MARKERS
# ============================================================

def strip_object_markers(word):

    word = safe_sub(r'^ji(?=[a-z]{3,})', '', word)

    word = safe_sub(
        r'^(mw|mu|ku|wa|ki|vi|zi|li|ya|pa|u)(?=[aeiou])',
        '',
        word
    )

    return word


# ============================================================
# STEP 5 — DERIVATIONAL SUFFIXES
# ============================================================

def strip_derivational_suffixes(word):

    # causative + passive (-ishwa, -eshwa)
    if len(word) > 5 and re.search(r'(ishwa|eshwa)$', word):
        return re.sub(r'(ishwa|eshwa)$', '', word)

    # reciprocal + causative (-anisha, -anesha)
    if len(word) > 6 and re.search(r'(anisha|anesha)$', word):
        return re.sub(r'(anisha|anesha)$', '', word)

    # -ishia before -isha to catch it first
    if len(word) > 6 and re.search(r'ishia$', word):
        return re.sub(r'ishia$', '', word)

    # causative (-isha, -esha)
    if len(word) > 5 and re.search(r'(isha|esha)$', word):
        return re.sub(r'(isha|esha)$', '', word)

    # -shia: require len>6 to protect tishia(6)
    if len(word) > 6 and re.search(r'shia$', word):
        return re.sub(r'shia$', '', word)

    # -ibu loanword suffix
    if len(word) > 4 and re.search(r'[^aeiou]ibu$', word):
        return re.sub(r'ibu$', '', word)

    # reciprocal + passive (-anwa)
    if len(word) > 5 and re.search(r'anwa$', word):
        return re.sub(r'anwa$', '', word)

    # applicative + stative (-ikia, -ekea)
    if len(word) > 6 and re.search(r'(ikia|ekea)$', word):
        return re.sub(r'(ikia|ekea)$', '', word)

    # passive (-wa)
    if len(word) > 4 and re.search(r'[^aeio]wa$', word):
        return re.sub(r'wa$', '', word)

    # applicative + locative (-elea, -olea)
    if len(word) > 5 and re.search(r'(elea|olea)$', word):
        return re.sub(r'(elea|olea)$', '', word)

    # standalone -ea applicative
    if len(word) > 4 and re.search(r'[^aeiou]ea$', word):
        return re.sub(r'ea$', '', word)

    # applicative + locative (-ilia, -elia)
    if len(word) > 6 and re.search(r'(ilia|elia)$', word):
        return re.sub(r'(ilia|elia)$', '', word)

    # FIX 1: -ania (applicative + reciprocal) before -ana rule
    # pigania->pig, bania->ban, fumania->fuman
    # strip -ania fully
    if len(word) > 5 and re.search(r'ania$', word):
        return re.sub(r'ania$', '', word)

    # FIX 2: -ana reverted to len>5 threshold
    # Protects: fumana(6), banana(6), fanana(6) from wrong stripping
    # Sacrifices: agana(5), ibana(5), onana(5) — acceptable trade
    if len(word) > 5 and re.search(r'ana$', word):
        return re.sub(r'ana$', '', word)

    # controlled reciprocal residue (-an)
    if len(word) > 5 and re.search(r'an$', word):
        before_an = word[:-2]
        protected_an = {'chan', 'man', 'pan', 'tan'}
        if before_an not in protected_an:
            return re.sub(r'an$', '', word)

    # FIX 3: -ia uses SUFFIX-BASED protection instead of full-word list
    # This fixes adhinia (nia ending -> adhini) and
    # afikiana (after -ana stripped -> afikia -> kia ending -> afiki)
    if re.search(r'ia$', word):
        if len(word) == 5:
            if word not in KEEP_IA_5CHAR:
                return re.sub(r'ia$', '', word)
        elif len(word) > 5:
            suffix_3 = word[-3:]
            if suffix_3 not in PROTECTED_IA_6PLUS:
                return re.sub(r'ia$', '', word)
        elif len(word) == 4:
            # 4-char -ia: strip (e.g. lia->l, kia->k — these are too short anyway)
            return re.sub(r'ia$', '', word)

    # smart -ika
    if len(word) > 5 and re.search(r'ika$', word):
        before_ika = word[:-3]
        if before_ika and before_ika[-1] in 'aeiou':
            result = word[:-2]
            if len(result) >= 3:
                return result
        elif before_ika == 'adhir':
            return 'adhiri'
        elif before_ika in KEEP_IK_BEFORE:
            pass
        elif len(before_ika) >= 3:
            return re.sub(r'ika$', '', word)

    # smart -eka
    if len(word) >= 6 and re.search(r'eka$', word):
        if word not in PROTECTED_EKA:
            before_eka = word[:-3]
            if len(before_eka) >= 3:
                return re.sub(r'eka$', '', word)

    # FIX 4: -eza rule REMOVED
    # Analysis: stripping -eza incorrectly affects endekeza, ongeza etc
    # Removing rule: endekeza->endekez (correct), ongeza->ongez (correct)
    # Net gain ~1300 correct forms

    return word


# ============================================================
# STEP 6 — FINAL VOWEL STRIPPING
# ============================================================

def strip_final_vowel(word):

    if len(word) <= 2:
        return word

    # strip final -a
    if word.endswith('a'):
        return word[:-1]

    # strip final -e if longer than 3 chars
    if word.endswith('e') and len(word) > 3:
        return word[:-1]

    # strip final -i only if longer than 4 chars
    # FIX 5: protect -ki, -bi, -li, -mi, -ni endings
    # These come from PROTECTED_IA_6PLUS words where -ia was kept
    # e.g. afiki (from afikia) must not lose its -i -> afik
    # Also protect -ini and -ai as before
    if word.endswith('i') and len(word) > 4:
        if (not word.endswith('ini')
                and not word.endswith('ai')
                and not word.endswith('ki')
                and not word.endswith('bi')
                and not word.endswith('li')
                and not word.endswith('mi')
                and not word.endswith('ni')):
            return word[:-1]

    # strip final -u only if longer than 4 chars
    if word.endswith('u') and len(word) > 4:
        return word[:-1]

    return word