from typing import Dict, Any
from loguru import logger

try:
    # Reuse existing analyzer
    from src.security_analyzer import SecurityAnalyzer  # type: ignore
except Exception as e:  # pragma: no cover
    logger.warning(f"Falling back: couldn't import SecurityAnalyzer: {e}")
    SecurityAnalyzer = None  # type: ignore


class SecurityChecks:
    def __init__(self):
        self.impl = SecurityAnalyzer() if SecurityAnalyzer else None

    def analyze(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        if self.impl:
            return self.impl.analyze_conversation(user_message, ai_response)
        # Minimal fallback if analyzer not available
        flags = []
        if any(k in user_message.lower() for k in ["ignore previous", "password", "token", "api key"]):
            flags.append("security_keyword_detected")
        return {"security_score": float(bool(flags)), "sentiment_score": 0.0, "flags": flags, "incidents": [], "metadata": {}}


