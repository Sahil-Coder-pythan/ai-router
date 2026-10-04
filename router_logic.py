import re
from typing import List, Dict

def estimate_response_complexity(messages: List[Dict]) -> str:
    """
    अनुमान लगाता है कि आने वाला उत्तर कितने शब्दों में होगा:
    - low: 20+ शब्द
    - medium: 50+ शब्द
    - hard: 100+ शब्द
    """
    if not messages:
        return "low"

    last_message = messages[-1].get("content", "").lower()
    word_count = len(re.findall(r'\b\w+\b', last_message))

    # कोड, निबंध या विस्तृत विवरण वाले शब्दों की पहचान
    hard_keywords = ["code", "script", "essay", "explain in detail", "write a story", "detailed", "विस्तार", "कोड"]
    medium_keywords = ["explain", "summary", "how to", "why", "difference", "समझाओ", "अंतर"]

    if any(k in last_message for k in hard_keywords) or word_count > 30:
        return "hard"
    elif any(k in last_message for k in medium_keywords) or word_count > 10:
        return "medium"
    else:
        return "low"
