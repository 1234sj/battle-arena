# D:\deeplearning\play\boxer\boxer.py
import math

import pygame


class Boxer:
    def __init__(self, char):
        self.char = char
        self.range = 115
        self.interval = 1.0 / 5
        self.timer = 0
        self.damage = 80
        self.total_dealt = 0
        self.speed_boosted = False

    def update(self):
        if not self.char.opponent or self.char.opponent.hp <= 0:
            return

        dx = self.char.opponent.x - self.char.x
        dy = self.char.opponent.y - self.char.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist <= self.range + self.char.opponent.radius:
            self.timer += 1 / 60
            if self.timer >= self.interval:
                self.timer = 0
                self.char.opponent.take_damage(self.damage)
                self.total_dealt += self.damage
                print(f"Boxer hit! Target HP: {self.char.opponent.hp}")  # 调试用
                if not self.speed_boosted and self.total_dealt >= 350:
                    self.speed_boosted = True
                    speed = math.sqrt(self.char.vx ** 2 + self.char.vy ** 2) * 2
                    if speed > 0:
                        angle = math.atan2(self.char.vy, self.char.vx)
                        self.char.vx = math.cos(angle) * speed
                        self.char.vy = math.sin(angle) * speed
                    print("Boxer speed boosted!")  # 调试用
        else:
            self.timer = 0

    def get_projectiles(self):
        return []

    def draw(self, screen, font):
        # 显示攻击范围
        pygame.draw.circle(screen, (100, 100, 100), (int(self.char.x), int(self.char.y)), self.range, 1)

        if self.speed_boosted:
            t = font.render("SPEED", True, (255, 255, 0))
            tr = t.get_rect(center=(self.char.x, self.char.y - self.char.radius - 20))
            screen.blit(t, tr)