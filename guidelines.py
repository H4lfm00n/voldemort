import json
import re
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class RuleResult:
    rule_id: str
    matched: bool
    matches: List[str]


class GuidelinesEvaluator:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            cfg = json.load(f)
        self.name = cfg.get("name", "Guidelines")
        self.rules = cfg.get("rules", [])
        scoring = cfg.get("scoring", {})
        self.base = float(scoring.get("base", 1.0))
        self.violations_penalty = float(scoring.get("violations_penalty", 0.25))
        self.max_penalty = float(scoring.get("max_penalty", 1.0))

    def evaluate(self, text: str) -> Dict[str, Any]:
        violations: List[RuleResult] = []
        for rule in self.rules:
            rid = rule.get("id", "rule")
            pats = rule.get("pattern_any", [])
            matches: List[str] = []
            for pat in pats:
                if re.search(re.escape(pat), text, re.IGNORECASE):
                    matches.append(pat)
            if matches:
                violations.append(RuleResult(rid, True, matches))

        penalty = min(self.max_penalty, self.violations_penalty * len(violations))
        score = max(0.0, self.base - penalty)
        return {
            "guideline_score": score,
            "violations": [r.__dict__ for r in violations],
        }


