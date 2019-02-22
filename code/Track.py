from Cell import *


def cellDist(cenOne, cenTwo):
    x_dist = abs(cenOne.centroid[0] - cenTwo.centroid[0])
    y_dist = abs(cenOne.centroid[1] - cenTwo.centroid[1])
    return x_dist + y_dist

def getInitialCells():
    return []


def addCellToTracked(time, newcell, cellList):
    min_distance = 99999
    index = -1
    counter =0
    for cell in cellList:
        distance = cellDist(cell,newcell)
        if distance < min_distance:
            if cell.lastTracked == time:
                cellList.append(newcell)
                return
            else:
                min_distance = distance
                index = counter
        counter += 1
    if min_distance < 20:
        cellList[index].locOverTime.append(newcell)
    else:
        cellList.append(newcell)
        
def outputData():
    doSomething = "output"
    # Implement print for all cells in list.