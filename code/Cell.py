
from Point import *
class Cell:

    def __init__(self, ident):
        self.id = ident
        self.daughterL = None
        self.daughterR = None
        self.locOverTime = []
        self.alive = True

    def mitosis(self):
        self.daughterL = Cell(id+"L")
        self.daughterR = Cell(id+"R")

    def death(self):
        self.alive = False

    def lastTracked(self):
        return self.locOverTime[-1].time
    
    def lastLoc(self):
        return self.locOverTime[-1]

    def addDaughter(self, left, cell):
        if left:
            self.daughterL  = cell
        else:
            self.daughterR = cell
    
    def addLocTime(self,time, x,y,z):
        self.locOverTime.append(Point(time,x,y,z))

    def getChildCount(self, daughter):
        if daughter is None:
            return 0
        if (daughter.daughterL is None and daughter.daughterR is None):
            return 1
        else:
            return getChildCount(daughter.daughterL) + getChildCount(daughter.daughterR)
        
    def __str__(self):
        rep = ""
        rep += ("cell {}\n".format(self.id))
        rep += ("{}\n".format(len(self.locOverTime)))
        for p in self.locOverTime:
            rep += ("{} {} {} {} -1 -1 -1 {}\n".format(p.time, p.x, p.y, p.z, p.comment))
        if self.daughterL != None:
            rep += str(self.daughterL)
        if self.daughterR != None:
            rep+= str(self.daughterR)
        rep+= "---\n"
        return rep