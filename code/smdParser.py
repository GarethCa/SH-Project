# Citation Needed for this block of code.


import csv


def getCellsAtTime(time, smdfile=""):
    smdfile = "newsmdfile.smd"
    # this is the timepoint where manual tracking started
    startingPoint = 24
    coords = list()
    smd = open(smdfile, "r")
    reader = csv.reader(smd)
    # skips first 8 lines as they're not cells
    for x in range(0, 8):
        reader.next()

    for line in reader:
        # first 3 lines in cell are just info
        for x in range(0, 3):
            line = reader.next()
        rows = int(line[0])
        # get cell positions
        for n in range(0, rows):
            line = reader.next()
            digits = line[0].split()
            if int(digits[0]) == int(time) + startingPoint:
                coords.append([digits[1], digits[2], digits[3]])

        line = reader.next()

    return coords


def getCellsAtTimeAndLayer(time, layer):
    coords = getCellsAtTime(time)
    px = []
    py = []
    for coord in coords:
        if coord[2] == str(layer):
            px.append(int(coord[0]))
            py.append(int(coord[1]))
    return px, py
