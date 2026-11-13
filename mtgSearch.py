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
    if request.status_code >= 400 and request.status_code <500:
        return "Client-side error"
    if request.status_code >= 500:
        return "Host-side error"
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
    print(f"Name: {card_json['name']}")
    card_color = card_json['color_identity']
    if not card_color:
        print("Colour identity: Colourless")
    else:
         print("Colour identity: " + ', '.join(card_color))
    pricelist = card_json['prices']
    print(f"Price non-foil: {pricelist['eur']}€")
    print(f"set and card number: {card_json['set']}, {card_json['collector_number']}")
    is_game_changer = card_json['game_changer']
    if is_game_changer:
        print("Game Changer: yes")
    else:
        print("Game Changer: No")
    

def _get_all_printings(card_name):
    _list = _get('/cards/search', q = {card_name}, unique='prints', order = 'released')



#def _get_mtg_sets(path, **params):
#TODO: When i want to create an option 
def _type_of_search(number):
    match number:
        case 1:
            #Generic search
            """generic card search"""
        case 2:
            """set search"""
        case 3:
            """"""



def main():

    print("""
███╗   ███╗████████╗ ██████╗
████╗ ████║╚══██╔══╝██╔════╝
██╔████╔██║   ██║   ██║  ███╗
██║╚██╔╝██║   ██║   ██║   ██║
██║ ╚═╝ ██║   ██║   ╚██████╔╝
╚═╝     ╚═╝   ╚═╝    ╚═════╝

    MAGIC THE GATHERING
    CARD DATABASE
        
    Powered by Scryfall API
       
""")
    print("""SELECT TYPE OF SEARCH
Generic card search = 1
Set search = 2
    """)

    while True:
        _input = input("Input search type (1 or 2): ").strip()
        if _input in ("1", "2"):
            break
        print("please enter 1 or 2")

if __name__ == "__main__":
    main()
