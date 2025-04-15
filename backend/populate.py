import requests
import json
import random
import os
from db import cards_col, players_col, battles_col
from datetime import datetime, timedelta

# Função para importar as cartas do Pokémon TCG
def fetch_pokemon_cards(limit=100):
    url = f"https://api.pokemontcg.io/v2/cards?pageSize={limit}"
    headers = {"X-Api-Key": "8734afc6-4841-4328-9a87-3cc1cb2969f9"}  # 👈 Coloque sua API Key aqui
    response = requests.get(url, headers=headers)
    data = response.json()["data"]

    cards = []
    for card in data:
        if "name" in card and "images" in card:
            card_data = {
                "id": card["id"],
                "name": card["name"],
                "image": card["images"]["small"],
                "hp": int(card["hp"]) if card.get("hp", "").isdigit() else 50,
                "types": card.get("types", ["Normal"]),
                "attacks": [a["name"] for a in card.get("attacks", [])]
            }
            cards.append(card_data)

    if not cards:
        print("Nenhuma carta válida encontrada!")
        return

    cards_col.delete_many({})  # Limpa as cartas antigas
    cards_col.insert_many(cards)

    # Remove ObjectId antes de salvar no arquivo
    for card in cards:
        card.pop("_id", None)

    with open("data/cards.json", "w") as f:
        json.dump(cards, f, indent=4)

# Função para criar um jogador com dados aleatórios
def create_player(nickname):
    return {
        "nickname": nickname,
        "trophies": random.randint(100, 5000),
        "level": random.randint(1, 50),
        "play_time": random.randint(10, 10000)
    }

# Função para simular uma batalha
def simulate_battle():
    players = list(players_col.find())
    cards = list(cards_col.find({"name": {"$exists": True}}))
    
    if len(players) < 2 or len(cards) < 16:
        print("Erro: Não há jogadores ou cartas suficientes para simular a batalha.")
        return

    player1, player2 = random.sample(players, 2)
    deck1 = random.sample(cards, 8)
    deck2 = random.sample(cards, 8)

    winner = random.choice([player1, player2])
    loser = player1 if winner == player2 else player2

    battle = {
        "timestamp": datetime.now() - timedelta(days=random.randint(0, 30)),
        "player1": player1["nickname"],
        "player2": player2["nickname"],
        "deck1": [c.get("name", "Unknown") for c in deck1],
        "deck2": [c.get("name", "Unknown") for c in deck2],
        "trophies_p1": player1["trophies"],
        "trophies_p2": player2["trophies"],
        "winner": winner["nickname"],
        "loser": loser["nickname"],
        "duration": random.randint(60, 300),
        "towers_destroyed_winner": random.randint(0, 3),
        "towers_destroyed_loser": random.randint(0, 3)
    }

    battles_col.insert_one(battle)

# Função para popular o banco de dados com jogadores e batalhas
def populate_database():
    players_col.delete_many({})
    battles_col.delete_many({})

    players = [create_player(f"Player{i}") for i in range(20)]
    players_col.insert_many(players)

    for _ in range(100):
        simulate_battle()

# Criação da pasta de dados
os.makedirs("data", exist_ok=True)

# Caminho para o arquivo cards.json
cards_json_path = "data/cards.json"

# Carrega ou importa as cartas
if not os.path.exists(cards_json_path):
    fetch_pokemon_cards(100)

# Popula jogadores e batalhas
populate_database()