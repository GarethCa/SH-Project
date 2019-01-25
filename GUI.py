from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
from PIL import Image, ImageTk
import os, re


def dirButtonHandler(lab, entry, num,text):
    directory = filedialog.askdirectory()
    fileList = sorted(os.listdir(directory))
    ima = Image.open(directory + "/" + fileList[int(num)])
    photo = ImageTk.PhotoImage(ima)
    lab.image = photo
    lab.config(image=photo)
    text.set(directory)

def changeFunc(lab,num,dire):
    dire = textForDir.get()
    fileList = sorted(os.listdir(dire))
    ima = Image.open(dire + "/" + fileList[int(num)])
    photo = ImageTk.PhotoImage(ima)
    lab.image = photo
    lab.config(image=photo)

#Create Window
window = Tk()

#Placeholder Image Loader
image = Image.open("./Resources/placeholder.png")
photo = ImageTk.PhotoImage(image)

# directory = filedialog.askdirectory()
# fil = ""
# fileList = sorted(os.listdir(directory))
# sub = 'X***L'
# listof = []
# for fils in fileList:
#     listof += re.findall(r'(X.+L)',fils)
#     fil = fils
# print(listof)
# print(sorted(set((listof))))

#Define Window

fpLabel = Label(window, text="Footprint").grid(row=2, column=0)
fpSelector = Entry(window).grid(row=2,column=1)

lbLabel = Label(window, text="LowBound").grid(row=3,column=0)
lbSelector = Entry(window).grid(row=3,column=1)
hbLabel = Label(window, text="HighBound").grid(row=3,column=2)
hbSelector = Entry(window).grid(row=3,column=3)

threshLabel = Label(window,text="Threshold").grid(row=4,column=0)
threshSelector = Entry(window).grid(row=4,column=1)

previewButton = Button(window,text="Preview").grid(row=5,column=0,columnspan=2)
trackButton = Button(window,text="Track").grid(row=5,column=2,columnspan=2)

progBar = Progressbar(window,length=400).grid(row=6,column=0,columnspan=4)

imLabel = Label(image=photo)
imLabel.image =photo
imLabel.grid(row=0,column=4, columnspan=3,rowspan=20)
textForDir = StringVar()

xSelect = Scale(window, from_=0,to=200,orient=HORIZONTAL,length=400)
xSelect.config(command= lambda x:changeFunc(imLabel,xSelect.get(),textForDir.get()))
xSelect.grid(row=18,column=0,columnspan=4)
lSelect = Scale(window, from_=0,to=200,orient=HORIZONTAL,length=400)
lSelect.grid(row=19,column=0,columnspan=4)


dirLabel = Label(window, text="Directory").grid(row=0,column=0)
dirText = Entry(window,text=".",textvariable=textForDir)
dirText.grid(row=0,column=1,columnspan=2)
dirButt = Button(window,text="Choose",command=lambda: dirButtonHandler(imLabel,dirText,xSelect.get(),textForDir)).grid(row=0,column=3)



#Run Window
window.mainloop()



    