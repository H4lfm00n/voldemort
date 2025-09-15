from typing import Dict


def overall_rating(security_score: float, grammar_score: float, guideline_score: float) -> Dict[str, float]:
    """Combine component scores into overall rating.
    Weights: security 0.5, guidelines 0.3, grammar 0.2. All inputs in [0,1].
    """
    security_w = 0.5
    guideline_w = 0.3
    grammar_w = 0.2
    overall = (
        security_w * (1 - min(max(security_score, 0.0), 1.0))  # lower security score => safer => higher contribution
        + guideline_w * min(max(guideline_score, 0.0), 1.0)
        + grammar_w * min(max(grammar_score, 0.0), 1.0)
    )
    return {
        "overall": overall,
        "components": {
            "security": 1 - min(max(security_score, 0.0), 1.0),
            "guidelines": min(max(guideline_score, 0.0), 1.0),
            "grammar": min(max(grammar_score, 0.0), 1.0),
        },
    }


