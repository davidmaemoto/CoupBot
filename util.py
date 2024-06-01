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
		'discard': [Discard(playerIndex, x) for x in range(numInfluences)]
	}
	result = []
	for action in set(actionList):
		result += actionDict[action]
	return result

