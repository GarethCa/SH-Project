from scipy import ndimage as ndi
import scipy.misc as ms
from skimage import measure
import numpy as np
import matplotlib.pyplot as plt
import cv2
from PIL import Image
import os
import ntpath
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.morphology import *
from multiprocessing import Pool
from VideoGen import *
from Cell import *
from smdParser import plotDetectedCells
from Track import  iterateThroughCells, outputData, tooShort
from time import time
from itertools import groupby
from sklearn.cluster import DBSCAN
import pandas as pd


def removeLabel(label_image, p):
    match = label_image == p.label
    label_image[match] = 0
    return label_image

def plotWatershed(image):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    axee= ax.imshow(image, cmap=plt.cm.nipy_spectral, interpolation='nearest')
    plt.colorbar(axee)
    plt.savefig("../Output/watershed.png")

def outputInformation(labels, filename):
    cellList = []
    counter = 0
    filename = filename.split("X")[1]
    filename = filename.split(".")[0]
    filename = filename.split("L")
    z = int(filename[1])
    time = int(filename[0])
    for lab in labels:
        cell = Cell(counter)
        cell.addLocTime(time, int(lab.centroid[0]), int(lab.centroid[1]), z)
        cellList.append(cell)
        counter = counter + 1
    return cellList

def outputInfo3D(labels,filename):
    cellList = []
    counter = 0
    filename = filename.split("X")[1]
    filename = filename.split(".")[0]
    filename = filename.split("L")
    time = int(filename[0])
    for lab in labels:
        cell = Cell(counter)
        cell.addLocTime(time,int(lab.centroid[0]), int(lab.centroid[1]), int(lab.centroid[2]))
        cellList.append(cell)
        counter = counter + 1
    return cellList
    

def preprocessImage(image,params):
    image = ndi.gaussian_filter(image, sigma=1)
    t = threshold_otsu(image) * params[2]
    image = image > t

    image = binary_closing(image)
    cleared = clear_border(image)
    return cleared

def segment(image, filename, params, bulk=True, display=False):

    # Preprocess Image
    if (image == 0).all():
        return ""
    copy = image.copy()
    cleared =  preprocessImage(image,params)
    distance = ndi.distance_transform_edt(image)

    # Perform Watershed Segmentation.
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((params[3], params[3])),
                                labels=cleared)
    markers = ndi.label(local_maxi)[0]
    label_im = watershed(-distance, markers, mask=cleared)
    label_im_orig = label_im.copy()
    label_info = measure.regionprops(label_im.astype(int))
    
    # Filter out Cells.
    for p in label_info:
        if p.convex_area < params[0] or p.convex_area > params[1]:
            label_im = removeLabel(label_im, p)
    image = copy
    cellList = outputInformation(label_info, filename)
    cellList = clusterTrimmer(cellList)

    # Output.
    if display:
        if bulk:
            del label_im
            del label_im_orig
            del cleared
            plotImage(image, cellList, filename)
        else:
            plotImage(
                image,
                cellList,
                filename)
    else:
        del label_im
        del label_im_orig
        del cleared
        return cellList


# Segment 3D Images
def segment3D(filename, params, bulk=True, display=False):

    # Create 3D Images
    images = []
    for fil in filename:
        image = cv2.imread(fil,0)
        if image.shape == None:
            image = images[-1]
        else:
            try:
                cleared =  preprocessImage(image,params)
            except ValueError:
                continue
            images.append(cleared)
    image = np.dstack(images)
    distance = ndi.distance_transform_edt(image)

    # Pre-Processess and Label via Watershed.
    local_max = peak_local_max(distance, indices=False, min_distance=100,
        labels=image, footprint=np.ones((int(params[3]),int(params[3]),2)))
    markers = ndi.label(local_max)[0]
    label_im = watershed(-distance, markers, mask=image)
    
    # Filter
    label_im_orig = label_im.copy()
    label_info = measure.regionprops(label_im.astype(int))
    for p in label_info:
        if p.area < params[0]*10 or p.area > params[1] *10:
            label_im = removeLabel(label_im, p)
    cellList = outputInfo3D(label_info, filename[0])
    cellList = clusterTrimmer(cellList)

    # Output
    print("Finished processing {}, found {} cells.".format(filename[0],len(cellList)))
    return cellList


# Output Cell Images for Preview and Video.
def plotImage(image, cellList, filename):
    fig = plt.figure()
    ax = plt.Axes(fig,[0.,0.,1.,1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    ax.imshow(image, cmap='gray')
    for c in cellList:
        loc = c.locOverTime[-1]
        ax.scatter(loc.y, loc.x, color='red', s=2)
    ax.axis('off')
    fig.savefig("../Output/" + ntpath.basename(filename), bbox_inches='tight')
    plt.close(fig)

#  Remove Clustered Objects
def clusterTrimmer(cellList):
    df = pd.DataFrame.from_records([c.to_dict_cluster() for c in cellList])
    clustering = DBSCAN(eps=20, min_samples=8).fit(df)
    counter = 0
    for lab in clustering.labels_:
        cellList[counter].setClustered(lab)
        counter += 1
    cellList = [cell for cell in cellList if cell.clustered > -1]
    return cellList

# Segment a single image.
def runSingle(argTuple):
    params = argTuple[0]
    filename = argTuple[1]
    disp = argTuple[2]
    image = cv2.imread(filename, 0)
    if image.shape != None:
        return segment(image, filename, params, bulk=False, display=disp)
    else:
        return "\n"

# Helper function for 3D segmentation.
def run3D(argTuple, files):
    params = argTuple
    return segment3D(files, params)

# Run Segmentation over Time for Video Output.
def runOnT(params, filename="", display=True):
    if filename is not "":
        files = os.listdir(str(filename.get()))
    else:
        files = os.listdir("../green_focus/")
    files = sorted(files)
    files = [f for f in files if f.endswith("005.TIF")]
    paramFileList = []
    for fil in files:
        paramFileList.append((params, "../green_focus/" + fil, display))
    for par in paramFileList:
        runSingle(par)

# Multithread 3D dection Enabler.
def mult3DSeg(tup):
    pa = tup[0]
    params = tup[1]
    secondParamList = []
    pa = ["../green_focus/"+f for f in pa]
    cells = run3D(params,pa)
    return cells

def runForTracking(params, filename=""):

    # Loads the Files in Directory
    if filename is not "":
        files = os.listdir(str(filename.get()))
    else:
        files = os.listdir("../green_focus/")
    files = sorted(files)
    groupedFiles = [list(g) for k, g in groupby(files, key=lambda x: x[:4])]
    
    # Multithreading - Detects Cells
    pool = Pool()
    t0 = time()
    paramList = []
    for group in groupedFiles:
        paramList.append((group,params))
    listsOfCells = pool.map(mult3DSeg,paramList) 
    t1 = time()
    pool.close()
    pool.join()

    print("Detection Complete, took {} seconds".format(t1-t0))
    cellLists = listsOfCells[0]

    print("Length of cells found in first", len(cellLists))

    t0 = time()
    disca = []

    # Link cells in tracking.
    counter = 0
    for lis in listsOfCells[1:]:
        lis = clusterTrimmer(lis)
        cellLists, discarded = iterateThroughCells(lis, cellLists)
        disca = disca + discarded
        print(counter, len(cellLists), len(disca))
        counter += 1
    t1 = time()
    
    # Re-add Dead Cells. - Filter away short cells.
    cellLists = cellLists + disca
    cellLists = [x for x in cellLists if not tooShort(x, 10)]

    # Output Data
    cellLists.sort(key=cellSort)
    counter = 0
    for cell in cellLists:
        cell.id = counter
        counter += 1
    print("Finished. Took {} seconds to process".format(t1-t0))
    outputData(cellLists)


def cellSort(cell):
    return cell.locOverTime[0].time
