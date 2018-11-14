from scipy import ndimage as ndi 
from scipy import misc 
from skimage import filters, measure
import numpy as np
import matplotlib.pyplot as plt
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square, watershed
from skimage.color import label2rgb
import cv2
import math
import os

def removeLabel(label_image, p):
    match = label_image == p.label
    label_image[match] = 0
    return label_image

def outputInformation(labels):
    with open('output.txt', 'a') as the_file:
        counter = 0
        for lab in labels:
            the_file.write(str(counter) + " " + str(map(math.floor,lab.centroid)) 
            + " " + str(lab.area)+'\n')
            counter = counter +1
        the_file.close()

def performWatershed(image,filename):
    image = ndi.gaussian_filter(image,sigma=1)
    thresh = threshold_otsu(image)

    
    bw = closing(image > thresh)
    
    cleared = clear_border(bw)

    distance = ndi.distance_transform_edt(cleared)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((3, 3)),
                                labels=cleared)
    markers = ndi.label(local_maxi)[0]
    label_im = watershed(-distance, markers, mask=cleared)


    new = measure.regionprops(label_im.astype(int))
    label_im_orig = label_im.copy()
    # for p in new:
    #     if p.area <5 or p.area > 60:
    #         label_im =removeLabel(label_im,p)

    new = measure.regionprops(label_im.astype(int))
    # outputInformation(new)
    plotImage(image,label_im_orig,label_im,cleared,new,filename)


def plotImage(image,label_im ,label_im_treated, cleared, centroids,filename):
    fig, axes = plt.subplots(ncols =1, sharex=True, sharey=True)
    # ax = axes.ravel()
    # ax[0].imshow(image, cmap='binary_r', interpolation='nearest')
    # ax[0].set_title('Original Image')
    # ax[1].imshow(cleared)
    # ax[1].set_title('Otsu Thresholded Image')
    # ax[2].imshow(label_im,cmap='nipy_spectral_r')
    # ax[2].set_title('Segmented Image')
    axes.imshow(label_im_treated,cmap='gray')
    # for c in centroids:
        # axes.scatter(c.centroid[1],c.centroid[0],c=0,s=2) 
    # axes.set_title('Centroids Found')

    fig.tight_layout()
    fig.savefig("Output/"+filename,bbox_inches='tight')
    plt.close()

image = cv2.imread("test.tif", 0)
files = os.listdir("./green_focus")
files = sorted(files, key=lambda item: (int(item.partition(' ')[0])
                               if item[0].isdigit() else float('inf'), item))

for filename in files:
    if filename.endswith("005.TIF"): 
        print(filename)
        image = cv2.imread("./green_focus/"+filename,0) 
        performWatershed(image,filename)
        del image
        continue
    else:
        continue


files = os.listdir("Output/")
files = sorted(files, key=lambda item: (int(item.partition(' ')[0])
                               if item[0].isdigit() else float('inf'), item))
frame = cv2.imread("Output/"+files[0])
height,width, layers = frame.shape
video = cv2.VideoWriter("OUTPUT.mp4",cv2.VideoWriter_fourcc(*'MP4V'), 16, (width,height))
for filename in files:
    video.write(cv2.imread("Output/"+filename))
cv2.destroyAllWindows()
video.release()


