import numpy
import cv2

file_name = "stopplaying.png"
img = cv2.imread(file_name)
white = [255, 255, 255]
need_color = [68,68,68]
h,w,_ = img.shape
for i in range(h):
    for j in range(w):
        if img[i][j][0]>200 and img[i][j][1]>200 and img[i][j][2] <10:
            img[i][j] = white
        if not (img[i][j]==white).all():
            img[i][j]=need_color
cv2.imwrite(file_name,img)