from Cell import *


def cellDist(cellOne, cellTwo):
    x_dist = abs(cellOne.locOverTime[-1].x - cellTwo.locOverTime[-1].x)
    y_dist = abs(cellOne.locOverTime[-1].y - cellTwo.locOverTime[-1].y)
    z_dist = abs(cellOne.locOverTime[-1].z - cellTwo.locOverTime[-1].z) * 5
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
            newCell.addLocTime(loc.time,loc.x,loc.y,loc.z)
            cellList.append(newCell)
            num_cells += 1
        else:
            dist = 99999
            for existCell in cellList:
                temp_dist =cellDist(cell, existCell)
                if temp_dist < dist:
                    dist = temp_dist
            if dist > 20:
                tooClose = False
            if not tooClose:
                newCell = Cell(num_cells)
                loc = cell.lastLoc()
                newCell.addLocTime(loc.time,loc.x,loc.y,loc.z)
                cellList.append(newCell)
                num_cells += 1
        counter += 1
    return cellList

def addCellToTracked(time, newcell, cellList):
    counter =0
    distances = []
    for cell in cellList:
        distance = cellDist(cell,newcell)
        distances.append(distance)
    minDist = min(distances)
    index = distances.index(minDist)
    if minDist < 40 and (cellList[index].lastTracked() != newcell.lastTracked() ):
        loc = newcell.lastLoc()
        cellList[index].addLocTime(loc.time,loc.x, loc.y, loc.z)
    else:
        print("new cell")
        newCell = Cell(len(cellList))
        loc = newcell.lastLoc()
        newCell.addLocTime(loc.time,loc.x,loc.y,loc.z)
        cellList.append(newCell)
    
def iterateThroughCells(cells, cellList):
    for cell in cells:
        addCellToTracked(1,cell, cellList)
    return cellList


def outputData(cellLists):
    text = "SIMI*BIOCELL\n400\n---\n0\n---\n1 1\n0\n---\n"
    for cell in cellLists:
        text+= str(cell)
    txt_output = open("output.txt", 'w')
    txt_output.write(text)
    txt_output.close()