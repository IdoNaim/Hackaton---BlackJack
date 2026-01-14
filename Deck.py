import random

class Deck:
    def __init__(self):
        # This list will hold tuples like (1, 0) for Ace of Spades
        self.cards = [] 
        self.build_deck()
        self.shuffle()

    def build_deck(self):
        """Populates the deck with 52 cards (ranks 1-13, suits 0-3)"""
        self.cards = []
        for suit in range(4):        # Suits 0 to 3
            for rank in range(1, 14): # Ranks 1 to 13
                self.cards.append((rank, suit))

    def shuffle(self):
        """Randomizes the order of the cards"""
        random.shuffle(self.cards)

    def draw(self):
        """Removes the top card from the deck and returns it"""
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            # Handle the empty deck case (optional: rebuild and shuffle)
            print("Deck is empty! Reshuffling...")
            self.build_deck()
            self.shuffle()
            return self.cards.pop()