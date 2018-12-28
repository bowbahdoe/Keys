from gamestate import GameState, Move, Respawn, Rotate, Reset
from board import Board

def _valid_team(obj):
    return obj == "gold" or obj == "silver"

def _valid_location(obj):
    return isinstance(obj, tuple) and len(obj) == 2 and \
        isinstance(obj[0], int) and isinstance(obj[1], int)

class SimplifiedKeysGame:
    """Keys game with a simplified interface as compared to... [shudders]"""
    def __init__(self):
        self.gamestate = GameState(Board.default())

    def move(self, team, from_, to):
        if not _valid_team(team):
            raise ValueError(f"Invalid Team {team}")
        if not _valid_location(from_):
            raise ValueError(f"Invalid 'from' Location {from_}")
        if not _valid_location(to):
            raise ValueError(f"Invalid 'to' Location {to}")

        Move(team=team, from_=from_, to=to)(self.gamestate)

    def rotate(self, team, at, facing):
        Rotate(team=team, at=at, facing=facing)(self.gamestate)

    def respawn(self, team, at):
        if not _valid_team(team):
            raise ValueError(f"Invalid Team {team}")
        if not _valid_location(at):
            raise ValueError(f"Invalid Location {at}")
        Respawn(team=team, at=at)(self.gamestate)

    def reset(self):
        Reset()(self.gamestate)

    def summarize(self):
        return self.gamestate.summarize()
