# D:\deeplearning\play\poker_master\poker_master.py

import pygame
import math
from .poker_weapon import PokerDeck
from character import Projectile

PROJECTILE_SPEED = 15


def draw_suit_symbol(screen, suit, cx, cy, size=10, color=(0, 0, 0)):
    """Draw suit symbol instead of letter"""
    if suit in ['a', 'c']:  # Spades, Clubs - black
        color = (0, 0, 0)
    else:  # Hearts, Diamonds - red
        color = (255, 0, 0)

    if suit == 'a':  # Spade
        points = [(cx, cy - size), (cx + size // 2, cy - size // 2), (cx + size // 4, cy),
                  (cx + size // 2, cy + size), (cx, cy + size // 2),
                  (-cx + size // 2, cy + size), (-cx + size // 4, cy), (-cx + size // 2, cy - size // 2)]
        # Simplified spade
        pygame.draw.circle(screen, color, (cx - size // 4, cy), size // 2)
        pygame.draw.circle(screen, color, (cx + size // 4, cy), size // 2)
        pygame.draw.polygon(screen, color, [(cx - size // 3, cy), (cx, cy + size), (cx + size // 3, cy)])
        pygame.draw.rect(screen, color, (cx - 1, cy, 2, size))
    elif suit == 'b':  # Heart
        pygame.draw.circle(screen, color, (cx - size // 4, cy - size // 4), size // 2)
        pygame.draw.circle(screen, color, (cx + size // 4, cy - size // 4), size // 2)
        pygame.draw.polygon(screen, color, [(cx - size // 2 + 2, cy - size // 4), (cx + size // 2 - 2, cy - size // 4),
                                            (cx, cy + size)])
    elif suit == 'c':  # Club
        pygame.draw.circle(screen, color, (cx, cy - size // 2), size // 3)
        pygame.draw.circle(screen, color, (cx - size // 3, cy), size // 3)
        pygame.draw.circle(screen, color, (cx + size // 3, cy), size // 3)
        pygame.draw.rect(screen, color, (cx - 1, cy, 2, size))
    elif suit == 'd':  # Diamond
        pygame.draw.polygon(screen, color,
                            [(cx, cy - size), (cx + size // 2, cy), (cx, cy + size), (cx - size // 2, cy)])


class PokerMaster:
    def __init__(self, char):
        self.char = char
        self.deck = PokerDeck()
        self.cards = []
        self.result = None
        self.damage = 0
        self.mult = 1
        self.timer = 0
        self.cooldown = 0.8
        self.display_duration = 1.0
        self.attacking = False
        self.phase = 0
        self.show_idx = 0
        self.show_timer = 0
        self.pending = []

    def update(self):
        if not self.char.opponent or self.char.opponent.hp <= 0:
            return
        if self.attacking:
            self.timer -= 1 / 60
            if self.phase == 1:
                self.show_timer -= 1 / 60
                if self.show_timer <= 0 and self.show_idx < len(self.cards):
                    self.show_idx += 1
                    self.show_timer = 0.10
                if self.show_idx >= len(self.cards) and self.timer < self.display_duration - 0.3:
                    self.phase = 2
                    self.fire()
            elif self.phase == 2 and self.timer <= 0:
                self.attacking = False
                self.phase = 0
                self.pending = []
        else:
            self.cooldown -= 1 / 60
            if self.cooldown <= 0:
                self.start()

    def start(self):
        if not self.char.opponent or self.char.opponent.hp <= 0:
            return
        self.attacking = True
        self.phase = 1
        self.timer = self.display_duration
        self.cooldown = 0.8
        self.cards = self.deck.draw(5)
        hand, base = self.deck.evaluate(self.cards)
        self.mult = self.deck.multiplier(self.char.hp, self.char.max_hp)
        self.damage = base * self.mult
        self.result = f"{hand} Base:{base}"
        self.show_idx = 0
        self.show_timer = 0.10

    def fire(self):
        opp = self.char.opponent
        if not opp:
            return
        dx = opp.x - self.char.x
        dy = opp.y - self.char.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist > 0:
            vx = dx / dist * PROJECTILE_SPEED
            vy = dy / dist * PROJECTILE_SPEED
        else:
            vx, vy = PROJECTILE_SPEED, 0
        p = Projectile(self.char.x, self.char.y, vx, vy, self.damage, self.char, opp, (255, 215, 0), 8)
        self.pending = [p]

    def get_projectiles(self):
        proj = self.pending[:]
        self.pending = []
        return proj

    def draw(self, screen, font):
        if not self.attacking:
            return
        x = self.char.x
        y = self.char.y - self.char.radius - 80
        w = len(self.cards) * 40 + 10
        pygame.draw.rect(screen, (50, 50, 50), (x - w // 2, y - 35, w, 55))
        pygame.draw.rect(screen, (200, 200, 200), (x - w // 2, y - 35, w, 55), 2)

        sf = pygame.font.Font(None, 18)
        for i, c in enumerate(self.cards):
            if i < self.show_idx:
                cx = x - (len(self.cards) * 40) // 2 + 20 + i * 40
                # Draw card background
                cr = pygame.Rect(cx - 16, y - 12, 32, 24)
                pygame.draw.rect(screen, (255, 255, 255), cr)
                pygame.draw.rect(screen, (0, 0, 0), cr, 1)
                # Draw value (number/letter)
                value = c[:-1]
                suit = c[-1]
                vt = sf.render(value, True, (0, 0, 0))
                screen.blit(vt, (cx - 14, y - 10))
                # Draw suit symbol
                draw_suit_symbol(screen, suit, cx + 6, y + 2, 8)

        if self.show_idx >= len(self.cards):
            mf = pygame.font.Font(None, 20)
            t1 = mf.render(self.result, True, (255, 255, 0))
            t2 = mf.render(f"x{self.mult}={self.damage}", True, (255, 165, 0))
            screen.blit(t1, t1.get_rect(center=(x, y + 40)))
            screen.blit(t2, t2.get_rect(center=(x, y + 60)))