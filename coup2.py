from game2 import Game
from agents import *
import sys
import collections
import signal

def default(str):
  return str + ' [Default: %default]'

def readCommand( argv ):
  """
  Processes the command used to run pacman from the command line.
  """
  from optparse import OptionParser
  usageStr = ""
  parser = OptionParser(usageStr)

  parser.add_option('-n', '--numGames', dest='numGames', type='int',
                    help=default('the number of GAMES to play'), metavar='GAMES', default=1)

  options, otherjunk = parser.parse_args(argv)
  if len(otherjunk) != 0:
    raise Exception('Command line input not understood: ' + str(otherjunk))
  args = dict()
  args['numGames'] = options.numGames

  return args

def runAllMatchups():
  signal.signal(signal.SIGALRM, signal_handler)
  names = ['qlearning']
           # , 'modified', 'aggressive', 'expectimax', 'liar', 'oracle'
  agents0 = {'qlearning': TDLearningAgent(0)}
    #          'modified': LyingRandomAgentExcludeChallenge(0), \
    # 'aggressive': LyingKillAgent(0), 'expectimax': ExpectimaxAgent(0), \
    # 'liar': LyingExpectimaxAgent(0), 'oracle': OracleExpectimaxAgent(0)}
  agents1 =  {'random': TDLearningAgent(1)}
    # {'random': RandomAgent(1), 'modified': LyingRandomAgentExcludeChallenge(1), \
    # 'aggressive': LyingKillAgent(1), 'expectimax': ExpectimaxAgent(1), \
    # 'liar': LyingExpectimaxAgent(1), 'oracle': OracleExpectimaxAgent(1)}
  agents2 = {'random': TDLearningAgent(2)}
    # , 'modified': LyingRandomAgentExcludeChallenge(2), \
    #          'aggressive': LyingKillAgent(2), 'expectimax': ExpectimaxAgent(2), \
    #          'liar': LyingExpectimaxAgent(2), 'oracle': OracleExpectimaxAgent(2)}
  agents = [TDLearningAgent(0), TDLearningAgent(1), TDLearningAgent(2)]
  for _ in range(5):
    signal.alarm(10)
    scoreFile = open('score-count-qlearning-qlearning-qlearning.txt', 'a')
    runGames(agents=agents, scoreFile=scoreFile)
    scoreFile.close()



def runGames(numGames=380, agents=[], scoreFile = None):
  wins = collections.Counter()
  numGames = numGames
  for i in range(numGames):
    game = Game(agents)
    winner = game.run()
    wins[winner] += 1
    print ('winner is %r' % winner)
    if scoreFile is not None:
      scoreFile.write( str(winner))
      scoreFile.write('\n')
    print ('Current score:', wins)

def signal_handler(signum, frame):
  raise Exception("Timed out!")

if __name__ == '__main__':
  args = readCommand( sys.argv[1:] ) # Get game components based on input
  #runGames( **args )
  runAllMatchups()
