# ==============================================================================
# STRATIC SOFT - INTELLIGENT ANSWER LENGTH ROUTER
# ==============================================================================

# यह router सवाल में मौजूद शब्दों की संख्या देखकर routing नहीं करता।
#
# इसका उद्देश्य यह अनुमान लगाना है कि सवाल का उचित उत्तर:
#   LOW    -> 1-50 words
#   MEDIUM -> 51-100 words
#   HARD   -> 101+ words
#
# फिर app.py उसी tier में dashboard से चुनी हुई API को इस्तेमाल करता है.
#
# IMPORTANT:
# app.py में कोई बदलाव जरूरी नहीं।
#
# LOW    -> product.low_provider
# MEDIUM -> product.medium_provider
# HARD   -> product.hard_provider

# ==============================================================================
import re
from typing import List, Dict


# ------------------------------------------------------------------------------
# ROUTING LIMITS
# ------------------------------------------------------------------------------

# Expected answer:
#
# 1 - 50 words    -> LOW
# 51 - 100 words  -> MEDIUM
# 101+ words      -> HARD

LOW_MAX_WORDS = 50
MEDIUM_MAX_WORDS = 100


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

def _detect_explicit_length(text: str):
    """
    User द्वारा मांगी गई explicit word/line length detect करता है.

    Examples:
        50 words
        100 words
        200 lines
        100 शब्द
        200 लाइन
    """

    patterns = [
        # English
        r"(?<!\d)(\d{1,6})\s*(?:\+|plus)?\s*words?\b",
        r"(?<!\d)(\d{1,6})\s*(?:\+|plus)?\s*lines?\b",

        # Hindi
        r"(?<!\d)(\d{1,6})\s*(?:\+|plus)?\s*शब्द",
        r"(?<!\d)(\d{1,6})\s*(?:\+|plus)?\s*लाइन",
        r"(?<!\d)(\d{1,6})\s*(?:\+|plus)?\s*लाइन्स",
        r"(?<!\d)(\d{1,6})\s*(?:\+|plus)?\s*लाइनों",
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

def _detect_range(text: str):
    """
    User द्वारा बताई गई approximate range detect करता है.

    Examples:
        50 se jyada 100 se kam
        50 से ज्यादा 100 से कम
        20 se kam
        100 se jyada
    """

    # ----------------------------------------------------------
    # Hindi / Hinglish:
    # "50 se jyada 100 se kam"
    # ----------------------------------------------------------

    match = re.search(
        r"(\d+)\s*(?:se|से)\s*(?:jyada|zyada|ज्यादा)\s*"
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
    तो उसी के आधार पर routing करता है.
    """

    detected_range = _detect_range(text)

    if detected_range is not None:

        lower, upper = detected_range

        # 101+ -> HARD
        if lower >= 101:
            return "hard"

        # 51+ -> MEDIUM
        if lower >= 51:
            return "medium"

        # maximum 50 -> LOW
        if upper is not None and upper <= 50:
            return "low"

        # Range 50 तक जा रही है
        if upper is not None and upper >= 50:
            return "medium"

    number = _detect_explicit_length(text)

    if number is None:
        return None

    # 101+
    if number >= 101:
        return "hard"

    # 51-100
    if number >= 51:
        return "medium"

    # 1-50
    return "low"


# ------------------------------------------------------------------------------
# HARD INTENT DETECTOR
# ------------------------------------------------------------------------------

HARD_INTENT_KEYWORDS = [

    # ------------------------------------------------------------------
    # English - very large / detailed requests
    # ------------------------------------------------------------------

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
    "long story",
    "detailed story",

    "in great detail",
    "very detailed",
    "extremely detailed",
    "deep explanation",
    "deep dive",
    "comprehensive explanation",

    "explain in detail",
    "explain everything",
    "everything about",
    "all details",
    "complete explanation",

    # ------------------------------------------------------------------
    # Hindi
    # ------------------------------------------------------------------

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
    "पूरी तरह समझाइए",
    "पूरा सिद्धांत",
    "पूरा विवरण",
    "पूरा इतिहास",

    "निबंध लिखो",
    "निबंध बताओ",
    "लंबी कहानी",
    "विस्तृत जानकारी",
    "विस्तारपूर्वक समझाओ",
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
    "summarize",

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

    "बताइए",
]


# ------------------------------------------------------------------------------
# CONCEPT / THEORY DETECTOR
# ------------------------------------------------------------------------------
#
# यह सबसे important हिस्सा है।
#
# छोटा question होने का मतलब यह नहीं कि answer छोटा होगा।
#
# Example:
#
# "Newton के गति के नियम बताओ"
#
# Question छोटा है लेकिन expected answer naturally कई paragraphs हो सकता है।
#
# इसलिए theory/concept topics को ज्यादा expected words दिए जाते हैं।
# ------------------------------------------------------------------------------

THEORY_KEYWORDS = [

    # Physics
    "newton",
    "न्यूटन",
    "गति के नियम",
    "गति का नियम",
    "laws of motion",
    "law of motion",

    "gravity",
    "गुरुत्वाकर्षण",
    "relativity",
    "सापेक्षता",
    "quantum",
    "क्वांटम",

    "thermodynamics",
    "ऊष्मागतिकी",

    "electromagnetism",
    "विद्युत चुंबकत्व",

    "photosynthesis",
    "प्रकाश संश्लेषण",

    "evolution",
    "विकासवाद",

    # Mathematics
    "theorem",
    "प्रमेय",
    "proof",
    "प्रमाण",
    "derivation",
    "व्युत्पत्ति",

    # Computer / AI concepts
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "ai",
    "neural network",
    "न्यूरल नेटवर्क",
    "algorithm",
    "एल्गोरिदम",

    # General theory
    "theory",
    "सिद्धांत",
    "concept",
    "अवधारणा",
    "principle",
    "सिद्धांत",
    "working principle",
    "कार्य सिद्धांत",
]


# ------------------------------------------------------------------------------
# MULTI-ITEM / LIST DETECTOR
# ------------------------------------------------------------------------------

MULTI_ITEM_KEYWORDS = [

    "all",
    "all the",
    "four",
    "five",
    "six",
    "multiple",
    "rules",
    "laws",
    "types",
    "steps",

    "सभी",
    "चारों",
    "पांचों",
    "छहों",
    "सारे",
    "सभी नियम",
    "नियम",
    "कानून",
    "प्रकार",
    "स्टेप",
    "चरण",
]


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
    ऐसे सवाल detect करता है जिनके लिए सामान्यतः explanation चाहिए।
    """

    return _contains_any(text, MEDIUM_INTENT_KEYWORDS)


# ------------------------------------------------------------------------------
# EXPECTED ANSWER LENGTH ESTIMATOR
# ------------------------------------------------------------------------------
#
# यह actual answer के words नहीं गिनता।
#
# API call से पहले question देखकर अनुमान लगाता है:
#
# LOW    -> expected 1-50 words
# MEDIUM -> expected 51-100 words
# HARD   -> expected 101+ words
#
# ------------------------------------------------------------------------------

def _estimate_expected_answer_words(text: str) -> int:
    """
    User के question के meaning/intent के आधार पर
    expected answer की approximate word length estimate करता है।
    """

    text = text.lower().strip()

    if not text:
        return 1

    # ----------------------------------------------------------
    # Explicit request सबसे ऊपर
    # ----------------------------------------------------------

    explicit_number = _detect_explicit_length(text)

    if explicit_number is not None:
        return explicit_number

    # ----------------------------------------------------------
    # Explicit range
    # ----------------------------------------------------------

    detected_range = _detect_range(text)

    if detected_range is not None:

        lower, upper = detected_range

        if upper is None:
            return max(lower, 101)

        return max(lower, upper)

    # ----------------------------------------------------------
    # बहुत detailed request
    # ----------------------------------------------------------

    if _detect_hard_intent(text):
        return 180

    # ----------------------------------------------------------
    # Theory / concept questions
    #
    # छोटे सवाल लेकिन naturally बड़ा answer
    # ----------------------------------------------------------

    if _contains_any(text, THEORY_KEYWORDS):

        # अगर multiple laws/rules/types हैं,
        # answer और बड़ा होने की संभावना है।
        if _contains_any(text, MULTI_ITEM_KEYWORDS):
            return 180

        # Theory/concept सामान्यतः 100+ हो सकता है।
        return 130

    # ----------------------------------------------------------
    # Multiple things पूछी गई हैं
    # ----------------------------------------------------------

    if _contains_any(text, MULTI_ITEM_KEYWORDS):

        return 110

    # ----------------------------------------------------------
    # Medium explanation
    # ----------------------------------------------------------

    if _detect_medium_intent(text):

        return 75

    # ----------------------------------------------------------
    # Coding request
    # ----------------------------------------------------------
    #
    # बिना explicit size के normal code request medium।
    #

    if _is_code_request(text):

        return 75

    # ----------------------------------------------------------
    # Very short conversational questions
    # ----------------------------------------------------------

    short_patterns = [
        "hello",
        "hi",
        "hey",
        "thanks",
        "thank you",
        "ok",
        "okay",
        "bye",

        "हेलो",
        "हाय",
        "धन्यवाद",
        "थैंक यू",
        "ओके",
        "बाय",
    ]

    if _contains_any(text, short_patterns):
        return 10

    # ----------------------------------------------------------
    # Simple factual question
    # ----------------------------------------------------------
    #
    # Default answer छोटा माना जाएगा।
    #

    return 35


# ------------------------------------------------------------------------------
# EXPECTED WORD COUNT -> TIER
# ------------------------------------------------------------------------------

def _tier_from_expected_words(expected_words: int) -> str:
    """
    Expected answer words को LOW/MEDIUM/HARD में बदलता है।

    1-50   -> LOW
    51-100 -> MEDIUM
    101+   -> HARD
    """

    try:
        expected_words = int(expected_words)
    except (TypeError, ValueError):
        expected_words = 35

    if expected_words <= 50:
        return "low"

    if expected_words <= 100:
        return "medium"

    return "hard"


# ------------------------------------------------------------------------------
# MAIN ROUTER
# ------------------------------------------------------------------------------

def estimate_response_complexity(messages: List[Dict]) -> str:
    """
    Intelligent Answer-Length Router.

    यह user के question की length नहीं देखता।

    पहले यह अनुमान लगाता है कि answer कितने words का
    हो सकता है।

    फिर:

        1-50    -> LOW
        51-100  -> MEDIUM
        101+    -> HARD

    Returns:
        "low"
        "medium"
        "hard"
    """

    # ----------------------------------------------------------
    # Get user question
    # ----------------------------------------------------------

    text = _get_last_message(messages)

    if not text:
        return "low"

    # ==========================================================
    # PRIORITY 1
    # ==========================================================
    # अगर user ने खुद output size बताई है,
    # तो वही सबसे accurate information है।
    #
    # Example:
    #
    # 20 words       -> LOW
    # 50 words       -> LOW
    # 51 words       -> MEDIUM
    # 100 words      -> MEDIUM
    # 101 words      -> HARD
    #
    # ==========================================================

    explicit_route = _route_from_explicit_length(text)

    if explicit_route is not None:
        return explicit_route

    # ==========================================================
    # PRIORITY 2
    # ==========================================================
    # अब question के expected answer को estimate करो।
    #
    # Actual API call से पहले।
    #
    # ==========================================================

    expected_words = _estimate_expected_answer_words(text)

    # ==========================================================
    # PRIORITY 3
    # ==========================================================
    # Expected words के आधार पर final tier।
    # ==========================================================

    return _tier_from_expected_words(expected_words)
