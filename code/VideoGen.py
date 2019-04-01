import cv2
import os


def makeVideo():
    files = os.listdir("../Output/")
    files = sorted(files, key=lambda item: (int(item.partition(' ')[0])
                                            if item[0].isdigit() else float('inf'), item))
    frame = cv2.imread("../Output/"+files[0])
    height, width, layers = frame.shape
    video = cv2.VideoWriter(
        "test.mp4", cv2.VideoWriter_fourcc(*'MP4V'), 16, (width, height))
    for filename in files:
        video.write(cv2.imread("../Output/"+filename))
    cv2.destroyAllWindows()
    video.release()
    print('Video Generated')
