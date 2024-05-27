import collections
import random
from actions import *
import util
import copy


class GameState:

    def __init__(self, prevState=None):
        """
        Generates a new state by copying information from its predecessor.
        """
        if prevState is None:
            self.players = []
            self.numPlayers = 0
            self.playerTurn = 0
            self.currentAction = None
            self.playerExchange = None
            self.playerChallenge = None
            self.playerBlock = None
            self.playerTarget = None
            self.punishedPlayers = []
            self.deck = []
            self.inactiveInfluences = collections.Counter()
            self.pastActions = []  # list of counters, one for each player
            self.nextActionType = None  # can be 'action', 'block', 'challenge', 'discard'
            self.challengeSuccess = None
            self.blockPhaseOccured = False
            self.actionStack = []
            self.playersCanAct = []
        else:
            self.players = list(prevState.players)
            self.numPlayers = prevState.numPlayers
            self.playerTurn = prevState.playerTurn
            self.currentAction = prevState.currentAction
            self.playerExchange = prevState.playerExchange
            self.playerChallenge = prevState.playerChallenge
            self.playerBlock = prevState.playerBlock
            self.playerTarget = prevState.playerTarget
            self.punishedPlayers = list(prevState.punishedPlayers)
            self.deck = list(prevState.deck)
            self.inactiveInfluences = collections.Counter(prevState.inactiveInfluences)
            self.pastActions = list(prevState.pastActions)
            self.nextActionType = prevState.nextActionType
            self.challengeSuccess = prevState.challengeSuccess
            self.actionStack = list(prevState.actionStack)
            self.playersCanAct = list(prevState.playersCanAct)
            self.blockPhaseOccured = prevState.blockPhaseOccured

    def __eq__(self, other):
        """
        Allows two states to be compared.
        """

    # def __hash__( self ):
    #   """
    #   Allows states to be keys of dictionaries.
    #   """

    def __str__(self):
        return """
      Players: %r
      Number Players: %r
      Player Turn: %r
      Current Action: %r
      Next Action Type: %r
      Player Block: %r
      Player Challenge: %r
      Challenge Success: %r
      Player Target: %r
      Player Exchange: %r
      Punished Players: %r
      Past Actions: %r
      Deck: %r
      Inactive Influences: %r
    """ % ([str(player) for player in self.players], self.numPlayers, self.playerTurn, self.currentAction, \
           self.nextActionType, self.playerBlock, self.playerChallenge, self.challengeSuccess, self.playerTarget, \
           self.playerExchange, self.punishedPlayers, self.pastActions, self.deck, self.inactiveInfluences)

    def detailedStr(self):
        out = str(self)
        out += """
      Challenge Success: %r
      Block Phase Occured: %r
      Players: 
      """ % (self.challengeSuccess, self.blockPhaseOccured)
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
            for a in self.getAllActions(p):
                astring += '\n\t\t\t%s' % a
            out += '\n\t\t%d: %s' % (p, astring)
        return out

    def initialize(self, numPlayers=4):
        """
        Creates an initial game state given a number of players.
        """
        self.numPlayers = numPlayers
        self.deck = ['ambassador', 'assassin', 'captain', 'contessa', 'duke'] * 3
        random.shuffle(self.deck)
        for i in range(numPlayers):
            nextInfluences = self.deck[0:2]
            self.deck = self.deck[2:]
            s = PlayerState(i, nextInfluences)  # initalizes player state with index number and two cards to have
            self.players.append(s)
        self.playerTurn = random.randint(0, self.numPlayers - 1)
        self.playersCanAct.append(self.playerTurn)
        self.nextActionType = 'action'

    def getLegalActions(self, playerIndex=0):
        playerState = self.players[playerIndex]
        if len(playerState.influences) == 0:
            return [None]
        if self.nextActionType == 'action':
            indexList = [x.playerIndex for x in self.players if len(x.influences) > 0 and x.playerIndex != playerIndex]
            if self.playerTurn != playerIndex:
                return []
            result = ['income', 'foreign aid']
            if playerState.coins >= 10:
                return util.ActionGenerator(['coup'], playerIndex=playerIndex, otherPlayers=indexList)
            if playerState.coins >= 7:
                result += ['coup']
            # now, we look at Influences
            for influence in playerState.influences:
                if influence in util.influenceToAction:
                    if influence != 'assassin' or playerState.coins >= 3:
                        result.append(util.influenceToAction[influence])
            return util.ActionGenerator(result, playerIndex=playerIndex, otherPlayers=indexList)
        elif self.nextActionType == 'block':
            # if the action is steal or assassination, then only the target can block
            # if action is foreign aid, anyone can block
            if self.playerTurn == playerIndex:
                return [None]
            if self.currentAction == 'foreign aid' or (
                    self.currentAction in ['steal', 'assassinate'] and playerIndex == self.playerTarget):
                for influence in playerState.influences:
                    if self.currentAction in util.blockToInfluence and influence in util.blockToInfluence[
                        self.currentAction]:
                        return util.ActionGenerator(['block'], playerIndex=playerIndex) + [None]
            return [None]
        elif self.nextActionType == 'challenge':
            if self.currentAction not in util.basicActions and (
                    (self.playerBlock is not None and playerIndex != self.playerBlock) \
                    or (self.playerBlock is None and playerIndex != self.playerTurn)):
                return util.ActionGenerator(['challenge'], playerIndex=playerIndex) + [None]
            else:
                return [None]
        elif self.nextActionType == 'discard':
            return util.ActionGenerator(['discard'], playerIndex=playerIndex,
                                        numInfluences=len(self.players[playerIndex].influences))

    def getBluffActions(self, playerIndex=0):
        playerState = self.players[playerIndex]
        if len(playerState.influences) == 0:
            return []
        if self.nextActionType == 'action':
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
        elif self.nextActionType == 'block':
            if self.playerTurn == playerIndex:
                return []
            if self.currentAction == 'foreign aid' or (
                    self.currentAction in ['steal', 'assassinate'] and playerIndex == self.playerTarget):
                canBlock = False
                for influence in util.influenceList:
                    if influence in util.blockToInfluence[self.currentAction] and influence in playerState.influences:
                        canBlock = True
                if canBlock:
                    return []
                else:
                    return util.ActionGenerator(['block'], playerIndex=playerIndex)
            else:
                return []
        elif self.nextActionType == 'challenge':
            return []
        elif self.nextActionType == 'discard':
            return []

    def getAllActions(self, playerIndex):  # be less hacky
        return self.getLegalActions(playerIndex) + self.getBluffActions(playerIndex)

    def continueTurn(self):
        nextState = self.deepCopy()
        # print 'nextState:', nextState
        if self.nextActionType == 'discard':
            nextState = nextState.resolveActions()
            nextState.punishedPlayers = [x for x in nextState.punishedPlayers if
                                         len(nextState.players[x].influences) > 0]
            nextState.playersCanAct = list(set(nextState.punishedPlayers))
            if len(nextState.punishedPlayers) == 0:
                nextState = nextState.finishTurn()
        elif self.nextActionType == 'challenge':
            if self.playerChallenge is not None:
                nextState = nextState.resolveTopAction()
            if not self.blockPhaseOccured and not self.challengeSuccess:
                nextState.blockPhaseOccured = True
                nextState.nextActionType = 'block'
                nextState.playersCanAct = [p for p in range(nextState.numPlayers) if
                                           len(nextState.players[p].influences) != 0 and p != nextState.playerTurn]
                # if nextState.currentAction not in util.blocks else []
            else:
                nextState = nextState.resolveActions()
                nextState.nextActionType = 'discard'
                nextState.playersCanAct = list(set(nextState.punishedPlayers))
        elif self.nextActionType == 'block' and self.blockPhaseOccured == True:
            nextState = nextState.resolveActions()
            nextState.nextActionType = 'discard'
            nextState.playersCanAct = list(set(nextState.punishedPlayers))
        elif self.nextActionType == 'block' or self.nextActionType == 'action':
            nextState.nextActionType = 'challenge'
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
        nextState.nextActionType = 'action'
        nextState.currentAction = None
        nextState.playerChallenge = None
        nextState.playerBlock = None
        nextState.playerTarget = None
        nextState.playerExchange = None
        nextState.punishedPlayers = []
        nextState.challengeSuccess = None
        nextState.blockPhaseOccured = False
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
        if self.nextActionType == 'action':
            requiredInfluences[self.playerTurn] = (util.actionToInfluence[nextState.currentAction],
                                                   True) if nextState.currentAction in util.actionToInfluence else (
            [], True)
        elif self.nextActionType == 'block' and nextState.playerBlock is not None:
            requiredInfluences[nextState.playerBlock] = (
            util.blockToInfluence[self.currentAction], True) if self.currentAction in util.blockToInfluence else (
            [], True)
        elif self.nextActionType == 'challenge' and nextState.playerChallenge is not None:
            if self.playerBlock == None:
                requiredInfluences[self.playerTurn] = (util.actionToInfluence[self.currentAction],
                                                       not nextState.challengeSuccess) if self.currentAction in util.actionToInfluence else (
                [], False)
            else:
                requiredInfluences[self.playerBlock] = (util.blockToInfluence[self.currentAction],
                                                        not nextState.challengeSuccess) if self.currentAction in util.blockToInfluence else (
                [], False)
        return requiredInfluences

    def isOver(self):
        activePlayers = [1 for player in self.players if len(player.influences) > 0]
        return sum(activePlayers) <= 1

    def printState(self):
        print(self)

    def deepCopy(self):
        # return GameState(self)
        return copy.deepcopy(self)

    def generateSuccessorStates(self, action, playerIndex):
        if action is None:
            newState = self.deepCopy()
            newState = newState.continueTurn()
            return [newState]
        if self.nextActionType == 'challenge':
            successState = self.deepCopy()
            successState = action.choose(successState)
            successState.actionStack[-1].challengeSuccess = True
            successState = successState.continueTurn()
            failState = self.deepCopy()
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


class PlayerState:
    """
    PlayerStates hold the state of a player (index, Influences etc).
    """

    def __init__(self, index, influences):
        self.playerIndex = index
        self.influences = influences
        self.coins = 2
        self.inactiveInfluences = []
        self.revealedInfluences = []
        self.possibleInfluences = collections.Counter({influence: 1 for influence in util.influenceList})

    def __str__(self):
        return str(self.playerIndex) + ': ' + str(self.influences) + ' (%d coins)' % self.coins

    # def __eq__( self, other ):

    # def __hash__(self):

    # def copy( self ):

