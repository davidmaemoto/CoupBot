import util


class Action:
    def __init__(self):
        pass

    def choose(self, state):
        gameState = state.deepCopy()
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        return gameState


class Challenge(Action):

    def __init__(self, playerChallenge):
        self.type = 'challenge'
        self.playerChallenge = playerChallenge

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.actionStack.append(self)
        gameState.playerChallenge = self.playerChallenge
        actionIsBlock = gameState.playerBlock is not None
        lastPlayer = gameState.playerBlock if actionIsBlock else gameState.playerTurn
        if not actionIsBlock:
            influences = util.actionToInfluence[gameState.currentAction]  # Influence is a list
            # want to see if playerTurn has that Influence
            result = any([True for x in influences if x in gameState.players[gameState.playerTurn].influences])
            self.punishedPlayer = self.playerChallenge if result else gameState.playerTurn
            self.challengeSuccess = not result
        else:
            influences = util.blockToInfluence[gameState.currentAction]  # Influence is a list
            # want to see if playerTurn has that Influence
            result = any([True for x in influences if x in gameState.players[gameState.playerBlock].influences])
            self.punishedPlayer = self.playerChallenge if result else gameState.playerBlock
            self.challengeSuccess = not result
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        gameState.challengeSuccess = self.challengeSuccess
        if self.challengeSuccess:
            gameState.actionStack.pop()
        gameState.punishedPlayers.append(self.punishedPlayer)
        return gameState

    def __str__(self):
        return 'Challenge by  %r' % (self.playerChallenge)


class Tax(Action):

    def __init__(self):
        self.type = 'tax'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.currentAction = 'tax'
        gameState.actionStack.append(self)
        gameState.players[gameState.playerTurn].possibleInfluences['duke'] += 1
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        # Current player's coin amount += 3
        gameState.players[gameState.playerTurn].coins += 3
        return gameState

    def __str__(self):
        return 'Tax'


class Assassinate(Action):

    def __init__(self, target):
        self.target = target
        self.type = 'assassinate'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.currentAction = 'assassinate'
        gameState.actionStack.append(self)
        gameState.players[gameState.playerTurn].possibleInfluences['assassin'] += 1
        gameState.players[gameState.playerTurn].coins -= 3
        gameState.playerTarget = self.target
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        gameState.punishedPlayers.append(self.target)
        return gameState

    def __str__(self):
        return 'Assassination of: %r' % (self.target)


class Exchange(Action):

    def __init__(self):
        self.type = 'exchange'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.currentAction = 'exchange'
        gameState.actionStack.append(self)
        gameState.players[gameState.playerTurn].possibleInfluences['ambassador'] += 1
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        gameState.playerExchange = gameState.playerTurn
        addCards = gameState.deck[0:2]
        gameState.deck = gameState.deck[2:]
        gameState.players[gameState.playerTurn].influences += addCards
        gameState.punishedPlayers += [gameState.playerTurn, gameState.playerTurn]
        return gameState

    def __str__(self):
        return 'Exchange'


class Steal(Action):

    def __init__(self, target):
        self.target = target
        self.type = 'steal'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.currentAction = 'steal'
        gameState.actionStack.append(self)
        gameState.players[gameState.playerTurn].possibleInfluences['captain'] += 1
        gameState.playerTarget = self.target
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        stolenCoins = min(gameState.players[self.target].coins, 2)
        gameState.players[self.target].coins -= stolenCoins
        gameState.players[gameState.playerTurn].coins += stolenCoins
        return gameState

    def __str__(self):
        return 'Steal from: %r' % (self.target)


class Income(Action):

    def __init__(self):
        self.type = 'income'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.currentAction = 'income'
        gameState.actionStack.append(self)
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        # Current player's coin amount += 1
        gameState.players[gameState.playerTurn].coins += 1
        return gameState

    def __str__(self):
        return 'Income'


class ForeignAid(Action):

    def __init__(self):
        self.type = 'foreign aid'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.currentAction = 'foreign aid'
        gameState.actionStack.append(self)
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        # Current player's coin amount += 2
        gameState.players[gameState.playerTurn].coins += 2
        return gameState

    def __str__(self):
        return 'Foreign Aid'


class Coup(Action):

    def __init__(self, target):
        self.target = target
        self.type = 'coup'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.currentAction = 'coup'
        gameState.actionStack.append(self)
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        gameState.players[gameState.playerTurn].coins -= 7
        gameState.punishedPlayers.append(self.target)
        return gameState

    def __str__(self):
        return 'Coup on: %r' % (self.target)


class Block(Action):

    def __init__(self, playerBlock):
        self.playerBlock = playerBlock
        self.type = 'block'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.playerBlock = self.playerBlock
        gameState.actionStack.append(self)
        if gameState.currentAction == 'foreign aid':
            gameState.players[gameState.playerTurn].possibleInfluences['duke'] += 1
        elif gameState.currentAction == 'assassinate':
            gameState.players[gameState.playerTurn].possibleInfluences['contessa'] += 1
        elif gameState.currentAction == 'steal':
            gameState.players[gameState.playerTurn].possibleInfluences['captain'] += 0.5
            gameState.players[gameState.playerTurn].possibleInfluences['ambassador'] += 0.5
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        gameState.playerBlock = None  # why?
        if len(gameState.actionStack) > 0:
            gameState.actionStack.pop()
        return gameState

    def __str__(self):
        return 'Block by: %r' % (self.playerBlock)


class Discard(Action):

    def __init__(self, player, influenceIndex):
        self.influenceIndex = influenceIndex
        self.player = player
        self.type = 'discard'

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.actionStack.insert(0, self)
        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        gameState.punishedPlayers.remove(self.player)
        influences = gameState.players[self.player].influences
        if len(influences) == 0:
            print('OOPS influences empty')
            return gameState
        if len(influences) <= self.influenceIndex:
            print('OOPS influences out of range')
            self.influenceIndex = len(influences) - 1
        if self.player == gameState.playerExchange:
            gameState.deck.append(influences[self.influenceIndex])
        else:
            gameState.inactiveInfluences[influences[self.influenceIndex]] += 1
        del gameState.players[self.player].influences[self.influenceIndex]
        return gameState

    def __str__(self):
        return 'Discard by: %r [%d]' % (self.player, self.influenceIndex)