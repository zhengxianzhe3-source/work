import pygame
import sys
import math
import random

# 1. 게임 초기화
pygame.init()
pygame.font.init()

# 화면 설정
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The 13th Path")
clock = pygame.time.Clock()

# 색상 정의
BLACK = (15, 15, 15)
WHITE = (240, 240, 240)
RED = (220, 50, 50)
GOLD = (235, 180, 50)
GRAY = (80, 80, 80)

# 💡 [해결 책] 시스템 폰트 대기 현상을 막기 위해 pygame 기본 기본 폰트(None)로 변경
FONT_LARGE = pygame.font.SysFont(None, 50)
FONT_MID = pygame.font.SysFont(None, 36)
FONT_SMALL = pygame.font.SysFont(None, 24)

# 2. 난이도 및 게임 상태 설정
DIFFICULTIES = {
    "Normal": {"life_drain_multiplier": 1.0, "boss_hp_multiplier": 1.0, "boss_speed_multiplier": 1.0},
    "Hard": {"life_drain_multiplier": 1.5, "boss_hp_multiplier": 1.3, "boss_speed_multiplier": 1.3},
    "Very Hard": {"life_drain_multiplier": 2.5, "boss_hp_multiplier": 1.8, "boss_speed_multiplier": 1.7},
    "Hell": {"life_drain_multiplier": 5.0, "boss_hp_multiplier": 2.5, "boss_speed_multiplier": 2.2},
    "Loop": {"life_drain_multiplier": 10.0, "boss_hp_multiplier": 4.0, "boss_speed_multiplier": 3.0}
}

class GameState:
    def __init__(self):
        self.mode = "MENU"  # MENU, PLAYING, GAME_OVER, VICTORY
        self.selected_difficulty = "Normal"
        
        # 라이프 설정 (초기값: 33,550,336)
        self.max_life = 33550336
        self.current_life = float(self.max_life)
        self.base_drain_per_second = 12.0
        
        # 보스 진행도 (총 13명)
        self.current_boss_index = 1
        self.total_bosses = 13
        self.boss_hp = 100.0
        self.boss_max_hp = 100.0
        
        # 보스 위치 및 이동 관련 변수
        self.boss_width = 300
        self.boss_height = 200
        self.boss_x = float(WIDTH // 2 - self.boss_width // 2)
        self.boss_y = 200
        self.boss_direction = 1  # 1: 오른쪽, -1: 왼쪽
        self.boss_base_speed = 150.0
        
        # 시간 추적
        self.elapsed_seconds = 0.0
        
    def start_game(self, difficulty):
        self.selected_difficulty = difficulty
        self.mode = "PLAYING"
        self.current_life = float(self.max_life)
        self.current_boss_index = 1
        self.elapsed_seconds = 0
        self.setup_boss()
        
    def setup_boss(self):
        diff_settings = DIFFICULTIES[self.selected_difficulty]
        hp_multiplier = diff_settings["boss_hp_multiplier"]
        
        if self.current_boss_index == 13:
            self.boss_max_hp = 300.0 * hp_multiplier
        else:
            self.boss_max_hp = (20.0 * self.current_boss_index) * hp_multiplier
            
        self.boss_hp = self.boss_max_hp
        self.boss_x = float(WIDTH // 2 - self.boss_width // 2)
        self.boss_direction = random.choice([-1, 1])

    def update(self, dt):
        if self.mode != "PLAYING":
            return
            
        self.elapsed_seconds += dt
        diff_settings = DIFFICULTIES[self.selected_difficulty]
        
        # 1. 라이프 감소 로직
        time_acceleration = 1.0 + (self.elapsed_seconds * 0.02) 
        difficulty_mult = diff_settings["life_drain_multiplier"]
        drain_this_frame = self.base_drain_per_second * difficulty_mult * time_acceleration * dt
        self.current_life -= drain_this_frame
        
        if self.current_life <= 0:
            self.current_life = 0
            self.mode = "GAME_OVER"
            
        # 2. 보스 이동 로직
        speed_mult = diff_settings["boss_speed_multiplier"]
        current_speed = self.boss_base_speed * speed_mult * (1.0 + (self.current_boss_index * 0.05))
        
        self.boss_x += self.boss_direction * current_speed * dt
        
        if self.boss_x <= 10:
            self.boss_x = 10
            self.boss_direction = 1
        elif self.boss_x + self.boss_width >= WIDTH - 10:
            self.boss_x = WIDTH - 10 - self.boss_width
            self.boss_direction = -1
            
    def defeat_boss(self):
        if self.current_boss_index < self.total_bosses:
            self.current_boss_index += 1
            self.setup_boss()
        else:
            self.mode = "VICTORY"

# 게임 매니저 생성
game = GameState()

# 3. 메인 게임 루프
running = True
last_time = pygame.time.get_ticks()

while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0
    last_time = current_time

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # 메뉴 화면
            if game.mode == "MENU":
                y_pos = 250
                for diff in DIFFICULTIES.keys():
                    rect = pygame.Rect(WIDTH//2 - 100, y_pos, 200, 40)
                    if rect.collidepoint(mx, my):
                        game.start_game(diff)
                        break
                    y_pos += 60
                    
            # 게임 진행 중
            elif game.mode == "PLAYING":
                boss_rect = pygame.Rect(int(game.boss_x), game.boss_y, game.boss_width, game.boss_height)
                if boss_rect.collidepoint(mx, my):
                    damage = 25 if game.current_boss_index != 13 else 15
                    game.boss_hp -= damage
                    if game.boss_hp <= 0:
                        game.defeat_boss()
                        
            # 게임 오버 또는 승리
            elif game.mode in ["GAME_OVER", "VICTORY"]:
                btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)
                if btn_rect.collidepoint(mx, my):
                    game.mode = "MENU"

    # 로직 업데이트
    game.update(dt)

    # 4. 화면 그리기 (렌더링)
    screen.fill(BLACK)
    
    if game.mode == "MENU":
        title_text = FONT_LARGE.render("The 13th Path", True, GOLD)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))
        
        subtitle_text = FONT_SMALL.render("Click the moving boss to defeat them.", True, WHITE)
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, 150))
        
        y_pos = 250
        for diff in DIFFICULTIES.keys():
            rect = pygame.Rect(WIDTH//2 - 100, y_pos, 200, 40)
            pygame.draw.rect(screen, GRAY, rect, border_radius=5)
            text = FONT_MID.render(diff, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos + 5))
            y_pos += 60

    elif game.mode == "PLAYING":
        info_str = f"Mode: {game.selected_difficulty} | Time: {int(game.elapsed_seconds)}s"
        info_text = FONT_SMALL.render(info_str, True, WHITE)
        screen.blit(info_text, (20, 20))
        
        life_text = FONT_LARGE.render(f"LIFE: {int(game.current_life):,}", True, RED)
        screen.blit(life_text, (WIDTH//2 - life_text.get_width()//2, 50))
        
        time_acceleration = 1.0 + (game.elapsed_seconds * 0.02)
        current_drain = game.base_drain_per_second * DIFFICULTIES[game.selected_difficulty]["life_drain_multiplier"] * time_acceleration
        drain_text = FONT_SMALL.render(f"(Life Drain: -{current_drain:.1f}/s)", True, RED)
        screen.blit(drain_text, (WIDTH//2 - drain_text.get_width()//2, 100))
        
        if game.current_boss_index == 13:
            boss_title = "Final BOSS : Yourself"
            boss_color = GOLD
        else:
            boss_title = f"BOSS {game.current_boss_index}/13"
            boss_color = WHITE
            
        boss_text = FONT_MID.render(boss_title, True, boss_color)
        screen.blit(boss_text, (WIDTH//2 - boss_text.get_width()//2, 160))
        
        boss_rect = pygame.Rect(int(game.boss_x), game.boss_y, game.boss_width, game.boss_height)
        pygame.draw.rect(screen, boss_color, boss_rect, width=2, border_radius=10)
        click_prompt = FONT_SMALL.render("CLICK ME!", True, GRAY)
        screen.blit(click_prompt, (int(game.boss_x) + game.boss_width//2 - click_prompt.get_width()//2, game.boss_y + game.boss_height//2 - 10))
        
        hp_bar_width = 400
        hp_percentage = max(0.0, game.boss_hp / game.boss_max_hp)
        pygame.draw.rect(screen, GRAY, (WIDTH//2 - hp_bar_width//2, 450, hp_bar_width, 20))
        pygame.draw.rect(screen, RED, (WIDTH//2 - hp_bar_width//2, 450, int(hp_bar_width * hp_percentage), 20))
        
        hp_text = FONT_SMALL.render(f"HP: {int(game.boss_hp)} / {int(game.boss_max_hp)}", True, WHITE)
        screen.blit(hp_text, (WIDTH//2 - hp_text.get_width()//2, 480))

    elif game.mode == "GAME_OVER":
        over_text = FONT_LARGE.render("GAME OVER", True, RED)
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//3))
        
        btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)
        pygame.draw.rect(screen, RED, btn_rect, border_radius=5)
        btn_text = FONT_MID.render("MENU", True, WHITE)
        screen.blit(btn_text, (WIDTH//2 - btn_text.get_width()//2, HEIGHT//2 + 110))

    elif game.mode == "VICTORY":
        victory_text = FONT_LARGE.render("VICTORY!", True, GOLD)
        screen.blit(victory_text, (WIDTH//2 - victory_text.get_width()//2, HEIGHT//3))
        
        btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)
        pygame.draw.rect(screen, GOLD, btn_rect, border_radius=5)
        btn_text = FONT_MID.render("MENU", True, BLACK)
        screen.blit(btn_text, (WIDTH//2 - btn_text.get_width()//2, HEIGHT//2 + 110))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()