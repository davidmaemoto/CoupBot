from actions import *
import influenceUtils
import random
import json
import collections

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
        print
        "Agent %d takes %s%s: %s" % (self.index, state.nextAction, \
                                     (' [--------BLUFF!!-------]' if str(a) in [str(act) for act in
                                                                                state.bluffActions(
                                                                                    self.index)] else ''), str(a))

    def gameOver(self, state, winner):
        pass

    
class MinimaxAgent(Agent):

    def getAction(self, state):
        actions = state.actions(self.index)
        for action in actions:
            if action and action.type == 'block':
                self.printAction(action, state)
                return action
        if random.random() > 0.35:
            for action in actions:
                if action and action.type =='assassinate':
                    self.printAction(action, state)
                    return action
        else:
            for action in actions:
                if action and action.type == 'coup' and state.players[self.index].coins >= 7:
                    self.printAction(action, state)
                    return action
        if random.random() > 0.35:
            a = random.choice(actions)
            self.printAction(a, state)
            return a
        actions = state.legalActions(self.index)
        a = random.choice(actions)
        self.printAction(a, state)
        return a
        

class BogoAgent(Agent):

    def getAction(self, state):
        actions = state.actions(self.index)
        a = random.choice(actions)
        self.printAction(a, state)
        return a

class ExpectimaxAgent(Agent):
    def __init__(self, index=0):
        Agent.__init__(self, index)

    def vopt(self, state, depth):
        if state.isOver():
            return state.getReward(self.index), None
        if depth == 0:
            return self.evaluationFunction(state), None
        if state.playerTurn == self.index:
            actions = state.legalActions(self.index)
            if len(actions) == 0:
                return self.evaluationFunction(state), None
            v = -float('inf')
            a = None
            for action in actions:
                v1, a1 = self.vopt(state, depth - 1)
                if v1 > v:
                    v = v1
                    a = action
            return v, a
        else:
            actions = state.actions(self.index)
            if len(actions) == 0:
                return self.evaluationFunction(state), None
            v = 0
            for action in actions:
                v1, a1 = self.vopt(state, depth - 1)
                v += v1
            return v / len(actions), None

    def evaluationFunction(self, state):
        score = 0
        playerState = state.players[self.index]
        score += (len(playerState.influences) * 100) + (playerState.coins * 10)
        return score

    def getAction(self, state):
        v, a = self.vopt(state, 2)
        self.printAction(a, state)
        return a

class QLearningAgent(ExpectimaxAgent):
    def __init__(self, index=0):
        ExpectimaxAgent.__init__(self, index)
        self.weights = collections.Counter()
        self.alpha = 0.1  # Adjusted learning rate
        self.discount = 0.9
        self.epsilon = 0.1  # Adjusted exploration rate
        self.lastState = None
        self.lastAction = None

    def getQValue(self, state, action):
        features = self.getFeatures(state, action)
        return sum(self.weights[feature] * value for feature, value in features.items())

    def getFeatures(self, state, action):
        features = collections.Counter()
        playerState = state.players[self.index]
        features['numInfluences'] = len(playerState.influences) if playerState.influences is not None else 0
        features['coins'] = playerState.coins if playerState.coins is not None else 0
        features['action'] = hash(action) if action is not None else 0
        # Additional features can be added here
        return features

    def update(self, state, action, nextState, reward):
        features = self.getFeatures(state, action)
        correction = reward + self.discount * self.getValue(nextState) - self.getQValue(state, action)
        for feature in features:
            self.weights[feature] += self.alpha * correction * features[feature]

    def getValue(self, state):
        actions = state.legalActions(self.index)
        if len(actions) == 0:
            return 0
        return max([self.getQValue(state, action) for action in actions])

    def getAction(self, state):
        actions = state.legalActions(self.index)
        if len(actions) == 0:
            return None
        if random.random() < self.epsilon:
            a = random.choice(actions)
        else:
            qValues = [self.getQValue(state, action) for action in actions]
            a = actions[qValues.index(max(qValues))]
        if self.lastState:
            reward = self.getReward(self.lastState, state)
            self.update(self.lastState, self.lastAction, state, reward)
        self.lastState = state
        self.lastAction = a
        return a

    def getReward(self, state, nextState):
        playerIndex = self.index
        current_player_state = state.players[playerIndex]
        next_player_state = nextState.players[playerIndex]
        reward = (next_player_state.coins - current_player_state.coins) * 10  # Reward for coins
        reward += (len(next_player_state.influences) - len(current_player_state.influences)) * 10  # Reward for remaining influences
        return reward

    def gameOver(self, state, winner):
        reward = self.getReward(self.lastState, state)
        self.update(self.lastState, self.lastAction, state, reward)