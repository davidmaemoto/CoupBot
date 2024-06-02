from game import Game
from agents import TDLearningAgent, ExpectimaxAgent, BogoAgent
import sys
import collections
import signal
from optparse import OptionParser


def signal_handler(signum, frame):
    raise Exception("Timed out!")


def default(option_desc: str) -> str:
    return f'{option_desc} [Default: %default]'


def readCommand(argv):
    """
    Processes the command used to run Coup from the command line.
    Currently supports the number of games to play.

    TODO: Add more options to the command line, such as the number of
    agents to play with, the agents to play with, etc.
    """
    usage_str = ""
    parser = OptionParser(usage_str)
    parser.add_option('-n', '--numGames', dest='numGames', type='int',
                      help=default('the number of GAMES to play'), metavar='GAMES', default=1)
    options, _ = parser.parse_args(argv)
    return {'numGames': options.numGames}


def runMatchups(numGames: int):
    """
    Runs the matchups between the different agents for a set number of games.
    """
    signal.signal(signal.SIGALRM, signal_handler)
    algorithms = ['expectimax', 'random']
    algorithms_to_agents = {
        'qlearning': TDLearningAgent,
        'expectimax': ExpectimaxAgent,
        'random': BogoAgent
    }
    agents_by_algorithm = {
        idx: {algo: algorithms_to_agents[algo](idx) for algo in algorithms}
        for idx in range(3)
    }

    for algorithm1 in algorithms:
        for algorithm2 in algorithms:
            for algorithm3 in algorithms:
                agents = [agents_by_algorithm[0][algorithm1],
                          agents_by_algorithm[1][algorithm2],
                          agents_by_algorithm[2][algorithm3]]
                signal.alarm(10)
                scores_file_path = f'scores/{algorithm1}-{algorithm2}-{algorithm3}.txt'
                with open(scores_file_path, 'a') as scores:
                    runGames(numGames=numGames, agents=agents, scores=scores)


def runGames(numGames: int = 100, agents: list = [], scores=None):
    """
    Runs the games for a set number of games with a set of agents.
    Prints out the winning bot for each game and the final scores.
    """
    wins = collections.Counter()
    for i in range(numGames):
        game = Game(agents)
        winner = game.run()
        wins[winner] += 1
        print('Winning Bot:', winner)
        if scores:
            scores.write(f'{winner}\n')
    print('Final scores:', wins)


if __name__ == '__main__':
    args = readCommand(sys.argv[1:])
    runMatchups(args['numGames'])
