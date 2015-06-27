#Copyright 2014 Ethan McCue
#All rights reserved to MacaulayCore
#import Board

try:
    import pygame
except(ImportError):
    import pyj2d as pygame
class Key:
    def __init__(self,Location,Direction,isLocked,Team,selected=False):
        self.Loc = Location
        self.Dir = Direction
        self.isLocked = isLocked
        self.team = Team
        self.isSelected = selected
         
        if self.team == "gold":
            self.baseTex = pygame.image.load("img/yellow1.png")
            self.texture = pygame.image.load("img/yellow1.png")
        else:
            self.baseTex = pygame.image.load("img/silver1.png")
            self.texture = pygame.image.load("img/silver1.png")
        if self.team == "gold":
            if self.Dir == "East":
                self.texture =pygame.transform.rotate(self.baseTex,45)
            if self.Dir == "SouthEast":
                self.texture =pygame.transform.rotate(self.baseTex,360)
            if self.Dir == "South":
                self.texture =pygame.transform.rotate(self.baseTex,-40)
            if self.Dir == "SouthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-90)
            if self.Dir == "West":
                self.texture =pygame.transform.rotate(self.baseTex,-135)
            if self.Dir == "NorthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-180)
            if self.Dir == "North":
                self.texture =pygame.transform.rotate(self.baseTex,135)
            if self.Dir == "NorthEast":
                self.texture =pygame.transform.rotate(self.baseTex,90)


        else:
            if self.Dir == "East":
                self.texture =pygame.transform.rotate(self.baseTex,-45)
            if self.Dir == "SouthEast":
                self.texture =pygame.transform.rotate(self.baseTex,-90)
            if self.Dir == "South":
                self.texture =pygame.transform.rotate(self.baseTex,-135)
            if self.Dir == "SouthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-180)
            if self.Dir == "West":
                self.texture =pygame.transform.rotate(self.baseTex,135)
            if self.Dir == "NorthWest":
                self.texture =pygame.transform.rotate(self.baseTex,90)
            if self.Dir == "North":
                self.texture =pygame.transform.rotate(self.baseTex,45)
            if self.Dir == "NorthEast":
                self.texture =pygame.transform.rotate(self.baseTex,0)
        

        self.frame = 1
    def getLocation(self):
        return self.Loc
    def setLocation(self,Loc):
        self.Loc = Loc
    def getDirection(self):
        return self.Dir
    def setDirection(self,Dir):
        self.Dir = Dir

        if self.team == "gold":
            if self.Dir == "East":
                self.texture =pygame.transform.rotate(self.baseTex,45)
            if self.Dir == "SouthEast":
                self.texture =pygame.transform.rotate(self.baseTex,360)
            if self.Dir == "South":
                self.texture =pygame.transform.rotate(self.baseTex,-40)
            if self.Dir == "SouthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-90)
            if self.Dir == "West":
                self.texture =pygame.transform.rotate(self.baseTex,-135)
            if self.Dir == "NorthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-180)
            if self.Dir == "North":
                self.texture =pygame.transform.rotate(self.baseTex,135)
            if self.Dir == "NorthEast":
                self.texture =pygame.transform.rotate(self.baseTex,90)


        else:
            if self.Dir == "East":
                self.texture =pygame.transform.rotate(self.baseTex,-45)
            if self.Dir == "SouthEast":
                self.texture =pygame.transform.rotate(self.baseTex,-90)
            if self.Dir == "South":
                self.texture =pygame.transform.rotate(self.baseTex,-135)
            if self.Dir == "SouthWest":
                self.texture =pygame.transform.rotate(self.baseTex,-180)
            if self.Dir == "West":
                self.texture =pygame.transform.rotate(self.baseTex,135)
            if self.Dir == "NorthWest":
                self.texture =pygame.transform.rotate(self.baseTex,90)
            if self.Dir == "North":
                self.texture =pygame.transform.rotate(self.baseTex,45)
            if self.Dir == "NorthEast":
                self.texture =pygame.transform.rotate(self.baseTex,0)
        

    def isLocked(self):
        return self.isLocked
    def setLocked(self,locked):
        '''True or False'''
        self.texture = pygame.image.load("img/Black_Lock.png")
        if locked:
            self.isLocked = True
        else:
            self.isLocked = False
    def getTeam(self):
        return self.team
    def setTeam(self,team):
        if self.team == "gold":
            self.texture = pygame.image.load("img/key-icon.png")
        else:
            self.texture = pygame.image.load("img/silver1.png") 
    def select(self):
        if self.isSelected:
            self.isSelected = False
        else:
            self.isSelected = True
    def _makeLocCartesian(self, Loc):
        returner = []
        locDic = {"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"H":8}
        
        returner.append(locDic[Loc[0]])
        returner.append(int(Loc[1]))
        return returner
    def _makeLocAlphaNumeric(self,Loc):
        
        locDic = {1:'A',2:'B',3:'C',4:'D',5:'E',6:'F',7:'G',8:'H'}
        returner = ""
        returner+=(locDic[Loc[0]])
        returner+=str(Loc[1])
        return returner
    def getTexture(self):
        return self.texture



