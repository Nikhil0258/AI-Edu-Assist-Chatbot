# assistant/filters.py
import re
from .Keywords import ENGINEERING_TERMS

def _compile_patterns(terms):
    """
    Compile case-insensitive regex patterns for each phrase.
    If a phrase starts/ends alphanumeric, wrap with word boundaries to avoid partial matches.
    Keeps special phrases like C/C++ or .NET matching properly.
    """
    patterns = []
    for t in terms:
        esc = re.escape(t)  # keeps C/C++, .net, etc. safe
        # If both ends are alphanumeric, use word boundaries to avoid partial hits.
        if t[0].isalnum() and t[-1].isalnum():
            pat = re.compile(rf"(?i)\b{esc}\b")
        else:
            pat = re.compile(rf"(?i){esc}")
        patterns.append(pat)
    return patterns

_PATTERNS = _compile_patterns(ENGINEERING_TERMS)

def contains_engineering_keywords(text: str) -> bool:
    if not text:
        return False
    s = " ".join(text.lower().split())
    return any(p.search(s) for p in _PATTERNS)
