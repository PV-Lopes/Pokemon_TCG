const API_BASE = "http://localhost:5000"; // ajuste se necessário

// Carregar cartas
fetch(`${API_BASE}/cards`)
  .then(res => res.json())
  .then(cards => {
    const container = document.getElementById("cardList");
    cards.forEach(card => {
      const div = document.createElement("div");
      div.className = "card-item";
      div.innerHTML = `
        <img src="${card.image}" alt="${card.name}">
        <p>${card.name}</p>
        <small>HP: ${card.hp}</small>
      `;
      container.appendChild(div);
    });
  });

// Carregar jogadores
fetch(`${API_BASE}/players`)
  .then(res => res.json())
  .then(players => {
    const ul = document.getElementById("playerList");
    players.forEach(player => {
      const li = document.createElement("li");
      li.textContent = `${player.nickname} - Nível ${player.level} - 🏆 ${player.trophies}`;
      ul.appendChild(li);
    });
  });

// Carregar batalhas
fetch(`${API_BASE}/battles`)
  .then(res => res.json())
  .then(battles => {
    const ul = document.getElementById("battleList");
    battles.forEach(battle => {
      const li = document.createElement("li");
      li.textContent = `🆚 ${battle.player1} vs ${battle.player2} - 🏆 Vencedor: ${battle.winner}`;
      ul.appendChild(li);
    });
  });
