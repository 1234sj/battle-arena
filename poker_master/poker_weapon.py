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

    def draw(self, n=5, hp=None, max_hp=None):
        """Draw cards, low HP gives better cards"""
        if len(self.cards) < n:
            self.create()

        # If HP is low, bias towards better hands
        if hp is not None and max_hp is not None and max_hp > 0:
            hp_ratio = hp / max_hp
            if hp_ratio < 0.5:
                # Low HP: draw multiple sets and pick the best
                num_attempts = int(3 + (0.5 - hp_ratio) * 10)  # 3-8 attempts
                best_cards = None
                best_score = -1

                for _ in range(num_attempts):
                    temp_cards = random.sample(self.cards, n)
                    hand_type, damage = self.evaluate(temp_cards)
                    if damage > best_score:
                        best_score = damage
                        best_cards = temp_cards

                drawn = best_cards
            else:
                drawn = random.sample(self.cards, n)
        else:
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
            return "Royal Flush", 800
        elif is_flush and is_straight:
            return "Straight Flush", 600
        elif counts == [4, 1]:
            return "Four of a Kind", 400
        elif counts == [3, 2]:
            return "Full House", 300
        elif is_flush:
            return "Flush", 250
        elif is_straight:
            return "Straight", 200
        elif counts == [3, 1, 1]:
            return "Three of a Kind", 180
        elif counts == [2, 2, 1]:
            return "Two Pair", 140
        elif counts == [2, 1, 1, 1]:
            return "One Pair", 70
        else:
            return "High Card", vals[0] * 2

    def card_color(self, card):
        s = card[-1]
        return (0, 0, 0) if s in ['a', 'c'] else (255, 0, 0)

    def multiplier(self, hp=None, max_hp=None):
        weights = [1.0 / (i * i) for i in range(3, 21)]  # range(3,21)产生3-20，共18个

        if hp is not None and max_hp is not None and max_hp > 0:
            hp_ratio = hp / max_hp
            if hp_ratio < 0.5:
                boost = int((0.5 - hp_ratio) * 20)
                for i in range(7, 18):  # 原来是 range(10, 20)，改成对应高倍率部分的索引
                    weights[i] *= (1 + boost * 0.5)

        total = sum(weights)
        probs = [w / total for w in weights]
        return random.choices(range(3, 21), weights=probs)[0]

    def get_key_cards(self, cards, hand_type):
        """获取牌型中起作用的牌"""
        vals = []
        for c in cards:
            vs = c[:-1]
            if vs in self.values:
                vals.append((self.values[vs], c))

        if hand_type in ["Royal Flush", "Straight Flush", "Flush", "Straight", "High Card"]:
            # 取最大的5张（全部）
            return cards
        elif hand_type == "Four of a Kind":
            # 取4张相同的
            val_counts = {}
            for v, c in vals:
                val_counts[v] = val_counts.get(v, []) + [c]
            for v, cs in val_counts.items():
                if len(cs) == 4:
                    return cs
        elif hand_type == "Full House":
            # 取3+2
            val_counts = {}
            for v, c in vals:
                val_counts[v] = val_counts.get(v, []) + [c]
            result = []
            for v, cs in val_counts.items():
                if len(cs) == 3:
                    result.extend(cs[:3])
            for v, cs in val_counts.items():
                if len(cs) == 2:
                    result.extend(cs[:2])
            return result
        elif hand_type == "Three of a Kind":
            val_counts = {}
            for v, c in vals:
                val_counts[v] = val_counts.get(v, []) + [c]
            for v, cs in val_counts.items():
                if len(cs) == 3:
                    return cs
        elif hand_type == "Two Pair":
            val_counts = {}
            for v, c in vals:
                val_counts[v] = val_counts.get(v, []) + [c]
            result = []
            for v, cs in val_counts.items():
                if len(cs) == 2:
                    result.extend(cs[:2])
            return result[:4]
        elif hand_type == "One Pair":
            val_counts = {}
            for v, c in vals:
                val_counts[v] = val_counts.get(v, []) + [c]
            for v, cs in val_counts.items():
                if len(cs) == 2:
                    return cs
        elif hand_type == "High Card":
            # 只返回最大的一张牌
            vals = []
            for c in cards:
                vs = c[:-1]
                if vs in self.values:
                    vals.append((self.values[vs], c))
            vals.sort(key=lambda x: x[0], reverse=True)
            return [vals[0][1]]  # 只返回最大的一张

        return cards