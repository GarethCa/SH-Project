import csv
from Cell import * 
import sys
import pandas as pd
import random
import math
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


def parseSMD(smdfile):
    cellList =  []
    coords = list()
    # Skip first 8 lines as they are SIMI Biocell Metadata
    smd = open(smdfile, "r")
    reader = csv.reader(smd)
    for x in range(0, 8):
        next(reader)
    cellCounter = 0
    for line in reader:
        # Ignore first few lines of input as they are cell metadata.
        for x in range(0, 3):
            line = next(reader)
        cell = Cell(cellCounter)
        rows = int(line[0])
        # Obtain Cell Postitions
        for coordLine in range(0, rows):
            line = next(reader)
            coord = line[0].split()
            cell.addLocTime(int(coord[0]), int(coord[1])
                            ,int(coord[2]), int(coord[3]))
        cellCounter += 1
        cellList.append(cell)
        line = next(reader)
    for x in range(0,len(cellList)):
        cellList[x].locOverTime = interpolatePoints(cellList[x])
    return cellList

def plotTrackedCells(cell):
    for cell in cells:
        if len(cell.locOverTime) >0:
            # 3D Plot
            locs = cell.locOverTime
            loc_df = pd.DataFrame.from_records([l.to_dict() for l in locs])
            fig = plt.figure()
            ax = fig.add_subplot(111,projection='3d')
            axeee =ax.scatter(loc_df['x'], loc_df['y'],loc_df['z'],c=loc_df['t'])
            ax.set_xlabel("X Location (Pixels)")
            ax.set_ylabel("Y Location (Pixels)")
            ax.set_zlabel("Z Location (Z-Stack)")
            ax.set_zlim(0,16)
            ax.set_xlim(0,500)
            ax.set_ylim(0,500)
            plt.colorbar(axeee)
            plt.show()
            # 2D Plot
            fig = plt.figure()
            ax = fig.add_subplot(111)
            axeee =ax.scatter(loc_df['x'], loc_df['y'],c=loc_df['t'])
            ax.set_xlabel("X Location (Pixels)")
            ax.set_ylabel("Y Location (Pixels)")
            ax.set_xlim(0,500)
            ax.set_ylim(0,500)
            plt.colorbar(axeee)
            plt.show()

# Plot all Cells
def plotDetectedCells(cells):
    locs = pd.DataFrame.from_records([c.to_dict() for c in cells])
    fig = plt.figure()
    ax = fig.add_subplot(111,projection='3d')
    ax.scatter(locs['x'], locs['y'],locs['z'])
    ax.set_xlabel("X Location (Pixels)")
    ax.set_ylabel("Y Location (Pixels)")
    ax.set_zlabel("Z Location (Z-Stack)")
    ax.set_zlim(0,16)
    ax.set_xlim(0,500)
    ax.set_ylim(0,500)
    plt.show()


def plotCellsAtATime(cells,length):
    for t in range(length,-1,-1):
        cellAtT = getListOfPointsAtTime(cells,t)
        if len(cellAtT) > 0:
            plotDetectedCells(cellAtT)

# Get all cells found at time t.
def getCellAtT(cells,t):
    cellAtT = []
    pointsAtT = []
    for cell in cells:
        locs = cell.locOverTime
        locAtTime = checkForTime(locs,t)
        if locAtTime is not None:
            cellAtT.append(cell)
            pointsAtT.append(Point(locAtTime.time,locAtTime.x,locAtTime.y,locAtTime.z))
    return cellAtT, pointsAtT

# Get a list of all the points which are occupied at time T.
def getListOfPointsAtTime(cells,t):
    cellAtT = []
    for cell in cells:
        locs = cell.locOverTime
        locAtTime = checkForTime(locs,t)
        if locAtTime is not None:
            cellAtT.append(Point(locAtTime.time,locAtTime.x,locAtTime.y,locAtTime.z))
    return cellAtT

# Find matching time locations.
def checkForTime(locs,time):
    for point in locs:
        if point.time == time:
            return point
    return None

# Interpolate the Movement of Cells provided from data.
def interpolatePoints(cell):
    locs = cell.locOverTime
    additionaltimes = []
    # Check every entry for missed time steps.
    for x in range(0,len(locs) -1):
        time = locs[x].time
        diff = locs[x +1].time - locs[x].time
        x_movement = (locs[x+1].x - locs[x].x) / diff
        y_movement = (locs[x+1].y - locs[x].y)/ diff
        z_movement = (locs[x+1].z - locs[x].z) / diff
        # If cell tracking is missed for a frame or more, interpolate.
        if diff > 1:
            for d in range(1,diff):
                newx = int(x_movement *d + locs[x].x)
                newy = int(y_movement *d + locs[x].y)
                newz = int(z_movement *d + locs[x].z)
                additionaltimes.append(Point(time+d, newx, newy, newz))
    # Return interpolated results.
    locs = locs + additionaltimes
    locs.sort()
    return locs

# Find the Best Matches for all Manual Cells in our Automated Cell Data.
def matchCells(manual, auto, offset, errorfile):
    matchedCells = []
    numMan = len(manual)
    for manCell in manual:
        if(len(manCell.locOverTime) > 10):
            manCellLoc = manCell.locOverTime[0]
            startTime = int(manCellLoc.time) - offset
            distanceList = [avPointDifference(manCell,c) for c in auto]
            minDist = min(distanceList)
            match  = auto[distanceList.index(minDist)]
            tup = (manCell,match)
            matchedCells.append(tup)
            overlap = cellOverlap(manCell,match)
            outputDist = avPointDifference(manCell,match,False)
            print("Match found. {} out of {} matched. Error of Average {}. Tracking Length: Auto {} Manual {}".format(len(matchedCells),
                                                                        numMan, minDist,len(match.locOverTime),len(manCell.locOverTime)))
            errorfile.write("{},{},{},{},{}\n".format(len(matchedCells),outputDist,len(match.locOverTime),len(manCell.locOverTime),overlap))
    return matchedCells

# Count how many time overlaps exist.
def cellOverlap(man, auto):
    counter = 0
    auto_locs = auto.locOverTime
    for loc in man.locOverTime:
        for au_loc in auto_locs:
            if au_loc.time == loc.time:
                counter += 1
    return counter

# Calculate average distance between like points.
def avPointDifference(manCell, autoCell, compute=True):
    auto_locs = autoCell.locOverTime
    counter = 0
    totalDist = 0
    for loc in manCell.locOverTime:
        for au_loc in auto_locs:
            if au_loc.time == loc.time:
                counter += 1
                totalDist += pointDist(loc,au_loc)
    av = 1000000
    if counter > 0:
        av = int(totalDist/counter)
    if compute:
        return av * (len(manCell.locOverTime) / len(autoCell.locOverTime))
    else:
        return av

def pointDist(pointOne, pointTwo):
    x_dist = abs(pointOne.x - pointTwo.x) **2
    y_dist = abs(pointOne.y - pointTwo.y) **2
    z_dist = (abs(pointOne.z - pointTwo.z) )** 2
    return math.sqrt(x_dist + y_dist + z_dist)

# Generate Metrics for Tracking.
def findErrorTracking(output, manual):
    errorfile = open("error.csv",'w')
    outputCells = parseSMD(output)
    manualCells = parseSMD(manual)
    errorfile.write("MatchNumber,AverageError,ManualLength,AutoLength,CellOverlap\n")
    matchedCells = matchCells(manualCells, outputCells, 19, errorfile)

# Generate Metrics for Cell Detection.
def findErrorDetection(output,manual, time=369):
    errorfile = open("errorDet.csv",'w')
    errorfile.write("Time,TotalError,AverageError,ManTrackedCells,AutoTrackedCells\n")
    outputCells = parseSMD(output)
    manualCells = parseSMD(manual)
    for t in range(0,time):
        counter = 0
        manLocsT = getListOfPointsAtTime(manualCells,t+19)
        outLocsT = getListOfPointsAtTime(outputCells,t)
        error = 0
        avError = 0
        if len(manLocsT) > 0 and len(outLocsT) > 0:
            for loc in manLocsT:
                distances = [pointDist(loc,l) for l in outLocsT]
                minDist = min(distances)
                error += minDist
                counter += 1
            avError = error/counter
        print("{},{},{},{},{}\n".format(t,error,avError,len(manLocsT), len(outLocsT)))
        errorfile.write("{},{},{},{},{}\n".format(t,error,avError,len(manLocsT), len(outLocsT)))


# Plot Matching Cells Together.
def plotMatchCells(matchTuples):
    for tup in matchTuples:
        man_locs = tup[0].locOverTime
        auto_locs = tup[1].locOverTime
        man_loc_df = pd.DataFrame.from_records([l.to_dict() for l in man_locs])
        auto_loc_df = pd.DataFrame.from_records([l.to_dict() for l in auto_locs])
        fig = plt.figure()
        ax = fig.add_subplot(111,projection='3d')
        ax.scatter(man_loc_df['x'], man_loc_df['y'],man_loc_df['z'],c='black',alpha=0.3)
        ax.scatter(auto_loc_df['x'], auto_loc_df['y'],auto_loc_df['z'],c='red')
        ax.set_xlabel("X Location (Pixels)")
        ax.set_ylabel("Y Location (Pixels)")
        ax.set_zlabel("Z Location (Z-Stack)")
        ax.set_zlim(0,16)
        ax.set_xlim(0,500)
        ax.set_ylim(0,500)
        plt.show()

if __name__ == "__main__":
    options = int(sys.argv[1])
    # Plot Tracked
    if options == 1:
        cells = parseSMD(sys.argv[2])
        cells = [cell for cell in cells if len(cell.locOverTime) >0]
        cells.sort(key=cellLengthSort, reverse=True)
        plotTrackedCells(cells)
    # Plot all Cells at Given Time.
    else if options ==2:
        cells = parseSMD(sys.argv[2])
        cells = [cell for cell in cells if len(cell.locOverTime) >0]
        plotCellsAtATime(cells,int(sys.argv[3]))
    # Find Error Metrics.
    else:
        findError(sys.argv[2],sys.argv[3])
        findErrorDetection(sys.argv[2],sys.argv[3])