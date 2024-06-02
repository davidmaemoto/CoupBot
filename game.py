from gamestate import GameState

"""
Simple class to manage the control flow of the game.
"""
class Game:
    def __init__(self, agents=[]):
        self.gameOver = False
        state = GameState(len(agents))
        self.state = state
        self.agents = agents

    """
    Main control loop for game play.
    """
    def run(self):
        while not self.state.isOver():
            for player in self.state.playersInAction:
                action = self.agents[player].getAction(self.state)
                if action:
                    self.state = action.choose(self.state)
                    break
            self.state = self.state.continue_turn()

        for i in range(self.state.numPlayers):
            if len(self.state.players[i].influences) > 0:
                winner = i
                print("Game over! Player %d wins. Final state: \n" % i, self.state)

        # for weight-dependent agents, save the weights. For example, expectimax agents
        for agent in self.agents:
            agent.saveWeights(self.state, winner)

        return winner
