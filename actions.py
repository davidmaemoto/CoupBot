import influenceUtils as utils


class Action:
    def __init__(self, action_type):
        self.type = action_type

    def choose(self, state):
        return state.deepCopy()

    def resolve(self, state):
        return state.deepCopy()

    def __str__(self):
        return self.type.capitalize()


class Challenge(Action):
    def __init__(self, playerChallenge):
        super().__init__('challenge')
        self.playerChallenge = playerChallenge

    def choose(self, state):
        gameState = state.deepCopy()
        gameState.actionStack.append(self)
        gameState.playerChallenged = self.playerChallenge
        actionIsBlock = gameState.playerBlocked is not None

        influences = utils.blockToInfluence[gameState.lastAction] if actionIsBlock else utils.actionToInfluence[
            gameState.lastAction]
        result = any(influence in gameState.players[
            gameState.playerTurn if not actionIsBlock else gameState.playerBlocked].influences for influence in
                     influences)

        self.punishedPlayer = self.playerChallenge if result else (
            gameState.playerTurn if not actionIsBlock else gameState.playerBlocked)
        self.challengeSuccess = not result

        return gameState

    def resolve(self, state):
        gameState = state.deepCopy()
        gameState.challengeSuccessful = self.challengeSuccess
        if self.challengeSuccess:
            gameState.actionStack.pop()
        gameState.punishedPlayers.append(self.punishedPlayer)
        return gameState

    def __str__(self):
        return f'Challenged by {self.playerChallenge}'


class Tax(Action):
    def __init__(self):
        super().__init__('tax')

    def choose(self, state):
        gameState = super().choose(state)
        gameState.lastAction = self.type
        gameState.actionStack.append(self)
        gameState.players[gameState.playerTurn].possibleInfluences['duke'] += 1
        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        gameState.players[gameState.playerTurn].coins += 3
        return gameState


class Assassinate(Action):
    def __init__(self, target):
        super().__init__('assassinate')
        self.target = target

    def choose(self, state):
        gameState = super().choose(state)
        gameState.lastAction = self.type
        gameState.actionStack.append(self)
        gameState.players[gameState.playerTurn].possibleInfluences['assassin'] += 1
        gameState.players[gameState.playerTurn].coins -= 3
        gameState.playerTargeted = self.target
        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        gameState.punishedPlayers.append(self.target)
        return gameState

    def __str__(self):
        return f'Assassination Attempt on {self.target}'


class Exchange(Action):
    def __init__(self):
        super().__init__('exchange')

    def choose(self, state):
        gameState = super().choose(state)
        gameState.lastAction = self.type
        gameState.actionStack.append(self)
        gameState.players[gameState.playerTurn].possibleInfluences['ambassador'] += 1
        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        gameState.playerExchanged = gameState.playerTurn
        addCards = gameState.deck[:2]
        gameState.deck = gameState.deck[2:]
        gameState.players[gameState.playerTurn].influences.extend(addCards)
        gameState.punishedPlayers.extend([gameState.playerTurn] * 2)
        return gameState


class Steal(Action):
    def __init__(self, target):
        super().__init__('steal')
        self.target = target

    def choose(self, state):
        gameState = super().choose(state)
        gameState.lastAction = self.type
        gameState.actionStack.append(self)
        gameState.players[gameState.playerTurn].possibleInfluences['captain'] += 1
        gameState.playerTargeted = self.target
        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        stolenCoins = min(gameState.players[self.target].coins, 2)
        gameState.players[self.target].coins -= stolenCoins
        gameState.players[gameState.playerTurn].coins += stolenCoins
        return gameState

    def __str__(self):
        return f'Steal from {self.target}'


class Income(Action):
    def __init__(self):
        super().__init__('income')

    def choose(self, state):
        gameState = super().choose(state)
        gameState.lastAction = self.type
        gameState.actionStack.append(self)
        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        gameState.players[gameState.playerTurn].coins += 1
        return gameState


class ForeignAid(Action):
    def __init__(self):
        super().__init__('foreign aid')

    def choose(self, state):
        gameState = super().choose(state)
        gameState.lastAction = self.type
        gameState.actionStack.append(self)
        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        gameState.players[gameState.playerTurn].coins += 2
        return gameState


class Coup(Action):
    def __init__(self, target):
        super().__init__('coup')
        self.target = target

    def choose(self, state):
        gameState = super().choose(state)
        gameState.lastAction = self.type
        gameState.actionStack.append(self)
        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        gameState.players[gameState.playerTurn].coins -= 7
        gameState.punishedPlayers.append(self.target)
        return gameState

    def __str__(self):
        return f'Coup Attempt on {self.target}'


class Block(Action):
    def __init__(self, playerBlock):
        super().__init__('block')
        self.playerBlock = playerBlock

    def choose(self, state):
        gameState = super().choose(state)
        gameState.playerBlocked = self.playerBlock
        gameState.actionStack.append(self)

        influences = utils.blockToInfluence.get(gameState.lastAction, [])
        for influence in influences:
            gameState.players[gameState.playerTurn].possibleInfluences[influence] += 1

        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        if gameState.actionStack:
            gameState.actionStack.pop()
        return gameState

    def __str__(self):
        return f'Blocked by {self.playerBlock}'


class Discard(Action):
    def __init__(self, player, influenceIndex):
        super().__init__('discard')
        self.influenceIndex = influenceIndex
        self.player = player

    def choose(self, state):
        gameState = super().choose(state)
        gameState.actionStack.insert(0, self)
        return gameState

    def resolve(self, state):
        gameState = super().resolve(state)
        gameState.punishedPlayers.remove(self.player)

        influences = gameState.players[self.player].influences
        influence_to_remove = influences.pop(self.influenceIndex)

        if self.player == gameState.playerExchanged:
            gameState.deck.append(influence_to_remove)
        else:
            gameState.inactiveInfluences[influence_to_remove] += 1

        return gameState

    def __str__(self):
        return f'Discard by {self.player} [{self.influenceIndex}]'
