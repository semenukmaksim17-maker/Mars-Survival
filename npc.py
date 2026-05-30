import pygame
from math import sin


class NPC:

    def __init__(self, game, x, y):

        self.game = game

        self.image = pygame.image.load(
            "images/npc.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (80, 110)
        )

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.float_time = 0

        self.opened = False

        self.buttons = []

        self.upgrades = [

            ["Oxygen I", 2, 1, False],
            ["Oxygen II", 4, 2, False],

            ["Mining", 3, 1, False],

            ["Rover Speed", 3, 2, False],

            ["Storm Shield", 4, 2, False],

            ["Night Shield", 4, 2, False],

            ["Rover Armor", 5, 3, False]

        ]

    def buy_upgrade(self, index):

        upgrade = self.upgrades[index]

        if upgrade[3]:
            return

        crystal_need = upgrade[1]
        uranium_need = upgrade[2]

        crystal = self.game.inventory_slots.count(
            "crystal"
        )

        uranium = self.game.inventory_slots.count(
            "uranium"
        )

        if crystal < crystal_need:
            return

        if uranium < uranium_need:
            return

        removed = 0

        for i in range(len(self.game.inventory_slots)):

            if self.game.inventory_slots[i] == "crystal":

                self.game.inventory_slots[i] = None

                removed += 1

                if removed == crystal_need:
                    break

        removed = 0

        for i in range(len(self.game.inventory_slots)):

            if self.game.inventory_slots[i] == "uranium":

                self.game.inventory_slots[i] = None

                removed += 1

                if removed == uranium_need:
                    break

        upgrade[3] = True

        if index == 0:

            self.game.player.max_energy += 25
            self.game.player.energy = self.game.player.max_energy


        elif index == 1:

            self.game.player.max_energy += 25
            self.game.player.energy = self.game.player.max_energy

        elif index == 2:

            self.game.mine_time_needed = max(
                10,
                self.game.mine_time_needed - 20
            )

        elif index == 3:

            self.game.rover.speed += 0.8

        elif index == 4:

            self.game.storm_damage *= 0.5

        elif index == 5:

            self.game.night_damage *= 0.5

        elif index == 6:

            self.game.rover.break_chance = 7

    def handle_event(self, event):

        player = self.game.player

        near = player.rect.colliderect(
            self.rect.inflate(120, 120)
        )

        if not near:
            return

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:

                self.opened = not self.opened
                return

        if not self.opened:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button != 1:
                return

            mx, my = pygame.mouse.get_pos()

            for i, button in enumerate(self.buttons):

                if button.collidepoint(mx, my):

                    self.buy_upgrade(i)

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

        self.float_time += 0.05

        if near and not self.opened:

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                18
            )

            text = font.render(
                "Натисніть R",
                False,
                (255, 255, 255)
            )

            outline = font.render(
                "Натисніть R",
                False,
                (0, 0, 0)
            )

            offset = int(
                sin(self.float_time) * 5
            )

            x = (
                self.rect.centerx -
                camera_x -
                text.get_width() // 2
            )

            y = (
                self.rect.y -
                camera_y -
                35 +
                offset
            )

            for dx in range(-2, 3):
                for dy in range(-2, 3):

                    if dx != 0 or dy != 0:

                        screen.blit(
                            outline,
                            (x + dx, y + dy)
                        )

            screen.blit(
                text,
                (x, y)
            )

        if self.opened:

            panel = pygame.Rect(
                10,
                50,
                780,
                410
            )

            pygame.draw.rect(
                screen,
                (20, 20, 20),
                panel
            )

            pygame.draw.rect(
                screen,
                (120, 120, 120),
                panel,
                4
            )

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                18
            )

            title_font = pygame.font.Font(
                "fonts/pixel.ttf",
                24
            )

            title = title_font.render(
                "UPGRADES",
                False,
                (255, 255, 255)
            )

            screen.blit(
                title,
                (
                    panel.centerx -
                    title.get_width() // 2,
                    70
                )
            )

            self.buttons = []

            y = 125

            for i, upgrade in enumerate(self.upgrades):

                bought = upgrade[3]

                text = font.render(
                    upgrade[0],
                    False,
                    (255, 255, 255)
                )

                screen.blit(
                    text,
                    (40, y)
                )

                price = font.render(
                    f"{upgrade[1]} Crystal | {upgrade[2]} Uranium",
                    False,
                    (180, 220, 255)
                )

                screen.blit(
                    price,
                    (285, y)
                )

                button = pygame.Rect(
                    680,
                    y - 4,
                    100,
                    30
                )

                self.buttons.append(button)

                color = (
                    (40, 140, 40)
                    if not bought else
                    (70, 70, 70)
                )

                pygame.draw.rect(
                    screen,
                    color,
                    button
                )

                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    button,
                    2
                )

                button_text = font.render(
                    "BUY" if not bought else "DONE",
                    False,
                    (255, 255, 255)
                )

                screen.blit(
                    button_text,
                    (
                        button.centerx -
                        button_text.get_width() // 2,

                        button.centery -
                        button_text.get_height() // 2
                    )
                )

                y += 45