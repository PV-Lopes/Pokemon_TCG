# API Pokémon TCG – Importar cartas
import requests
import json
from db import cards_col

def fetch_pokemon_cards(limit=100):
    url = f"https://api.pokemontcg.io/v2/cards?pageSize={limit}"
    headers = {"X-Api-Key": "SUA_API_KEY"}
    response = requests.get(url, headers=headers)
    data = response.json()["data"]

    cards = []
    for card in data:
        if "name" in card and "images" in card:
            cards.append({
                "id": card["id"],
                "name": card["name"],
                "image": card["images"]["small"],
                "hp": int(card["hp"]) if card.get("hp", "").isdigit() else 50,
                "types": card.get("types", ["Normal"]),
                "attacks": [a["name"] for a in card.get("attacks", [])]
            })

    cards_col.insert_many(cards)
    with open("data/cards.json", "w") as f:
        json.dump(cards, f, indent=4)

fetch_pokemon_cards(100)

# Jogadores e Batalhas
import random
from db import players_col, battles_col, cards_col
from datetime import datetime, timedelta

def create_player(nickname):
    return {
        "nickname": nickname,
        "trophies": random.randint(100, 5000),
        "level": random.randint(1, 50),
        "play_time": random.randint(10, 10000)
    }

def simulate_battle():
    players = list(players_col.find())
    cards = list(cards_col.find())
    player1, player2 = random.sample(players, 2)

    deck1 = random.sample(cards, 8)
    deck2 = random.sample(cards, 8)

    winner = random.choice([player1, player2])
    loser = player1 if winner == player2 else player2

    battle = {
        "timestamp": datetime.now() - timedelta(days=random.randint(0, 30)),
        "player1": player1["nickname"],
        "player2": player2["nickname"],
        "deck1": [c["name"] for c in deck1],
        "deck2": [c["name"] for c in deck2],
        "trophies_p1": player1["trophies"],
        "trophies_p2": player2["trophies"],
        "winner": winner["nickname"],
        "loser": loser["nickname"],
        "duration": random.randint(60, 300),
        "towers_destroyed_winner": random.randint(0, 3),
        "towers_destroyed_loser": random.randint(0, 3)
    }
    battles_col.insert_one(battle)

# Popular o banco
players_col.delete_many({})
battles_col.delete_many({})

players = [create_player(f"Player{i}") for i in range(20)]
players_col.insert_many(players)

for _ in range(100):
    simulate_battle()
