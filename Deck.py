import random

class Deck:
    def __init__(self):
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
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) > 0:
            return self.cards.pop()
        else:
            print("Deck is empty! Reshuffling...")
            self.build_deck()
            self.shuffle()
            return self.cards.pop()