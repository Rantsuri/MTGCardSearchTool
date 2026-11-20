import argparse
import json
import re
import sqlite3
import sys
import os
import time
from collections import Counter
from pathlib import Path

_JSON_DIR = os.path.dirname(os.path.abspath(__file__))

import requests

BASE = 'https://api.scryfall.com'
HEADERS = {'User-Agent': 'PersonalMTGTool/0.1', 'Accept': 'application/json'}
DATA = Path.home() / '.mtgtool'
DECKS = DATA / 'decks'
DECKS.mkdir(parents=True, exist_ok=True)
CACHE_TTL = 24 * 3600

_last_request = 0.0
_sets_cache = None


def _get(path, **params):
    global _last_request
    wait = 0.1 - (time.time() -  _last_request)
    if wait > 0:
        time.sleep(wait)
    request = requests.get(BASE + path, params = params, headers = HEADERS, timeout = 15)
    _last_request = time.time()
    if request.status_code >= 400 and request.status_code <500:
        return None
    request.raise_for_status()
    return request.json()

def _get_json(path):
     with open(path, encoding="utf-8") as file:
        return json.load(file)

def _parse_json(card_json):
    colors = ', '.join(card_json.get('color_identity', [])) or 'Colourless'
    eur = card_json.get('prices', {}).get('eur')
    price = f"{eur}€" if eur else "N/A"
   
    print(card_json)
    return (
        f"Name: {card_json['name']}\n"
        f"Colour identity: {colors}\n"
        f"Price (non-foil): {price}\n"
        f"Set: {card_json['set'].upper()} #{card_json['collector_number']}\n"
        f"Game Changer: {'Yes' if card_json.get('game_changer') else 'No'}\n"
        f"Commander legal: {'Yes' if card_json.get('legalities', {}).get('commander') else 'No'}\n"
    )

def _get_card_image_uri(card_json):
    image_uri= card_json.get('image_uris', {}).get('normal')
    return image_uri

#def _is_double_faced() TODO

def _get_keywords():
    return _get_json(os.path.join(_JSON_DIR, "data", "keywords.json"))       



def _get_all_printings(card_name):
    _list = _get('/cards/search', q = {card_name}, unique='prints', order = 'released')

def _get_set_cards(set_obj):
    cards = []
    data = _get_url(set_obj['search_uri'])
    while data:
        cards.extend(data['data'])
        if not data.get('has_more'):
            break
        data = _get_url(data['next_page'])
    return cards

def _find_sets(query):
    global _sets_cache
    if _sets_cache is None:
        _sets_cache = _get('/sets')['data']
    q = query.strip().lower()
    exact = [s for s in _sets_cache if s['code'] == q or s['name'].lower() == q]
    if exact:
        return exact[:1]
    return [s for s in _sets_cache if q in s['name'].lower()]

def _request(url, **params):
    global _last_request
    wait = 0.1 - (time.time() - _last_request)
    if wait > 0:
        time.sleep(wait)
    response = requests.get(url, params=params, headers=HEADERS, timeout=15)
    _last_request = time.time()
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()

def _get_image_bytes(url):
    global _last_request
    wait = 0.1 - (time.time() - _last_request)
    if wait > 0:
        time.sleep(wait)
    response = requests.get(url, headers=HEADERS, timeout=15)
    _last_request = time.time()
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.content

def _get_url(url):
    return _request(url)


#def _get_mtg_sets(path, **params):
#TODO: When i want to create an option 
