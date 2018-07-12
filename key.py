#Copyright 2014 Ethan McCue
#All rights reserved to MacaulayCore

class Key:
    def __init__(self, location, direction, isLocked, team, selected=False):
        self.location = location
        self.direction = direction
        self.isLocked = isLocked
        self.team = team
        self.isSelected = selected

    def lock(self):
        self.isLocked = True

    def select(self):
        self.isSelected = not self.isSelected
