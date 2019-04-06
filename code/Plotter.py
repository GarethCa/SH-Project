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
from Track import getInitialCells, iterateThroughCells, outputData, tooShort
from time import time
from itertools import groupby
from sklearn.cluster import DBSCAN
import pandas as pd


def removeLabel(label_image, p):
    match = label_image == p.label
    label_image[match] = 0
    return label_image


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


def segment(image, filename, params, bulk=True, display=False):

    if (image == 0).all():
        return ""
    # Sets all Values to either black or white.
    copy = image.copy()
    image = ndi.gaussian_filter(image, sigma=1)
    t = threshold_otsu(image)
    t = t * params[2]
    image = image > t

    image = binary_closing(image)
    # plt.imsave("../PipelineOutput/4BinClosing.png",image)
    # image = erosion(image)
    # plt.imsave('../PipelineOutput/5Erosion.png', image)
    

    cleared = clear_border(image)
    # plt.imsave('../PipelineOutput/6ClearedBorder.png', cleared)
    distance = ndi.distance_transform_edt(image)
    # plt.imsave("../PipelineOutput/7DistTransform.png",distance)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((params[3], params[3])),
                                labels=cleared)
    # plt.imsave("../PipelineOutput/8LocalMaxi.png",local_maxi)
    markers = ndi.label(local_maxi)[0]
    label_im = watershed(-distance, markers, mask=cleared)
    
    label_im_orig = label_im.copy()
    label_info = measure.regionprops(label_im.astype(int))
    cellList = outputInformation(label_info,filename)
    
    for p in label_info:
        if p.convex_area < params[0] or p.convex_area > params[1]:
            label_im = removeLabel(label_im, p)
    
    image = copy
    cellList = outputInformation(label_info, filename)
    cellList = clusterTrimmer(cellList)

    if display:
        if bulk:
            del label_im
            del label_im_orig
            del cleared
            plotImageBulk(image, cellList, filename)
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


def plotImageBulk(image, cellList, filename):
    fig, axes = plt.subplots(ncols=1, sharex=True, sharey=True)
    axes.imshow(image, cmap='gray')
    for c in centroids:
        loc = c.locOverTime[-1]
        axes.scatter(loc.x, loc.y, color='red', s=2)

    fig.savefig("../Output/" + ntpath.basename(filename), bbox_inches='tight')
    plt.close()


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
    # plt.close(fig)

def clusterTrimmer(cellList):
    df = pd.DataFrame.from_records([c.to_dict() for c in cellList])
    clustering = DBSCAN(eps=20, min_samples=8).fit(df)
    counter = 0
    for lab in clustering.labels_:
        cellList[counter].setClustered(lab)
        counter += 1
    cellList = [cell for cell in cellList if cell.clustered > -1]
    return cellList
    

def runSingle(argTuple):
    params = argTuple[0]
    filename = argTuple[1]
    disp = argTuple[2]
    image = cv2.imread(filename, 0)
    if image.shape != None:
        return segment(image, filename, params, bulk=False, display=disp)
    else:
        return "\n"


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
    pool = Pool()
    pool.map(runSingle, paramFileList)

    pool.close()
    pool.join()


def runForTracking(params, filename=""):
    if filename is not "":
        files = os.listdir(str(filename.get()))
    else:
        files = os.listdir("../green_focus/")
    files = sorted(files)
    filesFirst = [f for f in files if f.startswith("X000")]
    [f for f in files if (not f.startswith("X000"))]
    paramFileList = []
    groupedFiles = [list(g) for k, g in groupby(files, key=lambda x: x[:4])]
    for fil in filesFirst:
        paramFileList.append((params, "../green_focus/" + fil, False))

    pool = Pool()
    t0 = time()
    val = pool.map(runSingle, paramFileList)

    listTwo_Val = []
    for pa in groupedFiles:
        secondParamList = []
        for fil in pa:
            secondParamList.append((params, "../green_focus/" + fil, False))
        print(secondParamList[0])
        two_val = pool.map(runSingle, secondParamList)
        listTwo_Val.append(two_val)
    t1 = time()

    pool.close()
    pool.join()

    print("Detection Complete, took {} seconds".format(t1-t0))
    cellList = [item for sublist in val for item in sublist]
    cellLists = getInitialCells(cellList)

    print("Length of cells found in first", len(cellLists))

    t0 = time()
    disca = []

    pool = Pool()
    t0 = time()
    val = pool.map(runSingle, paramFileList)
    list_for_cells = pool.map(threadedCellTrack, listTwo_Val)
    t1 = time()
    pool.close()
    pool.join()

    counter = 0
    for lis in list_for_cells:
        lis = clusterTrimmer(lis)
        cellLists, discarded = iterateThroughCells(lis, cellLists)
        disca = disca + discarded
        print(counter, len(cellLists), len(disca))
        counter += 1

    t1 = time()
    cellLists = cellLists + disca
    cellLists = [x for x in cellLists if not tooShort(x, 10)]

    cellLists.sort(key=cellSort)
    counter = 0
    for cell in cellLists:
        cell.id = counter
        counter += 1
    print("Finished. Took {} seconds to process".format(t1-t0))
    outputData(cellLists)


def threadedCellTrack(lis):
    cellList2 = [item for sublist in lis for item in sublist]
    cellList2 = getInitialCells(cellList2)
    if(len(cellList2) > 0 ):
        print(cellList2[0].lastTracked())
    return cellList2


def nearestNeighbour(cell, next):
    best_val = 1000000
    best_idx = 0
    idx = 0
    for n in next:
        cur_val = cellDist(cell, n)
        if cur_val < best_val:
            best_val = cur_val
            best_idx = idx
        idx += 1

    if best_val > 20:
        return "100000"
    return best_idx

def chunks(l, n):
    n = max(1, n)
    return [l[i:i+n] for i in xrange(0, len(l), n)]


def cellSort(cell):
    return cell.locOverTime[0].time


if __name__ == "__main__":
    params = [10, 70, 1.2, 4]
    runOnT(params, display=True)
    makeVideo()
