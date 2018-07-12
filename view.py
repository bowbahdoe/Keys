import pygame

GOLD_UNLOCKED_TEXTURE = pygame.image.load("img/yellow1.png")
SILVER_UNLOCKED_TEXTURE = pygame.image.load("img/silver1.png")
GOLD_LOCKED_TEXTURE = pygame.image.load("img/gold_lock.png")
SILVER_LOCKED_TEXTURE = pygame.image.load("img/silver_lock.png")

def key_texture(key):
    """Gives the texture to use when rendering a key"""
    def base_texture(key):
        if key.team == "gold":
            if key.isLocked:
                return GOLD_LOCKED_TEXTURE
            else:
                return GOLD_UNLOCKED_TEXTURE
        else:
            if key.isLocked:
                return SILVER_LOCKED_TEXTURE
            else:
                return SILVER_UNLOCKED_TEXTURE

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
