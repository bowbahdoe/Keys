"""Helper functions for the Cartesian location hacking that is sprinkled everywhere."""

def makeLocCartesian(loc):
    locDic = { "A": 1,
               "B": 2,
               "C": 3,
               "D": 4,
               "E": 5,
               "F": 6,
               "G": 7,
               "H": 8 }
    return [locDic[loc[0]], int(loc[1])]

def makeLocAlphaNumeric(loc):
    locDic = { 1: 'A',
               2: 'B',
               3: 'C',
               4: 'D',
               5: 'E',
               6: 'F',
               7: 'G',
               8: 'H' }

    return "" + locDic[loc[0]] + str(loc[1])
