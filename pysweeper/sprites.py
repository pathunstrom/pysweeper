from ppb_vector import Vector2 as Vector
from pygame import Surface, Rect
from pygame.draw import circle, rect
import pygame.font as font
from pygame.sprite import DirtySprite, spritecollide

from pysweeper.color import (
    CHROME,
    GREEN,
    GREY,
    RED,
    YELLOW)
from pysweeper.locals import (
    SQUARE_RESOLUTION,
    SQUARES_GROUP,
    UI_GROUP,
    MINE_GROUP
)

"""
600 X 400 view

Squares are 18 X 18 with 2 pixel padding between squares.

Allows a 200 X 400 column for menu and controls.
"""


class SquareCollider(DirtySprite):

    def __init__(self):
        super().__init__()
        size = tuple(map(lambda x: x * 1.5, SQUARE_RESOLUTION))
        self.rect = Rect((0, 0), size)


class MineSquare(DirtySprite):
    number_surfaces = [None] * 9
    collider = SquareCollider()
    mine_image = None

    def __init__(self, scene, position):
        # pygame.Sprite setup
        super().__init__(scene.groups[SQUARES_GROUP])
        self.scene = scene
        self.image = Surface(SQUARE_RESOLUTION)
        self.image.fill(CHROME)
        self.rect = self.image.get_rect()
        self.position = Vector(*position)
        self.rect.centerx = self.position.x * 20 + 10
        self.rect.centery = self.position.y * 20 + 10

        # Minesweeper state
        self.opened = False
        self.primed = False
        self.wait = 0.6
        self.wait_counter = 0
        self.armed = False
        self.flagged = False
        self.questioned = False

    def update(self, time_delta: float):
        self.dirty = 1
        if not self.opened:
            if self.primed:
                self.wait_counter += time_delta

            if self.wait_counter >= self.wait:
                self.primed = False
                self.wait_counter = 0
                if self.flagged:
                    self.image.fill(YELLOW)
                    self.flagged = False
                    self.questioned = True
                elif self.questioned:
                    self.image.fill(CHROME)
                    self.questioned = False
                else:
                    self.image.fill(RED)
                    self.flagged = True

    def touch(self):
        if self.primed:
            self.open()
        else:
            self.primed = True

    def open(self):
        if not self.opened:
            if self.flagged:
                self.primed = False
                return
            self.opened = True
            if self.armed:
                if MineSquare.mine_image is None:
                    MineSquare.mine_image = Surface((18, 18))
                    circle(MineSquare.mine_image, RED, (9, 9), 7)
                self.image = MineSquare.mine_image
            else:
                self.scene.safe_open.append(self)
                mined = self.scene.groups[MINE_GROUP]
                self.collider.rect.center = self.rect.center
                armed_neighbors = len(spritecollide(self.collider, mined, False))
                if self.number_surfaces[armed_neighbors] is None:
                    new_surface = Surface(SQUARE_RESOLUTION)
                    print_font = font.Font(None, SQUARE_RESOLUTION[0])
                    numeral = print_font.render(str(armed_neighbors), True, (0, 0, 0))
                    new_surface.fill(GREY)
                    new_surface.blit(numeral, (0, 0))
                    self.number_surfaces[armed_neighbors] = new_surface
                self.image = self.number_surfaces[armed_neighbors]
                if armed_neighbors == 0:
                    squares = self.scene.groups[SQUARES_GROUP]
                    neighbors = spritecollide(self.collider, squares, False)
                    for neighbor in neighbors:
                        if not neighbor.opened:
                            neighbor.open()

    def arm(self):
        self.armed = True


class DifficultyButton(DirtySprite):

    difficulty_colors = [CHROME, GREEN, YELLOW, RED]

    def __init__(self, scene, position, difficulty):
        super().__init__(scene.groups[UI_GROUP])
        self.scene = scene
        self.image = Surface((20, 20))
        self.image.fill(self.difficulty_colors[difficulty])
        self.rect = self.image.get_rect()
        self.position = Vector(*position)
        self.rect.center = tuple(self.position)
        self.difficulty = difficulty

    def update(self, time_delta):
        self.dirty = 1

    def click_response(self, event):
        if self.rect.collidepoint(event.pos):
            self.scene.difficulty = self.difficulty
            print("Difficulty changed")


class NewGameButton(DirtySprite):

    def __init__(self, scene, position):
        super().__init__(scene.groups[UI_GROUP])
        button_font = font.Font(None, 30)
        self.scene = scene
        self.image = button_font.render("New Game", True, CHROME)
        self.rect = self.image.get_rect()
        self.rect.topleft = position

    def update(self, time_delta):
        self.dirty = 1

    def click_response(self, event):
        if self.rect.collidepoint(event.pos):
            self.scene.new_game()


class DifficultyHighlighter(DirtySprite):

    def __init__(self, scene, position):
        super().__init__(scene.groups[UI_GROUP])
        self.scene = scene
        self.image = Surface((24, 24))
        self.image.set_colorkey((0, 0, 0))
        rect(self.image, CHROME, Rect((0, 0), (23, 23)), 2)
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self, time_delta):
        self.dirty = 1
        self.rect.center = 450 + self.scene.difficulty * 24, 50

    def click_response(self, event):
        pass


class Timer(DirtySprite):

    def __init__(self, scene, position):
        super().__init__(scene.groups[UI_GROUP])
        self.font = font.Font(None, 30)
        self.time = 0
        self.image = None
        self.new_image()
        self.rect = Rect(position, (0, 0))
        self.running = False

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def reset(self):
        self.time = 0
        self.running = False

    def update(self, time_delta):
        self.dirty = 1
        if self.running:
            self.time += time_delta
            self.new_image()

    def new_image(self):
        self.image = self.font.render("{:4.2f}".format(self.time), True, CHROME)
