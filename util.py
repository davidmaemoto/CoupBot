from actions import *

influenceList = ['ambassador', 'assassin', 'captain', 'contessa', 'duke']

influenceToAction = {
	'ambassador': 'exchange',
	'assassin': 'assassinate',
	'captain' : 'steal',
	'duke': 'tax',
	'contessa': None
}

actionToInfluence = {
	'exchange': ['ambassador'],
	'assassinate': ['assassin'],
	'steal': ['captain'],
	'tax': ['duke']
}

blockToInfluence = {
	'steal': ['ambassador', 'captain'],
	'assassinate': ['contessa'],
	'foreign aid': ['duke']
}

influenceToBlock = {
	'ambassador': 'steal',
	'captain': 'steal',
	'contessa': 'assassinate',
	'duke:': 'foreign aid'
}

actionToReaction = {
	'action': [Block, Challenge, Discard],
	'block': [Challenge, Discard],
	'challenge': [Discard]
}

reactionToNextAction = {
	Action: 'action',
	Block: 'block',
	Challenge: 'challenge',
	Discard: 'discard'
}

basicActions = ['income', 'foreign aid', 'coup']
specialActions = ['steal', 'assassinate', 'exchange', 'tax']
blocks = ['steal', 'assassinate', 'foreign aid']

def ActionGenerator(actionList, playerIndex=0, otherPlayers=[], numInfluences=0):
	result = []
	actionSet = set(actionList)
	for action in actionSet:
		if action == 'income':
			result += [Income()]
		elif action == 'foreign aid':
			result += [ForeignAid()]
		elif action == 'coup':
			result += [Coup(x) for x in otherPlayers]
		elif action == 'block':
			result += [Block(playerIndex)]
		elif action == 'challenge':
			result += [Challenge(playerIndex)]
		elif action == 'tax':
			result += [Tax()]
		elif action == 'assassinate':
			result += [Assassinate(x) for x in otherPlayers]
		elif action == 'exchange':
			result += [Exchange()]
		elif action == 'steal':
			result += [Steal(x) for x in otherPlayers]
		elif action == 'discard':
			result += [Discard(playerIndex, x) for x in range(numInfluences)]
	return result

