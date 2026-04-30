# D:\deeplearning\play\poker_master\poker_weapon.py
import random


class PokerDeck:
    def __init__(self):
        self.suits = {'a': 'Spades', 'b': 'Hearts', 'c': 'Clubs', 'd': 'Diamonds'}
        self.values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12,
                       'K': 13, 'A': 14}
        self.cards = []
        self.create()

    def create(self):
        self.cards = []
        for v in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']:
            for s in ['a', 'b', 'c', 'd']:
                self.cards.append(f"{v}{s}")

    def draw(self, n=5):
        if len(self.cards) < n:
            self.create()
        drawn = random.sample(self.cards, n)
        for c in drawn:
            self.cards.remove(c)
        return drawn

    def evaluate(self, cards):
        vals = []
        suits = []
        for c in cards:
            vs = c[:-1]
            s = c[-1]
            if vs in self.values:
                vals.append(self.values[vs])
            suits.append(s)
        vals.sort(reverse=True)

        is_flush = len(set(suits)) == 1
        is_straight = False
        if len(set(vals)) == 5 and vals[0] - vals[4] == 4:
            is_straight = True
        if vals == [14, 5, 4, 3, 2]:
            is_straight = True
            vals = [5, 4, 3, 2, 1]

        vc = {}
        for v in vals:
            vc[v] = vc.get(v, 0) + 1
        counts = sorted(vc.values(), reverse=True)

        if is_flush and is_straight and vals[0] == 14:
            return "Royal Flush", 500
        elif is_flush and is_straight:
            return "Straight Flush", 400
        elif counts == [4, 1]:
            return "Four of a Kind", 300
        elif counts == [3, 2]:
            return "Full House", 200
        elif is_flush:
            return "Flush", 150
        elif is_straight:
            return "Straight", 125
        elif counts == [3, 1, 1]:
            return "Three of a Kind", 90
        elif counts == [2, 2, 1]:
            return "Two Pair", 75
        elif counts == [2, 1, 1, 1]:
            return "One Pair", 40
        else:
            return "High Card", vals[0]

    def card_color(self, card):
        s = card[-1]
        return (0, 0, 0) if s in ['a', 'c'] else (255, 0, 0)

    def multiplier(self, hp=None, max_hp=None):
        weights = [1.0 / (i * i) for i in range(1, 21)]

        # HP越低，高倍率概率越高
        if hp is not None and max_hp is not None:
            hp_ratio = hp / max_hp
            if hp_ratio < 0.5:
                boost = int((0.5 - hp_ratio) * 20)  # 血量越低boost越大
                for i in range(10, 20):
                    weights[i] *= (1 + boost * 0.5)

        total = sum(weights)
        probs = [w / total for w in weights]
        return random.choices(range(1, 21), weights=probs)[0]
