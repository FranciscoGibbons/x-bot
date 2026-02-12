import json
import random
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
TWEETS_FILE = CONTENT_DIR / "tweets.json"
STATE_FILE = CONTENT_DIR / "state.json"


def load_tweets() -> list[dict]:
    with open(TWEETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {"posted": [], "order": []}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def get_next_tweet() -> tuple[int, dict]:
    """Selecciona el proximo tweet no publicado. Retorna (indice, tweet)."""
    tweets = load_tweets()
    state = load_state()
    total = len(tweets)

    # Si no hay orden o todos fueron publicados, resetear y re-barajar
    if not state["order"] or len(state["posted"]) >= total:
        state["order"] = list(range(total))
        random.shuffle(state["order"])
        state["posted"] = []
        save_state(state)

    # Buscar el proximo indice no publicado en el orden
    for idx in state["order"]:
        if idx not in state["posted"]:
            return idx, tweets[idx]

    # Fallback: no deberia llegar aca
    state["order"] = list(range(total))
    random.shuffle(state["order"])
    state["posted"] = []
    save_state(state)
    idx = state["order"][0]
    return idx, tweets[idx]


def mark_as_posted(index: int) -> None:
    """Marca un tweet como publicado en el state."""
    state = load_state()
    state["posted"].append(index)
    save_state(state)
