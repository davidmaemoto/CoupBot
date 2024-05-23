import random

class CoupGame:
    def __init__(self):
        self.players = []
        self.game_state = {}
        self.deck = ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"] * 2
        self.current_turn_index = 0

    def start_game(self, players):
        self.players = players
        random.shuffle(self.deck)
        self.game_state = {player: {"coins": 2, "cards": [self.deck.pop(), self.deck.pop()]} for player in players}
        self.current_turn_index = 0

    def make_move(self, player, move):
        if move["action"] == "income":
            self.game_state[player]["coins"] += 1
        elif move["action"] == "coup":
            target = move["target"]
            self.game_state[player]["coins"] -= 7
            if target in self.game_state and self.game_state[target]["cards"]:
                self.game_state[target]["cards"].pop()
        self.current_turn_index = (self.current_turn_index + 1) % len(self.players)
        return {"status": "Move executed", "game_state": self.game_state}

    def get_status(self):
        return self.game_state

    def get_current_player(self):
        return self.players[self.current_turn_index]
