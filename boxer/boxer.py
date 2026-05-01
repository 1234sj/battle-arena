# D:\deeplearning\play\boxer\boxer.py
import math
import pygame


class Boxer:
    def __init__(self, char):
        self.char = char
        self.range = 100
        self.interval = 1.0 / 4
        self.timer = 0
        self.damage = 40
        self.total_dealt = 0
        self.speed_boosted = False
        self.boost_timer = 0
        self.boost_duration = 3.0
        self.boost_cooldown = 0
        self.boost_cooldown_duration = 4.0
        # 范围线透明度，0-255可调节
        self.range_alpha = 80

    def set_target(self, x, y):
        pass  # Boxer是近战，标靶模式不适用

    def update(self):
        if not self.char.opponent or self.char.opponent.hp <= 0:
            return

        # Boost cooldown
        if self.boost_cooldown > 0:
            self.boost_cooldown -= 1 / 60

        # Speed boost timer
        if self.speed_boosted:
            self.boost_timer -= 1 / 60
            if self.boost_timer <= 0:
                # Boost结束，进入冷却
                self.speed_boosted = False
                self.boost_cooldown = self.boost_cooldown_duration
                self.total_dealt = 0
                # 恢复原速度
                speed = math.sqrt(self.char.vx ** 2 + self.char.vy ** 2) / 2
                if speed > 0:
                    angle = math.atan2(self.char.vy, self.char.vx)
                    self.char.vx = math.cos(angle) * speed
                    self.char.vy = math.sin(angle) * speed

        # Attack
        dx = self.char.opponent.x - self.char.x
        dy = self.char.opponent.y - self.char.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        # 加速时范围1.5倍
        current_range = self.range * 1.5 if self.speed_boosted else self.range

        if dist <= current_range + self.char.opponent.radius:
            self.timer += 1 / 60
            if self.timer >= self.interval:
                self.timer = 0
                self.char.opponent.take_damage(self.damage)

                # 只在非冷却期间累计加速伤害
                if not self.speed_boosted and self.boost_cooldown <= 0:
                    self.total_dealt += self.damage
                    if self.total_dealt >= 300:
                        self.speed_boosted = True
                        self.boost_timer = self.boost_duration
                        # 速度翻倍
                        speed = math.sqrt(self.char.vx ** 2 + self.char.vy ** 2) * 2
                        if speed > 0:
                            angle = math.atan2(self.char.vy, self.char.vx)
                            self.char.vx = math.cos(angle) * speed
                            self.char.vy = math.sin(angle) * speed
        else:
            self.timer = 0

    def get_projectiles(self):
        return []

    def draw(self, screen, font):
        # 加速时范围线红色，否则灰色
        if self.speed_boosted:
            line_color = (255, 0, 0, self.range_alpha)
            current_range = int(self.range * 1.2)
        else:
            line_color = (100, 100, 100, self.range_alpha)
            current_range = self.range

        # 绘制半透明范围圈
        range_surface = pygame.Surface((current_range * 2, current_range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, line_color, (current_range, current_range), current_range, 1)
        screen.blit(range_surface, (int(self.char.x) - current_range, int(self.char.y) - current_range))

        # 状态显示
        if self.speed_boosted:
            t = font.render("SPEED", True, (255, 255, 0))
            tr = t.get_rect(center=(self.char.x, self.char.y - self.char.radius - 20))
            screen.blit(t, tr)
        elif self.boost_cooldown > 0:
            t = font.render(f"CD:{self.boost_cooldown:.1f}", True, (128, 128, 128))
            tr = t.get_rect(center=(self.char.x, self.char.y - self.char.radius - 20))
            screen.blit(t, tr)