import argparse
import json
import re
import sqlite3
import sys
import time
from collections import Counter
from pathlib import Path

import requests

BASE = 'https://api.scryfall.com'
HEADERS = {'User-Agent': 'PersonalMTGTool/0.1', 'Accept': 'application/json'}
DATA = Path.home() / '.mtgtool'
DECKS = DATA / 'decks'
DECKS.mkdir(parents=True, exist_ok=True)
CACHE_TTL = 24 * 3600
_last_request = 0.0
def _get(path, **params):
    global _last_request
    wait = 0.1 - (time.time() -  _last_request)
    if wait > 0:
        time.sleep(wait)
    request = requests.get(BASE + path, params = params, headers = HEADERS, timeout = 15)
    _last_request = time.time()
    if request.status_code == 404:
        return None
    request.raise_for_status()
    return request.json()



def _prompt():
    cardName = input("Card to search: ")
    card = _get('/cards/named', fuzzy = cardName)
    if card is None:
        print("No card found.")
        return None
    return card

def _parse_json(card_json):
    print(card_json)

    for key in card_json:
        print(key)
    print(card_json['name'])
    card_color = card_json['color_identity']
    print(', '.join(card_color))

def main():
    card = _prompt()
    _parse_json(card)

if __name__ == "__main__":
    main()
