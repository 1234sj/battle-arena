# D:\deeplearning\play\baddoctor\baddoctor.py
import math
from character import Projectile

PROJECTILE_SPEED = 12


class BadDoctor:
    def __init__(self, char):
        self.char = char
        self.interval = 1.4
        self.timer = 0
        self.pending = []
        self.has_static_target = False
        self.target_x = 0
        self.target_y = 0

    def set_target(self, x, y):
        self.has_static_target = True
        self.target_x = x
        self.target_y = y

    def update(self):
        if self.has_static_target:
            pass  # 有标靶继续执行
        if not self.has_static_target and (not self.char.opponent or self.char.opponent.hp <= 0):
            return

        # Update debuff on target
        if hasattr(self.char.opponent, 'debuff'):
            self.char.opponent.update_debuff()

        # Attack timer
        self.timer += 1 / 60
        if self.timer >= self.interval:
            self.timer = 0
            self.fire()

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
            p = Projectile(self.char.x, self.char.y, vx, vy, 60, self.char, self.char.opponent, (0, 255, 255), 6)
            p.target_x = self.target_x
            p.target_y = self.target_y
            self.pending.append(p)
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
        p = Projectile(self.char.x, self.char.y, vx, vy, 60, self.char, opp, (0, 255, 255), 6)
        p.is_syringe = True
        self.pending.append(p)

    def get_projectiles(self):
        proj = self.pending[:]
        self.pending = []
        return proj

    def draw(self, screen, font):
        pass