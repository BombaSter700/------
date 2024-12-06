import random
from game_objects import Platform, Coffee, Clock
from settings import *

def generate_initial_platforms(num_platforms, width, height, platform_width, platform_height):
    """Создаем начальный набор платформ и пол"""
    platforms = []
    for i in range(num_platforms):
        x = i * (platform_width + 50)
        y = random.randint(height // 2, height - platform_height - 100)
        platforms.append(Platform(x, y, platform_width, platform_height))
    return platforms

def generate_new_platform(last_platform, width, height, platform_width, platform_height, game_images):
    """Создаем новую платформу справа"""
    x = last_platform.rect.x + platform_width + random.randint(50, 200)  # Случайное расстояние
    y = random.randint(height // 2, height - platform_height - 100)  # Случайная высота
    new_platform = Platform(x, y, platform_width, platform_height)

    # Вероятность генерации бонуса
    if random.random() < 0.15:  # Менять шанс спавна 
        bonus_type = random.choice(["coffee", "clock"])  # Тип бонуса
        bonus_class = Coffee if bonus_type == "coffee" else Clock
        bonus_image = game_images[bonus_type]

        # Располагаем бонус над платформой
        bonus_x = random.randint(x, x + platform_width - 40)
        bonus_y = y - 40  # Чуть выше платформы
        new_bonus = bonus_class(bonus_x, bonus_y, bonus_image, bonus_type)
        return new_platform, new_bonus

    return new_platform, None


def update_floor_segments(floor_segments, camera_x, width, height):
    """Обновляем сегменты пола: добавляем новые и удаляем старые."""
    if not floor_segments:
        # Если список пуст, создаем первый сегмент пола
        floor_segments.append(Platform(0, height - 20, width, 20))

    # Добавляем новый сегмент справа
    if floor_segments[-1].rect.right < camera_x + width:
        new_x = floor_segments[-1].rect.right
        floor_segments.append(Platform(new_x, height - 20, width, 20))

    # Удаляем старые сегменты слева
    floor_segments = [segment for segment in floor_segments if segment.rect.right > camera_x - width]

    return floor_segments


def remove_old_platforms(platforms, camera_x, width):
    """Удаляем платформы, которые ушли за левый край"""
    return [platform for platform in platforms if platform.rect.right > camera_x - width]
