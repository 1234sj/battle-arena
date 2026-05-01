# D:\deeplearning\play\tennis_winner\tennis_winner.py
import math
import random
from character import Projectile

PROJECTILE_SPEED = 7.5


class TennisWinner:
    def __init__(self, char):
        self.char = char
        self.interval = 1.5
        self.timer = 0
        self.swing_before = 0.1
        self.swing_after = 0.1
        self.is_swinging = False
        self.swing_phase = None
        self.swing_timer = 0
        self.pending = []
        self.has_static_target = False
        self.target_x = 0
        self.target_y = 0

        # Crit system
        self.base_crit = 0.10
        self.crit_rate = 0.10
        self.crit_per_hit = 0.15
        self.attack_mult = 1.0
        self.base_damage = 140

    def set_target(self, x, y):
        self.has_static_target = True
        self.target_x = x
        self.target_y = y

    def update(self):
        if not self.has_static_target and (not self.char.opponent or self.char.opponent.hp <= 0):
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

    def calc_damage(self):
        """Calculate damage with crit"""
        is_crit = random.random() < self.crit_rate

        if is_crit:
            crit_mult = random.uniform(1.9, 2.4)
            damage = int(self.base_damage * self.attack_mult * crit_mult)
        else:
            damage = int(self.base_damage * self.attack_mult)

        return damage, is_crit

    def on_hit(self):
        """Increase crit rate on hit, convert overflow to attack"""
        self.crit_rate += self.crit_per_hit
        if self.crit_rate > 1.0:
            overflow = self.crit_rate - 1.0
            self.attack_mult += overflow * 0.5   # 改成 += 累加
            self.crit_rate = 1.0

    def fire(self):
        damage, is_crit = self.calc_damage()
        color = (255, 0, 0) if is_crit else (0, 255, 0)
        radius = 8 if is_crit else 6

        if self.has_static_target:
            dx = self.target_x - self.char.x
            dy = self.target_y - self.char.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist > 0:
                vx = dx / dist * PROJECTILE_SPEED
                vy = dy / dist * PROJECTILE_SPEED
            else:
                vx, vy = PROJECTILE_SPEED, 0

            p = Projectile(self.char.x, self.char.y, vx, vy, damage, self.char, self.char.opponent, color, radius)
            p.target_x = self.target_x
            p.target_y = self.target_y
            p.is_crit = is_crit
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

        p = Projectile(self.char.x, self.char.y, vx, vy, damage, self.char, opp, color, radius)
        p.is_crit = is_crit
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

        # Show crit rate and attack multiplier
        crit_text = font.render(f"CRT:{int(self.crit_rate * 100)}% ATK:x{self.attack_mult:.1f}", True, (255, 200, 0))
        tr = crit_text.get_rect(center=(self.char.x, self.char.y - self.char.radius - 50))
        screen.blit(crit_text, tr)