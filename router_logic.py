import re
from typing import List, Dict

CACHE = {
    "hello": "Hello! How can I help you today?",
    "hi": "Hi there! How can I assist you?",
    "hey": "Hey! What can I do for you?",
    "thanks": "You're welcome! Happy to help.",
    "thank you": "You're welcome!",
    "bye": "Goodbye! Have a great day!",
    "goodbye": "Goodbye! Take care!",
    "good morning": "Good morning! How can I help you?",
    "good evening": "Good evening! How can I assist you?"
}

def normalize(text: str) -> str:
    return text.lower().strip()

def get_cached_response(text: str) -> str | None:
    text = normalize(text)
    for key, value in CACHE.items():
        if key == text or key in text:
            return value
    return None

def estimate_complexity(messages: List[Dict]) -> str:
    """
    cheap  → बहुत छोटा सवाल
    medium → सामान्य सवाल
    expensive → बड़ा/गहरा सवाल
    """
    if not messages:
        return "cheap"

    last_message = messages[-1].get("content", "")
    word_count = len(re.findall(r'\b\w+\b', last_message))

    if word_count <= 10:
        return "cheap"
    elif word_count <= 50:
        return "medium"
    else:
        return "expensive"