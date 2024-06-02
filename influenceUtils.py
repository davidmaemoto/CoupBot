from actions import *

influences = ['ambassador', 'assassin', 'captain', 'contessa', 'duke']

influenceToAction = {
    'ambassador': 'exchange',
    'assassin': 'assassinate',
    'captain': 'steal',
    'duke': 'tax',
    'contessa': None
}

actionToInfluence = {
    'exchange': ['ambassador'],
    'assassinate': ['assassin'],
    'steal': ['captain'],
    'tax': ['duke'],
    None: 'contessa'
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

basicActions = ['income', 'foreign aid', 'coup']
influenceActions = ['steal', 'assassinate', 'exchange', 'tax']
blocks = ['steal', 'assassinate', 'foreign aid']


