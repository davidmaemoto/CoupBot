import random

# Initial deck
deck = ["contessa", "duke", "captain", "assassin", "ambassador",
        "contessa", "duke", "captain", "assassin", "ambassador"]

# Function to deal cards
def deal_cards(deck, num_players, cards_per_player):
    random.shuffle(deck)  # Shuffle the deck
    players = {f'Opponent { i +1}': {'cards': [], 'memory': []} for i in range(num_players - 1)}  # Initialize players
    players["Coup Bot"] = {'cards': [], 'memory': []}  # Add the Coup Bot

    # Assign cards to players
    for player in players:
        players[player]['cards'] = [deck.pop() for _ in range(cards_per_player)]

    return players, deck

# Game state
players = {}
coins = {}

# Initialize game
def start_game():
    global players, coins
    num_players = 3
    cards_per_player = 2

    # Deal the cards
    players, updated_deck = deal_cards(deck, num_players, cards_per_player)

    # Initialize coins
    coins = {player: 2 for player in players}

    # Each player initializes their memory with their own cards
    for player in players:
        players[player]['memory'].extend(players[player]['cards'])

    # Output the results
    print("Players and their cards:")
    for player, info in players.items():
        print(f"{player}: {info['cards']}")

    print("\nUpdated deck:")
    print(updated_deck)

    print("\nInitial coins:")
    print(coins)


# Challenge function
def challenge(action_player, claimed_card, challenger):
    print(f"{challenger} challenges {action_player} claiming to have {claimed_card}.")

    if claimed_card in players[action_player]['cards']:
        print(f"Challenge failed. {action_player} has {claimed_card}. {challenger} loses a card.")
        lost_card = players[challenger]['cards'].pop()
        players[challenger]['memory'].append(lost_card)
        print(f"{challenger} loses a card. Remaining cards: {players[challenger]['cards']}")

        # Update memory of all other players with challenger's lost card
        for player in players:
            if player != challenger:
                players[player]['memory'].append(lost_card)

        # The action player returns the claimed card to the deck, shuffles, and draws a new one
        players[action_player]['cards'].remove(claimed_card)
        deck.append(claimed_card)
        random.shuffle(deck)
        new_card = deck.pop()
        players[action_player]['cards'].append(new_card)
        players[action_player]['memory'] = list \
            (set(players[action_player]['memory']).union(set(players[action_player]['cards'])))
        print(f"{action_player} replaces {claimed_card} with {new_card}.")
        return False
    else:
        print(f"Challenge successful. {action_player} does not have {claimed_card}. {action_player} loses a card.")
        lost_card = players[action_player]['cards'].pop()
        players[action_player]['memory'].append(lost_card)
        print(f"{action_player} loses a card. Remaining cards: {players[action_player]['cards']}")

        # Update memory of all other players with action player's lost card
        for player in players:
            if player != action_player:
                players[player]['memory'].append(lost_card)
        return True

# Actions
def income(player):
    coins[player] += 1
    print(f"{player} takes Income. Coins: {coins[player]}")

def foreign_aid(player):
    coins[player] += 2
    print(f"{player} takes Foreign Aid. Coins: {coins[player]}")
    for opponent in players:
        if opponent != player and "duke" in players[opponent]['cards']:
            duke_block_foreign_aid(player, opponent)
            return

def duke_block_foreign_aid(player, blocker):
    print(f"{blocker} blocks Foreign Aid with Duke.")
    if ["duke", "duke"] in players[player]['memory']:
        print(f"{player} challenges {blocker} claiming to have Duke.")
        if challenge(blocker, "duke", player):
            return
    coins[player] -= 2



def ambassador_exchange(player, deck):
    # Draw 2 new cards before returning the old ones to avoid duplicates in the deck
    new_cards = [deck.pop() for _ in range(2)]

    # Update the player's memory to include the new cards
    players[player]['memory'] = list(set(players[player]['memory']).union(set(new_cards)))
    current_cards = players[player]['cards']
    all_cards = current_cards + new_cards

    # Determine how many cards the player can pick
    num_cards_to_pick = len(current_cards)

    # Choose the required number of cards randomly
    chosen_cards = random.sample(all_cards, num_cards_to_pick)

    # Return the unchosen cards to the deck
    unchosen_cards = [card for card in all_cards if card not in chosen_cards]
    deck.extend(unchosen_cards)
    random.shuffle(deck)

    # Update the player's cards
    players[player]['cards'] = chosen_cards
    print(f"{player} exchanges cards with the Ambassador. New cards: {players[player]['cards']}")

    # Reset memories of all other players to only their hole cards
    for p in players:
        if p != player:
            players[p]['memory'] = players[p]['cards'][:]

    # Challenge logic
    possible_challengers = [opponent for opponent in players if opponent != player]
    if possible_challengers:
        challenge(player, "ambassador", possible_challengers)

def assassinate(player, target):
    if coins[player] >= 3:
        coins[player] -= 3
        print(f"{player} assassinates {target}. Coins: {coins[player]}")
        challengers = [opponent for opponent in players if opponent != player and "assassin" in players[opponent]['memory']]
        if challengers and challenge(player, "assassin", challengers):
            return
        # Target loses a card
        if "contessa" in players[target]['cards']:
            print(f"{target} blocks assassination with Contessa.")
        else:
            lost_card = players[target]['cards'].pop()
            players[target]['memory'].append(lost_card)
            print(f"{target} loses a card. Remaining cards: {players[target]['cards']}")

def captain_steal(player, target):
    stolen_amount = min(2, coins[target])
    challengers = [opponent for opponent in players if opponent != player and "captain" in players[opponent]['memory']]
    if challengers and challenge(player, "captain", challengers):
        return
    coins[target] -= stolen_amount
    coins[player] += stolen_amount
    print \
        (f"{player} steals {stolen_amount} coins from {target}. {player} Coins: {coins[player]}, {target} Coins: {coins[target]}")

def block_steal(player, blocking_card):
    print(f"{player} blocks stealing with {blocking_card}.")

def duke_tax(player):
    coins[player] += 3
    print(f"{player} takes Tax with Duke. Coins: {coins[player]}")
    challengers = [opponent for opponent in players if opponent != player and "duke" in players[opponent]['memory']]
    if challengers:
        challenge(player, "duke", challengers)

def coup(player):
    if coins[player] >= 7:
        coins[player] -= 7
        # Choose a target
        target = None
        for opponent in players:
            if opponent != player:
                if not target:
                    target = opponent
                elif len(players[opponent]['cards']) > len(players[target]['cards']):
                    target = opponent
                elif len(players[opponent]['cards']) == len(players[target]['cards']) and coins[opponent] > coins[target]:
                    target = opponent
        print(f"{player} coups {target}. Coins: {coins[player]}")
        lost_card = players[target]['cards'].pop()
        players[target]['memory'].append(lost_card)
        print(f"{target} loses a card. Remaining cards: {players[target]['cards']}")

# Example gameplay
start_game()
income("Coup Bot")
foreign_aid("Opponent 1")
duke_tax("Opponent 2")
captain_steal("Coup Bot", "Opponent 1")
ambassador_exchange("Coup Bot", deck)
assassinate("Opponent 1", "Coup Bot")
coup("Coup Bot")