from textblob import TextBlob


def grammar_score(text: str) -> float:
    """Return a grammar/fluency score in [0,1] based on polarity+subjectivity heuristics.
    TextBlob does not provide grammar errors directly; this is a lightweight proxy.
    """
    if not text:
        return 0.0
    blob = TextBlob(text)
    # Polarity in [-1,1], subjectivity in [0,1]. Use a simple transform.
    polarity = (blob.sentiment.polarity + 1) / 2
    subjectivity = 1 - abs(blob.sentiment.subjectivity - 0.5) * 2  # centered preference
    # Combine with weights favoring polarity smoothness
    score = 0.6 * polarity + 0.4 * subjectivity
    return max(0.0, min(1.0, score))


