import cv2
import numpy as np
final_pic = cv2.imread('./work_folder/segmentation_temp/seg_photo.jpg')
sum_covery = final_pic.sum(axis=2)
for c in range(3):
    final_pic[:, :, c] = np.where(
        sum_covery != 0, 255,0)
cv2.imwrite('./test2.jpg',final_pic)