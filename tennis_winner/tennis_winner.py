# D:\deeplearning\play\tennis_winner\tennis_winner.py
import math
from character import Projectile

PROJECTILE_SPEED = 13


class TennisWinner:
    def __init__(self, char):
        self.char = char
        self.interval = 1.8
        self.timer = 0
        self.swing_before = 0.1
        self.swing_after = 0.1
        self.is_swinging = False
        self.swing_phase = None
        self.swing_timer = 0
        self.pending = []

    def update(self):
        if not self.char.opponent or self.char.opponent.hp <= 0:
            return

        if self.is_swinging:
            self.swing_timer -= 1 / 60
            if self.swing_phase == 'before' and self.swing_timer <= 0:
                self.swing_phase = 'after'
                self.swing_timer = self.swing_after
                self.fire()
                self.char.is_swinging = True
            elif self.swing_phase == 'after' and self.swing_timer <= 0:
                self.is_swinging = False
                self.swing_phase = None
                self.char.is_swinging = False
        else:
            self.timer += 1 / 60
            if self.timer >= self.interval:
                self.timer = 0
                self.is_swinging = True
                self.swing_phase = 'before'
                self.swing_timer = self.swing_before
                self.char.is_swinging = True

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
        p = Projectile(self.char.x, self.char.y, vx, vy, 115, self.char, opp, (0, 255, 0), 6)
        self.pending.append(p)

    def reflect(self, projectile):
        projectile.vx = -projectile.vx
        projectile.vy = -projectile.vy
        projectile.shooter = self.char
        projectile.target = self.char.opponent
        projectile.color = (255, 0, 255)

    def get_projectiles(self):
        proj = self.pending[:]
        self.pending = []
        return proj

    def draw(self, screen, font):
        if self.is_swinging:
            phase_txt = "SWING" if self.swing_phase == 'before' else "HIT!"
            color = (255, 255, 0) if self.swing_phase == 'before' else (255, 165, 0)
            t = font.render(phase_txt, True, color)
            screen.blit(t, t.get_rect(center=(self.char.x, self.char.y - self.char.radius - 30)))