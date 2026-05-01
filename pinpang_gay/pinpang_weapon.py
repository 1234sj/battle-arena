# D:\deeplearning\play\pinpang_gay\pinpang_weapon.py
import pygame
import math

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)


class PingPangBall:
    def __init__(self, x, y, vx, vy, owner, opponent):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = 8
        self.owner = owner
        self.opponent = opponent
        self.hit_count = 0
        self.max_hits = 3
        self.alive = True
        self.speed = math.sqrt(vx ** 2 + vy ** 2)

    def update(self, frame_rect):
        if not self.alive:
            return

        self.x += self.vx
        self.y += self.vy

        # Bounce off frame
        if self.x - self.radius < frame_rect.left:
            self.x = frame_rect.left + self.radius
            self.vx = abs(self.vx)
        elif self.x + self.radius > frame_rect.right:
            self.x = frame_rect.right - self.radius
            self.vx = -abs(self.vx)

        if self.y - self.radius < frame_rect.top:
            self.y = frame_rect.top + self.radius
            self.vy = abs(self.vy)
        elif self.y + self.radius > frame_rect.bottom:
            self.y = frame_rect.bottom - self.radius
            self.vy = -abs(self.vy)

        # Maintain speed
        current_speed = math.sqrt(self.vx ** 2 + self.vy ** 2)
        if current_speed > 0:
            self.vx = self.vx / current_speed * self.speed
            self.vy = self.vy / current_speed * self.speed

    def check_collision(self, target, push_out=False):
        """Check collision with a character"""
        dx = self.x - target.x
        dy = self.y - target.y
        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist < self.radius + target.radius:
            if push_out:
                overlap = self.radius + target.radius - dist
                if dist > 0:
                    nx = dx / dist
                    ny = dy / dist
                    self.x += nx * overlap
                    self.y += ny * overlap
            return True
        return False

    def reflect_towards_enemy(self):
        """Reflect ball towards opponent"""
        if not self.opponent or self.opponent.hp <= 0:
            self.vx = -self.vx
            self.vy = -self.vy
        else:
            dx = self.opponent.x - self.x
            dy = self.opponent.y - self.y
            dist = math.sqrt(dx ** 2 + dy ** 2)
            if dist > 0:
                self.vx = dx / dist * self.speed
                self.vy = dy / dist * self.speed
        self.hit_count = 0

    def reflect(self):
        """Simple reverse direction"""
        self.vx = -self.vx
        self.vy = -self.vy
        self.hit_count = 0

    def draw(self, screen):
        if not self.alive:
            return
        # Trail
        pygame.draw.circle(screen, (255, 255, 200), (int(self.x - self.vx * 0.5), int(self.y - self.vy * 0.5)),
                           self.radius // 2)
        # Ball
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 1)