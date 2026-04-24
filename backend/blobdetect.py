import cv2
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import math

TEST_PHOTOS_DIR = Path(__file__).resolve().parent / "Test Photos"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}

# --- DESKEWING HELPER FUNCTIONS ---
def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def deskew_image(img, corners):
    rect = order_points(corners)
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(img, matrix, (maxWidth, maxHeight))
# ----------------------------------

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

    blurred = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

    # Increased blockSize to 91 so massive close-up shadows don't hollow out
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, blockSize=91, C=12
    )

    fat_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fattened = cv2.dilate(thresh, fat_kernel, iterations=1)

    close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(fattened, cv2.MORPH_CLOSE, close_kernel)

    inverted = cv2.bitwise_not(closed)

    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 10
    params.maxThreshold = 255
    
    # Increased maxArea significantly to catch close-ups
    params.filterByArea = True
    params.minArea = 5          
    params.maxArea = 3000
    
    # Slightly more forgiving shapes for extreme angles
    params.filterByCircularity = True
    params.minCircularity = 0.3 
    params.filterByInertia = True
    params.minInertiaRatio = 0.1 
    params.filterByConvexity = True
    params.minConvexity = 0.5    
    params.filterByColor = True
    params.blobColor = 0 

    detector = cv2.SimpleBlobDetector_create(params)
    raw_keypoints = detector.detect(inverted)

    # --- DYNAMIC SCALE-INVARIANT CLUSTERING ---
    valid_keypoints = []
    flat_img = None
    
    if raw_keypoints:
        pts = [kp.pt for kp in raw_keypoints]
        
        # 1. Calculate the median distance between dots to figure out the current scale
        min_dists = []
        for i, p1 in enumerate(pts):
            dists = [math.hypot(p1[0]-p2[0], p1[1]-p2[1]) for j, p2 in enumerate(pts) if i != j]
            if dists:
                min_dists.append(min(dists))
                
        median_spacing = sorted(min_dists)[len(min_dists)//2] if min_dists else 10
        
        # 2. Search radius: 4x the dot spacing effortlessly jumps word gaps
        search_radius = max(median_spacing * 4.0, 25.0) 
        
        # 3. Group the dots
        clusters = []
        visited = set()
        
        for i, p in enumerate(pts):
            if i in visited: continue
            
            current_cluster = [raw_keypoints[i]]
            visited.add(i)
            
            queue = [p]
            while queue:
                curr_p = queue.pop(0)
                for j, other_p in enumerate(pts):
                    if j not in visited:
                        dist = math.hypot(curr_p[0]-other_p[0], curr_p[1]-other_p[1])
                        if dist <= search_radius:
                            visited.add(j)
                            current_cluster.append(raw_keypoints[j])
                            queue.append(other_p)
                            
            clusters.append(current_cluster)
            
        # 4. Score and filter clusters
        best_cluster = None
        best_score = 0
        
        for cluster in clusters:
            num_dots = len(cluster)
            
            # FILTER: Room signs have between 4 and ~80 dots. 
            # Anything > 80 is guaranteed to be a massive patch of carpet noise.
            if 4 <= num_dots <= 80:
                xs = [kp.pt[0] for kp in cluster]
                ys = [kp.pt[1] for kp in cluster]
                w = max(xs) - min(xs)
                h = max(ys) - min(ys)
                
                area = (w + 1) * (h + 1)
                density = num_dots / area
                score = density * math.sqrt(num_dots)
                
                if score > best_score:
                    best_score = score
                    best_cluster = cluster
                    
        # 5. Deskew the winning cluster
        if best_cluster is not None:
            valid_keypoints = best_cluster
            
            cluster_pts = np.array([kp.pt for kp in best_cluster], dtype=np.float32)
            rect = cv2.minAreaRect(cluster_pts)
            
            # Add padding based on the scale so the dots aren't right on the edge
            (cx, cy), (w, h), angle = rect
            pad = median_spacing * 1.5
            padded_rect = ((cx, cy), (w + pad, h + pad), angle)
            
            corners = cv2.boxPoints(padded_rect)
            plate_corners = np.int32(corners)
            
            cv2.drawContours(img, [plate_corners], -1, (255, 0, 0), 2)
            flat_img = deskew_image(img, plate_corners)

    # Draw ONLY the valid, filtered results
    img_with_keypoints = cv2.drawKeypoints(
        img, valid_keypoints, np.array([]), (0, 0, 255), 
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
        if img_to_show is None: return
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

    show_scaled("Preprocessed", inverted)
    show_scaled("Detected 3D Braille", img_with_keypoints)
    if flat_img is not None:
        show_scaled("Deskewed Plate (Ready for Decoding)", flat_img)
        
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        detect_3d_braille(sys.argv[1])
    else:
        open_test_photo_dropdown()