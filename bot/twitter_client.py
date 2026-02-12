import json
import sys
from pathlib import Path

import requests

TOKENS_FILE = Path(__file__).resolve().parent.parent / "content" / "tokens.json"
API_BASE = "https://api.x.com/2"


def load_tokens() -> dict:
    if not TOKENS_FILE.exists():
        print("Error: no se encontro content/tokens.json. Corré primero: python -m bot.setup", file=sys.stderr)
        sys.exit(1)
    with open(TOKENS_FILE, "r") as f:
        return json.load(f)


def save_tokens(tokens: dict) -> None:
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    """Renueva el access token usando el refresh token."""
    response = requests.post(
        f"{API_BASE}/oauth2/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
        },
        auth=(client_id, client_secret),
    )

    if response.status_code != 200:
        print(f"Error renovando token: {response.status_code} {response.text}", file=sys.stderr)
        sys.exit(1)

    data = response.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data.get("refresh_token", refresh_token),
    }


def get_access_token(client_id: str, client_secret: str) -> str:
    """Renueva y retorna el access token."""
    tokens = load_tokens()
    new_tokens = refresh_access_token(client_id, client_secret, tokens["refresh_token"])
    save_tokens(new_tokens)
    print("Token renovado correctamente.")
    return new_tokens["access_token"]


def _post(access_token: str, endpoint: str, payload: dict) -> dict:
    """POST a la API de X con OAuth 2.0 user token."""
    response = requests.post(
        f"{API_BASE}{endpoint}",
        json=payload,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    if response.status_code not in (200, 201):
        print(f"Error API ({response.status_code}): {response.text}", file=sys.stderr)
        sys.exit(1)

    return response.json()


def post_tweet(access_token: str, text: str) -> str:
    """Publica un tweet individual. Retorna el tweet ID."""
    data = _post(access_token, "/tweets", {"text": text})
    tweet_id = data["data"]["id"]
    print(f"Tweet publicado (ID: {tweet_id}): {text[:50]}...")
    return tweet_id


def post_thread(access_token: str, tweets: list[str]) -> list[str]:
    """Publica un hilo de tweets. Retorna lista de tweet IDs."""
    ids = []
    reply_to = None
    for i, text in enumerate(tweets):
        payload = {"text": text}
        if reply_to:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to}

        data = _post(access_token, "/tweets", payload)
        tweet_id = data["data"]["id"]
        ids.append(tweet_id)
        reply_to = tweet_id
        print(f"Hilo [{i + 1}/{len(tweets)}] publicado (ID: {tweet_id}): {text[:50]}...")
    return ids
