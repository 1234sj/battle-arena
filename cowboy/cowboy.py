# D:\deeplearning\play\cowboy\cowboy.py
from character import Projectile

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

    def update(self):
        if not self.char.opponent or self.char.opponent.hp <= 0:
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

        dy = abs(self.char.opponent.y - self.char.y)
        if dy <= self.v_range:
            self.timer += 1 / 60
            if self.timer >= self.interval:
                self.timer = 0
                self.shoot()
        else:
            self.timer = 0

    def shoot(self):
        opp = self.char.opponent
        if not opp:
            return
        dx = opp.x - self.char.x
        direction = 1 if dx > 0 else -1
        p = Projectile(
            self.char.x + direction * self.char.radius,
            self.char.y,
            direction * PROJECTILE_SPEED,
            0,
            75,
            self.char,
            opp,
            (139, 69, 19),
            4
        )
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
        if self.resting:
            t = font.render("Reload", True, (255, 165, 0))
            tr = t.get_rect(center=(self.char.x, self.char.y - self.char.radius - 40))
            screen.blit(t, tr)