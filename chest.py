import pygame


class Chest:

    def __init__(self, x, y):

        self.image = pygame.image.load(
            "images/chest.png"
        ).convert_alpha()

        self.image = pygame.transform.scale(
            self.image,
            (140, 80)
        )

        self.rect = self.image.get_rect(
            topleft=(x, y)
        )

        self.items = [None] * 12

    def draw(self, screen):

        screen.blit(
            self.image,
            self.rect
        )