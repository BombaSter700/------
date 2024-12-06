import pygame
from settings import *
from collections import deque


class Player:
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = 5
        self.on_ground = True
        self.jump_timer = 0  # Таймер прыжка, удобно даже если игрок на краю прыгает
        self.image = image

    def move(self, keys):
        self.velocity_x = 0
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.velocity_x = -self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < WIDTH - PLAYER_WIDTH:
            self.velocity_x = self.speed

    def jump(self):
        # Прыжок возможен, если персонаж на земле или таймер прыжка > 0
        if self.on_ground or self.jump_timer > 0:
            self.velocity_y = -15
            self.on_ground = False
            self.jump_timer = 0

    def apply_gravity(self):
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

    def update(self):
        if not self.on_ground and self.jump_timer > 0:
            self.jump_timer -= 1
        self.rect.x += self.velocity_x
    
    def draw(self, screen):
        scaled_image = pygame.transform.scale(
            self.image, 
            (int(DIVAN_WIDTH * screen.get_width() / WIDTH), int(DIVAN_HEIGHT * screen.get_height() / HEIGHT))
        )
        screen.blit(scaled_image, (self.rect.x, self.rect.y))


class Couch:
    def __init__(self, x, y, image):
        self.rect = pygame.Rect(x, y, DIVAN_WIDTH, DIVAN_HEIGHT)
        self.speed = 2
        self.paused = 0
        self.speed_m = 1 # Множитель скорости
        self.image = image
        self.path_index = 0  # Индекс для отслеживания позиции в пути
    """ОБРАБОТКА МАРШРУТА ТРЕБУЕТ ДОРАБОТКИ"""
    def move(self):
        self.rect.x += self.speed * self.speed_m

    def increase_speed(self, multiplier):
        self.speed_m = multiplier

    def move_along_path(self, player_path):
        """Движение дивана по маршруту игрока с задержкой."""
        if self.paused > 0:
            self.paused -= 1
            return

        if len(player_path) > 30:  # Убедимся, что есть задержка
            scale_x = self.rect.width / DIVAN_WIDTH
            scale_y = self.rect.height / DIVAN_HEIGHT
            target_state = player_path[0]
            target_x, target_y = target_state["x"] * scale_x, target_state["y"] * scale_y

            # Двигаемся к следующей точке
            if self.rect.x < target_x:
                self.rect.x += min(self.speed, target_x - self.rect.x)
            elif self.rect.x > target_x:
                self.rect.x -= min(self.speed, self.rect.x - target_x)

            if self.rect.y < target_y:
                self.rect.y += min(self.speed, target_y - self.rect.y)
            elif self.rect.y > target_y:
                self.rect.y -= min(self.speed, self.rect.y - target_y)

            # Удаляем точку из пути, если она достигнута
            if abs(self.rect.x - target_x) < self.speed and abs(self.rect.y - target_y) < self.speed:
                player_path.popleft()

    def stop(self, duration):
        self.paused = duration

    def draw(self, screen):
        scaled_image = pygame.transform.scale(
            self.image, 
            (int(DIVAN_WIDTH * screen.get_width() / WIDTH), int(DIVAN_HEIGHT * screen.get_height() / HEIGHT))
        )
        screen.blit(scaled_image, (self.rect.x, self.rect.y))



class Platform:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, screen, camera_x):
        """Рисуем платформу с учетом смещения камеры."""
        pygame.draw.rect(screen, GREEN, (self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))



class Coffee:
    def __init__(self, x, y, image, bonus_type):
        self.rect = pygame.Rect(x, y, 20, 35)
        self.image = image
        self.type = bonus_type

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Clock:
    def __init__(self, x, y, image, bonus_type):
        self.rect = pygame.Rect(x, y, 30, 30)
        self.image = image
        self.type = bonus_type

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))