import random


def monte_carlo_flush_draw(hand, community, iterations=10000):
    # Define all suits and ranks
    suits = ["Clubs", "Diamonds", "Spades", "Hearts"]  # Hearts, Diamonds, Clubs, Spades
    ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

    # Create a deck of cards and remove known cards
    deck = [[r, s] for r in ranks for s in suits]
    known_cards = hand + community
    print(f"deck: {deck}")
    print(f"known_cards: {known_cards}")
    for card in known_cards:
        deck.remove(card)
        print(f"removed {card}")

    # Count the number of flush completions
    flush_completions = 0
    for _ in range(iterations):
        # Shuffle the deck and draw the next cards
        random.shuffle(deck)
        next_cards = deck[:5 - len(community)]  # Draw enough cards to complete the board

        # Check if we complete our flush
        all_cards = hand + community + next_cards
        suits_in_hand = [card[1] for card in all_cards]
        if _ < 15:
            print(f"suits_in_hand: {suits_in_hand}")
        for suit in suits:
            if suits_in_hand.count(suit) >= 5:
                flush_completions += 1
                break

    print(flush_completions)
    print(iterations)

    # Calculate probability
    flush_probability = 100 * flush_completions / iterations
    return flush_probability
