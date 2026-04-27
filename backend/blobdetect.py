import cv2
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
TEST_PHOTOS_DIR = Path(__file__).resolve().parent / "Test Photos"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def open_test_photo_dropdown():
    photos = sorted(
        [p for p in TEST_PHOTOS_DIR.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS],
        key=lambda p: p.name.lower(),
    )

    if not photos:
        print(f"No images found in: {TEST_PHOTOS_DIR}")
        return

    root = tk.Tk()
    root.title("Select Test Photo")
    root.resizable(False, False)

    ttk.Label(root, text="Choose a photo:").pack(padx=12, pady=(12, 6))

    selected_name = tk.StringVar(value=photos[0].name)
    combo = ttk.Combobox(
        root,
        textvariable=selected_name,
        values=[p.name for p in photos],
        state="readonly",
        width=45,
    )
    combo.pack(padx=12, pady=6)
    combo.current(0)

    def run_detection():
        selected_path = TEST_PHOTOS_DIR / selected_name.get()
        if not selected_path.exists():
            messagebox.showerror("Error", f"File not found:\n{selected_path}")
            return
        root.destroy()
        detect_3d_braille(str(selected_path))

    ttk.Button(root, text="Detect Braille", command=run_detection).pack(padx=12, pady=(6, 12))
    root.mainloop()

def detect_3d_braille(image_path):
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found.")
        return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Edge-Preserving Blur
    blurred = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    # 2. Relaxed Threshold 
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, blockSize=41, C=12
    )

    # 3. Dilation
    fat_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fattened = cv2.dilate(thresh, fat_kernel, iterations=1)

    # 4. Morphological Closing
    close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(fattened, cv2.MORPH_CLOSE, close_kernel)

    inverted = cv2.bitwise_not(closed)

    # 5. Blob Detector
    params = cv2.SimpleBlobDetector_Params()
    
    params.minThreshold = 10
    params.maxThreshold = 255
    
    params.filterByArea = True
    params.minArea = 8           
    params.maxArea = 1000

    params.filterByCircularity = True
    params.minCircularity = 0.35 
    
    params.filterByInertia = True
    params.minInertiaRatio = 0.15 

    params.filterByConvexity = True
    params.minConvexity = 0.6    
    
    params.filterByColor = True
    params.blobColor = 0 

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(inverted)

    # Draw results
    img_with_keypoints = cv2.drawKeypoints(
        img, keypoints, np.array([]), (0, 0, 255), 
        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )

    # UI/Scaling
    try:
        root = tk.Tk()
        root.withdraw()
        screen_w = root.winfo_screenwidth()
        screen_h = root.winfo_screenheight()
        root.destroy()
    except Exception:
        screen_w, screen_h = 1920, 1080

    def show_scaled(title, img_to_show):
        h, w = img_to_show.shape[:2]
        max_w = int(screen_w * 0.9)
        max_h = int(screen_h * 0.8)
        scale = min(max_w / w, max_h / h, 1.0)
        disp_w, disp_h = int(w * scale), int(h * scale)
        if scale < 1.0:
            disp = cv2.resize(img_to_show, (disp_w, disp_h), interpolation=cv2.INTER_AREA)
        else:
            disp = img_to_show

        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(title, disp_w, disp_h)
        cv2.imshow(title, disp)

    show_scaled("Preprocessed (What Detector Sees)", inverted)
    show_scaled("Detected 3D Braille", img_with_keypoints)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        detect_3d_braille(sys.argv[1])
    else:
        open_test_photo_dropdown()