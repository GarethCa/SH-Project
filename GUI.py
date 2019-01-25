from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk

#Create Window
window = Tk()

# window.filename =  filedialog.askopenfilename(initialdir = ".",title = "Select file",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
filename = filedialog.askopenfilename()
#Load Image
image = Image.open(filename)
photo = ImageTk.PhotoImage(image)


#Define Window

l1 = Label(image=photo)
l1.image = photo
l1.grid(row=0, column=1)

l2 = Label(text="Nice")
l2.grid(row=0,column=0)



#Run Window
window.mainloop()
