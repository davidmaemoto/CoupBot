from actions import *
import influenceUtils
import random
import json


class Agent:
    """
    An agent must define a getAction method, but may also define the
    following methods which will be called if they exist:

    def registerInitialState(self, state): # inspects the starting state
    """

    def __init__(self, index=0):
        self.index = index

    def getAction(self, state):
        """
        The Agent will receive a GameState (from either {pacman, capture, sonar}.py) and
        must return an action from Directions.{North, South, East, West, Stop}
        """
        NotImplementedError()

    def printAction(self, a, state):
        print("Agent %d decides to %s%s: %s" % (self.index, state.nextAction, \
                                     (' [--------BLUFF!!-------]' if str(a) in [str(act) for act in
                                                                                state.bluffActions(
                                                                                    self.index)] else ''), str(a)))

    def saveWeights(self, state, winner):
        pass


class TruthKeyboardAgent(Agent):

    def getAction(self, state):
        actions = state.legalActions(self.index)
        if len(actions) == 1:
            print
            "Agent %d takes %s: %s" % (self.index, state.nextAction, str(actions[0]))
            return actions[0]
        print
        '===========STATE BEGIN===========\n', state.detailedStr(), '\n===========STATE END============='
        while True:
            print('Please enter the number of action from the following list: ')
            for i, a in enumerate(actions):
                print('(%d): %s' % (i + 1, str(a)))
            try:
                action = int(input())
                if action <= len(actions):
                    self.printAction(actions[action - 1], state)
                    return actions[action - 1]
            except:
                print('Invalid number, try again...')


class KeyboardAgent(Agent):

    def getAction(self, state):
        legalActions = state.legalActions(self.index)
        bluffActions = state.bluffActions(self.index)
        if len(legalActions) == 1 and len(bluffActions) == 0:
            self.printAction(legalActions[0], state)
            return legalActions[0]
        print
        """
    ===========STATE BEGIN===========
    ???
    ===========STATE END============="""
        while True:
            print
            'Please enter the number of action from the following list: '
            for i, a in enumerate(legalActions + bluffActions):
                print
                '(%d): %s%s' % (i + 1, ('[Bluff] ' if i >= len(legalActions) else ''), str(a))
            try:
                action = int(input())
                if action <= len(legalActions):
                    output = legalActions[action - 1]
                    self.printAction(output, state)
                    return output
                elif action - len(legalActions) < len(bluffActions):
                    output = bluffActions[action - len(legalActions)]
                    self.printAction(output, state)
                    return output
            except:
                print
                'Invalid number, try again...'


class TruthAgent(Agent):

    def getAction(self, state):
        actions = state.legalActions(self.index)
        a = random.choice(actions)
        self.printAction(a, state)
        return a


class TruthAgentNoChallenge(Agent):

    def getAction(self, state):
        actions = state.legalActions(self.index)
        actions = [x for x in actions if not isinstance(x, Challenge)]
        a = random.choice(actions)
        self.printAction(a, state)
        return a


class BogoAgent(Agent):

    def getAction(self, state):
        actions = state.actions(self.index)
        a = random.choice(actions)
        self.printAction(a, state)
        return a


class BogoAgentNoChallenge(Agent):

    def getAction(self, state):
        actions = state.actions(self.index)
        actions = [x for x in actions if not isinstance(x, Challenge)]
        a = random.choice(actions)
        self.printAction(a, state)
        return a


class KillAgent(Agent):

    def findAction(self, actionList, query):
        for action in actionList:
            if action and action.type == query:
                return action
        return None

    def getAction(self, state):
        selfState = state.players[self.index]
        actionList = state.actions(self.index)
        random.shuffle(actionList)
        actionList = [x for x in actionList if x is None or x.type != 'challenge']
        a = self.findAction(actionList, 'block')
        if a:
            self.printAction(a, state)
            return a
        if random.random() > 0.5:
            a = self.findAction(actionList, 'assassinate')
            if a:
                self.printAction(a, state)
                return a
        else:
            a = self.findAction(actionList, 'coup')
            if a:
                print
                actionList
                self.printAction(a, state)
                return a
        a = self.findAction(actionList, 'tax')
        if a:
            self.printAction(a, state)
            return a
        a = random.choice(actionList)
        self.printAction(a, state)
        return a


class ExpectimaxAgent(Agent):

    def evaluationFunction(self, state):
        score = 0
        playerState = state.players[self.index]
        score += len(playerState.influences) * 100
        score += playerState.coins
        for i, p in enumerate(state.players):
            if i != self.index:
                score -= 10 * len(p.influences)
        score += sum([-100 if x == self.index else +10 for x in state.punishedPlayers])
        return score

    def getActions(self, player, s):
        return s.actions(player) if player != self.index else s.legalActions(player)

    def findProbability(self, state, successorState):
        requiredInfluences = state.requiredInfluencesForState(successorState)
        probability = 1
        for p in requiredInfluences:
            if p == self.index:
                influenceList, hasInfluence = requiredInfluences[p]
                hasAny = False
                selfInfluences = state.players[p].influences
                for influence in influenceList:
                    if influence in selfInfluences:
                        hasAny = True
                if hasInfluence:
                    probability = 1 if hasAny else 0
                else:
                    probability = 0 if hasAny else 1
        return probability

    def vopt(self, s, d):
        if s.isOver():
            return 10000, [None]
        if d == 0:
            return self.evaluationFunction(s), None
        possibleActions = []
        for player in s.playersInAction:
            for action in self.getActions(player, s):
                newStates = s.generateSuccessorStates(action, player)
                for successorState in newStates:
                    possibleActions.append((self.findProbability(s, successorState) * self.vopt(successorState, d - 1)[0],
                                            action))
        return max(possibleActions, key=lambda x: x[0])

    def getAction(self, state):
        # choose a random action 5% of the time.
        e = random.random()
        if e < 0.05:
            return random.choice(self.getActions(self.index, state))
        v, a = self.vopt(state.deepCopy(), 3)
        self.printAction(a, state)
        return a

class TDLearningAgent(ExpectimaxAgent):

    def __init__(self, index=0):
        ExpectimaxAgent.__init__(self, index)
        self.weights = {}  # read from FILE
        self.stepSize = .01
        self.discount = 1
        self.lastFeatureVector = {}
        self.lastV = 0
        inputFile = open('td-learning-data.dat', 'r')
        jsonWeights = inputFile.read()
        if len(jsonWeights) > 0:
            self.weights = json.loads(jsonWeights)
        inputFile.close()

    # extract features from state into key-value pairs
    def featureExtractor(self, state):
        o = {}
        o['playersRemaining'] = sum([1 for p in state.players if len(p.influences) > 0])
        o['selfCoins'] = state.players[self.index].coins
        o['selfInfluences'] = len(state.players[self.index].influences)
        o['selfPunished'] = sum([1 for p in state.punishedPlayers if p == self.index])
        o['opponentsPunished'] = sum([1 for p in state.punishedPlayers if p != self.index])
        o['selfBlocked'] = 1 if state.playerTurn == self.index and state.playerBlocked is not None else 0
        o['selfChallenged'] = 1 if (
                                           state.playerTurn == self.index and state.playerBlocked is None and state.playerChallenged is not None) \
                                   or (state.playerBlocked == self.index and state.playerChallenged is not None) else 0
        o['opponentBlocked'] = 1 if state.playerTurn != self.index and state.playerBlocked is not None else 0
        o['opponentChallenged'] = 1 if (
                                               state.playerTurn != self.index and state.playerBlocked is None and state.playerChallenged is not None) \
                                       or (state.playerBlocked != self.index and state.playerChallenged is not None) else 0
        for p in range(state.numPlayers):
            if p != self.index:
                o['opp%dCoins' % p] = state.players[p].coins
                o['opp%dInfluences' % p] = len(state.players[p].influences)
                o['opp%dPunished' % p] = sum([1 for player in state.punishedPlayers if player == p])
        for influence in util.influenceList:
            o['selfHasInfluence_%s' % influence] = 1 if influence in state.players[self.index].influences else 0
        return o

    def evaluationFunction(self, state):
        v = 0
        features = self.featureExtractor(state)
        for feature in self.weights:
            if feature not in features:
                continue
            v += self.weights[feature] * features[feature]
        return v

    def updateW(self, newState, reward):
        constant = self.stepSize * (self.lastV - (reward + (self.discount * self.evaluationFunction(newState))))
        for feature in self.lastFeatureVector:
            currentWeight = self.weights[feature] if feature in self.weights else 0
            self.weights[feature] = currentWeight + (constant * self.lastFeatureVector[feature])
            # self.weights[feature] = currentWeight - (constant * self.lastFeatureVector[feature])

    def getAction(self, state):
        if state.playerTurn == self.index and state.currentAction == None:
            self.updateW(state, 0)
            v, a = self.vopt(state.deepCopy(), 3)
            self.lastV = v
            self.lastFeatureVector = self.featureExtractor(state)
        else:
            v, a = self.vopt(state.deepCopy(), 3)
        self.printAction(a, state)
        return a

    def saveWeights(self, state, winner):
        reward = 100 if winner == self.index else -100
        self.updateW(state, reward)
        outputFile = open('td-learning-data.dat', 'w')
        historyFile = open('td-learning-data-history.txt', 'a')
        jsonWeights = json.dumps(self.weights)
        outputFile.write(jsonWeights)
        historyFile.write(jsonWeights + '\n')
        outputFile.close()
        historyFile.close()
        print
        self.weights