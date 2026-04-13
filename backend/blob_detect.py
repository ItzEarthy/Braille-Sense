import cv2
import numpy as np
#grab modified photo through out_path
from photo_modification import out_path
#set up image and detector
image = out_path()
detector = cv2.SimpleBlobDetector_create()
#detect blobs
blobs = detector.detect(image)

image_blobs = cv2.drawKeypoints(image, *blobs, color=(255, 0, 0))

cv2.imshow("blobs found",image_blobs)
cv2.waitKey(0)
#parameters
parms = cv2.SimpleBlobDetector_Params()


