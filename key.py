#Copyright 2014 Ethan McCue
#All rights reserved to MacaulayCore

class Key:
    def __init__(self, location, direction, isLocked, team):
        self.location = location
        self.direction = direction
        self.isLocked = isLocked
        self.team = team

    def lock(self):
        self.isLocked = True
