from Cell import *


def cellDist(cellOne, cellTwo):
    x_dist = abs(cellOne.locOverTime[-1].x - cellTwo.locOverTime[-1].x)
    y_dist = abs(cellOne.locOverTime[-1].y - cellTwo.locOverTime[-1].y)
    z_dist = abs(cellOne.locOverTime[-1].z - cellTwo.locOverTime[-1].z) *3
    return (x_dist + y_dist + z_dist)


def getInitialCells(cellData):
    cellList = []
    counter = 0
    num_cells = 0
    for cell in cellData:
        tooClose = True
        if len(cellList) == 0:
            newCell = Cell(num_cells)
            loc = cell.lastLoc()
            newCell.addLocTime(loc.time, loc.x, loc.y, loc.z)
            cellList.append(newCell)
            num_cells += 1
        else:
            dist = 99999
            for existCell in cellList:
                temp_dist = cellDist(cell, existCell)
                if temp_dist < dist:
                    dist = temp_dist
            if dist > 6:
                tooClose = False
            if not tooClose:
                newCell = Cell(num_cells)
                loc = cell.lastLoc()
                newCell.addLocTime(loc.time, loc.x, loc.y, loc.z)
                cellList.append(newCell)
                num_cells += 1
        counter += 1
    return cellList


def addCellToTracked(time, newcell, cellList):
    distances = []
    for cell in cellList:
        distance = cellDist(cell, newcell)
        distances.append(distance)
    minDist = min(distances)
    index = distances.index(minDist)
    diff = abs(cellList[index].lastTracked() - newcell.lastTracked())
    if abs(minDist) < 6 and diff > 0:
        loc = newcell.lastLoc()
        cellList[index].addLocTime(loc.time, loc.x, loc.y, loc.z)
    else:
        newCell = Cell(len(cellList))
        loc = newcell.lastLoc()
        newCell.addLocTime(loc.time, loc.x, loc.y, loc.z)
        cellList.append(newCell)


def cellCleanup(cellList, time):
    discarded = [x for x in cellList if tooOld(x, time)]
    lis = cellList
    lis = [x for x in cellList if not tooOld(x, time)]
    print(len(lis), len(discarded))
    return lis, discarded


def tooOld(cell, time):
    return abs((cell.locOverTime[-1].time - time)) >3


def tooShort(cell, time):
    return len(cell.locOverTime) < time


def iterateThroughCells(cells, cellList):
    if len(cells) == 0:
        return cellList, []
    time = cells[0].lastLoc().time
    for cell in cells:
        addCellToTracked(1, cell, cellList)
    print(len(cellList))
    cellLis, discarded = cellCleanup(cellList, time)
    # print(len(cellList))
    return cellLis, discarded


def outputData(cellLists):
    text = "SIMI*BIOCELL\n400\n---\n0\n---\n1 1\n0\n---\n"
    for cell in cellLists:
        text += str(cell)
    txt_output = open("output.txt", 'w')
    txt_output.write(text)
    txt_output.close()
