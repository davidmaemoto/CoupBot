let currentPlayerIndex = 0;
const players = ["Bot 1", "Bot 2", "Bot 3"];

function startGame() {
    fetch("/start", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ players })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("game-status").innerText = `Game started with players: ${data.players.join(", ")}`;
        updateGameState(data.game_state);
        currentPlayerIndex = 0;
        updateCurrentPlayer();
    });
}

function nextTurn() {
    fetch("/move", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ player: currentPlayer(), move: { action: "income" } })  // Example move
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("game-status").innerText = "Move executed for current player";
        updateGameState(data.result.game_state);
        currentPlayerIndex = (currentPlayerIndex + 1) % players.length;
        updateCurrentPlayer();
    });
}

function restart() {
    fetch("/restart", {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById("game-status").innerText = "Game restarted";
        updateGameState(data.game_state);
        currentPlayerIndex = 0;
        updateCurrentPlayer();
    });
}

function updateGameState(gameState) {
    updatePlayerState("Bot 1", gameState["Bot 1"], 1);
    updatePlayerState("Bot 2", gameState["Bot 2"], 2);
    updatePlayerState("Bot 3", gameState["Bot 3"], 3);
}

function updatePlayerState(playerName, playerState, playerIndex) {
    document.getElementById(`coins${playerIndex}`).innerText = playerState.coins;
    updateCardImage(`card${playerIndex}-1`, playerState.cards[0]);
    updateCardImage(`card${playerIndex}-2`, playerState.cards[1]);
}

function updateCardImage(cardId, cardType) {
    const cardElement = document.getElementById(cardId);
    cardElement.src = getStaticUrl(`images/${cardType.toLowerCase()}.png`);
    cardElement.alt = cardType;
}

function getStaticUrl(filePath) {
    return `/static/${filePath}`;
}

function currentPlayer() {
    return players[currentPlayerIndex];
}

function updateCurrentPlayer() {
    document.getElementById("game-status").innerText = `Current turn: ${currentPlayer()}`;
}
