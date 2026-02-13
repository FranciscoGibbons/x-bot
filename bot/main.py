import os
import sys

from bot.twitter_client import get_access_token, post_tweet, post_thread
from bot.tweet_selector import get_next_tweet, mark_as_posted


def main():
    client_id = os.environ.get("CLIENT_ID")
    client_secret = os.environ.get("CLIENT_SECRET")

    if not all([client_id, client_secret]):
        print("Error: faltan variables de entorno (CLIENT_ID, CLIENT_SECRET)", file=sys.stderr)
        sys.exit(1)

    access_token = get_access_token(client_id, client_secret)

    index, tweet = get_next_tweet()

    # Saltear hilos por ahora
    while tweet["type"] == "thread":
        print(f"Salteando hilo (indice {index})")
        mark_as_posted(index)
        index, tweet = get_next_tweet()

    content = tweet["content"]
    print(f"Tweet seleccionado (indice {index})")
    post_tweet(access_token, content)

    mark_as_posted(index)
    print("State actualizado correctamente.")


if __name__ == "__main__":
    main()
