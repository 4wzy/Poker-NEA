import tkinter as tk
from tkinter import font as tkfont

class HowToPlay(tk.Tk):
    def __init__(self, controller, user_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.controller = controller
        self.user_id = user_id

        self.title("How to Play - AceAware Poker")
        self.configure(bg="#333333")

        # Setting up the frame for the 'How to Play' section
        container = tk.Frame(self, bg="#333333", bd=5)
        container.pack(side="top", fill="both", expand=True)

        title_label = tk.Label(container, text="How to Play", font=tkfont.Font(family="Cambria", size=18),
                               fg="#FFD700", bg="#333333", padx=20)
        title_label.grid(row=0, column=0, sticky="ew")

        # Scrollable text area for the rules
        text_scroll = tk.Scrollbar(container)
        text_scroll.grid(row=1, column=1, sticky='ns')

        text_rules = tk.Text(container, yscrollcommand=text_scroll.set, wrap="word", bg="#555555", fg="#FFFFFF",
                             font=("Cambria", 12), padx=10, pady=10, height=15, borderwidth=2, relief="sunken")
        text_rules.grid(row=1, column=0, sticky="nsew")

        text_scroll.config(command=text_rules.yview)

        # Filling the text area with the rules of Texas Hold'em Poker
        rules_content = """
        Basic Rules of Texas Hold'em Poker:

        Objective:
        The objective of the game is to be the last player remaining in a poker game.
        This is achieved when you have won all of the chips that you can win, and all of the other players have busted.
        
        The Setup:
        - A standard 52 card deck is used with the cards ranked from highest to lowest in this order: A, K, Q, J, 10, 
        9, 8, 7, 6, 5, 4, 3, 2
        - The deck is shuffled and then each player is dealt 2 private cards, known as ‘hole cards’
        - There are up to four rounds of betting (which I will discuss in more detail soon)
        - Five community cards are dealt face-up on the board
        - Players have the option to check, bet, call, raise, or fold when it’s their turn to act. Note that the 
        direction of play is clockwise, so the next player to act is always to the left of the previous player
        - The best five-card poker hand wins the pot
        
        Betting Rounds:
        - There are up to 4 rounds of betting, each with its own different name.
            - It’s important to note that there ‘Blinds’ in poker are mandatory bets which are placed by the two players 
            to the left of the dealer button before the cards are dealt in order to keep the action going and make sure that players are playing on at least some chips each poker round, keeping the game fair.
            - The dealer button is used to indicate the player who deals the cards for the current poker round.
        - Pre-Flop: Players take it in turns to bet after receiving their hole cards, starting with the player to the 
        left of the big blind and ending with the player who has the big blind.
        - Flop: Three community cards are dealt, followed by a round of betting. In this betting round and all 
        subsequent rounds, the player with the small blind (or the first active player after them) is the first to act and the player with the dealer button (or the first active player before them) is the last to act.
        - Turn: A fourth community card is dealt, followed by another round of betting
        - River: The final community card is dealt, followed by the last round of betting
        
        The Showdown:
        If two or more players remain after the final betting round, a showdown will occur.
        Players will reveal their hands, and the best hand according to the poker hand rankings, wins the pot.
        Hand Rankings (from best to worst):
        The Ace has a slightly different value in Poker than in other card games - it can either be the highest card (above a King) or the lowest card (below a 2) when forming a Straight or a Straight Flash. 

        - Royal Flush: A, K, Q, J, 10, all the same suit.
        - Straight Flush: Five cards in a sequence, all in the same suit.
        - Four of a Kind: All four cards of the same rank.
        - Full House: Three of a kind with a pair.
        - Flush: Any five cards of the same suit, but not in a sequence.
        - Straight: Five cards in a sequence, but not of the same suit.
        - Three of a Kind: Three cards of the same rank.
        - Two Pair: Two different pairs.
        - One Pair: Two cards of the same rank.
        - High Card: If nobody has any of the above, the highest card wins

        User Actions - Checking, Betting, Folding, Calling, and Raising:

        - In each betting round, players have the option to 'check', 'bet', 'fold', 'call', or 'raise'.
        - To check is to pass the action to the next player without betting.
          There are 2 possible conditions to be able to check:
              1. No other players have placed a bet during the current betting round
              2. All players before you in the betting round have checked
        
        - To call is to match the current bet and pass the turn along to the next player
        
        - To fold is to forfeit the current hand and all bets placed
        
        - To raise is to increase the size of the existing bet in the same betting round
        

        Remember, practice and respectful play are the keys to becoming good at Poker. Enjoy the game!
        """
        text_rules.insert("1.0", rules_content)
        text_rules.config(state="disabled")  # Prevent text editing

        back_button = tk.Button(container, text="Back to Main Menu", font=tkfont.Font(family="Cambria", size=16),
                                fg="#FFFFFF", bg="#444444", bd=0, padx=20, pady=10, command=lambda: self.controller.open_main_menu(
                self.user_id))
        back_button.grid(row=2, column=0, sticky="ew", pady=10)

        # Configure the grid layout to allow the text widget to expand
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
