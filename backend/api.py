from flask import Flask, jsonify, request
from db import cards as cards_col, players as players_col, battles as battles_col
from bson import json_util
from datetime import datetime


app = Flask(__name__)

# Função para serializar ObjectId e datetime
def serialize_cursor(cursor):
    return json_util.loads(json_util.dumps(cursor))

# Rota 1: Listar cartas
@app.route("/api/cartas")
def listar_cartas():
    cartas = list(cards_col.find({}, {"_id": 0}))
    return jsonify(cartas)

# Rota 2: Listar jogadores
@app.route("/api/jogadores")
def listar_jogadores():
    jogadores = list(players_col.find({}, {"_id": 0}))
    return jsonify(jogadores)

# Rota 3: Listar batalhas
@app.route("/api/batalhas")
def listar_batalhas():
    batalhas = list(battles_col.find())
    return jsonify(serialize_cursor(batalhas))

# Rota 4: Consultas personalizadas – Exemplo: vitórias por carta em intervalo
@app.route("/api/consultas/vitorias_por_carta")
def vitorias_por_carta():
    carta = request.args.get("carta")
    inicio = request.args.get("inicio")
    fim = request.args.get("fim")

    if not (carta and inicio and fim):
        return jsonify({"erro": "Parâmetros 'carta', 'inicio' e 'fim' são obrigatórios."}), 400

    try:
        inicio_dt = datetime.fromisoformat(inicio)
        fim_dt = datetime.fromisoformat(fim)
    except ValueError:
        return jsonify({"erro": "Formato de data inválido. Use AAAA-MM-DD."}), 400

    total = battles_col.count_documents({
        "timestamp": {"$gte": inicio_dt, "$lte": fim_dt},
        "$or": [
            {"deck1": carta, "winner": "$player1"},
            {"deck2": carta, "winner": "$player2"}
        ]
    })

    return jsonify({
        "carta": carta,
        "vitorias": total,
        "periodo": f"{inicio} até {fim}"
    })

# Página inicial
@app.route("/")
def home():
    return """
    <h1>API Pokémon Battle - Desafio do Mestre de Cartas</h1>
    <p>Use os endpoints para explorar as batalhas, jogadores e cartas.</p>
    <ul>
        <li><a href='/api/cartas'>/api/cartas</a></li>
        <li><a href='/api/jogadores'>/api/jogadores</a></li>
        <li><a href='/api/batalhas'>/api/batalhas</a></li>
        <li>/api/consultas/vitorias_por_carta?carta=NomeDaCarta&inicio=2024-01-01&fim=2024-12-31</li>
    </ul>
    """

if __name__ == "__main__":
    app.run(debug=True)
