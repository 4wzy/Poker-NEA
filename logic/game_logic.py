from random import randint

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} {self.suit}"


class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank)
                      for suit in ["Clubs", "Diamonds", "Spades", "Hearts"] for rank in
                      ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]]

    def shuffle(self):
        for i in range(len(self.cards)):
            swap_number = randint(0, len(self.cards) - 1)
            self.cards[swap_number], self.cards[i] = self.cards[i], self.cards[swap_number]

    # Debug method
    def print_cards(self):
        for card in self.cards:
            print(card)

    def deal_card(self):
        # This method deals a single card from the top of the deck
        return self.cards.pop()


class Player:
    def __init__(self, name, user_id, chips):
        self.name = name
        self.user_id = user_id
        self.profile_picture = None
        self.chips = chips
        self.hand = Hand([])

    def add_card(self, card):
        self.hand.cards.append(card)


class Game:
    def __init__(self, starting_chips=100):
        self.players = []
        self.available_positions = ["top_left", "top_middle", "top_right", "bottom_left", "bottom_middle", "bottom_right"]

        self.pot = Pot()
        self.board = []
        self.deck = Deck()
        self.deck.shuffle()

    def add_player(self, player: Player):
        position = self.available_positions.pop(0)
        self.players.append(player)

    def deal_cards(self, num_cards, player):
        for i in range(num_cards):
            card = self.deck.deal_card()
            player.add_card(card)

    def start_round(self):
        self.board = []
        for player in self.players:
            self.deal_cards(2, player)

    def flop(self):
        for i in range(3):
            card = self.deck.deal_card()
            self.board.append(card)

    def turn_river(self):
        card = self.deck.deal_card()
        self.board.append(card)

    def process_player_action(self, player_id, action):
        # Process a player action (fold, call, raise) and update the game state
        pass

    def send_game_state(self):
        # Send the current game state to all connected clients
        pass


class Pot:
    def __init__(self):
        self.chips = 0

    def add_chips(self, amount):
        self.chips += amount

    def subtract_chips(self, amount):
        self.chips -= amount

    def reset_pot(self):
        self.chips = 0


class Hand:
    def __init__(self, cards):
        self.cards = cards

    def evaluate_strength(self):
        pass


game = Game(["Player1", "Player2", "Player3", "Player4", "Player5", "Player6"])
game.start_round()
