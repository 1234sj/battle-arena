# D:\deeplearning\play\character.py
import pygame
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


class Projectile:
    def __init__(self, x, y, vx, vy, damage, shooter, target, color=YELLOW, radius=5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.shooter = shooter
        self.target = target
        self.color = color
        self.radius = radius
        self.is_syringe = False

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius // 2)


class Character:
    def __init__(self, x, y, radius, char_type, name, vx, vy, hp):
        self.x = x
        self.y = y
        self.radius = radius
        self.char_type = char_type
        self.name = name
        self.vx = vx
        self.vy = vy
        self.hp = hp
        self.max_hp = hp
        self.opponent = None
        self.color = BLUE if name == "P" else RED
        self.damage_texts = []

        self.special = None

        # Debuff system
        self.debuff_level = 0
        self.debuff_timer = 0
        self.original_speed = None

        self.init_special()

    def init_special(self):
        if self.char_type == "poker_master":
            from poker_master.poker_master import PokerMaster
            self.special = PokerMaster(self)
        elif self.char_type == "boxer":
            from boxer.boxer import Boxer
            self.special = Boxer(self)
        elif self.char_type == "cowboy":
            from cowboy.cowboy import Cowboy
            self.special = Cowboy(self)
        elif self.char_type == "tennis_winner":
            from tennis_winner.tennis_winner import TennisWinner
            self.special = TennisWinner(self)
        elif self.char_type == "baddoctor":
            from baddoctor.baddoctor import BadDoctor
            self.special = BadDoctor(self)

    def update(self):
        self.x += self.vx
        self.y += self.vy

        if self.special:
            self.special.update()

        # Update debuff
        self.update_debuff()

        for dt in self.damage_texts[:]:
            dt['timer'] -= 1 / 60
            dt['y'] -= 1
            if dt['timer'] <= 0:
                self.damage_texts.remove(dt)

    def update_debuff(self):
        if self.debuff_level > 0:
            self.debuff_timer -= 1 / 60
            if self.debuff_timer <= 0:
                self.remove_debuff()
            else:
                damage_per_sec = {1: 10, 2: 15, 3: 24}
                self.hp -= damage_per_sec[self.debuff_level] / 60
                if self.hp < 0:
                    self.hp = 0

    def apply_debuff(self):
        if self.debuff_level < 3:
            self.debuff_level += 1
            if self.debuff_level == 1:
                speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
                self.original_speed = speed
                self.set_speed(speed * 0.8)

        if self.debuff_level < 3:
            self.debuff_timer = 6.0
        elif self.debuff_level == 3:
            self.debuff_timer = 6.0

    def remove_debuff(self):
        self.debuff_level = 0
        self.debuff_timer = 0
        if self.original_speed is not None:
            self.set_speed(self.original_speed)
            self.original_speed = None

    def set_speed(self, speed):
        current_speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if current_speed > 0:
            self.vx = self.vx / current_speed * speed
            self.vy = self.vy / current_speed * speed

    def take_damage(self, damage, projectile=None):
        # Check for syringe debuff
        if projectile and hasattr(projectile, 'is_syringe') and projectile.is_syringe:
            self.apply_debuff()

        if self.char_type == "tennis_winner" and self.special and self.special.is_swinging and projectile:
            self.special.reflect(projectile)
            return

        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

        self.damage_texts.append({
            'damage': damage,
            'x': self.x,
            'y': self.y - self.radius - 20,
            'timer': 1.0,
            'color': RED if damage > 100 else YELLOW
        })

    def draw(self, screen, font):
        # Glow for boxer speed boost
        if self.char_type == "boxer" and self.special and self.special.speed_boosted:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius + 5, 2)

        # Ball
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 2)

        # Name
        text = font.render(self.name, True, WHITE)
        tr = text.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(text, tr)

        # Damage texts
        tiny_font = pygame.font.Font(None, 20)
        for dt in self.damage_texts:
            txt = tiny_font.render(f"-{dt['damage']}", True, dt['color'])
            tr = txt.get_rect(center=(dt['x'], dt['y']))
            screen.blit(txt, tr)

        # Debuff display
        if self.debuff_level > 0:
            debuff_text = font.render(f"DEBUFF Lv{self.debuff_level}", True, (255, 0, 255))
            tr = debuff_text.get_rect(center=(self.x, self.y - self.radius - 50))
            screen.blit(debuff_text, tr)

        # Special draw
        if self.special:
            self.special.draw(screen, font)