"""
Este módulo puntúa la tonalidad del texto asociado a un IPO.
Se cuenta el número de palabras negativas menos positivas y se mapea a [0,1].
Un valor alto implica mayor riesgo percibido.
"""

import re
from typing import Dict, Optional

from ..entities import IpoInput

POSITIVE_WORDS = {
    "growth",
    "profit",
    "strong",
    "expansion",
    "opportunity",
    "increase",
    "robust",
    "competitive",
}
NEGATIVE_WORDS = {
    "decline",
    "loss",
    "weak",
    "risk",
    "competition",
    "decrease",
    "uncertain",
    "volatile",
}


def compute_textual_features(ipo: IpoInput, prospectus_text: Optional[str]) -> Dict[str, float]:
    if not prospectus_text:
        return {"f_text": 0.5}
    tokens = re.findall(r"\b\w+\b", prospectus_text.lower())
    if not tokens:
        return {"f_text": 0.5}
    pos_count = sum(1 for t in tokens if t in POSITIVE_WORDS)
    neg_count = sum(1 for t in tokens if t in NEGATIVE_WORDS)
    sentiment = (neg_count - pos_count) / float(len(tokens))
    f_text = 0.5 + sentiment
    f_text = max(0.0, min(1.0, f_text))
    return {"f_text": f_text}
