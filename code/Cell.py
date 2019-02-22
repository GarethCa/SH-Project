class Cell:

    def __init__(self, id):
        self.id = id
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

    def addDaughter(self, left, cell):
        if left:
            self.daughterL  = cell
        else:
            self.daughterR = cell
        
    def __str__(self):
        rep = ""
        rep += ("cell {}\n".format(id))
        rep += ("{}\n".format(len(self.locOverTime)))
        for l in self.locOverTime:
            rep += ("{} {} {} {}\n".format(p.time, p.x, p.y, p.z))
        for daughter in self.daughter_cells:
            rep += str(daughter)
        return rep