# Senior Honours Project
##  Automatic Identification of Cell Motion, Splitting, and Death in a 4D Dataset
The following project was completed over the cource of the 2018/19 academic year as my 4th year dissertation project. 

Included within this repo is the dissertation for the final submission, along with the LaTex source code and the Python code used throughout the development.

The report itself is saved as SH-Project.pdf.  This project recieved 18.5/20 as the final mark.

## Abstract:
The aim of this project is to provide a program to be used by the Biology Department of the University of St. Andrews. The program will be used to monitor cell movement, cell splitting and cell death as they develop in the embryo; this enables researchers to understand the processes as cells start to form in organs. Biologists interested in tracking cell motion, splitting, and death, currently use a time consuming manual method of tracking the cells using bespoke software, pinpointing all cells location in 3D space at a given time, the time this takes to conduct limits the number of experiments they can conduct. This project seeks to automate this cell tracking process using computational methods, therefore enabling researchers to perform more detailed experiments and free up researchers time.


## Technologies Used in this Project Include:
- Python
- TKInter
- Scikit-Learn
- Open-Cv2
- Scikit-Image

## Solution
1. First load a Z-Stack of 2D Cell Microscopy Images.


![z stack](https://github.com/GarethCa/SH-Project/blob/master/CellTrackerImages/Capture.PNG)

2. Detect cells within a particular time in 3D space.


![detected cells](https://github.com/GarethCa/SH-Project/blob/master/CellTrackerImages/sf.PNG)

3. Optionally Output the cells tracked over time as a video.


![Gif for Output](https://github.com/GarethCa/SH-Project/blob/master/CellTrackerImages/GIF-Tracking.gif)

4. Track Cells over time.


![Tracked Cells](https://github.com/GarethCa/SH-Project/blob/master/CellTrackerImages/Tracking.PNG)

All of the above steps can be done from within a TKInter Python GUI. This was chosen so that the target users in the Biology department did not need to have command line user interface experience.
![GUI](https://github.com/GarethCa/SH-Project/blob/master/CellTrackerImages/GUI.PNG)
