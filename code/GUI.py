import glob
import ntpath
import os
import re
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *

from PIL import Image, ImageTk
from Plotter import *
from VideoGen import *

lScale = 0


def dirButtonHandler(lab, entry, barX, barY, text):
    directory = filedialog.askdirectory()
    fileList = sorted(glob.glob(directory + "/*L000.TIF"))
    regex = r"(X(0+)L).*"
    levels = len([f for f in os.listdir(
        directory + "/") if re.search(regex, f)])
    barX.config(to=len(fileList) - 1)
    barY.config(to=(levels - 2))
    global lScale
    lScale = levels
    ima = Image.open(fileList[0])
    photo = ImageTk.PhotoImage(ima)
    lab.image = photo
    lab.config(image=photo)
    text.set(directory)


def changeFunc(lab, barX, barL):
    index = (int(barX.get()) * lScale) + int(barL.get())
    directory = textForDir.get()
    fileList = sorted(glob.glob(directory + "/*.TIF"))
    ima = Image.open(fileList[index])
    photo = ImageTk.PhotoImage(ima)
    lab.image = photo
    lab.config(image=photo)


def preview(barX, barL, lab):
    params = [int(lbSelector.get()), int(hbSelector.get()),
              float(threshSelector.get()), int(fpSelector.get())]
    index = (int(barX.get()) * lScale) + int(barL.get())
    directory = textForDir.get()
    fileList = sorted(glob.glob(directory + "/*.TIF"))
    fileName = fileList[index]
    runSingle( (params,fileName,True))
    ima = Image.open("../Output/" + ntpath.basename(fileName))
    photo = ImageTk.PhotoImage(ima)
    lab.image = photo
    lab.config(image=photo)

def genMovie(filename):
    params = [int(lbSelector.get()), int(hbSelector.get()),
              float(threshSelector.get()), int(fpSelector.get())]
    runOnT(params,filename)
    makeVideo()

def runTracking(fileName):
    params = [int(lbSelector.get()), int(hbSelector.get()),
              float(threshSelector.get()), int(fpSelector.get())]
    runForTracking(params,fileName)


# Create Window
window = Tk()
window.title("Cell Tracker")

# Placeholder Image Loader
image = Image.open("../Resources/placeholder.png")
photo = ImageTk.PhotoImage(image)


# Define Window

lbVal = StringVar(window, value="10")
hbVal = StringVar(window, value="50")
threshVal = StringVar(window, value="1.4")
footprintVal = StringVar(window, value=8)

#Param Section##################################
fpLabel = Label(window, text="Footprint").grid(row=2, column=0)
fpSelector = Entry(window, textvariable=footprintVal)
fpSelector.grid(row=2, column=1)
lbLabel = Label(window, text="Minimum Size").grid(row=3, column=0)
lbSelector = Entry(window, textvariable=lbVal)
lbSelector.grid(row=3, column=1)
hbLabel = Label(window, text="Maximum Size").grid(row=4, column=0)
hbSelector = Entry(window, textvariable=hbVal)
hbSelector.grid(row=4, column=1)

threshLabel = Label(window, text="Threshold").grid(row=5, column=0)
threshSelector = Entry(window, textvariable=threshVal)
threshSelector.grid(row=5, column=1)


###################################################

progBar = Progressbar(window, length=400).grid(row=7, column=0, columnspan=4)

imLabel = Label(image=photo)
imLabel.image = photo
imLabel.grid(row=0, column=4, columnspan=3, rowspan=20)

textForDir = StringVar()

xSelect = Scale(window, from_=0, to=200, orient=HORIZONTAL, length=400)
xSelect.grid(row=17, column=0, columnspan=4)
xSelLabel = Label(window, text="X Level").grid(row=16, column=0)
lSelect = Scale(window, from_=0, to=200, orient=HORIZONTAL, length=400)
lSelLabel = Label(window, text="L Level").grid(row=18, column=0)
lSelect.grid(row=19, column=0, columnspan=4)
xSelect.config(command=lambda x: changeFunc(imLabel, xSelect, lSelect))
lSelect.config(command=lambda x: changeFunc(imLabel, xSelect, lSelect))


dirLabel = Label(window, text="Directory").grid(row=0, column=0)
dirText = Entry(window, text=".", textvariable=textForDir)
dirText.grid(row=0, column=1)
dirButt = Button(
    window,
    text="Choose",
    command=lambda: dirButtonHandler(
        imLabel,
        dirText,
        xSelect,
        lSelect,
        textForDir)).grid(
            row=0,
    column=2)

previewButton = Button(window, text="Preview")
previewButton.grid(row=6, column=0)
previewButton.config(command=lambda: preview(xSelect, lSelect, imLabel))
movieButton = Button(window, text="Generate Video")
movieButton.grid(row=6, column=1)
movieButton.config(command=lambda: genMovie(textForDir))

trackButton = Button(window, text="Track")
trackButton.grid(row=6, column=2)
trackButton.config(command=lambda: runTracking(textForDir))


# Run Window
window.mainloop()
