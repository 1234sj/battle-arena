# D:\deeplearning\play\poker_master\poker_master.py

import pygame
import math
from .poker_weapon import PokerDeck
from character import Projectile

PROJECTILE_SPEED = 15


def draw_suit_symbol(screen, suit, cx, cy, size=10, color=(0, 0, 0)):
    if suit in ['a', 'c']:
        color = (0, 0, 0)
    else:
        color = (255, 0, 0)

    if suit == 'a':
        pygame.draw.circle(screen, color, (cx - size // 4, cy), size // 2)
        pygame.draw.circle(screen, color, (cx + size // 4, cy), size // 2)
        pygame.draw.polygon(screen, color, [(cx - size // 3, cy), (cx, cy + size), (cx + size // 3, cy)])
        pygame.draw.rect(screen, color, (cx - 1, cy, 2, size))
    elif suit == 'b':
        pygame.draw.circle(screen, color, (cx - size // 4, cy - size // 4), size // 2)
        pygame.draw.circle(screen, color, (cx + size // 4, cy - size // 4), size // 2)
        pygame.draw.polygon(screen, color, [(cx - size // 2 + 2, cy - size // 4), (cx + size // 2 - 2, cy - size // 4),
                                            (cx, cy + size)])
    elif suit == 'c':
        pygame.draw.circle(screen, color, (cx, cy - size // 2), size // 3)
        pygame.draw.circle(screen, color, (cx - size // 3, cy), size // 3)
        pygame.draw.circle(screen, color, (cx + size // 3, cy), size // 3)
        pygame.draw.rect(screen, color, (cx - 1, cy, 2, size))
    elif suit == 'd':
        pygame.draw.polygon(screen, color,
                            [(cx, cy - size), (cx + size // 2, cy), (cx, cy + size), (cx - size // 2, cy)])


class PokerProjectile(Projectile):
    def __init__(self, x, y, vx, vy, damage, shooter, target, key_cards):
        super().__init__(x, y, vx, vy, damage, shooter, target, (255, 255, 255), 14)
        self.key_cards = key_cards

    def draw(self, screen):
        for i, card in enumerate(self.key_cards):
            offset_x = -i * 2
            offset_y = -i * 2
            cx = int(self.x) + offset_x
            cy = int(self.y) + offset_y

            card_rect = pygame.Rect(cx - 10, cy - 7, 20, 14)
            pygame.draw.rect(screen, (255, 255, 255), card_rect)
            pygame.draw.rect(screen, (0, 0, 0), card_rect, 1)

            value = card[:-1]
            suit = card[-1]
            tiny_font = pygame.font.Font(None, 10)
            suit_color = (0, 0, 0) if suit in ['a', 'c'] else (255, 0, 0)
            vt = tiny_font.render(value, True, suit_color)
            screen.blit(vt, (cx - 8, cy - 6))
            draw_suit_symbol(screen, suit, cx + 4, cy + 2, 4, suit_color)


class PokerMaster:
    def __init__(self, char):
        self.char = char
        self.deck = PokerDeck()
        self.cards = []
        self.key_cards = []
        self.hand_type = ""
        self.damage = 0
        self.mult = 1
        self.timer = 0
        self.cooldown = 0.8
        self.display_duration = 1.0
        self.attacking = False
        self.phase = 0
        self.show_idx = 0
        self.show_timer = 0
        self.merge_timer = 0
        self.fade_timer = 0
        self.pending = []
        self.has_static_target = False
        self.target_x = 0
        self.target_y = 0

    def update(self):
        if self.has_static_target:
            pass  # 有标靶就攻击
        elif not self.char.opponent or self.char.opponent.hp <= 0:
            return
        if self.attacking:
            self.timer -= 1 / 60
            if self.phase == 1:
                self.show_timer -= 1 / 60
                if self.show_timer <= 0 and self.show_idx < len(self.cards):
                    self.show_idx += 1
                    self.show_timer = 0.10
                if self.show_idx >= len(self.cards):
                    self.fade_timer -= 1 / 60
                    if self.fade_timer <= 0:
                        self.phase = 2
                        self.merge_timer = 0.3
            elif self.phase == 2:
                self.merge_timer -= 1 / 60
                if self.merge_timer <= 0:
                    self.phase = 3
                    self.fire()
            elif self.phase == 3 and self.timer <= 0:
                self.attacking = False
                self.phase = 0
                self.pending = []
        else:
            self.cooldown -= 1 / 60
            if self.cooldown <= 0:
                self.start()

    def start(self):
        if not self.has_static_target and (not self.char.opponent or self.char.opponent.hp <= 0):
            return
        self.attacking = True
        self.phase = 1
        self.timer = self.display_duration
        self.cooldown = 0.8
        self.cards = self.deck.draw(5, self.char.hp, self.char.max_hp)
        hand_type, base = self.deck.evaluate(self.cards)
        self.hand_type = hand_type
        self.mult = self.deck.multiplier(self.char.hp, self.char.max_hp)
        self.damage = base * self.mult
        self.key_cards = self.deck.get_key_cards(self.cards, hand_type)

        if self.mult >= 15:
            mult_text = f"{self.mult}!!!"
        elif self.mult >= 10:
            mult_text = f"{self.mult}!!"
        elif self.mult >= 5:
            mult_text = f"{self.mult}!"
        else:
            mult_text = str(self.mult)

        self.result = f"{hand_type}(x{mult_text})"
        self.show_idx = 0
        self.show_timer = 0.10
        self.fade_timer = 0.6

    def set_target(self, x, y):
        self.has_static_target = True
        self.target_x = x
        self.target_y = y

    def fire(self):
        if self.has_static_target:
            dx = self.target_x - self.char.x
            dy = self.target_y - self.char.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist > 0:
                vx = dx / dist * PROJECTILE_SPEED
                vy = dy / dist * PROJECTILE_SPEED
            else:
                vx, vy = PROJECTILE_SPEED, 0
            p = PokerProjectile(self.char.x, self.char.y, vx, vy, self.damage, self.char, None, self.key_cards)
            p.target_x = self.target_x
            p.target_y = self.target_y
            self.pending = [p]
            return

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
        p = PokerProjectile(self.char.x, self.char.y, vx, vy, self.damage, self.char, opp, self.key_cards)
        self.pending = [p]

    def get_projectiles(self):
        proj = self.pending[:]
        self.pending = []
        return proj

    def draw(self, screen, font):
        if not self.attacking:
            return
        x = self.char.x
        y = self.char.y - self.char.radius - 30
        card_y = y - 25

        if self.phase == 1 or self.phase == 2:
            if self.phase == 1:
                spacing = 30
                display_cards = self.cards
            else:
                progress = 1 - (self.merge_timer / 0.3)
                spacing = 30 * (1 - progress)
                # 合并阶段只显示关键牌，重新居中排列
                display_cards = [c for c in self.cards if c in self.key_cards]

            for i, c in enumerate(display_cards):
                if i >= self.show_idx and self.phase == 1:
                    continue
                is_key = c in self.key_cards

                cx = x - (len(display_cards) - 1) * spacing / 2 + i * spacing
                value = c[:-1]
                suit = c[-1]
                suit_color = (0, 0, 0) if suit in ['a', 'c'] else (255, 0, 0)

                if not is_key and self.phase == 1 and self.show_idx >= len(self.cards):
                    alpha = max(0, int(255 * (self.fade_timer / 0.6)))
                    if alpha <= 0:
                        continue
                    s = pygame.Surface((28, 20), pygame.SRCALPHA)
                    s.fill((255, 255, 255, alpha))
                    screen.blit(s, (cx - 5, card_y - 2))
                    pygame.draw.rect(screen, (0, 0, 0), (cx - 5, card_y - 2, 28, 20), 1)
                    tiny_font = pygame.font.Font(None, 14)
                    vt = tiny_font.render(value, True, suit_color)
                    screen.blit(vt, (cx - 2, card_y))
                    draw_suit_symbol(screen, suit, cx + 12, card_y + 4, 6, suit_color)
                    continue

                card_rect = pygame.Rect(cx - 6, card_y - 3, 30, 22)
                pygame.draw.rect(screen, (255, 255, 200), card_rect)
                pygame.draw.rect(screen, (255, 200, 0), card_rect, 2)

                tiny_font = pygame.font.Font(None, 14)
                vt = tiny_font.render(value, True, suit_color)
                screen.blit(vt, (cx - 2, card_y))
                draw_suit_symbol(screen, suit, cx + 12, card_y + 4, 6, suit_color)

        if self.show_idx >= len(self.cards):
            mf = pygame.font.Font(None, 18)
            t1 = mf.render(self.result, True, (255, 255, 0))
            text_y = y + 10
            screen.blit(t1, t1.get_rect(center=(x, text_y)))