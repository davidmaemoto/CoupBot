from game import Game
from agents import *
import sys
import collections
import signal

"""
Helper functions taken from the PacMan HW to read command line 
arguments and help with timeouts.
"""


def signal_handler(signum, frame):
    raise Exception("Timed out!")


def default(str):
    return str + ' [Default: %default]'


""" 
Processes the command used to run Coup from the command line, 
the only option is the number of games to play.

TODO: Add more options to the command line, such as the number of
agents to play with, the agents to play with, etc.
"""


def readCommand(argv):
    from optparse import OptionParser
    usageStr = ""
    parser = OptionParser(usageStr)
    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    options, _ = parser.parse_args(argv)
    args = {}
    args['numGames'] = options.numGames
    return args


"""
Runs the matchups between the different agents for a set number of games.
"""


def runMatchups(numGames):
    signal.signal(signal.SIGALRM, signal_handler)
    algorithms = ['expectimax', 'random']
    algorithmsToAgents = {'qlearning': TDLearningAgent, 'expectimax': ExpectimaxAgent, 'random': BogoAgent}
    agents0, agents1, agents2 = {}, {}, {}
    for algorithm in algorithms:
        agents0[algorithm] = algorithmsToAgents[algorithm](0)
        agents1[algorithm] = algorithmsToAgents[algorithm](1)
        agents2[algorithm] = algorithmsToAgents[algorithm](2)
    for algorithm1 in algorithms:
        for algorithm2 in algorithms:
            for algorithm3 in algorithms:
                agents = [agents0[algorithm1], agents1[algorithm2], agents2[algorithm3]]
                for _ in range(5):
                    signal.alarm(10)
                    scores = open('scores/score-count-%s-%s-%s.txt' % (algorithm1, algorithm2, algorithm3), 'a')
                    runGames(numGames=numGames, agents=agents, scores=scores)
                    scores.close()


"""
Runs the games for a set number of games with a set of agents.
Prints out the winning bot for each game and the final scores.
"""


def runGames(numGames=100, agents=[], scores=None):
    wins = collections.Counter()
    for i in range(numGames):
        game = Game(agents)
        winner = game.run()
        wins[winner] += 1
        print('Winning Bot:', winner)
        if scores is not None:
            scores.write(str(winner) + '\n')
    print('Final scores:', wins)


if __name__ == '__main__':
    args = readCommand(sys.argv[1:])
    runMatchups(args['numGames'])
