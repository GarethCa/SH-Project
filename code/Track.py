from Cell import *
import math

def cellDist(cellOne, cellTwo):
    x_dist = abs(cellOne.locOverTime[-1].x - cellTwo.locOverTime[-1].x) **2
    y_dist = abs(cellOne.locOverTime[-1].y - cellTwo.locOverTime[-1].y) **2
    z_dist = (abs(cellOne.locOverTime[-1].z - cellTwo.locOverTime[-1].z) *2 )** 2
    return math.sqrt(x_dist + y_dist + z_dist)

def calcVertDist(cellOne,cellTwo):
    z_dist = abs(cellOne.locOverTime[-1].z - cellTwo.locOverTime[-1].z)
    return z_dist

def calcHorDist(cellOne, cellTwo):
    x_dist = abs(cellOne.locOverTime[-1].x - cellTwo.locOverTime[-1].x) **2
    y_dist = abs(cellOne.locOverTime[-1].y - cellTwo.locOverTime[-1].y) **2
    return math.sqrt(x_dist + y_dist)


# Add a given cell to tracking info.
def addCellToTracked(time, newcell, cellList):
    distances = []
    counter =  0
    for cell in cellList:
        distance = cellDist(cell, newcell)
        distances.append(distance)
    while(counter < 2):
        minDist = min(distances)
        index = distances.index(minDist)
        diff = abs(cellList[index].lastTracked() - newcell.lastTracked())
        if abs(minDist) >20:
            newCell = Cell(len(cellList))
            loc = newcell.lastLoc()
            newCell.addLocTime(loc.time, loc.x, loc.y, loc.z)
            cellList.append(newCell)
            break
        if diff > 0:
            loc = newcell.lastLoc()
            cellList[index].addLocTime(loc.time, loc.x, loc.y, loc.z)
            return
        else:
            distances[index] = 100000
        counter +=1
    

def cellCleanup(cellList, time):
    discarded = [x for x in cellList if tooOld(x, time)]
    lis = cellList
    lis = [x for x in cellList if not tooOld(x, time)]
    return lis, discarded


def tooOld(cell, time):
    return abs((cell.locOverTime[-1].time - time)) >3


def tooShort(cell, time):
    return len(cell.locOverTime) < time


# Add new cellsto cell List.
def iterateThroughCells(cells, cellList):
    if len(cells) == 0:
        return cellList, []
    time = cells[0].lastLoc().time
    for cell in cells:
        addCellToTracked(1, cell, cellList)
    cellLis, discarded = cellCleanup(cellList, time)
    return cellLis, discarded


# Output Framework for Lists of Cells.
def outputData(cellLists):
    text = "SIMI*BIOCELL\n400\n---\n0\n---\n1 1\n0\n---\n"
    for cell in cellLists:
        text += str(cell)
    txt_output = open("../Output/output.smd", 'w')
    txt_output.write(text)
    txt_output.close()
