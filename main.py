# D:\deeplearning\play\main.py
import pygame
import sys
import random
import math
import json
import os
from config import *
from character import Character

pygame.init()

VERSION_FILE = os.path.join(os.path.dirname(__file__), "version.json")


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Battle Arena")
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)

        self.stats_file = os.path.join(os.path.dirname(__file__), "stats.json")
        self.stats = self.load_stats()

        frame_x = (WINDOW_WIDTH - FRAME_SIZE) // 2
        frame_y = (WINDOW_HEIGHT - FRAME_SIZE) // 2 + 30
        self.frame_rect = pygame.Rect(frame_x, frame_y, FRAME_SIZE, FRAME_SIZE)

        self.state = "select"
        self.selected_p = None
        self.selected_q = None
        self.ball_p = None
        self.ball_q = None
        self.projectiles = []
        self.winner = None
        self.winner_char = None
        self.over_delay = 3.0
        self.over_timer = 0

        self.back_button = pygame.Rect(WINDOW_WIDTH - 80, 65, 70, 30)
        self.game_mode = "battle"
        self.mode_button = pygame.Rect(50, WINDOW_HEIGHT - 60, 120, 30)

        # Target mode
        self.target_x = 0
        self.target_y = 0
        self.target_hp = 0
        self.target_radius = TARGET_RADIUS
        self.target_total_damage = 0
        self.target_damage_history = []
        self.game_timer = GAME_TIME
        self.target_debuff_level = 0
        self.target_debuff_timer = 0

        self.buttons = []
        self.create_buttons()

    def load_stats(self):
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {}

    def save_stats(self):
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def get_stats(self, char):
        if char not in self.stats:
            self.stats[char] = {"wins": 0, "total": 0}
        return self.stats[char]

    def record_win(self, char):
        if char not in self.stats:
            self.stats[char] = {"wins": 0, "total": 0}
        self.stats[char]["wins"] += 1
        self.stats[char]["total"] += 1

    def record_loss(self, char):
        if char not in self.stats:
            self.stats[char] = {"wins": 0, "total": 0}
        self.stats[char]["total"] += 1

    def create_buttons(self):
        btn_w = 220
        btn_h = 45
        start_x = WINDOW_WIDTH // 2 - btn_w // 2
        start_y = 220
        spacing = 55

        for i, char in enumerate(CHARACTERS):
            rect = pygame.Rect(start_x, start_y + i * spacing, btn_w, btn_h)
            self.buttons.append({
                'rect': rect,
                'char': char,
                'text': char.replace('_', ' ').title()
            })

    def create_ball(self, x, y, char_type, name):
        speed = BALL_SPEED
        angle = random.uniform(0, 2 * math.pi)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        return Character(x, y, BALL_RADIUS, char_type, name, vx, vy, BALL_HP)

    def reset_game(self):
        self.state = "select"
        self.selected_p = None
        self.selected_q = None
        self.ball_p = None
        self.ball_q = None
        self.projectiles = []
        self.target_total_damage = 0
        self.target_damage_history = []
        self.game_timer = GAME_TIME
        self.target_debuff_level = 0
        self.target_debuff_timer = 0

    def check_frame_collision(self, ball):
        speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)

        if ball.x - ball.radius < self.frame_rect.left:
            ball.x = self.frame_rect.left + ball.radius
            ball.vx = abs(ball.vx)
            current_speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)
            if current_speed > 0:
                ball.vx = ball.vx / current_speed * speed
        elif ball.x + ball.radius > self.frame_rect.right:
            ball.x = self.frame_rect.right - ball.radius
            ball.vx = -abs(ball.vx)
            current_speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)
            if current_speed > 0:
                ball.vx = ball.vx / current_speed * speed

        if ball.y - ball.radius < self.frame_rect.top:
            ball.y = self.frame_rect.top + ball.radius
            ball.vy = abs(ball.vy)
            current_speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)
            if current_speed > 0:
                ball.vy = ball.vy / current_speed * speed
        elif ball.y + ball.radius > self.frame_rect.bottom:
            ball.y = self.frame_rect.bottom - ball.radius
            ball.vy = -abs(ball.vy)
            current_speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)
            if current_speed > 0:
                ball.vy = ball.vy / current_speed * speed

    def check_ball_collision(self, b1, b2):
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist < b1.radius + b2.radius and dist > 0:
            overlap = b1.radius + b2.radius - dist
            nx = dx / dist
            ny = dy / dist
            b1.x -= overlap * nx / 2
            b1.y -= overlap * ny / 2
            b2.x += overlap * nx / 2
            b2.y += overlap * ny / 2

            speed1 = math.sqrt(b1.vx ** 2 + b1.vy ** 2)
            speed2 = math.sqrt(b2.vx ** 2 + b2.vy ** 2)

            dvx = b1.vx - b2.vx
            dvy = b1.vy - b2.vy
            dvn = dvx * nx + dvy * ny

            if dvn > 0:
                b1.vx -= dvn * nx
                b1.vy -= dvn * ny
                b2.vx += dvn * nx
                b2.vy += dvn * ny

                speed1_new = math.sqrt(b1.vx ** 2 + b1.vy ** 2)
                speed2_new = math.sqrt(b2.vx ** 2 + b2.vy ** 2)
                if speed1_new > 0:
                    b1.vx = b1.vx / speed1_new * speed1
                    b1.vy = b1.vy / speed1_new * speed1
                if speed2_new > 0:
                    b2.vx = b2.vx / speed2_new * speed2
                    b2.vy = b2.vy / speed2_new * speed2

    def check_ball_target_collision(self):
        if not self.ball_p:
            return
        dx = self.ball_p.x - self.target_x
        dy = self.ball_p.y - self.target_y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist < self.ball_p.radius + self.target_radius:
            nx = dx / dist if dist > 0 else 1
            ny = dy / dist if dist > 0 else 0
            speed = math.sqrt(self.ball_p.vx ** 2 + self.ball_p.vy ** 2)

            dvn = self.ball_p.vx * nx + self.ball_p.vy * ny
            self.ball_p.vx -= 2 * dvn * nx
            self.ball_p.vy -= 2 * dvn * ny

            new_speed = math.sqrt(self.ball_p.vx ** 2 + self.ball_p.vy ** 2)
            if new_speed > 0:
                self.ball_p.vx = self.ball_p.vx / new_speed * speed
                self.ball_p.vy = self.ball_p.vy / new_speed * speed

            overlap = self.ball_p.radius + self.target_radius - dist
            self.ball_p.x += nx * overlap
            self.ball_p.y += ny * overlap

    def draw_frame(self):
        pygame.draw.rect(self.screen, WHITE, self.frame_rect, 3)

    def draw_select_screen(self):
        self.screen.fill(BLACK)

        title = self.font_large.render("BATTLE ARENA", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        mode_name = "Battle" if self.game_mode == "battle" else "Target Practice"
        sub = self.font_medium.render(f"Mode: {mode_name}", True, CYAN)
        sub_rect = sub.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(sub, sub_rect)

        if self.game_mode == "target":
            if not self.selected_p:
                prompt = "Choose Character"
            else:
                prompt = "Press SPACE to Start"
        else:
            if not self.selected_p:
                prompt = "Choose P"
            elif not self.selected_q:
                prompt = "Choose Q"
            else:
                prompt = "Press SPACE to Start"

        prompt_text = self.font_medium.render(prompt, True, YELLOW)
        prompt_rect = prompt_text.get_rect(center=(WINDOW_WIDTH // 2, 170))
        self.screen.blit(prompt_text, prompt_rect)

        for btn in self.buttons:
            color = GRAY
            border = WHITE
            if self.selected_p == btn['char']:
                color = (0, 80, 200)
                border = BLUE
            elif self.selected_q == btn['char']:
                color = (200, 0, 0)
                border = RED

            if self.selected_p == btn['char'] or self.selected_q == btn['char']:
                pygame.draw.rect(self.screen, border, btn['rect'].inflate(4, 4))
            pygame.draw.rect(self.screen, color, btn['rect'])
            pygame.draw.rect(self.screen, border, btn['rect'], 2)

            text = self.font_small.render(btn['text'], True, WHITE)
            text_rect = text.get_rect(center=btn['rect'].center)
            self.screen.blit(text, text_rect)

        y = 480
        if self.selected_p:
            ps = self.get_stats(self.selected_p)
            wr = f"{ps['wins']}/{ps['total']}" if ps['total'] > 0 else "0/0"
            p_text = self.font_small.render(f"P: {self.selected_p.replace('_', ' ').title()} ({wr})", True, BLUE)
            self.screen.blit(p_text, (50, y))
        if self.selected_q and self.game_mode == "battle":
            qs = self.get_stats(self.selected_q)
            wr = f"{qs['wins']}/{qs['total']}" if qs['total'] > 0 else "0/0"
            q_text = self.font_small.render(f"Q: {self.selected_q.replace('_', ' ').title()} ({wr})", True, RED)
            self.screen.blit(q_text, (WINDOW_WIDTH - 350, y))

        stats_title = self.font_small.render("Win Rates:", True, WHITE)
        self.screen.blit(stats_title, (50, 550))
        for i, char in enumerate(CHARACTERS):
            s = self.get_stats(char)
            wr = f"{s['wins']}/{s['total']}" if s['total'] > 0 else "0/0"
            pct = f"{(s['wins'] / s['total'] * 100):.1f}%" if s['total'] > 0 else "N/A"
            line = self.font_tiny.render(f"{char.replace('_', ' ').title()}: {wr} ({pct})", True, GRAY)
            self.screen.blit(line, (50, 575 + i * 22))

        version = "1.0.0"
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE, 'r') as f:
                data = json.load(f)
                version = data.get('version', '1.0.0')
        ver_text = self.font_tiny.render(f"Version: {version}", True, (100, 100, 100))
        self.screen.blit(ver_text, (WINDOW_WIDTH - 120, WINDOW_HEIGHT - 25))

        mode_text = self.font_tiny.render(f"Mode: {'Battle' if self.game_mode == 'battle' else 'Target'}", True, WHITE)
        mode_rect = mode_text.get_rect(center=self.mode_button.center)
        pygame.draw.rect(self.screen, (80, 80, 80), self.mode_button)
        pygame.draw.rect(self.screen, WHITE, self.mode_button, 1)
        self.screen.blit(mode_text, mode_rect)

        pygame.display.flip()

    def start_game(self):
        margin = BALL_RADIUS + 10
        cx = self.frame_rect.centerx
        cy = self.frame_rect.centery

        if self.game_mode == "target":
            self.target_x = cx
            self.target_y = cy
            self.target_hp = TARGET_HP
            self.target_radius = TARGET_RADIUS
            self.target_total_damage = 0
            self.target_damage_history = [0]
            self.game_timer = GAME_TIME
            self.target_debuff_level = 0
            self.target_debuff_timer = 0
            self.selected_q = None

            while True:
                px = random.randint(self.frame_rect.left + margin, self.frame_rect.right - margin)
                py = random.randint(self.frame_rect.top + margin, self.frame_rect.bottom - margin)
                dist = math.sqrt((px - cx) ** 2 + (py - cy) ** 2)
                if dist > BALL_RADIUS + TARGET_RADIUS + 20:
                    break

            self.ball_p = self.create_ball(px, py, self.selected_p, "P")
            self.ball_p.opponent = None
            self.ball_p.color = BLUE
            self.ball_q = None

            if hasattr(self.ball_p, 'special') and self.ball_p.special:
                self.ball_p.special.set_target(cx, cy)
        else:
            px = random.randint(self.frame_rect.left + margin, cx - BALL_RADIUS)
            py = random.randint(self.frame_rect.top + margin, self.frame_rect.bottom - margin)

            qx = random.randint(cx + BALL_RADIUS, self.frame_rect.right - margin)
            qy = random.randint(self.frame_rect.top + margin, self.frame_rect.bottom - margin)

            self.ball_p = self.create_ball(px, py, self.selected_p, "P")
            self.ball_q = self.create_ball(qx, qy, self.selected_q, "Q")

            self.ball_p.opponent = self.ball_q
            self.ball_q.opponent = self.ball_p
            self.ball_p.color = BLUE
            self.ball_q.color = RED

        self.projectiles = []
        self.state = "playing"

    def check_target_hits(self):
        for p in self.projectiles[:]:
            dx = p.x - self.target_x
            dy = p.y - self.target_y
            if math.sqrt(dx ** 2 + dy ** 2) < self.target_radius + p.radius:
                self.target_total_damage += p.damage
                self.target_damage_history[-1] += p.damage

                if hasattr(p, 'shooter') and p.shooter and p.shooter.char_type == "tennis_winner" and p.shooter.special:
                    p.shooter.special.on_hit()

                if hasattr(p, 'is_syringe') and p.is_syringe:
                    self.target_debuff_level = min(3, self.target_debuff_level + 1)
                    self.target_debuff_timer = 6.0

                if p in self.projectiles:
                    self.projectiles.remove(p)

        if self.target_debuff_level > 0:
            self.target_debuff_timer -= 1 / 60
            if self.target_debuff_timer <= 0:
                self.target_debuff_level = 0
            else:
                damage_per_sec = {1: 25, 2: 30, 3: 40}
                self.target_total_damage += damage_per_sec[self.target_debuff_level] / 60
                self.target_damage_history[-1] += damage_per_sec[self.target_debuff_level] / 60

    def update(self):
        if self.state == "ending":
            self.over_timer -= 1 / 60
            if self.game_mode == "battle":
                if self.ball_p and self.ball_p.hp > 0:
                    self.ball_p.update()
                    self.check_frame_collision(self.ball_p)
                if self.ball_q and self.ball_q.hp > 0:
                    self.ball_q.update()
                    self.check_frame_collision(self.ball_q)
                if self.ball_p and self.ball_q and self.ball_p.hp > 0 and self.ball_q.hp > 0:
                    self.check_ball_collision(self.ball_p, self.ball_q)
            else:
                if self.ball_p:
                    self.ball_p.update()
                    self.check_frame_collision(self.ball_p)

            for p in self.projectiles[:]:
                p.update()
                if not self.is_in_frame(p, 100):
                    self.projectiles.remove(p)
            if self.game_mode == "target":
                self.check_target_hits()

            if self.over_timer <= 0:
                self.state = "over"
            return

        if self.state != "playing":
            return

        if self.game_mode == "target":
            self.game_timer -= 1 / 60
            if self.game_timer <= 0:
                self.state = "ending"
                self.over_timer = self.over_delay
                self.winner = "P"
                self.winner_char = self.selected_p
                self.ball_p.vx = 0
                self.ball_p.vy = 0
                return

            self.target_damage_history.append(0)
            if len(self.target_damage_history) > 60:
                self.target_damage_history.pop(0)

            self.ball_p.update()
            self.check_frame_collision(self.ball_p)
            self.check_ball_target_collision()

            if self.ball_p and self.ball_p.char_type == "pinpang_gay" and self.ball_p.special:
                self.ball_p.special.update_ball(self.frame_rect)

            for ball in [self.ball_p]:
                if ball and hasattr(ball, 'special') and ball.special:
                    projs = ball.special.get_projectiles()
                    self.projectiles.extend(projs)

            for p in self.projectiles[:]:
                p.update()
                if not self.is_in_frame(p, 100):
                    self.projectiles.remove(p)

            self.check_target_hits()
            return

        # Battle mode
        self.ball_p.update()
        self.ball_q.update()

        self.check_frame_collision(self.ball_p)
        self.check_frame_collision(self.ball_q)
        self.check_ball_collision(self.ball_p, self.ball_q)

        for ball in [self.ball_p, self.ball_q]:
            if ball and ball.char_type == "pinpang_gay" and ball.special:
                ball.special.update_ball(self.frame_rect)

        for ball in [self.ball_p, self.ball_q]:
            if ball and hasattr(ball, 'special') and ball.special:
                projs = ball.special.get_projectiles()
                self.projectiles.extend(projs)

        for p in self.projectiles[:]:
            p.update()
            if not self.is_in_frame(p, 100):
                self.projectiles.remove(p)

        self.check_hits()

        if self.ball_p.hp <= 0 or self.ball_q.hp <= 0:
            self.state = "ending"
            self.over_timer = self.over_delay
            if self.ball_p.hp <= 0:
                self.ball_p.vx = 0
                self.ball_p.vy = 0
                self.winner = "Q"
                self.winner_char = self.selected_q
                self.record_win(self.selected_q)
                self.record_loss(self.selected_p)
            else:
                self.ball_q.vx = 0
                self.ball_q.vy = 0
                self.winner = "P"
                self.winner_char = self.selected_p
                self.record_win(self.selected_p)
                self.record_loss(self.selected_q)
            self.save_stats()

    def is_in_frame(self, obj, margin=0):
        return (self.frame_rect.left - margin <= obj.x <= self.frame_rect.right + margin and
                self.frame_rect.top - margin <= obj.y <= self.frame_rect.bottom + margin)

    def check_hits(self):
        for p in self.projectiles[:]:
            target = p.target
            if target and target.hp > 0:
                dx = p.x - target.x
                dy = p.y - target.y
                if math.sqrt(dx ** 2 + dy ** 2) < target.radius + p.radius:
                    target.take_damage(p.damage, p)
                    if p in self.projectiles:
                        self.projectiles.remove(p)

    def draw_game(self):
        self.screen.fill(BLACK)
        self.draw_frame()

        if self.game_mode == "target":
            pygame.draw.circle(self.screen, (200, 200, 200), (int(self.target_x), int(self.target_y)),
                               self.target_radius)
            pygame.draw.circle(self.screen, WHITE, (int(self.target_x), int(self.target_y)), self.target_radius, 3)
            pygame.draw.circle(self.screen, RED, (int(self.target_x), int(self.target_y)), 10)

            timer_text = self.font_medium.render(f"Time: {int(max(0, self.game_timer))}s", True, WHITE)
            self.screen.blit(timer_text, (20, 100))
            dmg_text = self.font_small.render(f"Total: {int(self.target_total_damage)}", True, WHITE)
            self.screen.blit(dmg_text, (20, 140))
            dps = sum(self.target_damage_history) / max(1, len(self.target_damage_history))
            dps_text = self.font_small.render(f"DPS: {int(dps)}", True, YELLOW)
            self.screen.blit(dps_text, (20, 170))

        if self.ball_p:
            self.ball_p.draw(self.screen, self.font_small)
        if self.ball_q:
            self.ball_q.draw(self.screen, self.font_small)

        for p in self.projectiles:
            p.draw(self.screen)

        if self.game_mode == "battle":
            self.draw_hp_bars()

        pygame.draw.rect(self.screen, (80, 80, 80), self.back_button)
        pygame.draw.rect(self.screen, WHITE, self.back_button, 1)
        back_text = self.font_tiny.render("Back", True, WHITE)
        tr = back_text.get_rect(center=self.back_button.center)
        self.screen.blit(back_text, tr)

        pygame.display.flip()

    def draw_hp_bars(self):
        bw = 200
        bh = 18
        by = 20

        for ball, side in [(self.ball_p, "left"), (self.ball_q, "right")]:
            ratio = max(0, ball.hp / BALL_HP)
            if side == "left":
                bx = 20
            else:
                bx = WINDOW_WIDTH - 20 - bw

            pygame.draw.rect(self.screen, (50, 50, 50), (bx, by, bw, bh))
            pygame.draw.rect(self.screen, RED, (bx, by, bw, bh))
            if ratio > 0:
                pygame.draw.rect(self.screen, GREEN, (bx, by, int(bw * ratio), bh))
            pygame.draw.rect(self.screen, WHITE, (bx, by, bw, bh), 1)

            name = ball.char_type.replace('_', ' ').title()
            txt = self.font_tiny.render(f"{name}: {int(ball.hp)}/{BALL_HP}", True, WHITE)
            self.screen.blit(txt, (bx, by + bh + 3))

    def draw_over_screen(self):
        self.screen.fill(BLACK)
        self.draw_frame()

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        if self.game_mode == "target":
            win_text = self.font_large.render(f"Time's Up!", True, YELLOW)
        else:
            win_text = self.font_large.render(f"{self.winner} WINS!", True, YELLOW)
        wr = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.screen.blit(win_text, wr)

        char_text = self.font_medium.render(self.winner_char.replace('_', ' ').title(), True, WHITE)
        cr = char_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 15))
        self.screen.blit(char_text, cr)

        if self.game_mode == "target":
            dmg_text = self.font_small.render(f"Total Damage: {int(self.target_total_damage)}", True, CYAN)
            dr = dmg_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))
            self.screen.blit(dmg_text, dr)

        r_text = self.font_medium.render("Press R to Restart", True, GREEN)
        rr = r_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
        self.screen.blit(r_text, rr)

        q_text = self.font_small.render("Press Q to Quit", True, GRAY)
        qr = q_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 105))
        self.screen.blit(q_text, qr)

        pygame.display.flip()

    def handle_select_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                if self.selected_q:
                    self.selected_q = None
                elif self.selected_p:
                    self.selected_p = None
                return

            if event.button == 1:
                if self.mode_button.collidepoint(event.pos):
                    self.game_mode = "target" if self.game_mode == "battle" else "battle"
                    self.selected_q = None
                    return

                for btn in self.buttons:
                    if btn['rect'].collidepoint(event.pos):
                        if not self.selected_p:
                            self.selected_p = btn['char']
                        elif not self.selected_q:
                            self.selected_q = btn['char']
                        break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.game_mode == "target" and self.selected_p:
                    self.start_game()
                elif self.game_mode == "battle" and self.selected_p and self.selected_q:
                    self.start_game()
            elif event.key == pygame.K_ESCAPE:
                if self.selected_q:
                    self.selected_q = None
                elif self.selected_p:
                    self.selected_p = None

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == "select":
                    self.handle_select_event(event)
                elif self.state in ["playing", "ending"]:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if self.back_button.collidepoint(event.pos):
                            self.reset_game()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.reset_game()
                elif self.state == "over":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.reset_game()
                        elif event.key == pygame.K_q:
                            running = False

            if self.state == "select":
                self.draw_select_screen()
            elif self.state == "playing":
                self.update()
                self.draw_game()
            elif self.state == "ending":
                self.update()
                self.draw_game()
            elif self.state == "over":
                self.draw_over_screen()

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()