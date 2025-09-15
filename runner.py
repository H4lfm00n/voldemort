import os
import sys
import time
import random
from typing import Dict, Any

from loguru import logger

# Allow running as a script from this directory without package import
CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from question_generator import QuestionGenerator
from grammar import grammar_score
from guidelines import GuidelinesEvaluator
from security_wrapper import SecurityChecks
from rater import overall_rating

from src.config import Config  # relies on existing project config
import openai


def send_to_gpt(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
    messages = [{"role": "user", "content": prompt}]
    resp = client.chat.completions.create(model=model, messages=messages, max_tokens=700, temperature=0.7)
    return resp.choices[0].message.content


def run_loop(iterations: int = 10, delay_sec: tuple[int, int] = (2, 5), model: str = "gpt-3.5-turbo") -> None:
    generator = QuestionGenerator()
    guidelines_path = os.path.join(os.path.dirname(__file__), "guidelines.json")
    evaluator = GuidelinesEvaluator(guidelines_path)
    security = SecurityChecks()

    for i in range(iterations):
        prompt = generator.generate()
        logger.info(f"[#{i+1}] Prompt: {prompt}")
        try:
            reply = send_to_gpt(prompt, model=model)
        except Exception as e:
            logger.error(f"OpenAI error: {e}")
            continue

        sec = security.analyze(prompt, reply)
        guid = evaluator.evaluate(reply)
        gram = grammar_score(reply)

        # security_score in analyzer is a risk score [0,1], invert for contribution
        overall = overall_rating(sec.get("security_score", 0.0), gram, guid.get("guideline_score", 1.0))

        summary: Dict[str, Any] = {
            "prompt": prompt,
            "reply": reply,
            "security": sec,
            "guidelines": guid,
            "grammar_score": gram,
            "rating": overall,
        }

        logger.info({
            "rating_overall": round(overall["overall"], 3),
            "components": {k: round(v, 3) for k, v in overall["components"].items()},
            "security_flags": sec.get("flags", [])[:10],
            "guideline_violations": [v["rule_id"] for v in guid.get("violations", [])],
        })

        time.sleep(random.uniform(*delay_sec))


if __name__ == "__main__":
    run_loop()

