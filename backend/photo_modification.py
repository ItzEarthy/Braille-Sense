import cv2
from pathlib import Path

 
image_path = Path(__file__).resolve().parent / "Test Photos" / "2026-03-25T09-48-39-144Z-ada-braile-1-1200x1000.jpg"

image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)

output = image.copy()

cv2.imshow("Output", output)
cv2.waitKey(0)
cv2.destroyAllWindows()