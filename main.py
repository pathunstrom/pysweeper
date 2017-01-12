from game_engine import GameEngine

from pysweeper.scenes import Game

with GameEngine(Game) as engine:
    engine.run()
