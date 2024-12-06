import pygame
import os
from settings import *
from collections import deque

pygame.init()

"""Состояния игры"""
MENU = "menu"
PLAYING = "playing"
GAME_OVER = "game_over"
WIN = "game_win"

class Game:
    def __init__(self):
        current_dir = os.path.dirname(__file__)
        assets_dir = os.path.join(current_dir, 'assets', 'images')
        self.images = load_images(assets_dir)

        self.images["main_background"] = pygame.transform.scale(
            self.images["main_background"], (WIDTH, HEIGHT)
        )
        self.images["couch"] = pygame.transform.scale(
            self.images["couch"], (DIVAN_WIDTH, DIVAN_HEIGHT)
        )
        self.images["player"] = pygame.transform.scale(
            self.images["player"], (PLAYER_WIDTH, PLAYER_HEIGHT)
        )
        self.images["coffee"] = self.images["coffee"]
        self.images["clock"] = self.images["clock"]
        self.images["main_menu"] = self.images["main_menu"]
        self.images["lose_screen"] = self.images["lose_screen"]
        self.images["office"] = self.images["office"]

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Диванная революция")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = MENU
        self.score = 0
        self.bonuses = []
        self.player_path = deque(maxlen=100)  # Очередь записи маршрута игрока

        # Платформы
        self.platforms = []
        self.floor_segments = []
        self.camera_x = 0

        # Генерация начальных платформ
        self.platforms = generate_initial_platforms(
            num_platforms=10,
            width=WIDTH,
            height=HEIGHT,
            platform_width=PLATFORM_WIDTH,
            platform_height=PLATFORM_HEIGHT
        )

    def update_floor(self):
        """Обновляем сегменты пола."""
        self.floor_segments = update_floor_segments(
            self.floor_segments,
            camera_x=self.camera_x,
            width=WIDTH,
            height=HEIGHT
        )

    def generate_new_platforms(self):
        """Добавляем новые платформы справа."""
        last_platform = self.platforms[-1]
        if last_platform.rect.x < self.camera_x + WIDTH:
            new_platform, new_bonus = generate_new_platform(
                last_platform,
                width=WIDTH,
                height=HEIGHT,
                platform_width=PLATFORM_WIDTH,
                platform_height=PLATFORM_HEIGHT,
                game_images=self.images
            )
            self.platforms.append(new_platform)
            if new_bonus is not None:
                self.bonuses.append(new_bonus)

    def run(self):
        while self.running:
            if self.state == MENU:
                self.show_menu()
            elif self.state == PLAYING:
                self.play_game()
            elif self.state == GAME_OVER:
                self.show_game_over()
            elif self.state == WIN:
                self.win_screen()
            self.clock.tick(FPS)

        # Генерация новых платформ
            self.generate_new_platforms()

        # Удаление старых платформ
            self.platforms = remove_old_platforms(self.platforms, self.camera_x, WIDTH)
             
        pygame.quit()

    def show_menu(self):
        self.screen.blit(self.images["main_menu"], (0, 0))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    self.state = PLAYING
                    waiting = False

    def play_game(self):
        self.player = Player(200, HEIGHT - PLAYER_HEIGHT - PLATFORM_HEIGHT - 1, self.images["player"])
        self.couch = Couch(1, HEIGHT - DIVAN_HEIGHT, self.images["couch"])
        safe_timer = 30 # Задержка дивана
        elapsed_time = 0  # Время, проведенное в игре

        while self.state == PLAYING:
            elapsed_time += 1  # Увеличиваем счетчик времени (каждый кадр)
            self.screen.blit(self.images["main_background"], (0, 0))
            self.couch.draw(self.screen)
            self.update_floor()

            if elapsed_time % (FPS * 5) == 0:
                new_multiplier = min(1 + elapsed_time // (FPS * 5) * 0.2, 5)  # До 5x
                self.couch.increase_speed(new_multiplier)

            self.player_path.append({
                "x": self.player.rect.x,
                "y": self.player.rect.y,
                "on_ground": self.player.on_ground,
                "velocity_y": self.player.velocity_y
            })

            for event in pygame.event.get():    
                if event.type == pygame.QUIT:
                    self.running = False
                    self.state = None
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] and self.player.on_ground:
                self.player.jump()

            keys = pygame.key.get_pressed()
            self.player.move(keys)
            self.couch.move()
            # Проверяем столкновения с платформами и полом
            self.player.on_ground = False
            for platform in self.platforms + self.floor_segments:  # Проверка пол+платформы
                if self.player.rect.colliderect(platform.rect) and self.player.velocity_y >= 0:
                    self.player.velocity_y = 0
                    self.player.rect.bottom = platform.rect.top
                    self.player.on_ground = True
                    self.player.jump_timer = 10  # Обновляем таймер прыжка
                    break

            if not self.player.on_ground:
                self.player.apply_gravity()

            self.player.update()
            self.couch.move_along_path(self.player_path)

            if safe_timer <= 0:
                if self.couch.rect.colliderect(self.player.rect):
                    self.state = GAME_OVER
                    break
            safe_timer -= 1
            self.generate_new_platforms()

            if self.score > 100:
                self.state = WIN
                break

            """ОБНОВЛЕНИЕ СБОРА БОНУСОВ"""
            # Проверка на сбор бонусов
            for bonus in self.bonuses[:]:
                if self.player.rect.colliderect(bonus.rect):
                    if bonus.type == "coffee":
                        self.score += 10
                        self.player.speed += 0.7
                    elif bonus.type == "clock":
                        self.score += 5
                        self.couch.stop(90)
                    self.bonuses.remove(bonus)

            for bonus in self.bonuses:
                bonus.draw(self.screen)

            # Удаление бонусов, которые вышли за экран
            self.bonuses = [bonus for bonus in self.bonuses if bonus.rect.right > 0]
            """КОНЕЦ ОБНОВЫ"""

            self.platforms = remove_old_platforms(self.platforms, self.camera_x, WIDTH)

            # Прокрутка уровня
            if self.player.rect.centerx > WIDTH // 2 and self.player.velocity_x > 0:
                for platform in self.platforms:
                    platform.rect.x -= self.player.velocity_x
                for bonus in self.bonuses:
                    bonus.rect.x -= self.player.velocity_x  # Смещаем бонусы
                self.couch.rect.x -= self.player.velocity_x
                self.player.rect.x = WIDTH // 2 - PLAYER_WIDTH // 2

            # Отрисовка объектов
            for floor_segment in self.floor_segments:
                floor_segment.draw(self.screen, camera_x=self.camera_x)  # Отрисовка пола
            for platform in self.platforms:
                platform.draw(self.screen, camera_x=0) 
            self.player.draw(self.screen)

            self.player.draw(self.screen)

            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))

            pygame.display.flip()
            self.clock.tick(FPS)



    def show_game_over(self):
        self.screen.blit(self.images["lose_screen"], (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.state = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.state = MENU

    def win_screen(self):
        # Заполнение экрана чёрным цветом
        self.screen.fill((0, 0, 0))
        
        # Основной текст "ТЫ СБЕЖАЛ!"
        font_large = pygame.font.Font(None, 72)
        win_text = font_large.render("ТЫ СБЕЖАЛ!", True, WHITE)
        self.screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 3))
        
        # Текст "Нажми R, чтобы начать заново"
        font_small = pygame.font.Font(None, 36)
        restart_text = font_small.render("Нажми R, чтобы начать заново", True, WHITE)
        self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
        
        pygame.display.flip()

        # Ожидание действий игрока
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Перезапуск игры
                        self.state = MENU
                        self.score = 0
                        waiting = False

            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        waiting = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.state = MENU
                            self.office = None
                            self.score = 0
                            waiting = False


if __name__ == "__main__":
    from game_objects import Player, Couch
    from assets import load_images
    from generation import *
    game = Game()
    game.run()