import pygame


class Windmill:

    def __init__(self, x, y):

        self.frames = [

            pygame.image.load(
                "images/windmill1.png"
            ).convert_alpha(),

            pygame.image.load(
                "images/windmill2.png"
            ).convert_alpha(),

            pygame.image.load(
                "images/windmill3.png"
            ).convert_alpha(),

            pygame.image.load(
                "images/windmill4.png"
            ).convert_alpha()
        ]

        self.frames = [

            pygame.transform.scale(img, (120, 180))

            for img in self.frames
        ]

        self.frame = 0

        self.image = self.frames[0]

        self.rect = self.image.get_rect(
            center=(x, y)
        )

        self.anim_timer = 0

    def update(self):

        self.anim_timer += 1

        if self.anim_timer >= 12:

            self.anim_timer = 0

            self.frame += 1

            if self.frame >= len(self.frames):
                self.frame = 0

            self.image = self.frames[self.frame]

    def draw(self, screen, camera_x, camera_y):

        screen.blit(

            self.image,

            (
                self.rect.x - camera_x,
                self.rect.y - camera_y
            )
        )