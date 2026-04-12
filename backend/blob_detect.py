import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage import feature, color, io
from photo_modification import out_path

image = out_path()

detector = cv2.SimpleBlobDetector_create()

blobs = detector.detect(image)


image_blobs = cv2.drawKeypoints()