# D:\deeplearning\play\pinpang_gay\pinpang_gay.py
import pygame
import math
import random
from .pinpang_weapon import PingPangBall


class PinPangGay:
    def __init__(self, char):
        self.char = char
        self.ball = None
        self.spawn_delay = 0.5
        self.spawn_timer = 0
        self.need_new_ball = True
        self.ball_speed = 12
        self.has_hit_this_pass = False  # 加这行
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

        if self.need_new_ball and not (self.ball and self.ball.alive):
            self.spawn_timer += 1 / 60
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_timer = 0
                self.spawn_ball()
                self.need_new_ball = False

    def update_ball(self, frame_rect):
        if not self.ball or not self.ball.alive:
            return

        self.ball.update(frame_rect)

        # Reset opponent transparency
        if self.char.opponent:
            self.char.opponent.flash_timer -= 1 / 60 if hasattr(self.char.opponent,
                                                                'flash_timer') and self.char.opponent.flash_timer > 0 else 0

        # Check collision with opponent (pass through, no bounce)
        if self.ball.check_collision(self.char.opponent, push_out=False):
            if not self.has_hit_this_pass:
                self.char.opponent.take_damage(60)
                self.ball.hit_count += 1
                self.has_hit_this_pass = True
                # Make opponent slightly transparent
                self.char.opponent.flash_timer = 0.2
                if self.ball.hit_count >= self.ball.max_hits:
                    self.ball.alive = False
                    self.need_new_ball = True
        else:
            self.has_hit_this_pass = False

        # Check collision with owner (reflect towards enemy)
        if self.ball.check_collision(self.char, push_out=True):
            self.ball.reflect_towards_enemy()
            self.has_hit_this_pass = False

    def spawn_ball(self):
        if self.has_static_target:
            # 创建虚拟目标对象给乒乓球用
            class DummyTarget:
                def __init__(self, x, y, r):
                    self.x = x
                    self.y = y
                    self.hp = 999999
                    self.radius = r

            dummy = DummyTarget(self.target_x, self.target_y, 40)

            dx = self.target_x - self.char.x
            dy = self.target_y - self.char.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist > 0:
                vx = dx / dist * self.ball_speed
                vy = dy / dist * self.ball_speed
            else:
                angle = random.uniform(0, 2 * math.pi)
                vx = math.cos(angle) * self.ball_speed
                vy = math.sin(angle) * self.ball_speed
            self.ball = PingPangBall(self.char.x, self.char.y, vx, vy, self.char, dummy)
            return
        opp = self.char.opponent
        if not opp:
            return
        dx = opp.x - self.char.x
        dy = opp.y - self.char.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist > 0:
            vx = dx / dist * self.ball_speed
            vy = dy / dist * self.ball_speed
        else:
            angle = random.uniform(0, 2 * math.pi)
            vx = math.cos(angle) * self.ball_speed
            vy = math.sin(angle) * self.ball_speed
        self.ball = PingPangBall(self.char.x, self.char.y, vx, vy, self.char, self.char.opponent)

    def get_projectiles(self):
        return []

    def draw(self, screen, font):
        if self.ball and self.ball.alive:
            self.ball.draw(screen)