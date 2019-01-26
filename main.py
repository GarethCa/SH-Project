from scipy import ndimage as ndi, misc 
from skimage import filters, measure
import numpy as np
import matplotlib.pyplot as plt
import cv2, math, os
import ntpath
from skimage.feature import peak_local_max,blob_dog
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square, watershed, disk
from skimage.color import label2rgb


def removeLabel(label_image, p):
    match = label_image == p.label
    label_image[match] = 0
    return label_image

def outputInformation(labels):
    with open('output.txt', 'w') as the_file:
        counter = 0
        for lab in labels:
            the_file.write(str(counter) + " " + str(map(math.floor,lab.centroid)) 
            + " " + str(lab.area)+'\n')
            counter = counter +1
        the_file.close()

def segment(image,filename,bulk=True, display=False):

    image = ndi.gaussian_filter(image,sigma=0.3)
    thresh = threshold_otsu(image)
    bw = closing(image > thresh*1.2)
    cleared = clear_border(bw)
    distance = ndi.distance_transform_edt(cleared)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((4,4)),
                                labels=cleared)
    markers = ndi.label(local_maxi)[0]
    label_im = watershed(-distance, markers, mask=cleared)

    label_im_orig = label_im.copy()
    label_info = measure.regionprops(label_im.astype(int))
    for p in label_info:
        if p.convex_area <10 or p.convex_area >70 :
            label_im =removeLabel(label_im,p)

    label_info = measure.regionprops(label_im.astype(int))
    outputInformation(label_info)
    if display:
        if bulk:
            plotImageBulk(image,label_info,filename)
        else:
            plotImage(image,label_im_orig,label_im,cleared,label_info,filename)
    return label_info


def plotImageBulk(image, centroids,filename):
    fig, axes = plt.subplots(ncols =1, sharex=True, sharey=True)
    axes.imshow(image,cmap='gray')
    for c in centroids:
        axes.scatter(c.centroid[1],c.centroid[0],color='red',s=2) 

    fig.tight_layout()
    fig.savefig("./Output/"+filename,bbox_inches='tight')
    plt.close()

def plotImage(image,label_im ,label_im_treated, cleared, centroids,filename):
    # fig, axes = plt.subplots(ncols =2,nrows=2, sharex=True, sharey=True)
    # ax = axes.ravel()
    # ax[0].imshow(image, cmap='binary_r', interpolation='nearest')
    # ax[0].set_title('Original Image')
    # ax[1].imshow(cleared)
    # ax[1].set_title('Otsu Thresholded Image')
    # ax[2].imshow(label_im,cmap='nipy_spectral_r')
    # ax[2].set_title('Segmented Image')
    # ax[3].imshow(image,cmap='gray')
    # for c in centroids:
    #     ax[3].scatter(c.centroid[1],c.centroid[0],color='red',s=5) 
    # ax[3].set_title('Centroids Found')

    # plt.tight_layout()
    # # plt.show()
    # plt.savefig("Output/"+filename,bbox_inches='tight')
    # plt.close()
    fig, axes = plt.subplots(ncols =1, sharex=True, sharey=True)
    axes.imshow(image,cmap='gray')
    for c in centroids:
        axes.scatter(c.centroid[1],c.centroid[0],color='red',s=2) 

    fig.tight_layout()
    fig.savefig("./Output/"+ntpath.basename(filename),bbox_inches='tight')

def runOnT():
    files = os.listdir("./green_focus")
    files = sorted(files, key=lambda item: (int(item.partition(' ')[0])
                                if item[0].isdigit() else float('inf'), item))

    for filename in files:
        if filename.endswith("005.TIF"): 
            print(filename)
            image = cv2.imread("./green_focus/"+filename,0) 
            segment(image,filename,bulk=True)
            del image
            continue
        else:
            continue

def runSingle(filename):
    image = cv2.imread(filename,0)
    segment(image,filename,bulk=False,display=True)

def makeVideo():
    files = os.listdir("Output/")
    files = sorted(files, key=lambda item: (int(item.partition(' ')[0])
                                if item[0].isdigit() else float('inf'), item))
    frame = cv2.imread("Output/"+files[0])
    height,width, layers = frame.shape
    video = cv2.VideoWriter("test.mp4",cv2.VideoWriter_fourcc(*'MP4V'), 16, (width,height))
    for filename in files:
        video.write(cv2.imread("Output/"+filename))
    cv2.destroyAllWindows()
    video.release()
    print('Video Generated')

def nearestNeighbour(cell, next):
    best_val = 1000000
    best_idx = 0
    idx = 0
    for n in next:
        cur_val = cellDist(cell,n)
        if cur_val < best_val:
            best_val = cur_val
            best_idx = idx
        idx += 1

    if best_val > 20:
        return "100000"
    return  best_idx 

def cellDist(cenOne, cenTwo):
    x_dist = abs(cenOne.centroid[0] - cenTwo.centroid[0])
    y_dist = abs(cenOne.centroid[1] - cenTwo.centroid[1])
    return x_dist + y_dist

# runOnT()
# makeVideo()
