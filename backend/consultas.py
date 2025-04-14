from db import battles
from datetime import datetime

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")

# Consulta 1 - Porcentagem de vitórias de uma carta entre duas datas
def win_loss_percentage(card_name, start, end):
    start_date, end_date = parse_date(start), parse_date(end)

    total = battles.count_documents({
        "timestamp": {"$gte": start_date, "$lte": end_date},
        "$or": [{"deck1": card_name}, {"deck2": card_name}]
    })

    wins = battles.count_documents({
        "timestamp": {"$gte": start_date, "$lte": end_date},
        "$or": [
            {"deck1": card_name, "winner": "$player1"},
            {"deck2": card_name, "winner": "$player2"}
        ]
    })

    return {"card": card_name, "total": total, "wins": wins, "losses": total - wins}


# Consulta 2 - Decks com maior porcentagem de vitórias
def decks_com_maior_porcentagem_vitorias(percentual, inicio, fim):
    inicio = parse_date(inicio)
    fim = parse_date(fim)
    pipeline = [
        {"$match": {"timestamp": {"$gte": inicio, "$lte": fim}}},
        {"$group": {
            "_id": {"deck": "$deck1"},
            "total": {"$sum": 1},
            "vitorias": {"$sum": {"$cond": [{"$eq": ["$winner", "$player1"]}, 1, 0]}}
        }},
        {"$project": {
            "deck": "$_id.deck",
            "porcentagem_vitorias": {
                "$cond": [{"$eq": ["$total", 0]}, 0, {"$multiply": [{"$divide": ["$vitorias", "$total"]}, 100]}]
            }
        }},
        {"$match": {"porcentagem_vitorias": {"$gte": percentual}}}
    ]
    return list(battles.aggregate(pipeline))


# Consulta 3 - Derrotas com determinado combo de cartas
def derrotas_por_combo(combo, inicio, fim):
    inicio = parse_date(inicio)
    fim = parse_date(fim)
    return battles.count_documents({
        "timestamp": {"$gte": inicio, "$lte": fim},
        "$or": [
            {"deck1": {"$all": combo}, "winner": "$player2"},
            {"deck2": {"$all": combo}, "winner": "$player1"}
        ]
    })


# Consulta 4 - Vitórias com desvantagem
def vitorias_com_desvantagem(carta, percentual):
    pipeline = [
        {"$match": {
            "timestamp": {"$gte": datetime(2024, 1, 1)},
            "duration": {"$lt": 120},
            "towers_destroyed_loser": {"$gte": 2},
            "$expr": {
                "$lt": [
                    {"$cond": [
                        {"$eq": ["$winner", "$player1"]},
                        "$trophies_p1", "$trophies_p2"
                    ]},
                    {"$multiply": [
                        {"$cond": [
                            {"$eq": ["$winner", "$player1"]},
                            "$trophies_p2", "$trophies_p1"
                        ]},
                        (1 - percentual / 100)
                    ]}
                ]
            },
            "$or": [
                {"deck1": carta},
                {"deck2": carta}
            ]
        }}
    ]
    return list(battles.aggregate(pipeline))


# Consulta 5 - Melhores combos (cartas mais vencedoras em decks)
def melhores_combos(tamanho, percentual, inicio, fim):
    inicio = parse_date(inicio)
    fim = parse_date(fim)
    pipeline = [
        {"$match": {
            "timestamp": {"$gte": inicio, "$lte": fim},
            "winner": {"$exists": True}
        }},
        {"$project": {
            "deck": "$deck1",
            "winner": "$winner",
            "player1": "$player1"
        }},
        {"$match": {"$expr": {"$eq": ["$winner", "$player1"]}}},
        {"$unwind": "$deck"},
        {"$group": {"_id": "$deck", "vitorias": {"$sum": 1}}},
        {"$match": {"vitorias": {"$gte": percentual}}},
        {"$limit": tamanho}
    ]
    return list(battles.aggregate(pipeline))
