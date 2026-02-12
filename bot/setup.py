"""
Script de setup OAuth 2.0 - Correr UNA sola vez.

1. Abre un link en el browser para autorizar la app
2. Vos pegas la URL de redireccion aca
3. Guarda los tokens en content/tokens.json
"""

import json
import os
import sys
import hashlib
import base64
import secrets
from urllib.parse import urlencode

import requests

TOKENS_FILE = os.path.join(os.path.dirname(__file__), "..", "content", "tokens.json")

SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]


def main():
    client_id = os.environ.get("CLIENT_ID") or input("Client ID: ").strip()
    client_secret = os.environ.get("CLIENT_SECRET") or input("Client Secret: ").strip()

    if not client_id or not client_secret:
        print("Error: necesitas CLIENT_ID y CLIENT_SECRET", file=sys.stderr)
        sys.exit(1)

    # PKCE: generar code_verifier y code_challenge
    code_verifier = secrets.token_urlsafe(64)[:128]
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()

    state = secrets.token_urlsafe(32)

    # La redirect URI tiene que coincidir con la configurada en el developer portal
    redirect_uri = "https://example.com/callback"

    auth_url = "https://x.com/i/oauth2/authorize?" + urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": " ".join(SCOPES),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    })

    print("\n1. Abri este link en tu browser:\n")
    print(auth_url)
    print("\n2. Autorizá la app. Te va a redirigir a una URL que empieza con https://example.com/callback?...")
    print("3. Copiá TODA esa URL y pegala aca:\n")

    callback_url = input("URL de callback: ").strip()

    # Extraer el code de la URL
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)

    if "code" not in params:
        print("Error: no se encontro el 'code' en la URL. Intentá de nuevo.", file=sys.stderr)
        sys.exit(1)

    code = params["code"][0]

    # Intercambiar code por tokens
    response = requests.post(
        "https://api.x.com/2/oauth2/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "code_verifier": code_verifier,
        },
        auth=(client_id, client_secret),
    )

    if response.status_code != 200:
        print(f"Error obteniendo tokens: {response.status_code} {response.text}", file=sys.stderr)
        sys.exit(1)

    data = response.json()
    tokens = {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
    }

    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)

    print(f"\nTokens guardados en content/tokens.json")
    print("El bot ya puede publicar. El refresh token se renueva automaticamente en cada run.")


if __name__ == "__main__":
    main()
