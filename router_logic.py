# ==============================================================================
# STRATIC SOFT - INTELLIGENT ANSWER LENGTH ROUTER
# ==============================================================================
# यह router सवाल में मौजूद शब्दों की संख्या देखकर routing नहीं करता।
#
# इसका उद्देश्य यह अनुमान लगाना है कि सवाल का उचित उत्तर:
#   LOW    -> छोटा
#   MEDIUM -> मध्यम
#   HARD   -> बड़ा / detailed
#
# फिर app.py उसी tier में dashboard से चुनी हुई API को इस्तेमाल करता है.
#
# IMPORTANT:
# अभी Production Key / Provider Mapping के लिए app.py में कोई बदलाव जरूरी नहीं।
# app.py पहले से:
#
# LOW    -> product.low_provider
# MEDIUM -> product.medium_provider
# HARD   -> product.hard_provider
#
# ==============================================================================

import re
from typing import List, Dict


# ------------------------------------------------------------------------------
# ROUTING LIMITS
# ------------------------------------------------------------------------------
#
# Expected answer:
#
# 0 - 49 words    -> LOW
# 50 - 99 words   -> MEDIUM
# 100+ words      -> HARD
#
# ये limits company dashboard में चुनी हुई API को decide करने के लिए हैं.
# ------------------------------------------------------------------------------

LOW_MAX_WORDS = 49
MEDIUM_MAX_WORDS = 99


# ------------------------------------------------------------------------------
# GET LAST USER MESSAGE
# ------------------------------------------------------------------------------

def _get_last_message(messages: List[Dict]) -> str:
    """
    Conversation की आखिरी message निकालता है।
    """

    if not messages:
        return ""

    last_message = messages[-1].get("content", "")

    if last_message is None:
        return ""

    return str(last_message).strip().lower()


# ------------------------------------------------------------------------------
# KEYWORD HELPER
# ------------------------------------------------------------------------------

def _contains_any(text: str, keywords: List[str]) -> bool:
    """
    Check करता है कि text में कोई keyword मौजूद है या नहीं।
    """

    return any(keyword in text for keyword in keywords)


# ------------------------------------------------------------------------------
# EXPLICIT OUTPUT LENGTH DETECTOR
# ------------------------------------------------------------------------------
#
# अगर user खुद बोलता है:
#
# "100 line ka code"
# "100 words mein explain karo"
# "50 lines ka program"
#
# तो यह explicit requirement है।
#
# इसे सबसे ज्यादा priority दी जाती है।
# ------------------------------------------------------------------------------

def _detect_explicit_length(text: str):
    """
    User द्वारा मांगी गई explicit word/line length detect करता है।

    Return:
        integer -> अगर explicit number मिला
        None    -> अगर नहीं मिला
    """

    patterns = [
        # English
        r"(?<!\d)(\d{1,5})\s*(?:\+|plus)?\s*words?\b",
        r"(?<!\d)(\d{1,5})\s*(?:\+|plus)?\s*lines?\b",

        # Hindi
        r"(?<!\d)(\d{1,5})\s*(?:\+|plus)?\s*शब्द",
        r"(?<!\d)(\d{1,5})\s*(?:\+|plus)?\s*लाइन",
        r"(?<!\d)(\d{1,5})\s*(?:\+|plus)?\s*लाइन्स",
        r"(?<!\d)(\d{1,5})\s*(?:\+|plus)?\s*लाइनों",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)

        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass

    return None


# ------------------------------------------------------------------------------
# EXPLICIT RANGE DETECTOR
# ------------------------------------------------------------------------------
#
# Example:
#
# "50 se jyada 100 se kam"
# "50 से ज्यादा 100 से कम"
#
# ऐसे cases में हम upper/lower range देखकर tier decide करते हैं।
# ------------------------------------------------------------------------------

def _detect_range(text: str):
    """
    User द्वारा बताई गई approximate range detect करता है।

    Examples:
        50 se jyada 100 se kam
        50 से ज्यादा 100 से कम
        20 se kam
        100 se jyada

    Return:
        tuple(lower, upper)
        या None
    """

    # ----------------------------------------------------------
    # Hindi / Hinglish:
    # "50 se jyada 100 se kam"
    # ----------------------------------------------------------

    match = re.search(
        r"(\d+)\s*(?:se|से)\s*(?:jyada|zyada|ज्यादा|ज्यादा)\s*"
        r"(\d+)\s*(?:se|से)\s*(?:kam|कम)",
        text,
        flags=re.IGNORECASE
    )

    if match:
        lower = int(match.group(1))
        upper = int(match.group(2))
        return lower, upper

    # ----------------------------------------------------------
    # "20 se kam"
    # ----------------------------------------------------------

    match = re.search(
        r"(\d+)\s*(?:se|से)\s*(?:kam|कम)",
        text,
        flags=re.IGNORECASE
    )

    if match:
        upper = int(match.group(1)) - 1
        return 0, max(0, upper)

    # ----------------------------------------------------------
    # "100 se jyada"
    # ----------------------------------------------------------

    match = re.search(
        r"(\d+)\s*(?:se|से)\s*(?:jyada|zyada|ज्यादा)",
        text,
        flags=re.IGNORECASE
    )

    if match:
        lower = int(match.group(1)) + 1
        return lower, None

    return None


# ------------------------------------------------------------------------------
# EXPLICIT LENGTH ROUTING
# ------------------------------------------------------------------------------

def _route_from_explicit_length(text: str):
    """
    अगर user ने answer की length खुद बताई है,
    तो उसी के आधार पर routing करता है।
    """

    # पहले range check करें
    detected_range = _detect_range(text)

    if detected_range is not None:

        lower, upper = detected_range

        # 100+ range -> HARD
        if lower >= 100:
            return "hard"

        # अगर range 50 से शुरू हो रही है
        if lower >= 50:
            return "medium"

        # अगर maximum 49 है
        if upper is not None and upper <= 49:
            return "low"

        # अगर range 50 तक जा रही है,
        # तो medium safer choice है।
        if upper is not None and upper >= 50:
            return "medium"

    # फिर direct number detect करें
    number = _detect_explicit_length(text)

    if number is None:
        return None

    # 100+
    if number >= 100:
        return "hard"

    # 50-99
    if number >= 50:
        return "medium"

    # 0-49
    return "low"


# ------------------------------------------------------------------------------
# HARD INTENT DETECTOR
# ------------------------------------------------------------------------------
#
# यहां हम यह नहीं कह रहे कि सवाल लंबा है।
#
# हम देख रहे हैं कि user ने ऐसा काम मांगा है जिसका normal answer
# naturally बड़ा / detailed होने की संभावना है।
# ------------------------------------------------------------------------------

HARD_INTENT_KEYWORDS = [

    # English
    "full project",
    "complete project",
    "entire project",
    "complete application",
    "full application",
    "complete system",
    "full system",

    "complete code",
    "full code",
    "entire code",

    "write an essay",
    "essay",
    "write a long story",
    "detailed story",

    "in great detail",
    "very detailed",
    "extremely detailed",
    "deep explanation",
    "deep dive",
    "comprehensive explanation",

    # Hindi
    "पूरा प्रोजेक्ट",
    "पूरी एप्लीकेशन",
    "पूरी एप्लिकेशन",
    "पूरा सिस्टम",
    "पूरा कोड",
    "पूरी कोडिंग",

    "विस्तार से",
    "बहुत विस्तार से",
    "पूरी जानकारी",
    "पूरी तरह समझाओ",
    "पूरा सिद्धांत",
    "पूरा विवरण",

    "निबंध लिखो",
    "लंबी कहानी",
]


# ------------------------------------------------------------------------------
# MEDIUM INTENT DETECTOR
# ------------------------------------------------------------------------------

MEDIUM_INTENT_KEYWORDS = [

    # English
    "explain",
    "explain this",
    "explain how",
    "how does",
    "how do",
    "how to",
    "step by step",

    "difference between",
    "difference",
    "compare",
    "comparison",

    "why",
    "reason",
    "reasons",

    "summary",
    "describe",
    "describe this",

    "example",
    "examples",

    # Hindi / Hinglish
    "समझाओ",
    "समझाइए",
    "कैसे काम करता",
    "कैसे काम करती",
    "कैसे करें",
    "कैसे करे",
    "स्टेप बाय स्टेप",
    "अंतर बताओ",
    "अंतर",
    "तुलना करो",
    "तुलना",
    "क्यों",
    "कारण बताओ",
    "उदाहरण",
    "उदाहरण सहित",
]


# ------------------------------------------------------------------------------
# HARD ROUTING
# ------------------------------------------------------------------------------

def _detect_hard_intent(text: str) -> bool:
    """
    ऐसे सवाल detect करता है जिनका expected answer सामान्यतः बड़ा होता है।
    """

    return _contains_any(text, HARD_INTENT_KEYWORDS)


# ------------------------------------------------------------------------------
# MEDIUM ROUTING
# ------------------------------------------------------------------------------

def _detect_medium_intent(text: str) -> bool:
    """
    ऐसे सवाल detect करता है जिनके लिए सामान्यतः थोड़ा explanation चाहिए।
    """

    return _contains_any(text, MEDIUM_INTENT_KEYWORDS)


# ------------------------------------------------------------------------------
# CODE REQUEST DETECTOR
# ------------------------------------------------------------------------------

def _is_code_request(text: str) -> bool:
    """
    Coding request detect करता है।
    """

    code_keywords = [
        "code",
        "coding",
        "program",
        "script",
        "python",
        "javascript",
        "html",
        "css",
        "flask",
        "fastapi",
        "api",
        "app",
        "application",

        "कोड",
        "कोडिंग",
        "प्रोग्राम",
        "स्क्रिप्ट",
        "एप",
        "ऐप",
    ]

    return _contains_any(text, code_keywords)


# ------------------------------------------------------------------------------
# MAIN ROUTER
# ------------------------------------------------------------------------------

def estimate_response_complexity(messages: List[Dict]) -> str:
    """
    Intelligent Answer-Length Router.

    IMPORTANT:
    यह function user के question की length नहीं देखता।

    यह अनुमान लगाता है कि user के सवाल का उचित answer
    कितना बड़ा होना चाहिए।

    Returns:
        "low"
        "medium"
        "hard"
    """

    # ----------------------------------------------------------
    # Empty conversation
    # ----------------------------------------------------------

    text = _get_last_message(messages)

    if not text:
        return "low"

    # ==========================================================
    # PRIORITY 1
    # ==========================================================
    # User ने अगर खुद output size बताई है,
    # तो वही सबसे ज्यादा important है।
    #
    # Example:
    # 20 line code       -> LOW
    # 50 words           -> MEDIUM
    # 100 line code      -> HARD
    # ==========================================================

    explicit_route = _route_from_explicit_length(text)

    if explicit_route is not None:
        return explicit_route

    # ==========================================================
    # PRIORITY 2
    # ==========================================================
    # बहुत बड़ा / detailed task
    # ==========================================================

    if _detect_hard_intent(text):
        return "hard"

    # ==========================================================
    # PRIORITY 3
    # ==========================================================
    # Medium explanation वाला task
    # ==========================================================

    if _detect_medium_intent(text):
        return "medium"

    # ==========================================================
    # PRIORITY 4
    # ==========================================================
    # Code request
    #
    # बिना requested size के code को सीधे HARD नहीं भेजेंगे।
    # सामान्य coding request को MEDIUM माना जाएगा।
    #
    # अगर user "full/complete/100 lines" बोलेगा,
    # ऊपर वाले rules उसे HARD कर देंगे।
    # ==========================================================

    if _is_code_request(text):
        return "medium"

    # ==========================================================
    # PRIORITY 5
    # ==========================================================
    # सामान्य short/factual question
    #
    # जैसे:
    # "hello"
    # "taj mahal kisne banaya"
    # "India ki capital kya hai"
    #
    # ऐसे simple questions को LOW भेजना economical है।
    # ==========================================================

    return "low"
