import pygame
import sys
import random


pygame.init()
bullets_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
health_packs_group = pygame.sprite.Group()
poison_zones_group = pygame.sprite.Group()  # Группа для ядовитых зон
poison_zone_spawn_timer = 0
poison_zones_limit = 100
poison_zone_spawn_interval = 15
poison_zone_size_multiplier = 4
kill_count = 0  # Инициализация счетчика убийств
clock = pygame.time.Clock()
# Инициализация таймера
game_timer = 0
start_time = pygame.time.get_ticks()

pygame.mixer.init()  # Музыка
pygame.mixer.music.load(
    "music.mp3"
)

pygame.mixer.music.play(-1)  # Музыка будет воспроизводиться бесконечно

background_image = pygame.image.load(
    "background_image.jpg"
)
background_rect = background_image.get_rect()

# Загрузка изображения персонажа
character_image = pygame.image.load("charcter_image.gif")
scaled_character_image = pygame.transform.scale(character_image, (40, 40))

# Определение размера экрана
screen_width, screen_height = 1920, 1080
screen_center_x = screen_width // 2
screen_center_y = screen_height // 2

# Задайте смещение для границы относительно центра экрана
boundary_offset_x = 300  # Смещение по горизонтали
boundary_offset_y = 200  # Смещение по вертикали

# Определите координаты границы
boundary_x = screen_center_x - boundary_offset_x
boundary_y = screen_center_y - boundary_offset_y

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Decisive survival")
# Определение размеров и границ локации
location_width = 4000
location_height = 4000

# Размер изометрического тайла
tile_width, tile_height = 90, 90

# Цвета для тайлов
tile_color = (200, 200, 200)
highlight_color = (255, 0, 0)

location_image_choice = 1
# Текущая позиция камеры и максимальная позиция камеры
camera_x, camera_y = 0, 0
max_camera_x, max_camera_y = screen_width, screen_height


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.lifespan = 2

    def update(self):
        speed = 10
        self.rect.x += self.direction[0] * speed
        self.rect.y += self.direction[1] * speed
        self.lifespan -= 1


# Появления пули (каждые 2 секунды)
bullet_spawn_frequency = 2
# Таймер для автоматического запуска пули
bullet_spawn_timer = 0


class PoisonZone(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((400, 400), pygame.SRCALPHA)
        pygame.draw.polygon(
            self.image,
            (148, 0, 211, 128),
            [(20 * 4, 0), (40 * 4, 20 * 4), (20 * 4, 40 * 4), (0, 20 * 4)],
        )
        # Фиолетовый ромб с прозрачностью
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.duration = 15  # Длительность существования ядовитой зоны в секундах
        self.damage_per_second = 5  # Урон в секунду

    def update(self):
        self.duration -= 1 / 60  # Уменьшаем таймер длительности
        if self.duration <= 0:
            self.kill()  # Удаляем ядовитую зону после завершения длительности


class HealthPack(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 255, 0))  # Зелёный квадратик
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def heal_player(self, player):
        # Восстанавливаем здоровье игрока
        player.health += 10
        if player.health > 100:
            player.health = 100
        # Удаляем зелёный квадратик после использования
        self.kill()


num_health_packs = random.randint(5, 100)
for _ in range(num_health_packs):
    health_pack = HealthPack(
        boundary_x + random.randint(0, location_width - 30),
        boundary_y + random.randint(0, location_height - 30),
    )
    health_packs_group.add(health_pack)


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((0, 0, 255))  # Синий цвет для портала
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def teleport_player(self, player):
        # При соприкосновении с порталом переместить игрока в рандомную часть карты
        player.rect.x = boundary_x + random.randint(0, location_width - 40)
        player.rect.y = boundary_y + random.randint(0, location_height - 40)


num_portals = random.randint(1, 100)
portals_group = pygame.sprite.Group()
for _ in range(num_portals):
    portal = Portal(
        boundary_x + random.randint(0, location_width - 40),
        boundary_y + random.randint(0, location_height - 40),
    )
    portals_group.add(portal)


class Character:
    def __init__(self, name, health=100):
        self.name = name
        self.health = health
        self.image = scaled_character_image
        self.rect = self.rect = pygame.Rect(
            location_width // 2 - 20, location_height // 2 - 20, 40, 40
        )
        self.speed = 5

    @staticmethod
    def draw_health_bar(screen, x, y, health, max_health):
        bar_width = 40  # Ширина полоски здоровья
        bar_height = 5  # Высота полоски здоровья
        outline_rect = pygame.Rect(x, y, bar_width, bar_height)
        filled_rect = pygame.Rect(
            x, y, int(bar_width * (health / max_health)), bar_height
        )

        # Отрисовка контура полоски
        pygame.draw.rect(
            screen, (255, 0, 0), outline_rect, 1
        )  # Красный цвет для контура

        # Отрисовка заполненной части полоски
        if health > 0:  # Проверка, чтобы не отрисовывать пустую полоску
            pygame.draw.rect(
                screen, (0, 255, 0), filled_rect
            )  # Зеленый цвет для заполненной части

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def is_alive(self):
        return self.health > 0


# Определение класса CharacterSprite
class CharacterSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health=100):
        super().__init__()
        self.health = health
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.attack_cooldown = 0
        self.attack = 5  # Значение атаки врага
        self.attack_speed = 1  # Скорость атаки врага

    def take_damage(self, damage):
        self.health -= damage

    def hit_by_bullet(self):
        global kill_count
        self.take_damage(100)
        if not self.is_alive():
            self.kill()  # Удалить врага из всех групп, к которым он принадлежит
            kill_count += 1
            spawn_enemy()

    def is_alive(self):
        return self.health > 0

    def move_towards_player(self, player):
        dx = player.rect.x - self.rect.x
        dy = player.rect.y - self.rect.y
        distance = max(1, ((dx**2) + (dy**2)) ** 0.5)
        dx /= distance
        dy /= distance
        speed = 1
        self.rect.x += dx * speed
        self.rect.y += dy * speed

    def attack_target(self, target):
        if self.attack_cooldown <= 0:
            target.take_damage(self.attack)
            self.attack_cooldown = 1 / self.attack_speed
            self.time_since_last_attack = 0

    def update_boundary(self, boundary_rect):
        # Проверяем, находится ли враг в пределах границы, и корректируем его положение при необходимости
        self.rect.x = max(
            boundary_rect.left, min(self.rect.x, boundary_rect.right - self.rect.width)
        )
        self.rect.y = max(
            boundary_rect.top, min(self.rect.y, boundary_rect.bottom - self.rect.height)
        )


class LocationBoundary(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.update_image()

    def update_image(self):
        if location_image_choice == 1:
            self.image = pygame.image.load(
                "icemap.jpg"
            )
        elif location_image_choice == 2:
            self.image = pygame.image.load(
                "grassmap.jpg"
            )
        elif location_image_choice == 3:
            self.image = pygame.image.load(
                "castle.jpg"
            )

    def set_location_choice(self, choice):
        global location_image_choice
        location_image_choice = choice
        self.update_image()


boundary = LocationBoundary(boundary_x, boundary_y, location_width, location_height)
player = Character("Игрок", health=100)
character_sprite = CharacterSprite(scaled_character_image, x=5, y=5)

# Количество противников
num_enemies = 300
for _ in range(num_enemies):
    # Генерация случайных координат для каждого противника
    x = boundary_x + random.randint(0, location_width - 40)
    y = boundary_y + random.randint(0, location_height - 40)

    # Создание экземпляра врага и добавление его в список
    enemy = Enemy(x, y, health=100)
    enemies_group.add(enemy)


def check_enemy_collisions(enemies):
    for enemy1 in enemies:
        for enemy2 in enemies:
            if enemy1 != enemy2:
                if enemy1.rect.colliderect(enemy2.rect):
                    # Если есть коллизия между enemy1 и enemy2, перемещение их так, чтобы они больше не пересекались
                    dx = enemy2.rect.x - enemy1.rect.x
                    dy = enemy2.rect.y - enemy1.rect.y
                    distance = max(1, ((dx**2) + (dy**2)) ** 0.5)
                    overlap = (
                        20 - distance
                    ) / 2  # Вычисление на сколько переместить каждого врага

                    dx /= distance
                    dy /= distance

                    enemy1.rect.x -= dx * overlap
                    enemy1.rect.y -= dy * overlap

                    enemy2.rect.x += dx * overlap
                    enemy2.rect.y += dy * overlap


def check_enemy_collisions_with_player(enemies, player):
    for enemy in enemies:
        if player.rect.colliderect(enemy.rect):
            if enemy.attack_cooldown <= 0:
                player.take_damage(3)
                enemy.attack_cooldown = 30


def draw_kill_count(kill_count, screen):
    font = pygame.font.Font(None, 50)
    count_text = font.render(f"Kills: {kill_count}", True, (255, 255, 255))
    screen.blit(count_text, (1350, 300))


def draw_timer(game_timer, screen):
    font = pygame.font.Font(None, 50)
    timer_text = font.render(f"TIME: {int(game_timer) // 60}:{int(game_timer) % 60}",
                             True, (255, 255, 255))
    screen.blit(timer_text, (1350, 250))


def spawn_enemy():
    x = boundary_x + random.randint(0, location_width - 40)
    y = boundary_y + random.randint(0, location_height - 40)
    new_enemy = Enemy(x, y, health=100)
    enemies_group.add(new_enemy)


class Menu:
    def __init__(self, options):
        self.options = options
        self.selected_option = 0
        self.font = pygame.font.Font(None, 57)
        self.menu_active = True
        self.key_repeat_delay = 0.2
        self.key_repeat_timer = 0.0

    def draw_menu(self, screen):
        screen.blit(background_image, background_rect)
        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("Decisive survival", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 400))
        for i, option in enumerate(self.options):
            text = self.font.render(
                option,
                True,
                (255, 255, 255) if i == self.selected_option else (128, 128, 128),
            )
            text_rect = text.get_rect(center=(screen_width // 2, 700 + i * 50))
            screen.blit(text, text_rect)

    def handle_input(self, keys):
        if keys[pygame.K_UP]:
            self.handle_key_repeat(pygame.K_UP)
        if keys[pygame.K_DOWN]:
            self.handle_key_repeat(pygame.K_DOWN)

    def handle_key_repeat(self, key):
        # Если таймер истек, обработка нажатие клавиши
        if self.key_repeat_timer <= 0:
            if key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)

            # Сброс таймера на начальную задержку для следующего нажатия клавиши
            self.key_repeat_timer = self.key_repeat_delay
        else:
            self.key_repeat_timer -= 1 / 60


menu = Menu(["Начать игру", "Выбор уровня", "Настройки", "Выход"])


class SettingsMenu(Menu):
    def __init__(self, options, main_menu):
        super().__init__(options)
        self.brightness = 50
        self.volume = 50
        self.main_menu = main_menu
        self.back_button_text = self.font.render("Назад", True, (255, 255, 255))
        self.value_font = pygame.font.Font(None, 36)  # Шрифт для отображения значений
        self.volume_text = self.value_font.render(
            str(self.volume), True, (255, 255, 255)
        )

    def draw_menu(self, screen):
        screen.blit(background_image, background_rect)
        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("Настройки", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 200))

        # Отображение текста опций и кнопки "Назад"
        for i, option in enumerate(self.options):
            text_color = (
                (255, 255, 255) if i == self.selected_option else (128, 128, 128)
            )
            text = self.font.render(option, True, text_color)
            text_rect = text.get_rect(center=(screen_width // 2, 400 + i * 100))
            screen.blit(text, text_rect)

        # Отображение ползунков для громкости
        volume_slider_rect = pygame.Rect(screen_width // 2 - 100, 450, 200, 10)

        # Отображение ползунков
        pygame.draw.rect(screen, (255, 255, 255), volume_slider_rect)

        # Отображение ползунка громкости
        volume_slider_position = volume_slider_rect.x + int(
            volume_slider_rect.width * self.volume / 100
        )
        pygame.draw.rect(
            screen,
            (0, 128, 255),
            (volume_slider_position - 5, volume_slider_rect.y - 5, 10, 20),
        )

        # Отображение цифровых значений
        volume_text_rect = self.volume_text.get_rect(center=(screen_width // 2, 480))
        screen.blit(self.volume_text, volume_text_rect)

    def handle_input(self, keys):

        super().handle_input(keys)

        if keys[pygame.K_RETURN]:
            self.enter_pressed = True
        elif self.enter_pressed:
            self.enter_pressed = False
            if self.options[self.selected_option] == "Назад":
                self.menu_active = False
                self.main_menu.menu_active = True
                global menu
                menu = self.main_menu

        if keys[pygame.K_LEFT] and self.selected_option == 0:  # Громкость
            self.volume = max(0, self.volume - 1)
        elif keys[pygame.K_RIGHT] and self.selected_option == 0:  # Громкость
            self.volume = min(100, self.volume + 1)

        # Обновление текстовых значений
        self.volume_text = self.value_font.render(
            str(self.volume), True, (255, 255, 255)
        )

        # Обновление громкости музыки
        pygame.mixer.music.set_volume(self.volume)


# Экземпляр меню настроек, передавая ему ссылку на основное меню
settings_menu = SettingsMenu(["Громкость", "Назад"], menu)


class LevelMenu(Menu):
    def __init__(self, options, main_menu):
        super().__init__(options)
        self.main_menu = main_menu  # Ссылка на объект основного меню
        self.menu_active = True
        self.value_font = pygame.font.Font(None, 36)

    def draw_menu(self, screen):
        screen.blit(background_image, background_rect)
        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("Выбор уровня", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 200))

        # Отображение текста опций и кнопки "Назад"
        for i, option in enumerate(self.options):
            text_color = (
                (255, 255, 255) if i == self.selected_option else (128, 128, 128)
            )
            text = self.font.render(option, True, text_color)
            text_rect = text.get_rect(center=(screen_width // 2, 400 + i * 100))
            screen.blit(text, text_rect)

    def handle_input(self, keys):
        super().handle_input(keys)
        if keys[pygame.K_RETURN]:
            self.enter_pressed = True
        elif self.enter_pressed:
            self.enter_pressed = False
            if self.options[self.selected_option] == "Назад":
                self.menu_active = False
                self.main_menu.menu_active = True
                global menu
                menu = self.main_menu

            elif self.options[self.selected_option] == "1 уровень":
                boundary.set_location_choice(1)
            elif self.options[self.selected_option] == "2 уровень":
                boundary.set_location_choice(2)
            elif self.options[self.selected_option] == "3 уровень":
                boundary.set_location_choice(3)


level_menu = LevelMenu(["1 уровень", "2 уровень", "3 уровень", "Назад"], menu)


class DeathMenu(Menu):
    def __init__(self, options, main_menu):
        super().__init__(options)
        self.main_menu = main_menu
        self.menu_active = True
        self.font = pygame.font.Font(None, 57)

    def draw_menu(self, screen):
        screen.fill((0, 0, 0))
        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("Вы умерли", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 400))

        for i, option in enumerate(self.options):
            text = self.font.render(
                option,
                True,
                (255, 255, 255) if i == self.selected_option else (128, 128, 128),
            )
            text_rect = text.get_rect(center=(screen_width // 2, 700 + i * 50))
            screen.blit(text, text_rect)

    def handle_input(self, keys):
        if keys[pygame.K_UP]:
            self.handle_key_repeat(pygame.K_UP)
        if keys[pygame.K_DOWN]:
            self.handle_key_repeat(pygame.K_DOWN)

    def handle_key_repeat(self, key):

        if self.key_repeat_timer <= 0:
            if key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
            elif key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
            self.key_repeat_timer = self.key_repeat_delay
        else:
            self.key_repeat_timer -= 1 / 60


death_menu = DeathMenu(["Начать игру заново", "Выйти в меню"], menu)


class PauseMenu(Menu):
    def __init__(self, options, main_menu):
        super().__init__(options)
        self.main_menu = main_menu
        self.menu_active = True
        self.enter_pressed = False
        self.font = pygame.font.Font(None, 57)

    def draw_menu(self, screen):
        screen.fill((0, 0, 0))
        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("Пауза", True, (255, 255, 255))
        screen.blit(title_text, (screen_width // 2 - title_text.get_width() // 2, 400))

        for i, option in enumerate(self.options):
            text = self.font.render(
                option,
                True,
                (255, 255, 255) if i == self.selected_option else (128, 128, 128),
            )
            text_rect = text.get_rect(center=(screen_width // 2, 700 + i * 50))
            screen.blit(text, text_rect)

    def handle_input(self, keys):
        super().handle_input(keys)

        if keys[pygame.K_RETURN]:
            self.enter_pressed = True
        elif self.enter_pressed:
            self.enter_pressed = False

            if self.options[self.selected_option] == "Выйти в меню":
                self.menu_active = False
                self.main_menu.menu_active = True
                global menu
                menu = self.main_menu


pause_menu = PauseMenu(["Выйти в меню"], menu)


class LevelCompletionMenu(Menu):
    def __init__(self, options, main_menu):
        super().__init__(options)
        self.main_menu = main_menu
        self.menu_active = True
        self.options = options
        self.enter_pressed = False

    def draw_menu(self, screen):
        screen.fill((0, 0, 0))
        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("Вы прошли уровень", True, (255, 255, 255))
        screen.blit(
            title_text, (screen_width // 2 - title_text.get_width() // 2, 400)
        )

        for i, option in enumerate(self.options):
            text = self.font.render(
                option,
                True,
                (255, 255, 255) if i == self.selected_option else (128, 128, 128),
            )
            text_rect = text.get_rect(center=(screen_width // 2, 700 + i * 50))
            screen.blit(text, text_rect)

    def handle_input(self, keys):
        if keys[pygame.K_UP]:
            self.handle_key_repeat(pygame.K_UP)
        if keys[pygame.K_DOWN]:
            self.handle_key_repeat(pygame.K_DOWN)

        super().handle_input(keys)

        if keys[pygame.K_RETURN]:
            self.enter_pressed = True
        elif self.enter_pressed:
            self.enter_pressed = False

            if (
                self.options[self.selected_option] == "Выйти в меню"
                and not self.menu_active
            ):
                self.menu_active = False
                self.main_menu.menu_active = True
                global menu
                menu = self.main_menu


level_completion_menu = LevelCompletionMenu(["Выйти в меню"], menu)


# Основной цикл игры
level_duration = 30  # 3 минуты
level_start_time = 0
level_completed = False
running = True
mouse_button_pressed = False
menu.menu_active = True
pygame.mouse.set_visible(False)
paused = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            paused = not paused

    keys = pygame.key.get_pressed()  # Получение состояния всех клавиш

    if not paused:
        if menu.menu_active:
            menu.handle_input(keys)
            menu.draw_menu(screen)
            pygame.display.flip()

            if keys[pygame.K_RETURN]:
                if menu.options[menu.selected_option] == "Начать игру":
                    menu.menu_active = False
                    level_start_time = pygame.time.get_ticks() / 1000
                elif menu.options[menu.selected_option] == "Выбор уровня":
                    menu = level_menu
                elif menu.options[menu.selected_option] == "Настройки":
                    menu = settings_menu
                elif menu.options[menu.selected_option] == "Выход":
                    pygame.quit()
                    sys.exit()
        elif player.is_alive():
            # Сохранение текущей позиции персонажа
            prev_x, prev_y = player.rect.x, player.rect.y
            # Обработка клавиш для перемещения персонажа
            if keys[pygame.K_w]:
                if player.rect.y - player.speed >= boundary_y:
                    player.rect.y -= player.speed
            if keys[pygame.K_s]:
                if player.rect.y + player.speed <= boundary_y + location_height - 40:
                    player.rect.y += player.speed
            if keys[pygame.K_a]:
                if player.rect.x - player.speed >= boundary_x:
                    player.rect.x -= player.speed
            if keys[pygame.K_d]:
                if player.rect.x + player.speed <= boundary_x + location_width - 40:
                    player.rect.x += player.speed

            check_enemy_collisions_with_player(enemies_group, player)
            check_enemy_collisions(enemies_group)

            camera_x = player.rect.x - screen_width // 2
            camera_y = player.rect.y - screen_height // 2

            for health_pack in health_packs_group.copy():
                if player.rect.colliderect(health_pack.rect):
                    health_pack.heal_player(player)

            for health_pack in health_packs_group.copy():
                if player.rect.colliderect(health_pack.rect):
                    health_pack.heal_player(player)

            for portal in portals_group:
                if player.rect.colliderect(portal.rect):
                    portal.teleport_player(player)

            # Генерация ядовитых зон
            poison_zone_spawn_timer += 1 / 60
            if poison_zone_spawn_timer >= poison_zone_spawn_interval:
                # Проверка лимита на количество ядовитых зон
                num_poison_zones = random.randint(
                    1, 100
                )  # Рандомное количество ядовитых зон от 1 до 5 (можете настроить по вашему желанию)

                for _ in range(num_poison_zones):
                    poison_zone = PoisonZone(
                        boundary_x + random.randint(0, location_width - 40),
                        boundary_y + random.randint(0, location_height - 40),
                    )

                    poison_zones_group.add(poison_zone)
                    poison_zone_spawn_timer = 0  # Сбрасываем таймер

            # Обновление ядовитых зон
            poison_zones_group.update()

            # Проверка нахождения персонажа в ядовитых зонах и нанесение урона
            for poison_zone in pygame.sprite.spritecollide(
                player, poison_zones_group, False
            ):
                player.take_damage(poison_zone.damage_per_second / 60)
            poison_zones_group.update()

            bullet_spawn_timer += (
                1 / 60
            )

            if bullet_spawn_timer >= bullet_spawn_frequency:
                bullet_x, bullet_y = player.rect.center
                direction = (1, 0)
                bullet = Bullet(bullet_x, bullet_y, direction)
                bullets_group.add(bullet)
                bullet_spawn_timer = 0
            for bullet in bullets_group:
                bullet.update()

            for enemy in enemies_group:
                if enemy.attack_cooldown > 0:
                    enemy.attack_cooldown -= 1

            for enemy in enemies_group:
                enemy.move_towards_player(player)
                if not enemy.is_alive():
                    enemies_group.remove(enemy)
                    if len(enemies_group) < num_enemies:
                        spawn_enemy(enemy)
                enemy.update_boundary(boundary.rect)

            # Центрирование камеры на персонаже
            camera_x = player.rect.x - screen_width // 2
            camera_y = player.rect.y - screen_height // 2

            # Очистка экрана
            screen.fill((255, 255, 255))

            # Отрисовка границы локации
            screen.blit(
                boundary.image, (boundary.rect.x - camera_x, boundary.rect.y - camera_y)
            )
            for health_pack in health_packs_group:
                screen.blit(
                    health_pack.image,
                    (health_pack.rect.x - camera_x, health_pack.rect.y - camera_y),
                )
            for portal in portals_group:
                screen.blit(
                    portal.image, (portal.rect.x - camera_x, portal.rect.y - camera_y)
                )
            for poison_zone in poison_zones_group:
                screen.blit(
                    poison_zone.image,
                    (poison_zone.rect.x - camera_x, poison_zone.rect.y - camera_y),
                )
            # Отрисовка врагов
            for enemy in enemies_group:
                screen.blit(
                    enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y)
                )

            # Отрисовка персонажа (с учетом позиции камеры)
            screen.blit(
                player.image, (player.rect.x - camera_x, player.rect.y - camera_y)
            )

            player_health = player.health
            max_player_health = 100  # Максимальное значение здоровья персонажа
            Character.draw_health_bar(
                screen,
                player.rect.x - camera_x,
                player.rect.y - camera_y - 20,
                player_health,
                max_player_health,
            )
            for bullet in bullets_group:
                screen.blit(
                    bullet.image, (bullet.rect.x - camera_x, bullet.rect.y - camera_y)
                )

            for bullet in bullets_group:
                for enemy in enemies_group:
                    if pygame.sprite.collide_rect(bullet, enemy):
                        enemy.hit_by_bullet()  # Вызываем новый метод при попадании пули во врага
                        bullets_group.remove(bullet)  # Удаление пули

            # Если пуля не попала во врага и улетела, удалите её
            for bullet in bullets_group.copy():
                if (
                    bullet.rect.x < 0
                    or bullet.rect.x > screen_width
                    or bullet.rect.y < 0
                    or bullet.rect.y > screen_height
                    or bullet.lifespan <= 0
                ):
                    bullets_group.remove(bullet)

            draw_kill_count(kill_count, screen)

            # Обновление таймера
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - start_time) / 1000  # в секундах
            game_timer += elapsed_time
            start_time = current_time

            # Отображение таймера на экране
            draw_timer(game_timer, screen)

            # Проверка, достигнута ли продолжительность уровня
            current_time = pygame.time.get_ticks() / 1000
            elapsed_time = current_time - level_start_time
            if elapsed_time >= level_duration and not level_completed:
                level_completion_menu.handle_input(keys)
                level_completion_menu.draw_menu(screen)
                pygame.display.flip()
                if keys[pygame.K_RETURN]:
                    if level_completion_menu.options[level_completion_menu.selected_option] == "Выйти в меню":
                        level_completion_menu.menu_active = False
                        menu.menu_active = True
                        kill_count = 0
                        game_timer = 0
        else:
            death_menu.handle_input(keys)
            death_menu.draw_menu(screen)
            pygame.display.flip()

            if keys[pygame.K_RETURN]:
                if (
                    death_menu.options[death_menu.selected_option]
                    == "Начать игру заново"
                ):
                    player = Character("Игрок", health=100)
                    game_timer = 0
                    kill_count = 0
                elif death_menu.options[death_menu.selected_option] == "Выйти в меню":
                    death_menu.menu_active = False
                    menu.menu_active = True
                    game_timer = 0
                    kill_count = 0

    else:
        pause_menu.handle_input(keys)
        pause_menu.draw_menu(screen)
        pygame.display.flip()

    # Обновление экрана
    pygame.display.flip()
    clock.tick(60)

# Завершение Pygame
pygame.quit()
sys.exit()
