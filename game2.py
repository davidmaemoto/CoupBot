from util import *
from gamestate import GameState

"""
TODO:

Make sure optimal choices are actually being made
Use A/B pruning?
Make states hashable so we can store hashes of traversed states and remember vopt for them
implement revealed influences and use them to our advantage
python profiler to speed up algorithm
do we reveal unintended information to AI agent by limiting playersCanAct?`
"""


class Game:
  """
  The Game manages the control flow, soliciting actions from agents.
  """

  def __init__(self, agents = []):
    self.gameOver = False
    state = GameState()
    state.initialize(len(agents))
    self.state = state
    self.agents = agents

  def run( self ):
    """
    Main control loop for game play.
    """
    numAgents = len( self.agents )
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
        winningPlayer = i
        break

    print("Game over! Player %d wins. Final state: \n" % winningPlayer, self.state)

    for agent in self.agents:
      agent.gameOver(self.state, winningPlayer)

    return winningPlayer








