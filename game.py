from util import *
from gamestate import GameState


class Game:
    """
  The Game manages the control flow, soliciting actions from agents.
  """

    def __init__(self, agents=None):
        if agents is None:
            agents = []
        self.gameOver = False
        state = GameState(len(agents))
        self.state = state
        self.agents = agents

    def run(self):
        """
        Main control loop for game play.
        """
        print(self.state.detailedStr())
        while not self.state.isOver():
            for player in self.state.playersCanAct:
                action = self.agents[player].getAction(self.state)
                if action is not None:
                    self.state = action.choose(self.state)
                    break
            self.state = self.state.continueTurn()

        for i in range(self.state.numPlayers):
            if len(self.state.players[i].influences) > 0:
                winner = i
                break

        print("Game over! Player %d wins. Final state: \n" % winner, self.state)

        for agent in self.agents:
            agent.gameOver(self.state, winner)

        return winner
