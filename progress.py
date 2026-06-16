"""Persistent player progress: the coin wallet and shop ownership.

This is separate from the per-run score/coins in Game. The wallet accumulates
coins collected across every play session and is what the Shop spends.
"""
import json
import os

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "progress.json")

# The very first character + its default skin are owned for free so the player
# always has something to play as.
DEFAULT_CHARACTER = "jin"
DEFAULT_SKIN = "classic"


def _default_progress():
    return {
        "wallet": 0,
        "owned_characters": [DEFAULT_CHARACTER],
        # Map of character id -> list of owned skin ids.
        "owned_skins": {DEFAULT_CHARACTER: [DEFAULT_SKIN]},
        "selected_character": DEFAULT_CHARACTER,
        "selected_skin": DEFAULT_SKIN,
    }


def load_progress():
    data = _default_progress()
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            saved = json.load(f)
        if isinstance(saved, dict):
            data["wallet"] = int(saved.get("wallet", 0))
            owned_chars = saved.get("owned_characters")
            if isinstance(owned_chars, list):
                data["owned_characters"] = list(dict.fromkeys(
                    [DEFAULT_CHARACTER] + [str(c) for c in owned_chars]))
            owned_skins = saved.get("owned_skins")
            if isinstance(owned_skins, dict):
                merged = data["owned_skins"]
                for cid, skins in owned_skins.items():
                    if isinstance(skins, list):
                        existing = set(merged.get(cid, []))
                        existing.update(str(s) for s in skins)
                        merged[cid] = list(existing)
                data["owned_skins"] = merged
            data["selected_character"] = str(
                saved.get("selected_character", DEFAULT_CHARACTER))
            data["selected_skin"] = str(saved.get("selected_skin", DEFAULT_SKIN))
    except Exception:
        pass
    return data


def save_progress(data):
    try:
        with open(_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass
