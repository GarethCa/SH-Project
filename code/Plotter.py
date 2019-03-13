from scipy import ndimage as ndi, misc
from skimage import measure
import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import ntpath
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.morphology import closing, watershed
from multiprocessing import Pool
from VideoGen import *
from Cell import *
from Track import getInitialCells, iterateThroughCells, outputData
from time import time
from itertools import groupby


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
        cell.addLocTime(time,int(lab.centroid[0]),int(lab.centroid[1]),z)
        cellList.append(cell)
        counter = counter + 1
    return cellList


def segment(image, filename, params, bulk=True, display=False):
    image = ndi.gaussian_filter(image, sigma=0.4)
    if (image == 0).all():
        return ""
    thresh = threshold_otsu(image)
    bw = closing(image > thresh * params[2])
    cleared = clear_border(bw)
    distance = ndi.distance_transform_edt(cleared)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((params[3], params[3])),
                                labels=cleared)
    markers = ndi.label(local_maxi)[0]
    label_im = watershed(-distance, markers, mask=cleared)

    label_im_orig = label_im.copy()
    label_info = measure.regionprops(label_im.astype(int))
    for p in label_info:
        if p.convex_area < params[0] or p.convex_area > params[1]:
            label_im = removeLabel(label_im, p)

    label_info = measure.regionprops(label_im.astype(int))
    outputInformation(label_info, filename)
    if display:
        if bulk:
            del label_im
            del label_im_orig
            del cleared
            plotImageBulk(image, label_info, filename)
        else:
            plotImage(
                image,
                label_im_orig,
                label_im,
                cleared,
                label_info,
                filename)
    else:
        del label_im
        del label_im_orig
        del cleared
        return outputInformation(label_info, filename)





def plotImageBulk(image, centroids, filename):
    fig, axes = plt.subplots(ncols=1, sharex=True, sharey=True)
    axes.imshow(image, cmap='gray')
    for c in centroids:
        axes.scatter(c.centroid[1], c.centroid[0], color='red', s=2)

    fig.savefig("../Output/" + ntpath.basename(filename), bbox_inches='tight')
    plt.close()


def plotImage(image, label_im, label_im_treated, cleared, centroids, filename):
    fig, axes = plt.subplots(ncols=1, squeeze=True)
    axes.imshow(image, cmap='gray')
    for c in centroids:
        axes.scatter(c.centroid[1], c.centroid[0], color='red', s=2)

    fig.tight_layout()
    axes.axis('off')
    fig.savefig("../Output/" + ntpath.basename(filename), bbox_inches='tight')
    # plt.close(fig)


def runSingle(argTuple):
    params = argTuple[0]
    filename = argTuple[1]
    disp = argTuple[2]
    image = cv2.imread(filename, 0)
    if image.shape != None:
        return segment(image, filename, params, bulk=False, display=disp)
    else:
        return "\n"


def runOnT(params, filename="", display = True):
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
    val = pool.map(runSingle, paramFileList)

    pool.close()
    pool.join()

def runForTracking(params, filename=""):
    if filename is not "":
        files = os.listdir(str(filename.get()))
    else:
        files = os.listdir("../green_focus/")
    files = sorted(files)
    filesFirst = [f for f in files if f.startswith("X001")]
    restOfFiles = [f for f in files if  (not f.startswith("X001"))]
    paramFileList = []
    groupedFiles = [list(g) for k, g in groupby(files, key=lambda x: x[:4])]
    for fil in filesFirst:
        paramFileList.append((params, "../green_focus/" + fil, False))
    
    pool = Pool()
    t0 = time()
    val = pool.map(runSingle, paramFileList)
    listTwo_Val = []
    for pa in groupedFiles[1:50]:
        secondParamList =[]
        for fil in pa:
            secondParamList.append((params, "../green_focus/"+ fil, False))
        print(secondParamList[0])
        two_val = pool.map(runSingle,secondParamList)
        listTwo_Val.append(two_val)
    t1 = time()
    
    pool.close()
    pool.join()

    
    print("Detection Complete, took {} seconds".format(t1-t0))
    cellList = [item for sublist in val for item in sublist]
    cellList2 = [item for sublist in two_val for item in sublist]
    cellLists = getInitialCells(cellList)
    print("Iterate")
    t0 = time()
    iterateThroughCells(cellList2, cellLists)
    t1 = time()
    print("Finished. Took {} seconds to process".format(t1-t0))
    outputData(cellLists)

    


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


def plotImageMethod(image, label_im, label_im_treated,
                    cleared, centroids, filename):
    fig, axes = plt.subplots(ncols=2, nrows=2, sharex=True, sharey=True)
    ax = axes.ravel()
    ax[0].imshow(image, cmap='binary_r', interpolation='nearest')
    ax[0].set_title('Original Image')
    ax[1].imshow(cleared)
    ax[1].set_title('Otsu Thresholded Image')
    ax[2].imshow(label_im, cmap='nipy_spectral_r')
    ax[2].set_title('Segmented Image')
    ax[3].imshow(image, cmap='gray')
    for c in centroids:
        ax[3].scatter(c.centroid[1], c.centroid[0], color='red', s=5)
    ax[3].set_title('Centroids Found')

    plt.tight_layout()
    plt.savefig("../Output/" + ntpath.basename(filename), bbox_inches='tight')

def chunks(l, n):
    n = max(1, n)
    return [l[i:i+n] for i in xrange(0, len(l), n)]


if __name__ == "__main__":
    params = [10, 70, 1.2, 4]
    runOnT(params, display=True)
    makeVideo()

