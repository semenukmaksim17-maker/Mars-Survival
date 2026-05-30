import pygame
import random
from math import sin


class Rover:

    def __init__(self, game, x, y):

        self.game = game

        self.images = {

            "up": pygame.transform.scale(

                pygame.image.load(
                    "images/car_up.png"
                ).convert_alpha(),

                (100, 110)
            ),

            "down": pygame.transform.scale(

                pygame.image.load(
                    "images/car_down.png"
                ).convert_alpha(),

                (100, 110)
            ),

            "left": pygame.transform.scale(

                pygame.image.load(
                    "images/car_left.png"
                ).convert_alpha(),

                (160, 120)
            ),

            "right": pygame.transform.scale(

                pygame.image.load(
                    "images/car_right.png"
                ).convert_alpha(),

                (150, 110)
            )
        }

        self.direction = "down"

        self.image = self.images[self.direction]

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.speed = 1.7
        self.break_chance = 4

        self.in_rover = False

        self.broken = False

        self.break_timer = 0

        self.sound = pygame.mixer.Sound(
            "sounds/car.mp3"
        )

        self.channel = pygame.mixer.Channel(5)

    def handle_event(self, event):

        if event.type != pygame.KEYDOWN:
            return

        if event.key != pygame.K_e:
            return

        player = self.game.player

        near = player.rect.colliderect(
            self.rect.inflate(120, 120)
        )

        if not near:
            return

        if self.broken:

            battery = self.game.inventory_slots.count(
                "battery"
            )

            wire = self.game.inventory_slots.count(
                "wire"
            )

            if battery >= 1 and wire >= 2:

                removed = 0

                for i in range(len(self.game.inventory_slots)):

                    if self.game.inventory_slots[i] == "battery":

                        self.game.inventory_slots[i] = None
                        break

                for i in range(len(self.game.inventory_slots)):

                    if self.game.inventory_slots[i] == "wire":

                        self.game.inventory_slots[i] = None

                        removed += 1

                        if removed == 2:
                            break

                self.broken = False

            return

        self.in_rover = not self.in_rover

        if self.in_rover:

            self.channel.play(
                self.sound,
                loops=-1
            )

        else:

            self.channel.stop()

    def update(self):

        keys = pygame.key.get_pressed()

        if self.in_rover and not self.broken:

            moved = False

            if keys[pygame.K_w]:
                self.rect.y -= self.speed
                self.direction = "up"
                moved = True

            if keys[pygame.K_s]:
                self.rect.y += self.speed
                self.direction = "down"
                moved = True

            if keys[pygame.K_a]:
                self.rect.x -= self.speed
                self.direction = "left"
                moved = True

            if keys[pygame.K_d]:
                self.rect.x += self.speed
                self.direction = "right"
                moved = True

            self.image = self.images[self.direction]

            self.game.player.rect.center = self.rect.center

            if moved:

                self.break_timer += 1

                if self.break_timer >= 500:

                    self.break_timer = 0

                    if random.randint(
                            1,
                            self.break_chance
                    ) == 1:

                        self.broken = True

                        self.in_rover = False

                        self.channel.stop()

    def draw(self, screen, camera_x, camera_y):

        screen.blit(

            self.image,

            (
                self.rect.x - camera_x,
                self.rect.y - camera_y
            )
        )

        player = self.game.player

        near = player.rect.colliderect(
            self.rect.inflate(120, 120)
        )

        if near:

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                18
            )

            if self.broken:

                text = "1 battery + 2 wire"

            elif self.in_rover:

                text = "Вийти E"

            else:

                text = "Натисніть E"

            offset = int(
                sin(self.game.float_time) * 5
            )

            w = font.render(
                text,
                False,
                (255, 255, 255)
            ).get_width()

            self.game.draw_text_outline(

                text,

                self.rect.centerx -
                camera_x - w // 2,

                self.rect.y -
                camera_y - 40 + offset
            )