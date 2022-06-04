import cv2
import numpy as np

#read image as numpy array
img = cv2.imread("ndl_temp.png")

#make arrays of all-non-black pixels on each axis
y_nonzero, x_nonzero, _ = np.nonzero(img)

#calculate black border based on leftmost, topmost, rightmost and bottommost non-black pixel
left = np.min(x_nonzero[0:img.shape[1]*100*3]) #measures leftmost non-black pixel starting approx. 100 pixels from top of image to avoid top border and page-turning arrows
top = np.min(y_nonzero)
right = np.max(x_nonzero[0:img.shape[1]*100*3]) + 1 #measures rightmost non-black starting approx. 100 pixels from top of image to avoid top border and page-turning arrows
bottom = np.max(y_nonzero) + 1

#print dimensions to screen for testing
#print("{0}, {1}, {2}, {3}".format(left,top,right,bottom))

with open("ndl_dimensions.txt", "w") as f:
    f.write("{0}, {1}, {2}, {3}".format(left,top,right,bottom))
