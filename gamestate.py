import collections
import random
from actions import *
import copy
import influenceUtils as influences


def actionCoalesce(actionList, playerIndex=0, otherPlayers=[], numInfluences=0):
    result = []
    actionSet = set(actionList)
    actionDict = {
        'income': [Income()],
        'foreign aid': [ForeignAid()],
        'coup': [Coup(x) for x in otherPlayers],
        'block': [Block(playerIndex)],
        'challenge': [Challenge(playerIndex)],
        'tax': [Tax()],
        'assassinate': [Assassinate(x) for x in otherPlayers],
        'exchange': [Exchange()],
        'steal': [Steal(x) for x in otherPlayers],
        'discard': [Discard(playerIndex, x) for x in range(numInfluences)],
        None: [],
    }
    for action in actionSet:
        if action in actionDict:
            result += actionDict[action]
    return result


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
        self.playerExchanged = None
        self.playerChallenged = None
        self.playerBlocked = None
        self.playerTargeted = None
        self.punishedPlayers = []
        self.deck = ['ambassador', 'assassin', 'captain', 'contessa', 'duke'] * (3 if self.numPlayers >= 6 else 2)
        random.shuffle(self.deck)
        for i in range(numPlayers):
            s = PlayerState(i, [self.deck.pop(), self.deck.pop()])
            self.players.append(s)
        self.inactiveInfluences = collections.Counter()
        self.nextAction = 'action'
        self.challengeSuccessful = None
        self.blockOngoing = False
        self.actionStack = []
        self.playersInAction = [self.playerTurn]

    def __str__(self):
        return """
      Players: %r
      Player Turn: %r
      Current Action: %r
      Next Action: %r
      Player Block: %r
      Player Challenge: %r
      Challenge Success: %r
      Player Target: %r
      Player Exchange: %r
      Punished Players: %r
      Deck: %r
      Discarded Influences: %r
    """ % ([str(player) for player in self.players], self.playerTurn, self.lastAction,
           self.nextAction, self.playerBlocked, self.playerChallenged, self.challengeSuccessful, self.playerTargeted,
           self.playerExchanged, self.punishedPlayers, self.deck, self.inactiveInfluences)

    def detailedStr(self):
        out = [
            str(self),
            f"Block Phase Occurred: {self.blockOngoing}",
            "Players:"
        ]

        for player in self.players:
            player_details = (
                f"\n\t{player}\n\t\tInactive Influences: {player.inactiveInfluences}"
                f"\n\t\tRevealed Influences: {player.revealedInfluences}"
                f"\n\t\tPossible Influences: {player.possibleInfluences}"
            )
            out.append(player_details)

        out.append("\n\tActions:")
        for action in self.actionStack:
            out.append(f"\n\t\t{action}")

        out.append(f"\n\tPlayers that can act: {self.playersInAction}")

        out.append("\n\tPossible actions:")
        for i, player in enumerate(self.players):
            actions = "\n".join(f"\n\t\t\t{action}" for action in self.actions(i))
            out.append(f"\n\t\t{i}: {actions}")

        return "".join(out)

    def _getActionLegalActions(self, playerIndex, playerState):
        if self.playerTurn != playerIndex:
            return []

        otherPlayers = [x.playerIndex for x in self.players if len(x.influences) > 0 and x.playerIndex != playerIndex]
        result = ['income', 'foreign aid']

        if playerState.coins >= 10:
            return actionCoalesce(['coup'], playerIndex=playerIndex, otherPlayers=otherPlayers)
        if playerState.coins >= 7:
            result.append('coup')

        for influence in playerState.influences:
            if influence in influences.influenceToAction:
                if influence != 'assassin' or playerState.coins >= 3:
                    result.append(influences.influenceToAction[influence])

        return actionCoalesce(result, playerIndex=playerIndex, otherPlayers=otherPlayers)

    def _getBlockLegalActions(self, playerIndex, playerState):
        if self.playerTurn == playerIndex:
            return [None]
        if self.lastAction == 'foreign aid' or (
                self.lastAction in ['steal', 'assassinate'] and playerIndex == self.playerTargeted):
            for influence in playerState.influences:
                if (self.lastAction in influences.blockToInfluence and
                        influence in influences.blockToInfluence[self.lastAction]):
                    return actionCoalesce(['block'], playerIndex=playerIndex) + [None]
        return [None]

    def _getChallengeLegalActions(self, playerIndex):
        if self.lastAction not in influences.basicActions and (
                (self.playerBlocked is not None and playerIndex != self.playerBlocked) or
                (self.playerBlocked is None and playerIndex != self.playerTurn)):
            return actionCoalesce(['challenge'], playerIndex=playerIndex) + [None]

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
            return actionCoalesce(['discard'], playerIndex=playerIndex,
                                  numInfluences=len(self.players[playerIndex].influences))

    def _handleActionPhase(self, playerIndex, playerState):
        if self.playerTurn != playerIndex or playerState.coins >= 10:
            return []

        indexList = [x.playerIndex for x in self.players if len(x.influences) > 0 and x.playerIndex != playerIndex]
        possibleActions = []

        for influence in influences.influences:
            if influence not in playerState.influences and influence in influences.influenceToAction:
                if influence != 'assassin' or playerState.coins >= 3:
                    possibleActions.append(influences.influenceToAction[influence])

        return actionCoalesce(possibleActions, playerIndex=playerIndex, otherPlayers=indexList)

    def _handleBlockPhase(self, playerIndex, playerState):
        if self.playerTurn == playerIndex:
            return []

        if self._canBlock(playerIndex, playerState):
            return []

        return actionCoalesce(['block'], playerIndex=playerIndex)

    def _canBlock(self, playerIndex, playerState):
        if self.lastAction == 'foreign aid' or (
                self.lastAction in ['steal', 'assassinate'] and playerIndex == self.playerTargeted):
            for influence in influences.influences:
                if influence in influences.blockToInfluence[self.lastAction] and influence in playerState.influences:
                    return True
        return False

    def bluffActions(self, playerIndex=0):
        playerState = self.players[playerIndex]

        if not playerState.influences:
            return []
        if self.nextAction == 'action':
            return self._handleActionPhase(playerIndex, playerState)
        elif self.nextAction == 'block':
            return self._handleBlockPhase(playerIndex, playerState)

        return []

    def actions(self, playerIndex):
        return self.legalActions(playerIndex) + self.bluffActions(playerIndex)

    def _continueDiscardPhase(self, state):
        state = state.resolveActions()
        state.punishedPlayers = [x for x in state.punishedPlayers if len(state.players[x].influences) > 0]
        state.playersInAction = list(set(state.punishedPlayers))
        if not state.punishedPlayers:
            state = state.finishTurn()
        return state

    def _continueChallengePhase(self, state):
        if self.playerChallenged is not None:
            state = state.resolveTopAction()
        if not self.blockOngoing and not self.challengeSuccessful:
            state.blockOngoing = True
            state.nextAction = 'block'
            state.playersInAction = [p for p in range(state.numPlayers) if
                                     len(state.players[p].influences) > 0 and p != state.playerTurn]
        else:
            state = state.resolveActions()
            state.nextAction = 'discard'
            state.playersInAction = list(set(state.punishedPlayers))
        return state

    def _continueBlockPhase(self, state):
        if self.blockOngoing:
            state = state.resolveActions()
            state.nextAction = 'discard'
            state.playersInAction = list(set(state.punishedPlayers))
        else:
            state.nextAction = 'challenge'
            state.playersInAction = [p for p in range(state.numPlayers) if
                                     len(state.players[p].influences) > 0 and p != state.playerTurn]
        return state

    def _continueActionPhase(self, state):
        state.nextAction = 'challenge'
        state.playersInAction = [p for p in range(state.numPlayers) if
                                 len(state.players[p].influences) > 0 and p != state.playerTurn]
        return state

    def continue_turn(self):
        state = self.deepCopy()

        if self.nextAction == 'discard':
            state = self._continueDiscardPhase(state)
        elif self.nextAction == 'challenge':
            state = self._continueChallengePhase(state)
        elif self.nextAction == 'block':
            state = self._continueBlockPhase(state)
        elif self.nextAction == 'action':
            state = self._continueActionPhase(state)

        while not state.playersInAction:
            state = state.continue_turn()

        return state

    def resolveActions(self):
        state = self.deepCopy()
        while len(state.actionStack) > 0:
            nextAction = state.actionStack.pop()
            state = nextAction.resolve(state)
        return state

    def resolveTopAction(self):
        state = self.deepCopy()
        action = state.actionStack.pop()
        state = action.resolve(state)
        return state

    def finishTurn(self):
        state = self.deepCopy()
        state.nextAction = 'action'
        state.lastAction = None
        state.playerChallenged = None
        state.playerBlocked = None
        state.playerTargeted = None
        state.playerExchanged = None
        state.punishedPlayers = []
        state.challengeSuccessful = None
        state.blockOngoing = False
        while True:
            state.playerTurn = (state.playerTurn + 1) % state.numPlayers
            if len(state.players[state.playerTurn].influences) > 0:
                break
        state.playersInAction = [state.playerTurn]
        return state


    def requiredInfluencesForState(self, nextState):
        requiredInfluences = {}
        if self.nextAction == 'action':
            requiredInfluences[self.playerTurn] = (influences.actionToInfluence[nextState.lastAction],
                                                   True) if nextState.lastAction in influences.actionToInfluence else (
                [], True)
        elif self.nextAction == 'block' and nextState.playerBlocked is not None:
            requiredInfluences[nextState.playerBlocked] = (
                influences.blockToInfluence[self.lastAction], True) if self.lastAction in influences.blockToInfluence else (
                [], True)
        elif self.nextAction == 'challenge' and nextState.playerChallenged is not None:
            if not self.playerBlocked:
                requiredInfluences[self.playerTurn] = (influences.actionToInfluence[self.lastAction],
                                                       not nextState.challengeSuccessful) if (self.lastAction in
                                                                                              influences.actionToInfluence) else ([], False)
            else:
                requiredInfluences[self.playerBlocked] = (influences.blockToInfluence[self.lastAction],
                                                          not nextState.challengeSuccessful) if (self.lastAction in
                                                                                               influences.blockToInfluence) else ([], False)
        return requiredInfluences

    def isOver(self):
        activePlayers = [1 for player in self.players if len(player.influences) > 0]
        return sum(activePlayers) <= 1


    def deepCopy(self):
        return copy.deepcopy(self)

    def generateSuccessorStates(self, action, playerIndex=0):
        state = self.deepCopy()
        if action is None:
            state = state.continue_turn()
            return [state]
        if self.nextAction == 'challenge':
            state = action.choose(state)
            state.actionStack[-1].challengeSuccessful = True
            successState = state.continue_turn()
            failState = action.choose(successState)
            failState.actionStack[-1].challengeSuccessful = False
            failState = failState.continue_turn()
            return [successState, failState]
        else:
            state = action.choose(state)
            state = state.continue_turn()
            return [state]


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
        self.possibleInfluences = collections.Counter({influence: 1 for influence in influences})

    def __str__(self):
        return str(self.playerIndex) + ': ' + str(self.influences) + ' (%d coins)' % self.coins
