"""Helper functions for the Cartesian location hacking that is for some reason
sprinkled everywhere."""

def makeLocCartesian(Loc):
    returner = []
    locDic = {"A":1,"B":2,"C":3,"D":4,"E":5,"F":6,"G":7,"H":8}

    returner.append(locDic[Loc[0]])
    returner.append(int(Loc[1]))
    return returner

def makeLocAlphaNumeric(Loc):
    locDic = {1:'A',2:'B',3:'C',4:'D',5:'E',6:'F',7:'G',8:'H'}
    returner = ""
    returner+=(locDic[Loc[0]])
    returner+=str(Loc[1])
    return returner
