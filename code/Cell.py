class Cell:

    def __init__(self, id):
        self.id = id
        self.daughterL = None
        self.daughterR = None
        self.times = []
        self.alive = True

    def mitosis(self):
        self.daughterL = Cell(id+"L")
        self.daughterR = Cell(id+"R")

    def death(self):
        self.alive = False
