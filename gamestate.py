import collections
import random
from actions import *
import util
import copy


class GameState:

    def __init__(self, numPlayers=3):
        """
        Generates a new state by copying information from its predecessor.
        """
        if numPlayers > 10:
            raise ValueError('Cannot have more than 10 players')
        self.players = []
        self.numPlayers = numPlayers
        self.playerTurn = random.randint(0, self.numPlayers - 1)
        self.lastAction = None
        self.playerExchange = None
        self.playerChallenge = None
        self.playerBlock = None
        self.playerTarget = None
        self.punishedPlayers = []
        self.deck = ['ambassador', 'assassin', 'captain', 'contessa', 'duke'] * (3 if self.numPlayers >= 6 else 2)
        random.shuffle(self.deck)
        for i in range(numPlayers):
            s = PlayerState(i, [self.deck.pop(), self.deck.pop()])
            self.players.append(s)
        self.inactiveInfluences = collections.Counter()
        self.nextAction = 'action'
        self.challengeSuccess = None
        self.blockPhaseOccurred = False
        self.actionStack = []
        self.playersCanAct = [self.playerTurn]

    def __str__(self):
        return """
      Players: %r
      Player Turn: %r
      Current Action: %r
      Next Action Type: %r
      Player Block: %r
      Player Challenge: %r
      Challenge Success: %r
      Player Target: %r
      Player Exchange: %r
      Punished Players: %r
      Deck: %r
      Discarded Influences: %r
    """ % ([str(player) for player in self.players], self.playerTurn, self.lastAction,
           self.nextAction, self.playerBlock, self.playerChallenge, self.challengeSuccess, self.playerTarget,
           self.playerExchange, self.punishedPlayers, self.deck, self.inactiveInfluences)

    def detailedStr(self):
        out = str(self)
        out += """
      Block Phase Occurred: %r
      Players: 
      """ % (self.blockPhaseOccurred)
        for p in self.players:
            out += '\n\t%s\n\t\tInactive Influences: %s\n\t\tRevealed Influences: %s\n\t\tPossible Influences: %s' % (
                p, p.inactiveInfluences, p.revealedInfluences, p.possibleInfluences)
        out += '\n\tAction Stack:'
        for a in self.actionStack:
            out += '\n\t\t%s' % a
        out += '\n\tPlayers that can act: %r' % self.playersCanAct
        out += '\n\tPossible actions for each player:'
        for p in range(len(self.players)):
            astring = ''
            for a in self.actions(p):
                astring += '\n\t\t\t%s' % a
            out += '\n\t\t%d: %s' % (p, astring)
        return out

    def _getActionLegalActions(self, playerIndex, playerState):
        if self.playerTurn != playerIndex:
            return ['income']

        otherPlayers = [x.playerIndex for x in self.players if len(x.influences) > 0 and x.playerIndex != playerIndex]
        result = ['income', 'foreign aid']

        if playerState.coins >= 10:
            return util.ActionGenerator(['coup'], playerIndex=playerIndex, otherPlayers=otherPlayers)
        if playerState.coins >= 7:
            result.append('coup')

        for influence in playerState.influences:
            if influence in util.influenceToAction:
                if influence != 'assassin' or playerState.coins >= 3:
                    result.append(util.influenceToAction[influence])

        return util.ActionGenerator(result, playerIndex=playerIndex, otherPlayers=otherPlayers)

    def _getBlockLegalActions(self, playerIndex, playerState):
        if self.playerTurn == playerIndex:
            return [None]
        if self.lastAction == 'foreign aid' or (
                self.lastAction in ['steal', 'assassinate'] and playerIndex == self.playerTarget):
            for influence in playerState.influences:
                if (self.lastAction in util.blockToInfluence and
                        influence in util.blockToInfluence[self.lastAction]):
                    return util.ActionGenerator(['block'], playerIndex=playerIndex) + [None]
        return [None]

    def _getChallengeLegalActions(self, playerIndex):
        if self.lastAction not in util.basicActions and (
                (self.playerBlock is not None and playerIndex != self.playerBlock) or
                (self.playerBlock is None and playerIndex != self.playerTurn)):
            return util.ActionGenerator(['challenge'], playerIndex=playerIndex) + [None]

        return [None]


    def legalActions(self, playerIndex=0):
        playerState = self.players[playerIndex]
        if len(playerState.influences) == 0:
            return [None]
        if self.nextAction == 'action':
            return self._getActionLegalActions(playerIndex, playerState)
        elif self.nextAction == 'block':
            return self._getBlockLegalActions(playerIndex, playerState)
        elif self.nextAction == 'challenge':
            return self._getChallengeLegalActions(playerIndex)
        elif self.nextAction == 'discard':
            return util.ActionGenerator(['discard'], playerIndex=playerIndex,
                                        numInfluences=len(self.players[playerIndex].influences))

    def bluffActions(self, playerIndex=0):
        playerState = self.players[playerIndex]
        if len(playerState.influences) == 0:
            return []
        if self.nextAction == 'action':
            indexList = [x.playerIndex for x in self.players if len(x.influences) > 0 and x.playerIndex != playerIndex]
            if self.playerTurn != playerIndex:
                return []
            if playerState.coins >= 10:
                return []
            result = []
            for influence in util.influenceList:
                if influence not in playerState.influences:
                    if influence in util.influenceToAction:
                        if influence != 'assassin' or playerState.coins >= 3:
                            result.append(util.influenceToAction[influence])
            return util.ActionGenerator(result, playerIndex=playerIndex, otherPlayers=indexList)
        elif self.nextAction == 'block':
            if self.playerTurn == playerIndex:
                return []
            if self.lastAction == 'foreign aid' or (
                    self.lastAction in ['steal', 'assassinate'] and playerIndex == self.playerTarget):
                canBlock = False
                for influence in util.influenceList:
                    if influence in util.blockToInfluence[self.lastAction] and influence in playerState.influences:
                        canBlock = True
                if canBlock:
                    return []
                else:
                    return util.ActionGenerator(['block'], playerIndex=playerIndex)
        return []

    def actions(self, playerIndex):
        return self.legalActions(playerIndex) + self.bluffActions(playerIndex)

    def continueTurn(self):
        nextState = self.deepCopy()
        if self.nextAction == 'discard':
            nextState = nextState.resolveActions()
            nextState.punishedPlayers = [x for x in nextState.punishedPlayers if
                                         len(nextState.players[x].influences) > 0]
            nextState.playersCanAct = list(set(nextState.punishedPlayers))
            if len(nextState.punishedPlayers) == 0:
                nextState = nextState.finishTurn()
        elif self.nextAction == 'challenge':
            if self.playerChallenge is not None:
                nextState = nextState.resolveTopAction()
            if not self.blockPhaseOccurred and not self.challengeSuccess:
                nextState.blockPhaseOccurred = True
                nextState.nextAction = 'block'
                nextState.playersCanAct = [p for p in range(nextState.numPlayers) if
                                           len(nextState.players[p].influences) != 0 and p != nextState.playerTurn]
                # if nextState.currentAction not in util.blocks else []
            else:
                nextState = nextState.resolveActions()
                nextState.nextAction = 'discard'
                nextState.playersCanAct = list(set(nextState.punishedPlayers))
        elif self.nextAction == 'block' and self.blockPhaseOccurred == True:
            nextState = nextState.resolveActions()
            nextState.nextAction = 'discard'
            nextState.playersCanAct = list(set(nextState.punishedPlayers))
        elif self.nextAction == 'block' or self.nextAction == 'action':
            nextState.nextAction = 'challenge'
            nextState.playersCanAct = [p for p in range(nextState.numPlayers) if
                                       len(nextState.players[p].influences) != 0 and p != nextState.playerTurn]
            # if nextState.currentAction not in util.basicActions else []
        while len(nextState.playersCanAct) == 0:
            nextState = nextState.continueTurn()
        return nextState

    def resolveActions(self):
        nextState = self.deepCopy()
        while len(nextState.actionStack) > 0:
            nextAction = nextState.actionStack.pop()
            nextState = nextAction.resolve(nextState)
        return nextState

    def resolveTopAction(self):
        nextState = self.deepCopy()
        nextAction = nextState.actionStack.pop()
        nextState = nextAction.resolve(nextState)
        return nextState

    def finishTurn(self):
        nextState = self.deepCopy()
        nextState.nextAction = 'action'
        nextState.lastAction = None
        nextState.playerChallenge = None
        nextState.playerBlock = None
        nextState.playerTarget = None
        nextState.playerExchange = None
        nextState.punishedPlayers = []
        nextState.challengeSuccess = None
        nextState.blockPhaseOccurred = False
        while True:
            nextState.playerTurn = (nextState.playerTurn + 1) % nextState.numPlayers
            if len(nextState.players[nextState.playerTurn].influences) > 0:
                break
        nextState.playersCanAct = [nextState.playerTurn]
        return nextState

    # Returns:
    #   Dictionary{ Player -> ([list of influences], boolean hasInfluence}
    #   nextState can follow self if:
    #     if hasInfluence: Player must have at least one influence in list
    #     if not hasInfluence: Player must not have any influences in list
    def requiredInfluencesForState(self, nextState):
        requiredInfluences = {}
        if self.nextAction == 'action':
            requiredInfluences[self.playerTurn] = (util.actionToInfluence[nextState.lastAction],
                                                   True) if nextState.lastAction in util.actionToInfluence else (
                [], True)
        elif self.nextAction == 'block' and nextState.playerBlock is not None:
            requiredInfluences[nextState.playerBlock] = (
                util.blockToInfluence[self.lastAction], True) if self.lastAction in util.blockToInfluence else (
                [], True)
        elif self.nextAction == 'challenge' and nextState.playerChallenge is not None:
            if self.playerBlock == None:
                requiredInfluences[self.playerTurn] = (util.actionToInfluence[self.lastAction],
                                                       not nextState.challengeSuccess) if self.lastAction in util.actionToInfluence else (
                    [], False)
            else:
                requiredInfluences[self.playerBlock] = (util.blockToInfluence[self.lastAction],
                                                        not nextState.challengeSuccess) if self.lastAction in util.blockToInfluence else (
                    [], False)
        return requiredInfluences

    def isOver(self):
        activePlayers = [1 for player in self.players if len(player.influences) > 0]
        return sum(activePlayers) <= 1

    def printState(self):
        print(self)

    def deepCopy(self):
        return copy.deepcopy(self)

    def generateSuccessorStates(self, action, playerIndex=0):
        if action is None:
            newState = self.deepCopy()
            newState = newState.continueTurn()
            return [newState]
        if self.nextAction == 'challenge':
            successState = self.deepCopy()
            successState = action.choose(successState)
            successState.actionStack[-1].challengeSuccess = True
            successState = successState.continueTurn()
            failState = action.choose(successState)
            failState.actionStack[-1].challengeSuccess = False
            failState = failState.continueTurn()
            return [successState, failState]
        else:
            # other RNG..... exchange???
            newState = self.deepCopy()
            newState = action.choose(newState)
            newState = newState.continueTurn()
            return [newState]


"""
PlayerState holds the information needed for each of the players in the game.
For example, their player index, their influences (what they have and what they 
could bluff), their coins, etc.
"""


class PlayerState:
    def __init__(self, index, influences):
        self.playerIndex = index
        self.influences = influences
        self.coins = 2
        self.inactiveInfluences = []
        self.revealedInfluences = []
        self.possibleInfluences = collections.Counter({influence: 1 for influence in util.influenceList})

    def __str__(self):
        return str(self.playerIndex) + ': ' + str(self.influences) + ' (%d coins)' % self.coins
