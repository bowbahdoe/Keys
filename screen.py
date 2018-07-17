import logging
import pygame
from pygame.locals import *

class Screen:
    def __init__(self, *, fps, gamestate, resolution):
        self.gamestate = gamestate
        self.board = gamestate.board
        self.resolution = resolution
        self.fps = fps

    def init(self):
        pygame.init()
        pygame.display.set_caption("Keys")
        self._display = pygame.display.set_mode(self.resolution)
        self._fpsclock = pygame.time.Clock()
        self.update()
        return self

    def getLocOfKeyPress(self, event):
        log = logging.getLogger(__name__)
        log.debug("User clicked at %s", event.pos)
        clickX, clickY = event.pos
        board_location = (clickY // self._sheight + 1, clickX // self._swidth + 1)
        log.debug("Click Interpreted as being at %s", board_location)
        return board_location

    @property
    def _swidth(self):
        return self.resolution[0] // 8

    @property
    def _sheight(self):
        return self.resolution[1] // 8

    @property
    def _background(self):
        background = self._transparent_surface()
        self._drawBoard(background)
        return background

    @property
    def _unlocked_keys(self):
        unlocked_keys = self._transparent_surface()
        self._drawKeysOnBoard(unlocked_keys, self.board)
        return unlocked_keys

    @property
    def _locked_keys(self):
        locked_keys = self._transparent_surface()
        self._drawLockedKeysOnBoard(locked_keys, self.board)
        return locked_keys

    def _transparent_surface(self):
        surface = pygame.Surface(self.resolution, pygame.SRCALPHA, 32)
        surface.convert_alpha()
        return surface

    def update(self):
        def draw(surface):
            self._display.blit(surface, (0, 0))

        draw(self._background)
        draw(self._locked_keys)
        draw(self._unlocked_keys)


        for location in self.board.getRotatePointsofKeyAtLoc(self.gamestate.pieceSelected).values():
            self._highlightSquare(self._display, (location[1], location[0]), (23,223,12))

        for location in self.gamestate.validMoves:
            self._highlightSquare(self._display, (location[1], location[0]), (213,23,12))

        for location in self.board.getFreeRespawnPointsForTeam(self.gamestate.teamRespawning):
            self._highlightSquare(self._display, (location[1], location[0]), (233,34,223))

        pygame.display.update()
        self._fpsclock.tick(self.fps)

    def _drawKeyAtLoc(self, display, key, loc):
        if key != None:
            texture = Screen._key_texture(key)
            texture = pygame.transform.scale(texture, (self._sheight, self._swidth))
            display.blit(texture, (self._swidth*(loc[1]-1), self._sheight*(loc[0]-1)))

    def _drawKeysOnBoard(self, display, board):
        for loc in board.all_locations():
            key = board.getUnlocked(loc)
            self._drawKeyAtLoc(display, key, loc)

    def _drawLockedKeysOnBoard(self, display, board):
        for loc in board.all_locations():
            key = board.getLocked(loc)
            self._drawKeyAtLoc(display, key, loc)

    def _drawBoard(self, display, color1=(0,0,0), color2=(100,100,100)):
        display.fill(color1)
        for row in range(8):
            for column in range(8):
                if column % 2 == row % 2:
                    pygame.draw.rect(
                        display,
                        color2,
                        (column * self._sheight, row * self._swidth, self._sheight, self._swidth)
                    )


    def _highlightSquare(self, display, cartesian_loc, color):
        x = cartesian_loc[0] - 1
        y = cartesian_loc[1] - 1
        pygame.draw.rect(
            display,
            color,
            (x * self._swidth, y * self._sheight, self._swidth, self._sheight),
            5
        )

    _GOLD_UNLOCKED_TEXTURE = pygame.image.load("img/yellow1.png")
    _SILVER_UNLOCKED_TEXTURE = pygame.image.load("img/silver1.png")
    _GOLD_LOCKED_TEXTURE = pygame.image.load("img/gold_lock.png")
    _SILVER_LOCKED_TEXTURE = pygame.image.load("img/silver_lock.png")

    @staticmethod
    def _key_texture(key):
        """Gives the texture to use when rendering a key"""
        def base_texture(key):
            if key.team == "gold":
                if key.isLocked:
                    return Screen._GOLD_LOCKED_TEXTURE
                else:
                    return Screen._GOLD_UNLOCKED_TEXTURE
            else:
                if key.isLocked:
                    return Screen._SILVER_LOCKED_TEXTURE
                else:
                    return Screen._SILVER_UNLOCKED_TEXTURE

        def texture_rotation(key):
            rotation_map = {
                "East":         { "gold":   45, "silver":  -45 },
                "SouthEast":    { "gold":  360, "silver":  -90 },
                "South":        { "gold":  -45, "silver": -135 },
                "SouthWest":    { "gold":  -90, "silver": -180 },
                "West":         { "gold": -135, "silver":  135 },
                "NorthWest":    { "gold": -180, "silver":   90 },
                "North":        { "gold":  135, "silver":   45 },
                "NorthEast":    { "gold":   90, "silver":    0 }
            }

            if key.isLocked:
                return 0
            else:
                return rotation_map[key.direction][key.team]

        texture = base_texture(key)
        return pygame.transform.rotate(texture, texture_rotation(key))
