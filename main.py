# D:\deeplearning\play\main.py
import pygame
import sys
import random
import math
import json
import os
from config import *
from character import Character
import updater

pygame.init()

def check_for_updates():
    try:
        import updater
        if updater.check_and_update():
            # 更新完成后重启游戏
            print("Update installed! Please restart the game.")
    except Exception as e:
        print(f"Update check failed: {e}")


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Battle Arena")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)

        # Stats file
        self.stats_file = os.path.join(os.path.dirname(__file__), "stats.json")
        self.stats = self.load_stats()

        # Frame
        frame_x = (WINDOW_WIDTH - FRAME_SIZE) // 2
        frame_y = (WINDOW_HEIGHT - FRAME_SIZE) // 2 + 30
        self.frame_rect = pygame.Rect(frame_x, frame_y, FRAME_SIZE, FRAME_SIZE)

        # Game state
        self.state = "select"  # select, playing, over
        self.selected_p = None
        self.selected_q = None
        self.ball_p = None
        self.ball_q = None
        self.projectiles = []
        self.winner = None
        self.winner_char = None

        # Buttons
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

    def check_frame_collision(self, ball):
        """Collision with frame - only velocity direction changes, speed stays same"""
        speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)

        if ball.x - ball.radius < self.frame_rect.left:
            ball.x = self.frame_rect.left + ball.radius
            ball.vx = abs(ball.vx)
            # Maintain speed
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
        """Ball collision - speed preserved, only direction changes"""
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        dist = math.sqrt(dx ** 2 + dy ** 2)

        if dist < b1.radius + b2.radius and dist > 0:
            # Separate balls
            overlap = b1.radius + b2.radius - dist
            nx = dx / dist
            ny = dy / dist
            b1.x -= overlap * nx / 2
            b1.y -= overlap * ny / 2
            b2.x += overlap * nx / 2
            b2.y += overlap * ny / 2

            # Save speeds
            speed1 = math.sqrt(b1.vx ** 2 + b1.vy ** 2)
            speed2 = math.sqrt(b2.vx ** 2 + b2.vy ** 2)

            # Elastic collision
            dvx = b1.vx - b2.vx
            dvy = b1.vy - b2.vy
            dvn = dvx * nx + dvy * ny

            if dvn > 0:
                b1.vx -= dvn * nx
                b1.vy -= dvn * ny
                b2.vx += dvn * nx
                b2.vy += dvn * ny

                # Restore original speeds
                speed1_new = math.sqrt(b1.vx ** 2 + b1.vy ** 2)
                speed2_new = math.sqrt(b2.vx ** 2 + b2.vy ** 2)
                if speed1_new > 0:
                    b1.vx = b1.vx / speed1_new * speed1
                    b1.vy = b1.vy / speed1_new * speed1
                if speed2_new > 0:
                    b2.vx = b2.vx / speed2_new * speed2
                    b2.vy = b2.vy / speed2_new * speed2

    def draw_frame(self):
        pygame.draw.rect(self.screen, WHITE, self.frame_rect, 3)

    def draw_select_screen(self):
        self.screen.fill(BLACK)

        title = self.font_large.render("BATTLE ARENA", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        sub = self.font_medium.render("Select P and Q", True, CYAN)
        sub_rect = sub.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(sub, sub_rect)

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

        # Show selected
        y = 480
        if self.selected_p:
            ps = self.get_stats(self.selected_p)
            wr = f"{ps['wins']}/{ps['total']}" if ps['total'] > 0 else "0/0"
            p_text = self.font_small.render(f"P: {self.selected_p.replace('_', ' ').title()} ({wr})", True, BLUE)
            self.screen.blit(p_text, (50, y))
        if self.selected_q:
            qs = self.get_stats(self.selected_q)
            wr = f"{qs['wins']}/{qs['total']}" if qs['total'] > 0 else "0/0"
            q_text = self.font_small.render(f"Q: {self.selected_q.replace('_', ' ').title()} ({wr})", True, RED)
            self.screen.blit(q_text, (WINDOW_WIDTH - 350, y))

        # Stats table
        stats_title = self.font_small.render("Win Rates:", True, WHITE)
        self.screen.blit(stats_title, (50, 550))
        for i, char in enumerate(CHARACTERS):
            s = self.get_stats(char)
            wr = f"{s['wins']}/{s['total']}" if s['total'] > 0 else "0/0"
            pct = f"{(s['wins'] / s['total'] * 100):.1f}%" if s['total'] > 0 else "N/A"
            line = self.font_tiny.render(f"{char.replace('_', ' ').title()}: {wr} ({pct})", True, GRAY)
            self.screen.blit(line, (50, 575 + i * 22))

        pygame.display.flip()

    def start_game(self):
        margin = BALL_RADIUS + 10
        cx = self.frame_rect.centerx

        # P spawns in left half
        px = random.randint(self.frame_rect.left + margin, cx - BALL_RADIUS)
        py = random.randint(self.frame_rect.top + margin, self.frame_rect.bottom - margin)

        # Q spawns in right half
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

    def update(self):
        if self.state != "playing":
            return

        self.ball_p.update()
        self.ball_q.update()

        self.check_frame_collision(self.ball_p)
        self.check_frame_collision(self.ball_q)
        self.check_ball_collision(self.ball_p, self.ball_q)

        # Collect projectiles
        for ball in [self.ball_p, self.ball_q]:
            if hasattr(ball, 'special'):
                projs = ball.special.get_projectiles()
                self.projectiles.extend(projs)

        # Update projectiles
        for p in self.projectiles[:]:
            p.update()
            if not self.is_in_frame(p, 100):
                self.projectiles.remove(p)

        # Check projectile hits
        self.check_hits()

        # Check game over
        if self.ball_p.hp <= 0:
            self.game_over("Q")
        elif self.ball_q.hp <= 0:
            self.game_over("P")

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

    def game_over(self, winner):
        self.state = "over"
        self.winner = winner
        if winner == "P":
            self.winner_char = self.selected_p
            self.record_win(self.selected_p)
            self.record_loss(self.selected_q)
        else:
            self.winner_char = self.selected_q
            self.record_win(self.selected_q)
            self.record_loss(self.selected_p)
        self.save_stats()

    def draw_game(self):
        self.screen.fill(BLACK)
        self.draw_frame()

        self.ball_p.draw(self.screen, self.font_small)
        self.ball_q.draw(self.screen, self.font_small)

        for p in self.projectiles:
            p.draw(self.screen)

        self.draw_hp_bars()
        pygame.display.flip()

    def draw_hp_bars(self):
        bw = 200
        bh = 18
        by = 20

        for ball, label, side in [(self.ball_p, "P", "left"), (self.ball_q, "Q", "right")]:
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
            txt = self.font_tiny.render(f"{name}: {ball.hp}/{BALL_HP}", True, WHITE)
            self.screen.blit(txt, (bx, by + bh + 3))

    def draw_over_screen(self):
        self.screen.fill(BLACK)
        self.draw_frame()

        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        win_text = self.font_large.render(f"{self.winner} WINS!", True, YELLOW)
        wr = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 60))
        self.screen.blit(win_text, wr)

        char_text = self.font_medium.render(self.winner_char.replace('_', ' ').title(), True, WHITE)
        cr = char_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 15))
        self.screen.blit(char_text, cr)

        s = self.get_stats(self.winner_char)
        wr_text = self.font_small.render(f"Record: {s['wins']}/{s['total']}", True, CYAN)
        wr_rect = wr_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))
        self.screen.blit(wr_text, wr_rect)

        r_text = self.font_medium.render("Press R to Restart", True, GREEN)
        rr = r_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
        self.screen.blit(r_text, rr)

        q_text = self.font_small.render("Press Q to Quit", True, GRAY)
        qr = q_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 105))
        self.screen.blit(q_text, qr)

        pygame.display.flip()

    def handle_select_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for btn in self.buttons:
                if btn['rect'].collidepoint(event.pos):
                    if not self.selected_p:
                        self.selected_p = btn['char']
                    elif not self.selected_q and btn['char'] != self.selected_p:
                        self.selected_q = btn['char']

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.selected_p and self.selected_q:
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
                elif self.state == "over":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.state = "select"
                            self.selected_p = None
                            self.selected_q = None
                            self.ball_p = None
                            self.ball_q = None
                            self.projectiles = []
                        elif event.key == pygame.K_q:
                            running = False

            if self.state == "select":
                self.draw_select_screen()
            elif self.state == "playing":
                self.update()
                self.draw_game()
            elif self.state == "over":
                self.draw_over_screen()

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    check_for_updates()  # 启动时检查更新
    game = Game()
    game.run()