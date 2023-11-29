from shared.game_logic import Card, Deck, Hand


# I have chosen to get these odds using a Monte Carlo situation due to its good balance between accuracy and
# computational efficiency, which can be very useful for poker which is a real-time game.
# Additionally, the option to change the accuracy of the odds is powerful.
def monte_carlo_hand_odds(hand_cards, community_cards, iterations=2000):
    print(f"Hand cards: {hand_cards}")
    print(f"Community cards: {community_cards}")

    if len(hand_cards) != 2:
        return False

    modified_hand_cards = [Card(hand_cards[0][0], hand_cards[0][1]), Card(hand_cards[1][0], hand_cards[1][1])]

    modified_community_cards = []
    for i in range(len(community_cards)):
        modified_community_cards.append(Card(community_cards[i][0], community_cards[i][1]))

    print(f"New hand cards: {modified_hand_cards}")
    print(f"New community cards: {modified_community_cards}")

    hand_odds = {
        "Royal Flush": 0,
        "Straight Flush": 0,
        "Four of a Kind": 0,
        "Full House": 0,
        "Flush": 0,
        "Straight": 0,
        "Three of a Kind": 0,
        "Two Pair": 0,
        "Pair": 0
    }

    # Create a deck (and deck copy) and remove known cards
    deck = Deck()

    for card in modified_hand_cards + modified_community_cards:
        if card in deck.cards:
            deck.cards.remove(card)
        else:
            print(f"Card {card} not found in deck!")

    remaining_deck = deck.cards.copy()

    hand_type_counters = {hand_type: 0 for hand_type in hand_odds}
    # Simulate the remaining community card draws
    for simulation in range(iterations):
        print("-------------------------")

        deck.cards = remaining_deck.copy()  # Reset the deck to its original state for each iteration
        deck.shuffle()
        remaining_cards_to_draw = 5 - len(modified_community_cards)
        simulated_community = modified_community_cards + deck.cards[:remaining_cards_to_draw]

        simulated_hand = Hand(modified_hand_cards + simulated_community)
        hand_results = simulated_hand.evaluate_rankings_for_odds_calculation()

        print(f"hand_type_counters: {hand_type_counters}")
        print("Current hand being evaluated:")
        for card in simulated_hand.cards:
            print(f"Card: {card.rank} {card.suit}")
        print(f"hand_results: {hand_results}")

        # Increment the counters for each hand type that is true
        for hand_type, found in hand_results.items():
            if found:
                hand_type_counters[hand_type] += 1
                print(f"Incremented {hand_type} by 1")

        print("-------------------------")

    # Convert the counts to probabilities
    for hand_type in hand_odds:
        hand_odds[hand_type] = hand_type_counters[hand_type] / iterations

    print(f"Hand odds: {hand_odds}")
    for hand_type, probability in hand_odds.items():
        print(f"Odds of {hand_type}: {probability:.2%}")
    return hand_odds
