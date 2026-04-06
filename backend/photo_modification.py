import cv2
from pathlib import Path

# Gaussian Blur
BLUR_KERNEL = 15      # Must be an odd number (e.g., 9, 11, 15). Blurs out paper texture.

# Adaptive Thresholding
BLOCK_SIZE = 51       # Must be an odd number (e.g., 31, 51, 99). Should be larger than a Braille dot.
C_VALUE = 10          # Subtracted from the mean. Higher = less noise, but might erase dots. Try 2 to 15.
INVERT_COLORS = False # False = Black dots on white paper. True = White dots on black paper.

# Resolve input path
image_path = Path(__file__).resolve().parent / "Test Photos" / "test (5).jpg"

# Read the image in grayscale
img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
assert img is not None, f"file could not be read: {image_path}"

# 1. Apply Gaussian blur to reduce paper grain noise
img_blur = cv2.GaussianBlur(img, (BLUR_KERNEL, BLUR_KERNEL), 0)

# 2. Determine threshold type based on setting
thresh_type = cv2.THRESH_BINARY_INV if INVERT_COLORS else cv2.THRESH_BINARY

# 3. Apply adaptive Gaussian thresholding
adaptive = cv2.adaptiveThreshold(
    img_blur, 
    255, 
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
    thresh_type, 
    BLOCK_SIZE, 
    C_VALUE
)

# 4. Generate dynamic output filename and resolve path
original_name = image_path.stem
new_filename = f"{original_name}_blur{BLUR_KERNEL}_block{BLOCK_SIZE}_c{C_VALUE}_inv{INVERT_COLORS}.png"
out_path = Path(__file__).resolve().parent / "Test output" / new_filename

# 5. Save output
if cv2.imwrite(str(out_path), adaptive):
    print(f"Saved adaptive Gaussian threshold to: {out_path}")
else:
    print(f"Failed to save adaptive output to: {out_path}")