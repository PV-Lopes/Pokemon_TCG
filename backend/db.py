# models.py
from pymongo import MongoClient
from datetime import datetime
import os

# Conectando ao MongoDB Atlas
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['pokemon_game']

# Coleções
players = db['players']
battles = db['battles']
cards = db['cards']

def add_card(card_data):
    if cards.find_one({"id": card_data["id"]}):
        return
    cards.insert_one(card_data)

def add_player(player_data):
    players.insert_one(player_data)

def add_battle(battle_data):
    battles.insert_one(battle_data)

