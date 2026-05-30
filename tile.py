import pygame

class Player:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.speed = 1

        self.direction = "down"

        self.step_timer = 0
        self.is_moving = False

        self.max_energy = 100
        self.energy = 100

        # 🔥 анимации
        self.animations = {
            "down": [
                pygame.image.load("Player_Animations/down_0.png").convert_alpha(),
                pygame.image.load("Player_Animations/down_1.png").convert_alpha(),
                pygame.image.load("Player_Animations/down_2.png").convert_alpha(),
            ],
            "up": [
                pygame.image.load("Player_Animations/up_0.png").convert_alpha(),
                pygame.image.load("Player_Animations/up_1.png").convert_alpha(),
                pygame.image.load("Player_Animations/up_2.png").convert_alpha(),
            ],
            "left": [
                pygame.image.load("Player_Animations/left_0.png").convert_alpha(),
                pygame.image.load("Player_Animations/left_1.png").convert_alpha(),
                pygame.image.load("Player_Animations/left_2.png").convert_alpha(),
            ],
            "right": [
                pygame.image.load("Player_Animations/right_0.png").convert_alpha(),
                pygame.image.load("Player_Animations/right_1.png").convert_alpha(),
                pygame.image.load("Player_Animations/right_2.png").convert_alpha(),
            ],
        }

        self.frame_index = 0
        self.anim_timer = 0
        self.direction = "down"

    def update(self, keys):
        dx = 0
        dy = 0

        moving = False

        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.direction = "left"
            moving = True

        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.direction = "right"
            moving = True

        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            self.direction = "up"
            moving = True

        if keys[pygame.K_s]:
            self.rect.y += self.speed
            self.direction = "down"
            moving = True

        # --- АНИМАЦИЯ ---
        if moving:

            self.step_timer += 1
            if self.step_timer >= 25:
                self.step_timer = 0
            self.anim_timer += 1

            if self.anim_timer >= 25:  # скорость анимации
                self.anim_timer = 0
                self.frame_index += 1

                if self.frame_index >= len(self.animations[self.direction]):
                    self.frame_index = 0
        else:
            self.frame_index = 0

        self.is_moving = moving

    def get_frame(self):

        frames = self.animations[self.direction]

        index = int(self.frame_index) % len(frames)

        return frames[index]


class Resource:
    def __init__(self, x, y, resource_type):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.type = resource_type

        # 🔥 картинки для разных ресурсов
        self.images = {
            "iron": pygame.transform.scale(pygame.image.load("resources/iron.png").convert_alpha(), (50, 50)),
            "scrap": pygame.transform.scale(pygame.image.load("resources/scrap.png").convert_alpha(), (50, 50)),
            "copper": pygame.transform.scale(pygame.image.load("resources/copper.png").convert_alpha(), (50, 50)),
            "energy": pygame.transform.scale(pygame.image.load("resources/energy.png").convert_alpha(), (50, 50)),
            "crystal": pygame.transform.scale(pygame.image.load("resources/crystal.png").convert_alpha(), (50, 50)),
            "uranium": pygame.transform.scale(pygame.image.load("resources/uranium.png").convert_alpha(), (50, 50)),
        }
        self.image = self.images[self.type]


    def draw(self, screen, camera_x, camera_y):
        screen.blit(
            self.image,
            (
                self.rect.x - camera_x,
                self.rect.y - camera_y
            )
        )

class Base:
    def __init__(self):
        self.rect = pygame.Rect(350, 250, 100, 100)
        self.level = 1

    def draw(self, screen):
        pygame.draw.rect(screen, (200, 200, 0), self.rect)

class Windmill:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 200, 200), self.rect)