import pygame
import sys
import math

# 1. 게임 초기화
pygame.init()
pygame.font.init()

# 화면 설정
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The 13th Path: 세계를 구하기 위한 여정")
clock = pygame.time.Clock()

# 색상 정의
BLACK = (15, 15, 15)
WHITE = (240, 240, 240)
RED = (220, 50, 50)
GOLD = (235, 180, 50)
GRAY = (80, 80, 80)

# 폰트 설정
FONT_LARGE = pygame.font.SysFont("malgungothic", 40, bold=True)
FONT_MID = pygame.font.SysFont("malgungothic", 24, bold=True)
FONT_SMALL = pygame.font.SysFont("malgungothic", 18)

# 2. 난이도 및 게임 상태 설정
DIFFICULTIES = {
    "일반": {"life_drain_multiplier": 1.0, "boss_hp_multiplier": 1.0},
    "보통": {"life_drain_multiplier": 1.5, "boss_hp_multiplier": 1.3},
    "어려움": {"life_drain_multiplier": 2.5, "boss_hp_multiplier": 1.8},
    "지옥": {"life_drain_multiplier": 5.0, "boss_hp_multiplier": 2.5},
    "윤회": {"life_drain_multiplier": 10.0, "boss_hp_multiplier": 4.0}
}

class GameState:
    def __init__(self):
        self.mode = "MENU"  # MENU, PLAYING, GAME_OVER, VICTORY
        self.selected_difficulty = "일반"
        
        # 라이프 설정 (초기값: 33,550,336)
        self.max_life = 33550336
        self.current_life = float(self.max_life)
        self.base_drain_per_second = 12.0
        
        # 보스 진행도 (총 13명)
        self.current_boss_index = 1
        self.total_bosses = 13
        self.boss_hp = 100.0
        self.boss_max_hp = 100.0
        
        # 시간 추적 (가속도 계산용)
        self.elapsed_seconds = 0.0
        
    def start_game(self, difficulty):
        self.selected_difficulty = difficulty
        self.mode = "PLAYING"
        self.current_life = float(self.max_life)
        self.current_boss_index = 1
        self.elapsed_seconds = 0
        self.setup_boss()
        
    def setup_boss(self):
        multiplier = DIFFICULTIES[self.selected_difficulty]["boss_hp_multiplier"]
        if self.current_boss_index == 13:
            # 마지막 13번째 보스는 내 자신의 복제이자 실력이 13배
            self.boss_max_hp = 1000.0 * multiplier * 13
        else:
            # 1~12번째 보스 (내 삶의 중요한 12명)
            self.boss_max_hp = (100.0 * self.current_boss_index) * multiplier
        self.boss_hp = self.boss_max_hp

    def update(self, dt):
        if self.mode != "PLAYING":
            return
            
        self.elapsed_seconds += dt
        
        # 💡 설정 반영: 시간이 지날수록 라이프가 깎이는 속도가 빨라짐 (가속도 매초 +2%씩 증가)
        time_acceleration = 1.0 + (self.elapsed_seconds * 0.02) 
        difficulty_mult = DIFFICULTIES[self.selected_difficulty]["life_drain_multiplier"]
        
        # 이번 프레임에 깎일 라이프 계산
        drain_this_frame = self.base_drain_per_second * difficulty_mult * time_acceleration * dt
        self.current_life -= drain_this_frame
        
        # ❌ 패배 조건: 라이프가 0 이하가 되면 패배
        if self.current_life <= 0:
            self.current_life = 0
            self.mode = "GAME_OVER"
            
    def defeat_boss(self):
        if self.current_boss_index < self.total_bosses:
            self.current_boss_index += 1
            self.setup_boss()
        else:
            # 🏆 승리 조건: 13명의 보스를 모두 꺾으면 승리
            self.mode = "VICTORY"

# 게임 매니저 생성
game = GameState()

# 3. 메인 게임 루프
running = True
last_time = pygame.time.get_ticks()

while running:
    # 델타 타임 계산 (초 단위)
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0
    last_time = current_time

    # 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # 메뉴 화면 상호작용
            if game.mode == "MENU":
                y_pos = 250
                for diff in DIFFICULTIES.keys():
                    rect = pygame.Rect(WIDTH//2 - 100, y_pos, 200, 40)
                    if rect.collidepoint(mx, my):
                        game.start_game(diff)
                        break
                    y_pos += 60
                    
            # 게임 진행 중 (테스트용 보스 타격/처치 메커니즘)
            elif game.mode == "PLAYING":
                # 보스 영역을 클릭하면 대미지 부여
                boss_rect = pygame.Rect(WIDTH//2 - 150, 200, 300, 200)
                if boss_rect.collidepoint(mx, my):
                    # 13번째 보스는 강하므로 대미지가 적게 들어감 처리 가능
                    damage = 25 if game.current_boss_index != 13 else 5
                    game.boss_hp -= damage
                    if game.boss_hp <= 0:
                        game.defeat_boss()
                        
            # 게임 오버 또는 승리 시 메뉴로 돌아가기 버튼 클릭
            elif game.mode in ["GAME_OVER", "VICTORY"]:
                btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)
                if btn_rect.collidepoint(mx, my):
                    game.mode = "MENU"

    # 로직 업데이트
    game.update(dt)

    # 4. 화면 그리기 (렌더링)
    screen.fill(BLACK)
    
    if game.mode == "MENU":
        # 타이틀 화면
        title_text = FONT_LARGE.render("The 13th Path: 세계를 위한 희생", True, GOLD)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 80))
        
        subtitle_text = FONT_SMALL.render("세계를 구하기 위해, 당신의 삶에 중요했던 12명과 당신 자신을 파괴하십시오.", True, WHITE)
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, 150))
        
        # 난이도 버튼 그리기
        y_pos = 250
        for diff in DIFFICULTIES.keys():
            rect = pygame.Rect(WIDTH//2 - 100, y_pos, 200, 40)
            pygame.draw.rect(screen, GRAY, rect, border_radius=5)
            text = FONT_MID.render(diff, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos + 5))
            y_pos += 60

    elif game.mode == "PLAYING":
        # 상단 정보 (난이도 및 시간)
        info_str = f"모드: {game.selected_difficulty} | 진행 시간: {int(game.elapsed_seconds)}초"
        info_text = FONT_SMALL.render(info_str, True, WHITE)
        screen.blit(info_text, (20, 20))
        
        # 🔴 라이프 시스템 UI (콤마 표기 포맷 적용)
        life_text = FONT_LARGE.render(f"LIFE: {int(game.current_life):,}", True, RED)
        screen.blit(life_text, (WIDTH//2 - life_text.get_width()//2, 50))
        
        # 현재 초당 라이프 감소 속도 시각화
        time_acceleration = 1.0 + (game.elapsed_seconds * 0.02)
        current_drain = game.base_drain_per_second * DIFFICULTIES[game.selected_difficulty]["life_drain_multiplier"] * time_acceleration
        drain_text = FONT_SMALL.render(f"(초당 라이프 감소 속도: -{current_drain:.1f})", True, RED)
        screen.blit(drain_text, (WIDTH//2 - drain_text.get_width()//2, 100))
        
        # 보스 인덱스 및 정보 표시
        if game.current_boss_index == 13:
            boss_title = "최종 BOSS : 거울 속의 자신 (실력 13배)"
            boss_color = GOLD
        else:
            boss_title = f"BOSS {game.current_boss_index}/13 : 소중한 기억의 인물"
            boss_color = WHITE
            
        boss_text = FONT_MID.render(boss_title, True, boss_color)
        screen.blit(boss_text, (WIDTH//2 - boss_text.get_width()//2, 160))
        
        # 보스 그래픽 대체 영역 (클릭하여 공격 가능)
        boss_rect = pygame.Rect(WIDTH//2 - 150, 200, 300, 200)
        pygame.draw.rect(screen, boss_color, boss_rect, width=2, border_radius=10)
        click_prompt = FONT_SMALL.render("마우스 클릭으로 타격", True, GRAY)
        screen.blit(click_prompt, (WIDTH//2 - click_prompt.get_width()//2, 290))
        
        # 보스 체력 바
        hp_bar_width = 400
        hp_percentage = max(0.0, game.boss_hp / game.boss_max_hp)
        pygame.draw.rect(screen, GRAY, (WIDTH//2 - hp_bar_width//2, 430, hp_bar_width, 20))
        pygame.draw.rect(screen, RED, (WIDTH//2 - hp_bar_width//2, 430, int(hp_bar_width * hp_percentage), 20))
        
        hp_text = FONT_SMALL.render(f"HP: {int(game.boss_hp)} / {int(game.boss_max_hp)}", True, WHITE)
        screen.blit(hp_text, (WIDTH//2 - hp_text.get_width()//2, 460))

    elif game.mode == "GAME_OVER":
        # ❌ 패배 화면 (임무 실패)
        over_text = FONT_LARGE.render("임무 실패: 라이프가 전멸했습니다.", True, RED)
        screen.blit(over_text, (WIDTH//2 - over_text.get_width()//2, HEIGHT//3))
        
        # 패배 버튼
        btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)
        pygame.draw.rect(screen, RED, btn_rect, border_radius=5)
        btn_text = FONT_MID.render("다시 시도 (메뉴)", True, WHITE)
        screen.blit(btn_text, (WIDTH//2 - btn_text.get_width()//2, HEIGHT//2 + 110))

    elif game.mode == "VICTORY":
        # 🏆 승리 화면 (임무 완수)
        vic_text = FONT_LARGE.render("임무 완수: 세계가 구원받았습니다.", True, GOLD)
        screen.blit(vic_text, (WIDTH//2 - vic_text.get_width()//2, HEIGHT//3 - 30))
        
        story_text = FONT_SMALL.render("당신은 소중한 12명과 자신을 희생하여 종말을 막았습니다.", True, WHITE)
        screen.blit(story_text, (WIDTH//2 - story_text.get_width()//2, HEIGHT//3 + 40))
        
        # 복귀 버튼
        btn_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)
        pygame.draw.rect(screen, GOLD, btn_rect, border_radius=5)
        btn_text = FONT_MID.render("처음으로 (메뉴)", True, BLACK)
        screen.blit(btn_text, (WIDTH//2 - btn_text.get_width()//2, HEIGHT//2 + 110))

    pygame.display.flip()
    clock.tick(60) # 60 FPS 유지

pygame.quit()
sys.exit()
