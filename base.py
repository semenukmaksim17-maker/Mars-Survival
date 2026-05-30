import pygame
from config import WIDTH, HEIGHT, FPS
from tile import Player, Resource, Base
import random
from math import sin
from chest import Chest
from rover import Rover
from npc import NPC
from windmill import Windmill


class Game:

    def __init__(self):

        # важное

        self.running = True

        self.mining = False
        self.mining_target = None
        self.mine_timer = 0
        self.mine_time_needed = 60

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Mars Game")
        pygame.mixer.init()

        self.pickup_sound = pygame.mixer.Sound("sounds/pickup.mp3")
        self.craft_sound = pygame.mixer.Sound("sounds/craft.mp3")
        self.door_sound = pygame.mixer.Sound("sounds/door.mp3")
        self.win_sound = pygame.mixer.Sound("sounds/win.mp3")
        self.step_sound = pygame.mixer.Sound("sounds/walk.mp3")

        self.pickup_sound.set_volume(0.4)
        self.craft_sound.set_volume(0.5)
        self.door_sound.set_volume(0.6)
        self.win_sound.set_volume(0.8)
        self.step_sound.set_volume(0.2)

        self.earth = pygame.image.load(
            "images/earth.png"
        ).convert_alpha()

        self.earth = pygame.transform.scale(
            self.earth,
            (900, 900)
        )

        self.step_channel = pygame.mixer.Channel(1)

        self.clock = pygame.time.Clock()

        self.scene = "menu"

        self.dead = False

        self.paused = False

        self.day_time = 0

        self.day_length = 120

        self.is_night = False

        self.play_button = pygame.Rect(
            WIDTH // 2 - 150,
            HEIGHT - 100,
            300,
            80
        )

        self.chests = [

            Chest(420, 70),

            Chest(560, 70)
        ]

        self.opened_chest = None
        self.near_chest = None
        self.slots = [None] * 12

        self.map = pygame.image.load("scenes/map.png").convert()
        self.map = pygame.transform.scale(self.map, (3000, 3000))

        self.base_inside_img = pygame.image.load(
            "scenes/base_inside.png"
        ).convert_alpha()

        self.base_inside_img = pygame.transform.scale(
            self.base_inside_img,
            (WIDTH, HEIGHT)
        )

        self.inside_spawn = (
            WIDTH // 2,
            HEIGHT - 120
        )

        self.base_walls = [

            pygame.Rect(0, 0, WIDTH, 40),

            pygame.Rect(
                0,
                HEIGHT - 40,
                WIDTH // 2 - 60,
                40
            ),

            pygame.Rect(
                WIDTH // 2 + 60,
                HEIGHT - 40,
                WIDTH // 2 - 60,
                40
            ),

            pygame.Rect(0, 0, 40, HEIGHT),

            pygame.Rect(
                WIDTH - 40,
                0,
                40,
                HEIGHT
            )
        ]

        self.camera_x = 0
        self.camera_y = 0

        self.inventory_open = False

        self.inventory_slots = [None] * 27

        self.drag_item = None
        self.drag_from = None

        self.craft_grid = [None, None, None, None]

        self.result_item = None

        self.result_rect = pygame.Rect(
            0,
            0,
            60,
            60
        )

        self.float_time = 0

        self.pickup_target = None

        self.near_door = False

        self.near_rocket = False

        self.rocket_fixed = False

        map_w = self.map.get_width()
        map_h = self.map.get_height()

        self.base = Base()

        self.base.rect.center = (
            map_w // 2,
            map_h // 2
        )

        self.base_img = pygame.image.load(
            "scenes/base.png"
        ).convert_alpha()

        self.base_img = pygame.transform.scale(
            self.base_img,
            (1000, 1000)
        )

        self.base_draw_x = (
            self.base.rect.x -
            self.base_img.get_width() // 2
        )

        self.base_draw_y = (
            self.base.rect.y -
            self.base_img.get_height() // 2
        )

        self.base_collision_center = (
            self.base_draw_x + 485,
            self.base_draw_y + 470
        )

        self.base_collision_radius = 150

        self.base_door_rect = pygame.Rect(
            self.base.rect.centerx - 40,
            self.base.rect.bottom - 20,
            80,
            40
        )

        self.player = Player()

        self.player.rect.center = (
            self.base.rect.centerx,
            self.base.rect.bottom + 40
        )

        self.rover = Rover(

            self,

            self.base.rect.centerx + 350,
            self.base.rect.centery + 220
        )

        self.npc = NPC(
            self,
            240,
            260
        )

        self.resources = []

        types = [
            "iron",
            "scrap",
            "copper",
            "energy",
            "crystal",
            "uranium"
        ]

        for _ in range(60):

            x = random.randint(0, map_w)
            y = random.randint(0, map_h)

            self.resources.append(
                Resource(
                    x,
                    y,
                    random.choice(types)
                )
            )

        self.recipes = {

            ("battery", "plate"): "windmill",

            ("iron", "iron"): "plate",

            ("copper", "energy"): "battery",

            ("iron", "scrap"): "wire"
        }

        self.windmills = []

        self.craft_slots = [
            pygame.Rect(0, 0, 50, 50)
            for _ in range(4)
        ]

        self.rocket = pygame.image.load(
            "images/rocket.png"
        ).convert_alpha()

        self.rocket_pos = (
            self.base.rect.centerx + 120,
            self.base.rect.centery - 80
        )

        self.sandstorm = False
        self.sandstorm_timer = 0
        self.sandstorm_duration = 0

        self.storm_damage = 0.8
        self.night_damage = 6

        self.rover.break_chance = 4

        self.sand_particles = []

    def draw_text_outline(self, text, x, y):

        font = pygame.font.Font(
            "fonts/pixel.ttf",
            18
        )

        base = font.render(
            text,
            False,
            (255, 255, 255)
        )

        outline = font.render(
            text,
            False,
            (0, 0, 0)
        )

        for dx in range(-2, 3):
            for dy in range(-2, 3):

                if dx != 0 or dy != 0:
                    self.screen.blit(
                        outline,
                        (x + dx, y + dy)
                    )

        self.screen.blit(
            base,
            (x, y)
        )

    def draw_inventory(self):

        slot = 50
        pad = 5

        panel_w = 700
        panel_h = 400

        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = HEIGHT // 2 - panel_h // 2 - 20

        pygame.draw.rect(
            self.screen,
            (25, 25, 25),
            (panel_x, panel_y, panel_w, panel_h)
        )

        frame = pygame.transform.scale(
            self.player.get_frame(),
            (120, 120)
        )

        self.screen.blit(
            frame,
            (panel_x + 45, panel_y + 35)
        )

        inv_x = panel_x + 30
        inv_y = panel_y + panel_h - 170

        self.inv_rects = []

        for i in range(27):

            x = inv_x + (i % 9) * (slot + pad)
            y = inv_y + (i // 9) * (slot + pad)

            rect = pygame.Rect(
                x,
                y,
                slot,
                slot
            )

            self.inv_rects.append(rect)

            pygame.draw.rect(
                self.screen,
                (70, 70, 70),
                rect
            )

            item = self.inventory_slots[i]

            if item:

                img = pygame.transform.scale(
                    pygame.image.load(
                        f"resources/{item}.png"
                    ).convert_alpha(),
                    (32, 32)
                )

                self.screen.blit(
                    img,
                    (x + 9, y + 5)
                )

        craft_x = panel_x + panel_w - 220
        craft_y = panel_y + 60

        result_x = craft_x + 140
        result_y = craft_y + 25

        self.result_rect = pygame.Rect(
            result_x,
            result_y,
            60,
            60
        )

        pygame.draw.rect(
            self.screen,
            (120, 120, 120),
            self.result_rect
        )

        if self.result_item:

            img = pygame.transform.scale(
                pygame.image.load(
                    f"resources/{self.result_item}.png"
                ).convert_alpha(),
                (40, 40)
            )

            self.screen.blit(
                img,
                (result_x + 10, result_y + 10)
            )

        for i in range(2):
            for j in range(2):

                index = i * 2 + j

                x = craft_x + j * (slot + pad)
                y = craft_y + i * (slot + pad)

                rect = pygame.Rect(
                    x,
                    y,
                    slot,
                    slot
                )

                self.craft_slots[index] = rect

                pygame.draw.rect(
                    self.screen,
                    (100, 100, 100),
                    rect
                )

                item = self.craft_grid[index]

                if item:

                    img = pygame.transform.scale(
                        pygame.image.load(
                            f"resources/{item}.png"
                        ).convert_alpha(),
                        (32, 32)
                    )

                    self.screen.blit(
                        img,
                        (x + 9, y + 5)
                    )

        if self.drag_item:

            mx, my = pygame.mouse.get_pos()

            img = pygame.transform.scale(
                pygame.image.load(
                    f"resources/{self.drag_item}.png"
                ).convert_alpha(),
                (32, 32)
            )

            self.screen.blit(
                img,
                (mx - 16, my - 16)
            )

    def run(self):

        while self.running:

            self.events()
            self.update()
            self.draw()

            self.clock.tick(FPS)
    def events(self):

        for event in pygame.event.get():

            self.npc.handle_event(event)

            if self.npc.opened:

                if event.type != pygame.KEYDOWN:
                    continue

                if event.key != pygame.K_r:
                    continue

            self.rover.handle_event(event)

            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.mining = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mining = False
                    self.mining_target = None

            if self.scene == "menu":

                if event.type == pygame.MOUSEBUTTONDOWN:

                    mx, my = pygame.mouse.get_pos()

                    if self.play_button.collidepoint(mx, my):
                        self.scene = "world"

                continue

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_f:

                    if "windmill" in self.inventory_slots:

                        for i in range(len(self.inventory_slots)):

                            if self.inventory_slots[i] == "windmill":
                                self.inventory_slots[i] = None
                                break

                        self.windmills.append(

                            Windmill(

                                self.base.rect.centerx + 180,
                                self.base.rect.centery
                            )
                        )

                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused

                if event.key == pygame.K_TAB:
                    self.inventory_open = not self.inventory_open

                if event.key == pygame.K_q:

                    if self.near_chest:

                        if self.opened_chest == self.near_chest:
                            self.opened_chest = None

                        else:
                            self.opened_chest = self.near_chest

                if event.key == pygame.K_e:

                    if self.scene == "world" and self.near_door:

                        self.door_sound.play()
                        self.scene = "base_inside"

                        self.player.rect.center = (
                            self.inside_spawn
                        )

                        return


                    elif self.scene == "base_inside":

                        self.scene = "world"

                        self.player.rect.center = (

                            self.base.rect.centerx,

                            self.base.rect.bottom + 60

                        )

                        self.near_door = False

                        self.near_rocket = False

                    if self.near_rocket and not self.rocket_fixed:

                        wire_count = self.inventory_slots.count("wire")
                        plate_count = self.inventory_slots.count("plate")
                        battery_count = self.inventory_slots.count("battery")

                        if (
                            wire_count >= 3 and
                            plate_count >= 3 and
                            battery_count >= 2
                        ):

                            removed = 0

                            for i in range(len(self.inventory_slots)):

                                if self.inventory_slots[i] == "wire":

                                    self.inventory_slots[i] = None

                                    removed += 1

                                    if removed == 3:
                                        break

                            removed = 0

                            for i in range(len(self.inventory_slots)):

                                if self.inventory_slots[i] == "plate":

                                    self.inventory_slots[i] = None

                                    removed += 1

                                    if removed == 3:
                                        break

                            removed = 0

                            for i in range(len(self.inventory_slots)):

                                if self.inventory_slots[i] == "battery":

                                    self.inventory_slots[i] = None

                                    removed += 1

                                    if removed == 2:
                                        break

                            self.rocket_fixed = True
                            self.win_sound.play()

            if self.inventory_open:

                if self.opened_chest:

                    if (
                            event.type == pygame.MOUSEBUTTONDOWN and
                            event.button == 1
                    ):

                        mx, my = pygame.mouse.get_pos()

                        # ИЗ СУНДУКА
                        for i, rect in enumerate(self.chest_rects):

                            if (
                                    rect.collidepoint(mx, my)
                                    and
                                    self.opened_chest.items[i]
                            ):
                                self.drag_item = (
                                    self.opened_chest.items[i]
                                )

                                self.drag_from = (
                                    "chest",
                                    i
                                )

                                self.opened_chest.items[i] = None

                                return

                    if (
                            event.type == pygame.MOUSEBUTTONUP and
                            self.drag_item
                    ):

                        mx, my = pygame.mouse.get_pos()

                        # В СУНДУК
                        for i, rect in enumerate(self.chest_rects):

                            if rect.collidepoint(mx, my):

                                if self.opened_chest.items[i] is None:

                                    self.opened_chest.items[i] = (
                                        self.drag_item
                                    )

                                else:

                                    (
                                        self.opened_chest.items[i],
                                        self.drag_item
                                    ) = (
                                        self.drag_item,
                                        self.opened_chest.items[i]
                                    )

                                self.drag_item = None

                                return

                if (
                    event.type == pygame.MOUSEBUTTONDOWN and
                    event.button == 1
                ):

                    mx, my = pygame.mouse.get_pos()

                    if (
                        self.result_rect.collidepoint(mx, my)
                        and
                        self.result_item
                    ):

                        for i in range(len(self.inventory_slots)):

                            if self.inventory_slots[i] is None:

                                self.inventory_slots[i] = (
                                    self.result_item
                                )

                                self.craft_grid = [
                                    None,
                                    None,
                                    None,
                                    None
                                ]

                                self.result_item = None

                                return

                    for i, rect in enumerate(self.craft_slots):

                        if (
                            rect.collidepoint(mx, my)
                            and
                            self.craft_grid[i]
                        ):

                            self.drag_item = self.craft_grid[i]

                            self.drag_from = (
                                "craft",
                                i
                            )

                            self.craft_grid[i] = None

                            return

                    for i, rect in enumerate(self.inv_rects):

                        if (
                            rect.collidepoint(mx, my)
                            and
                            self.inventory_slots[i]
                        ):

                            self.drag_item = (
                                self.inventory_slots[i]
                            )

                            self.drag_from = (
                                "inv",
                                i
                            )

                            self.inventory_slots[i] = None

                            return

                if (
                    event.type == pygame.MOUSEBUTTONUP and
                    self.drag_item
                ):

                    mx, my = pygame.mouse.get_pos()

                    for i, rect in enumerate(self.inv_rects):

                        if rect.collidepoint(mx, my):

                            if self.inventory_slots[i] is None:

                                self.inventory_slots[i] = (
                                    self.drag_item
                                )

                            else:

                                (
                                    self.inventory_slots[i],
                                    self.drag_item
                                ) = (
                                    self.drag_item,
                                    self.inventory_slots[i]
                                )

                            self.drag_item = None

                            return

                    for i, rect in enumerate(self.craft_slots):

                        if rect.collidepoint(mx, my):

                            if self.craft_grid[i] is None:

                                self.craft_grid[i] = (
                                    self.drag_item
                                )

                            else:

                                (
                                    self.craft_grid[i],
                                    self.drag_item
                                ) = (
                                    self.drag_item,
                                    self.craft_grid[i]
                                )

                            self.drag_item = None

                            return

                    src_type, idx = self.drag_from

                    if src_type == "craft":

                        self.craft_grid[idx] = self.drag_item

                    else:

                        self.inventory_slots[idx] = (
                            self.drag_item
                        )

                    self.drag_item = None

    def update(self):

        if self.paused:
            return

        if self.scene == "menu":
            return

        dt = self.clock.get_time() / 1000

        keys = pygame.key.get_pressed()

        if self.npc.opened:
            self.player.is_moving = False
            return

        old_rect = self.player.rect.copy()

        if not self.rover.in_rover:
            self.player.update(keys)

        if self.rover.in_rover:
            self.player.is_moving = False

        if self.player.is_moving:

            self.player.step_timer += 1

            if self.player.step_timer >= 25:

                self.player.step_timer = 0

                if not self.step_channel.get_busy():
                    self.step_channel.play(self.step_sound)

        else:
            self.player.step_timer = 0

        self.day_time += dt

        if self.day_time >= self.day_length:
            self.day_time = 0

        self.is_night = self.day_time >= (
                self.day_length / 2
        )

        if self.scene == "base_inside":

            self.near_chest = None

            player_hitbox = self.player.rect.inflate(40, 40)

            for chest in self.chests:

                if player_hitbox.colliderect(chest.rect):
                    self.near_chest = chest

                    break

            for wall in self.base_walls:

                if self.player.rect.colliderect(wall):
                    self.player.rect = old_rect

                    break

            self.player.energy = min(
                self.player.energy + 5 * dt,
                self.player.max_energy
            )

            self.player.rect.x = max(
                0,
                min(
                    self.player.rect.x,
                    WIDTH - self.player.rect.width
                )
            )

            self.player.rect.y = max(
                0,
                min(
                    self.player.rect.y,
                    HEIGHT - self.player.rect.height
                )
            )

            self.camera_x = 0
            self.camera_y = 0

            return

        items = [i for i in self.craft_grid if i]

        if len(items) == 2:

            key = tuple(sorted(items))

            self.result_item = self.recipes.get(key)

        else:

            self.result_item = None

        if not self.inventory_open:
            self.player.energy -= 2 * dt

        if self.player.energy <= 0:
            self.player.energy = 0
            self.dead = True

        self.pickup_target = None

        for r in self.resources:

            if (
                self.player.rect.inflate(260, 260)
                .colliderect(r.rect)
            ):

                self.pickup_target = r

                break

        if self.mining and self.pickup_target:

            self.mining_target = self.pickup_target

            self.mine_timer += 1

            if self.mine_timer >= self.mine_time_needed:

                self.mine_timer = 0

                if self.mining_target in self.resources:

                    mined_type = self.mining_target.type

                    self.resources.remove(
                        self.mining_target
                    )

                    self.pickup_sound.play()

                    for i in range(len(self.inventory_slots)):

                        if self.inventory_slots[i] is None:
                            self.inventory_slots[i] = mined_type
                            break

                    self.mining = False
                    self.mining_target = None

        else:

            self.mine_timer = 0

        self.sandstorm_timer += dt
        for particle in self.sand_particles:
            particle[0] += 12

        if not self.sandstorm and self.sandstorm_timer >= 45:
            self.sandstorm = True

            self.sandstorm_duration = 8

            self.sandstorm_timer = 0

        if self.sandstorm:

            self.sandstorm_duration -= dt

            self.player.energy -= self.storm_damage * dt

            for _ in range(2):
                self.sand_particles.append([

                    random.randint(0, WIDTH),
                    random.randint(0, HEIGHT),

                    random.randint(1, 3)
                ])

            if self.sandstorm_duration <= 0:
                self.sandstorm = False
                self.sand_particles.clear()

        self.float_time += dt * 4

        self.near_door = self.player.rect.colliderect(
            self.base_door_rect
        )

        if self.is_night and self.scene != "base_inside":
            self.player.energy -= self.night_damage * dt

        rocket_rect = pygame.Rect(
            self.rocket_pos[0],
            self.rocket_pos[1],
            180,
            180
        )

        self.near_rocket = self.player.rect.colliderect(
            rocket_rect.inflate(80, 80)
        )

        cx, cy = self.base_collision_center

        target_rect = self.player.rect

        if self.rover.in_rover:
            target_rect = self.rover.rect

        dx_base = target_rect.centerx - cx
        dy_base = target_rect.centery - cy

        distance = (
                           dx_base ** 2 + dy_base ** 2
                   ) ** 0.5

        radius = self.base_collision_radius

        if self.rover.in_rover:
            radius += 40

        if distance < radius:

            if distance != 0:

                angle_x = dx_base / distance
                angle_y = dy_base / distance

                target_rect.centerx = (
                        cx + angle_x * radius
                )

                target_rect.centery = (
                        cy + angle_y * radius
                )

                if self.rover.in_rover:
                    self.player.rect.center = (
                        self.rover.rect.center
                    )

        self.player.rect.x = max(
            0,
            min(
                self.player.rect.x,
                self.map.get_width() -
                self.player.rect.width
            )
        )

        self.player.rect.y = max(
            0,
            min(
                self.player.rect.y,
                self.map.get_height() -
                self.player.rect.height
            )
        )

        target = self.player.rect

        if self.rover.in_rover:
            target = self.rover.rect

        self.camera_x = (
                target.x - WIDTH // 2
        )

        self.camera_y = (
                target.y - HEIGHT // 2
        )

        self.camera_x = max(
            0,
            min(
                self.camera_x,
                self.map.get_width() - WIDTH
            )
        )

        self.camera_y = max(
            0,
            min(
                self.camera_y,
                self.map.get_height() - HEIGHT
            )
        )

        self.rover.update()
        for windmill in self.windmills:
            windmill.update()

    def draw_chest(self):

        if not self.opened_chest:
            return

        panel = pygame.Rect(
            WIDTH // 2 - 220,
            HEIGHT // 2 - 140,
            440,
            280
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 30),
            panel
        )

        pygame.draw.rect(
            self.screen,
            (120, 120, 120),
            panel,
            4
        )

        font = pygame.font.Font(
            "fonts/pixel.ttf",
            20
        )

        text = font.render(
            "CHEST",
            False,
            (255, 255, 255)
        )

        self.screen.blit(
            text,
            (panel.x + 20, panel.y + 15)
        )

        slot_size = 50
        padding = 10

        self.chest_rects = []

        for i in range(12):

            x = panel.x + 20 + (i % 4) * (slot_size + padding)
            y = panel.y + 60 + (i // 4) * (slot_size + padding)

            rect = pygame.Rect(
                x,
                y,
                slot_size,
                slot_size
            )

            self.chest_rects.append(rect)

            pygame.draw.rect(
                self.screen,
                (70, 70, 70),
                rect
            )

            item = self.opened_chest.items[i]

            if item:
                img = pygame.transform.scale(
                    pygame.image.load(
                        f"resources/{item}.png"
                    ).convert_alpha(),
                    (32, 32)
                )

                self.screen.blit(
                    img,
                    (x + 9, y + 9)
                )
    def draw(self):

        if self.dead:
            self.screen.fill((0, 0, 0))

            font = pygame.font.Font("fonts/pixel.ttf", 42)

            text = font.render(
                "YOU DIED",
                False,
                (255, 0, 0)
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    HEIGHT // 2 - text.get_height() // 2
                )
            )

            pygame.display.flip()
            return

        if self.scene == "menu":

            self.screen.fill((10, 10, 15))

            title_font = pygame.font.Font(
                "fonts/pixel.ttf",
                42
            )

            text_font = pygame.font.Font(
                "fonts/pixel.ttf",
                12
            )

            title = title_font.render(
                "MARS SURVIVAL",
                False,
                (255, 255, 255)
            )

            self.screen.blit(
                title,
                (
                    WIDTH // 2 - title.get_width() // 2,
                    80
                )
            )

            pygame.draw.rect(
                self.screen,
                (40, 40, 40),
                self.play_button
            )

            pygame.draw.rect(
                self.screen,
                (255, 255, 255),
                self.play_button,
                4
            )

            play = text_font.render(
                "ГРАТИ",
                False,
                (255, 255, 255)
            )

            self.screen.blit(
                play,
                (
                    self.play_button.centerx -
                    play.get_width() // 2,

                    self.play_button.centery -
                    play.get_height() // 2
                )
            )

            left_instructions = [

                "WASD - рух",
                "TAB - інвентар",
                "E - взаємодія",
                "F - встановити вітряк",
                "R - апгрейди",

                "",

                "МЕТА:",

                "Озеленити Марс",
                "та полетіти додому",

                "",

                "РЕМОНТ РАКЕТИ:",

                "3 wire",
                "3 plate",
                "2 battery"
            ]

            right_instructions = [

                "КРАФТИ:",

                "iron + iron",
                "= plate",

                "",

                "scrap + iron",
                "= wire",

                "",

                "copper + energy",
                "= battery",

                "",

                "ВІТРЯК:",

                "battery + plate",
                "= windmill"
            ]

            left_y = 180

            for line in left_instructions:
                txt = text_font.render(
                    line,
                    False,
                    (180, 180, 180)
                )

                self.screen.blit(
                    txt,
                    (
                        120,
                        left_y
                    )
                )

                left_y += 20

            right_y = 180

            for line in right_instructions:
                txt = text_font.render(
                    line,
                    False,
                    (180, 180, 180)
                )

                self.screen.blit(
                    txt,
                    (
                        WIDTH - 340,
                        right_y
                    )
                )

                right_y += 20

            pygame.display.flip()

            return

        if self.scene == "base_inside":

            self.screen.blit(
                self.base_inside_img,
                (0, 0)
            )

            for chest in self.chests:
                chest.draw(self.screen)

            self.npc.draw(
                self.screen,
                0,
                0
            )

            if self.is_night:

                if len(self.resources) < 120:

                    if random.randint(1, 20) == 1:
                        types = [
                            "iron",
                            "scrap",
                            "copper",
                            "energy",
                            "crystal",
                            "uranium"
                        ]

                        x = random.randint(
                            0,
                            self.map.get_width()
                        )

                        y = random.randint(
                            0,
                            self.map.get_height()
                        )

                        self.resources.append(

                            Resource(
                                x,
                                y,
                                random.choice(types)
                            )
                        )

            if self.near_chest:
                text = "Відкрити Q"

                font = pygame.font.Font(
                    "fonts/pixel.ttf",
                    18
                )

                text_surface = font.render(
                    text,
                    False,
                    (255, 255, 255)
                )

                w = text_surface.get_width()

                self.draw_text_outline(
                    text,
                    self.near_chest.rect.centerx - w // 2,
                    self.near_chest.rect.y - 35
                )

            if not self.npc.opened:
                frame = pygame.transform.scale(
                    self.player.get_frame(),
                    (64, 64)
                )

                self.screen.blit(
                    frame,
                    (
                        self.player.rect.x - 32,
                        self.player.rect.y - 32
                    )
                )

            text = "Натисніть E для виходу"

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                24
            )

            w = font.render(
                text,
                False,
                (255, 255, 255)
            ).get_width()

            self.draw_text_outline(
                text,
                WIDTH // 2 - w // 2,
                HEIGHT - 50
            )

            if self.inventory_open:
                overlay = pygame.Surface((WIDTH, HEIGHT))

                overlay.set_alpha(60)

                overlay.fill((0, 0, 0))

                self.screen.blit(
                    overlay,
                    (0, 0)
                )

                self.draw_inventory()

            self.draw_chest()

            pygame.display.flip()

            return


        self.screen.blit(
            self.map,
            (
                -self.camera_x,
                -self.camera_y
            )
        )

        if len(self.windmills) > 0:
            size = 700

            earth = pygame.transform.scale(
                self.earth,
                (size, size)
            )

            self.screen.blit(

                earth,

                (
                    self.base.rect.centerx -
                    self.camera_x -
                    size // 2 - 120,

                    self.base.rect.centery -
                    self.camera_y -
                    size // 2
                )
            )

        for r in self.resources:

            r.draw(
                self.screen,
                self.camera_x,
                self.camera_y
            )

        self.screen.blit(
            self.base_img,
            (
                self.base.rect.x -
                self.camera_x -
                self.base_img.get_width() // 2,

                self.base.rect.y -
                self.camera_y -
                self.base_img.get_height() // 2
            )
        )

        for windmill in self.windmills:
            windmill.draw(
                self.screen,
                self.camera_x,
                self.camera_y
            )

        self.rover.draw(

            self.screen,
            self.camera_x,
            self.camera_y
        )

        if self.near_door:

            x = (
                self.base_door_rect.centerx -
                self.camera_x
            )

            y = (
                self.base_door_rect.y -
                self.camera_y
            )

            offset = int(
                sin(self.float_time) * 5
            )

            text = "Натисніть E"

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                18
            )

            w = font.render(
                text,
                False,
                (255, 255, 255)
            ).get_width()

            self.draw_text_outline(
                text,
                x - w // 2,
                y - 40 + offset
            )

        if not self.rover.in_rover:
            frame = pygame.transform.scale(
                self.player.get_frame(),
                (64, 64)
            )

            self.screen.blit(
                frame,
                (
                    self.player.rect.x -
                    self.camera_x - 32,

                    self.player.rect.y -
                    self.camera_y - 32
                )
            )

        if self.is_night:
            darkness = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            darkness.fill((0, 20, 40, 140))

            self.screen.blit(
                darkness,
                (0, 0)
            )

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                20
            )

            time_text = "NIGHT" if self.is_night else "DAY"

            text = font.render(
                time_text,
                False,
                (180, 220, 255) if self.is_night else (255, 220, 120)
            )

            self.screen.blit(
                text,
                (WIDTH - 140, 20)
            )

        rocket_img = pygame.transform.scale(
            self.rocket,
            (180, 180)
        )

        self.screen.blit(
            rocket_img,
            (
                self.rocket_pos[0] -
                self.camera_x,

                self.rocket_pos[1] -
                self.camera_y
            )
        )

        if self.near_rocket and not self.rocket_fixed:

            x = (
                self.rocket_pos[0] -
                self.camera_x + 90
            )

            y = (
                self.rocket_pos[1] -
                self.camera_y
            )

            offset = int(
                sin(self.float_time) * 5
            )

            text = "Полагодити E"

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                18
            )

            w = font.render(
                text,
                False,
                (255, 255, 255)
            ).get_width()

            self.draw_text_outline(
                text,
                x - w // 2,
                y - 40 + offset
            )

        bar_width = int(self.player.max_energy * 2.2)

        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            (
                20,
                20,
                bar_width,
                24
            )
        )

        pygame.draw.rect(
            self.screen,
            (0, 200, 255),
            (
                20,
                20,
                int(
                    (
                            self.player.energy /
                            self.player.max_energy
                    ) * bar_width
                ),
                24
            )
        )

        font = pygame.font.Font(
            "fonts/pixel.ttf",
            16
        )

        label = font.render(
            "Oxygen",
            False,
            (255, 255, 255)
        )

        self.screen.blit(
            label,
            (20, 0)
        )

        oxygen_text = font.render(
            f"{int(self.player.energy)}%",
            False,
            (255, 255, 255)
        )

        self.screen.blit(
            oxygen_text,
            (95, 22)
        )

        if self.player.energy <= 25:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT)
            )

            overlay.set_alpha(35)

            overlay.fill((255, 0, 0))

            self.screen.blit(
                overlay,
                (0, 0)
            )

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                24
            )

            text = font.render(
                "LOW OXYGEN",
                False,
                (255, 80, 80)
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    40
                )
            )

        if self.inventory_open:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT)
            )

            overlay.set_alpha(60)

            overlay.fill((0, 0, 0))

            self.screen.blit(
                overlay,
                (0, 0)
            )

            self.draw_inventory()

        if self.pickup_target:

            x = (
                self.pickup_target.rect.centerx -
                self.camera_x
            )

            y = (
                self.pickup_target.rect.y -
                self.camera_y
            )

            offset = int(
                sin(self.float_time) * 5
            )

            text = "Натисніть ЛКМ"

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                18
            )

            w = font.render(
                text,
                False,
                (255, 255, 255)
            ).get_width()

            self.draw_text_outline(
                text,
                x - w // 2,
                y - 40 + offset
            )

        if self.rocket_fixed:

            overlay = pygame.Surface(
                (WIDTH, HEIGHT)
            )

            overlay.set_alpha(220)

            overlay.fill((0, 0, 0))

            self.screen.blit(
                overlay,
                (0, 0)
            )

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                42
            )

            text = font.render(
                "YOU ESCAPED MARS",
                False,
                (255, 255, 255)
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2 -
                    text.get_width() // 2,

                    HEIGHT // 2 -
                    text.get_height() // 2
                )
            )

        if self.paused:
            overlay = pygame.Surface(
                (WIDTH, HEIGHT)
            )

            overlay.set_alpha(180)

            overlay.fill((0, 0, 0))

            self.screen.blit(
                overlay,
                (0, 0)
            )

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                42
            )

            text = font.render(
                "PAUSED",
                False,
                (255, 255, 255)
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    HEIGHT // 2 - text.get_height() // 2
                )
            )

        if self.mining and self.mining_target:
            start_x = (
                    self.player.rect.centerx -
                    self.camera_x
            )

            start_y = (
                    self.player.rect.centery -
                    self.camera_y - 22
            )

            end_x = (
                    self.mining_target.rect.centerx -
                    self.camera_x
            )

            end_y = (
                    self.mining_target.rect.centery -
                    self.camera_y
            )

            beam_surface = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            pygame.draw.line(
                beam_surface,
                (100, 220, 255, 140),
                (start_x, start_y),
                (end_x, end_y),
                8
            )

            pygame.draw.circle(
                beam_surface,
                (120, 240, 255, 180),
                (end_x, end_y),
                6
            )

            self.screen.blit(
                beam_surface,
                (0, 0)
            )

        if self.sandstorm:

            storm = pygame.Surface(
                (WIDTH, HEIGHT),
                pygame.SRCALPHA
            )

            storm.fill((255, 140, 40, 90))

            self.screen.blit(
                storm,
                (
                    -random.randint(0, 4),
                    random.randint(0, 4)
                )
            )

            for particle in self.sand_particles:
                pygame.draw.circle(

                    self.screen,

                    (255, 170, 80),

                    (int(particle[0]), int(particle[1])),

                    particle[2]

                )

            font = pygame.font.Font(
                "fonts/pixel.ttf",
                24
            )

            text = font.render(
                "SANDSTORM",
                False,
                (255, 220, 180)
            )

            self.screen.blit(
                text,
                (
                    WIDTH // 2 - text.get_width() // 2,
                    80
                )
            )

        self.draw_chest()

        if self.inventory_open:
            overlay = pygame.Surface((WIDTH, HEIGHT))

            overlay.set_alpha(60)

            overlay.fill((0, 0, 0))

            self.screen.blit(overlay, (0, 0))

            self.draw_inventory()

        pygame.display.flip()
        return