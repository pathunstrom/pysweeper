from random import sample

from game_engine import BaseScene
from game_engine.abc import Engine

from pysweeper.color import DARK_GREY
from pysweeper.locals import MINE_GROUP, SQUARES_GROUP, UI_GROUP
from pysweeper.sprites import (
    DifficultyButton,
    DifficultyHighlighter,
    MineSquare,
    NewGameButton,
    Timer
)


class Game(BaseScene):

    def __init__(self, engine: Engine):
        super().__init__(engine, background_color=DARK_GREY)
        self.difficulty = 1
        for x in range(1, 4):
            DifficultyButton(self, (450 + x * 24, 50), x)
        DifficultyHighlighter(self, (474, 50))
        NewGameButton(self, (450, 80))
        self.timer = Timer(self, (425, 300))
        self.safe_open = []
        self.win_state = 400
        self.ready = True
        self.started = False
        self.new_game()

    def simulate(self, time_delta: float):
        super().simulate(time_delta)
        for mine in self.groups[MINE_GROUP]:
            if mine.opened:
                # Game_over
                self.end_game(False)
        if len(self.safe_open) >= self.win_state:
            self.end_game(True)

    def __mouse_up__(self, event):
        if event.pos[0] <= 400:
            if self.ready:
                for mine_square in self.groups[SQUARES_GROUP].sprites():
                    if mine_square.rect.collidepoint(event.pos):
                        mine_square.touch()
                        break
                if not self.started:
                    self.started = True
                    self.timer.start()
        else:
            for ui_element in self.groups[UI_GROUP].sprites():
                ui_element.click_response(event)

    def new_game(self):
        self.ready = True
        self.timer.reset()
        self.groups[SQUARES_GROUP].empty()
        self.groups[MINE_GROUP].empty()
        self.safe_open = []
        for x in range(20):
            for y in range(20):
                MineSquare(self, (x, y))
        mine_count = self.difficulty * 20
        sprites_list = self.groups[SQUARES_GROUP].sprites()
        self.win_state = 400 - mine_count
        for square in sample(sprites_list, mine_count):
            square.arm()
            square.add(self.groups[MINE_GROUP])

    def end_game(self, win):
        self.ready = False
        self.started = False
        self.timer.stop()
        if not win:
            for mine in self.groups[MINE_GROUP].sprites():
                mine.open()
