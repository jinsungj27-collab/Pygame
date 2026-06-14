import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")


def load_high_score():
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            return int(json.load(f).get("high", 0))
    except Exception:
        return 0


def save_high_score(value):
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump({"high": int(value)}, f)
    except Exception:
        pass
