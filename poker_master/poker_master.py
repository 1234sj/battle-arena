# D:\deeplearning\play\poker_master\poker_master.py
import pygame
import math
from .poker_weapon import PokerDeck
from character import Projectile

PROJECTILE_SPEED = 15


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
        w = len(self.cards) * 35 + 10
        pygame.draw.rect(screen, (50, 50, 50), (x - w // 2, y - 35, w, 55))
        pygame.draw.rect(screen, (200, 200, 200), (x - w // 2, y - 35, w, 55), 2)

        sf = pygame.font.Font(None, 18)
        for i, c in enumerate(self.cards):
            if i < self.show_idx:
                cx = x - (len(self.cards) * 35) // 2 + 17 + i * 35
                color = self.deck.card_color(c)
                cr = pygame.Rect(cx - 13, y - 10, 26, 20)
                pygame.draw.rect(screen, (255, 255, 255), cr)
                pygame.draw.rect(screen, (0, 0, 0), cr, 1)
                t = sf.render(c, True, color)
                screen.blit(t, t.get_rect(center=(cx, y)))

        if self.show_idx >= len(self.cards):
            mf = pygame.font.Font(None, 20)
            t1 = mf.render(self.result, True, (255, 255, 0))
            t2 = mf.render(f"x{self.mult}={self.damage}", True, (255, 165, 0))
            screen.blit(t1, t1.get_rect(center=(x, y + 40)))
            screen.blit(t2, t2.get_rect(center=(x, y + 60)))