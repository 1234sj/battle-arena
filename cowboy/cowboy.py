# D:\deeplearning\play\cowboy\cowboy.py
import pygame
from character import Projectile
import math

PROJECTILE_SPEED = 10


class Cowboy:
    def __init__(self, char):
        self.char = char
        self.v_range = 50
        self.interval = 1.0 / 6
        self.timer = 0
        self.bullets = 0
        self.max_bullets = 10
        self.rest = 1.5
        self.rest_timer = 0
        self.resting = False
        self.pending = []
        self.speed_boosted = False
        self.boost_timer = 0
        self.boost_duration = 3.0
        self.has_static_target = False
        self.target_x = 0
        self.target_y = 0

    def set_target(self, x, y):
        self.has_static_target = True
        self.target_x = x
        self.target_y = y

    def update(self):
        if not self.has_static_target and (not self.char.opponent or self.char.opponent.hp <= 0):
            return

        # Speed boost timer
        if self.speed_boosted:
            self.boost_timer -= 1 / 60
            if self.boost_timer <= 0:
                self.speed_boosted = False

        if self.resting:
            self.rest_timer -= 1 / 60
            if self.rest_timer <= 0:
                self.resting = False
                self.bullets = 0
            return

        # 标靶模式直接攻击
        if self.has_static_target:
            self.timer += 1 / 60
            if self.timer >= self.interval:
                self.timer = 0
                self.shoot()
            return

        # 对战模式检查范围
        dy = abs(self.char.opponent.y - self.char.y)
        if dy <= self.v_range:
            self.timer += 1 / 60
            if self.timer >= self.interval:
                self.timer = 0
                self.shoot()
        else:
            self.timer = 0

    def shoot(self):
        if self.has_static_target:
            dx = self.target_x - self.char.x
            dy = self.target_y - self.char.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist > 0:
                vx = dx / dist * PROJECTILE_SPEED
                vy = dy / dist * PROJECTILE_SPEED
            else:
                vx, vy = PROJECTILE_SPEED, 0
            p = Projectile(self.char.x, self.char.y, vx, vy, 50, self.char, self.char.opponent, (139, 69, 19), 4)
            p.target_x = self.target_x
            p.target_y = self.target_y
            self.pending.append(p)
            self.bullets += 1
            if self.bullets >= self.max_bullets:
                self.resting = True
                self.rest_timer = self.rest
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
            vx = PROJECTILE_SPEED
            vy = 0
        p = Projectile(self.char.x, self.char.y, vx, vy, 50, self.char, opp, (139, 69, 19), 4)
        self.pending.append(p)
        self.bullets += 1
        if self.bullets >= self.max_bullets:
            self.resting = True
            self.rest_timer = self.rest

    def get_projectiles(self):
        proj = self.pending[:]
        self.pending = []
        return proj

    def draw(self, screen, font):
        # 显示竖直攻击范围
        top = self.char.y - self.v_range
        bottom = self.char.y + self.v_range
        start_x = max(0, self.char.x - 40)
        end_x = min(screen.get_width(), self.char.x + 40)

        # 两条虚线
        for y in [top, bottom]:
            x = 0
            while x < screen.get_width():
                pygame.draw.line(screen, (100, 100, 100), (x, int(y)), (x + 20, int(y)), 1)
                x += 30

        # 竖线连接
        pygame.draw.line(screen, (100, 100, 100), (int(self.char.x), int(top)), (int(self.char.x), int(bottom)), 1)

        if self.resting:
            t = font.render("Reload", True, (255, 165, 0))
            tr = t.get_rect(center=(self.char.x, self.char.y - self.char.radius - 40))
            screen.blit(t, tr)