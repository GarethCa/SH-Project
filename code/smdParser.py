# Citation Needed for this block of code.
# Adapted from previous year's attempt.

import csv
from Cell import * 
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np


def parseSMD(smdfile):
    cellList =  []
    coords = list()
    smd = open(smdfile, "r")
    reader = csv.reader(smd)
    # skips first 8 lines as they're not cells
    for x in range(0, 8):
        next(reader)

    cellCounter = 0
    for line in reader:
        # first 3 lines in cell are just info
        for x in range(0, 3):
            line = next(reader)
        cell = Cell(cellCounter)
        rows = int(line[0])
        # get cell positions
        for coordLine in range(0, rows):
            line = next(reader)
            coord = line[0].split()
            cell.addLocTime(int(coord[0]), int(coord[1])
                            ,int(coord[2]), int(coord[3]))
        cellCounter += 1
        cellList.append(cell)
        line = next(reader)
    return cellList

def plotTrackedCells(cell):
    for cell in cells:
        locs = cell.locOverTime
        print(len(locs))
        loc_df = pd.DataFrame.from_records([l.to_dict() for l in locs])
        fig = plt.figure()
        ax = fig.add_subplot(111,projection='3d')
        ax.scatter(loc_df['x'], loc_df['y'],loc_df['z'],c=loc_df['t'])
        ax.set_xlabel("X Location (Pixels)")
        ax.set_ylabel("Y Location (Pixels)")
        ax.set_zlabel("Z Location (Z-Stack")
        ax.set_zlim(0,16)
        ax.set_xlim(0,500)
        ax.set_ylim(0,500)
        plt.show()

if __name__ == "__main__":
    cells = parseSMD("output.smd")
    cells.sort(key=cellLengthSort, reverse=True)
    plotTrackedCells(cells)