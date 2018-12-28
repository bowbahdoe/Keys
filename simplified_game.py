from gamestate import GameState, Move, Respawn, Rotate, Reset
from board import Board

class SimplifiedKeysGame:
    """Keys game with a simplified interface as compared to... [shudders]"""
    def __init__(self):
        self.gamestate = GameState(Board.default())

    def move(self, team, from_, to):
        Move(team=team, from_=from_, to=to)(self.gamestate)

    def rotate(self, team, at, facing):
        Rotate(team=team, at=at, facing=facing)(self.gamestate)

    def respawn(self, team, at):
        Respawn(team=team, at=at)(self.gamestate)

    def reset(self):
        Reset()(self.gamestate)

    def summarize(self):
        return self.gamestate.summarize()
