import cv2
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import math

TEST_PHOTOS_DIR = Path(__file__).resolve().parent / "Test Photos"
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}

# Standard braille geometry (Library of Congress spec):
#   within-cell dot pitch:   1.0 u  (≈ 2.34 mm)
#   cell-to-cell pitch (x):  2.66 u (≈ 6.22 mm)
#   line-to-line pitch (y):  4.27 u (≈ 10.0 mm)
CELL_STRIDE_X_U = 2.66
LINE_STRIDE_Y_U = 4.27

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
    """Returns (warped_image, perspective_matrix). The matrix can be reused
    via cv2.perspectiveTransform to map points from the original image into
    the deskewed coordinate space."""
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
    warped = cv2.warpPerspective(img, matrix, (maxWidth, maxHeight))
    return warped, matrix

def _transform_keypoints(keypoints, matrix):
    """Apply a perspective matrix to a list of keypoints (positions + sizes
    are preserved, sizes are not rescaled — fine for clustering, dot pitch
    is re-estimated downstream from the transformed positions)."""
    if not keypoints:
        return []
    pts = np.array(
        [[[float(kp.pt[0]), float(kp.pt[1])]] for kp in keypoints],
        dtype=np.float32,
    )
    transformed = cv2.perspectiveTransform(pts, matrix)
    return [
        cv2.KeyPoint(float(p[0][0]), float(p[0][1]), kp.size)
        for kp, p in zip(keypoints, transformed)
    ]
# ----------------------------------

# --- DETECTION PIPELINE HELPERS ---
def _preprocess_for_blobs(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, blockSize=91, C=12
    )
    fat_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fattened = cv2.dilate(thresh, fat_kernel, iterations=1)
    close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    closed = cv2.morphologyEx(fattened, cv2.MORPH_CLOSE, close_kernel)
    return cv2.bitwise_not(closed)

def _make_blob_detector():
    params = cv2.SimpleBlobDetector_Params()
    params.minThreshold = 10
    params.maxThreshold = 255
    params.filterByArea = True
    params.minArea = 5
    # Bumped from 3000 to 8000: close-up shots (~6 in away) produce dots that
    # are 50-80 px in diameter, easily exceeding 3000 px² area. Size-consistency
    # filtering downstream rejects the resulting oversized noise.
    params.maxArea = 8000
    # Relaxed shape filters: 3D braille dots viewed with side-lighting often
    # appear as crescents in the binary image (one side highlight, one side
    # shadow). Strict circularity/convexity filters were rejecting these.
    # Size-consistency filtering downstream catches the resulting noise.
    params.filterByCircularity = True
    params.minCircularity = 0.15
    params.filterByInertia = True
    params.minInertiaRatio = 0.05
    params.filterByConvexity = True
    params.minConvexity = 0.3
    params.filterByColor = True
    params.blobColor = 0
    return cv2.SimpleBlobDetector_create(params)

def _size_consistency(keypoints):
    """Returns 1.0 for perfectly uniform sizes, → 0 for chaotic ones.
    Uses coefficient of variation of blob diameters."""
    sizes = [kp.size for kp in keypoints]
    if len(sizes) < 2:
        return 1.0
    mean = sum(sizes) / len(sizes)
    if mean <= 0:
        return 0.0
    var = sum((s - mean) ** 2 for s in sizes) / len(sizes)
    cv = math.sqrt(var) / mean
    return 1.0 / (1.0 + cv * 2.0)

def _spacing_regularity(keypoints):
    """Returns 1.0 if every dot's nearest-neighbor distance is the same
    (real braille — dots are deliberately placed at a fixed pitch),
    → 0 for randomly-spaced wall/floor texture."""
    pts = [kp.pt for kp in keypoints]
    if len(pts) < 3:
        return 1.0
    min_dists = []
    for i, p1 in enumerate(pts):
        d = min(math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                for j, p2 in enumerate(pts) if i != j)
        min_dists.append(d)
    mean = sum(min_dists) / len(min_dists)
    if mean <= 0:
        return 0.0
    var = sum((d - mean) ** 2 for d in min_dists) / len(min_dists)
    cv = math.sqrt(var) / mean
    return 1.0 / (1.0 + cv * 1.5)

def _largest_spatial_cluster(keypoints, search_radius_factor=5.0):
    """Group keypoints by spatial proximity (flood fill within
    search_radius_factor × median nearest-neighbor distance) and return
    the largest group. Drops isolated outlier dots far from the main braille."""
    if len(keypoints) <= 1:
        return list(keypoints)
    pts = [kp.pt for kp in keypoints]
    min_dists = []
    for i, p1 in enumerate(pts):
        d = min(math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                for j, p2 in enumerate(pts) if i != j)
        min_dists.append(d)
    median = sorted(min_dists)[len(min_dists) // 2] if min_dists else 10.0
    radius = max(median * search_radius_factor, 25.0)

    clusters = []
    visited = set()
    for i, p in enumerate(pts):
        if i in visited:
            continue
        cluster = [keypoints[i]]
        visited.add(i)
        queue = [p]
        while queue:
            curr = queue.pop(0)
            for j, op in enumerate(pts):
                if j not in visited and math.hypot(curr[0] - op[0], curr[1] - op[1]) <= radius:
                    visited.add(j)
                    cluster.append(keypoints[j])
                    queue.append(op)
        clusters.append(cluster)
    return max(clusters, key=len)

def _filter_by_size_consistency(keypoints, tolerance=0.4):
    """Keep keypoints whose diameter is within ±tolerance of the median."""
    if len(keypoints) < 3:
        return list(keypoints)
    sizes = sorted(kp.size for kp in keypoints)
    median = sizes[len(sizes) // 2]
    lo = median * (1.0 - tolerance)
    hi = median * (1.0 + tolerance)
    return [kp for kp in keypoints if lo <= kp.size <= hi]

def _estimate_unit_spacing(keypoints):
    pts = [kp.pt for kp in keypoints]
    if len(pts) < 2:
        return 10.0
    min_dists = []
    for i, p1 in enumerate(pts):
        d = min(math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                for j, p2 in enumerate(pts) if i != j)
        min_dists.append(d)
    return sorted(min_dists)[len(min_dists)//2]
# ----------------------------------

# --- BRAILLE GRID EXTRACTION ---
def _cluster_1d(values, tol):
    if not values:
        return []
    vals = sorted(values)
    clusters = [[vals[0]]]
    for v in vals[1:]:
        if v - clusters[-1][-1] <= tol:
            clusters[-1].append(v)
        else:
            clusters.append([v])
    return [sum(c) / len(c) for c in clusters]

def keypoints_to_braille_binary(keypoints, unit):
    """
    Map detected dot keypoints (on a deskewed image) to a list of 6-bit binary
    strings, one per braille cell, in reading order (left-to-right, top-to-bottom).
    Bit order within a cell: r0c0, r0c1, r1c0, r1c1, r2c0, r2c1
    (i.e. braille positions 1, 4, 2, 5, 3, 6).
    Empty cells between detected cells (clear horizontal gaps) are emitted as '000000'.
    """
    if not keypoints or unit <= 0:
        return []

    pts = sorted([kp.pt for kp in keypoints], key=lambda p: (p[1], p[0]))

    # Group dots into horizontal sub-rows by y-coordinate.
    y_tol = unit * 0.5
    rows = []
    for p in pts:
        for row in rows:
            if abs(row['y'] - p[1]) <= y_tol:
                n = len(row['pts'])
                row['y'] = (row['y'] * n + p[1]) / (n + 1)
                row['pts'].append(p)
                break
        else:
            rows.append({'y': p[1], 'pts': [p]})
    rows.sort(key=lambda r: r['y'])

    # Group sub-rows into braille lines (≤3 sub-rows per line).
    lines = []
    if rows:
        current = [rows[0]]
        for r in rows[1:]:
            gap = r['y'] - current[-1]['y']
            if gap < unit * 2.0 and len(current) < 3:
                current.append(r)
            else:
                lines.append(current)
                current = [r]
        lines.append(current)

    # Drop "lines" that are clearly minor compared to the largest — these are
    # almost always noise dots near the edge of the deskewed plate. A real
    # secondary line of braille text is rarely < 25% the size of the main one.
    if len(lines) > 1:
        line_sizes = [sum(len(r['pts']) for r in line) for line in lines]
        max_size = max(line_sizes)
        threshold = max(2, max_size * 0.25)
        lines = [line for line, size in zip(lines, line_sizes) if size >= threshold]

    cell_stride_x = unit * CELL_STRIDE_X_U
    result = []

    for line in lines:
        # Within a line, snap each sub-row to dot-row 0/1/2 by relative y.
        # Assumes some cell on this line has a dot in dot-row 0.
        y_top = min(r['y'] for r in line)
        for r in line:
            dr = round((r['y'] - y_top) / unit)
            r['dotrow'] = max(0, min(2, dr))

        line_dots = [(p[0], r['dotrow']) for r in line for p in r['pts']]
        if not line_dots:
            continue
        line_dots.sort(key=lambda d: d[0])

        # Cluster x-coords to find dot columns.
        col_centers = _cluster_1d([d[0] for d in line_dots], unit * 0.5)
        col_dotrows = {ci: set() for ci in range(len(col_centers))}
        for x, dr in line_dots:
            ci = min(range(len(col_centers)),
                     key=lambda i: abs(col_centers[i] - x))
            col_dotrows[ci].add(dr)

        # Pair consecutive columns into cells when their gap is < ~1.5u.
        cells = []
        ci = 0
        while ci < len(col_centers):
            cell = [ci]
            if (ci + 1 < len(col_centers)
                    and col_centers[ci + 1] - col_centers[ci] < unit * 1.5):
                cell.append(ci + 1)
                ci += 2
            else:
                ci += 1
            cells.append(cell)

        # Emit binary, inserting empty cells across wide horizontal gaps.
        prev_left_x = None
        for cell in cells:
            cell_left_x = col_centers[cell[0]]
            if prev_left_x is not None:
                # Number of cell-widths from previous cell's left to this one.
                n_steps = round((cell_left_x - prev_left_x) / cell_stride_x)
                for _ in range(max(0, n_steps - 1)):
                    result.append('000000')

            # Within the cell, leftmost detected col is dot_col 0; if a second
            # col exists ~u to the right it's dot_col 1.
            col_to_dotcol = {}
            for c in cell:
                dc = round((col_centers[c] - cell_left_x) / unit)
                col_to_dotcol[c] = max(0, min(1, dc))

            bits = []
            for dr in range(3):
                for dc in range(2):
                    hit = any(col_to_dotcol[c] == dc and dr in col_dotrows[c]
                              for c in cell)
                    bits.append('1' if hit else '0')
            result.append(''.join(bits))
            prev_left_x = cell_left_x

    return result
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
        binary = detect_3d_braille(str(selected_path))
        print("Braille binary:", binary)

    ttk.Button(root, text="Detect Braille", command=run_detection).pack(padx=12, pady=(6, 12))
    root.mainloop()

def detect_3d_braille(image_path):
    """
    Detect a braille plate in the image, deskew it, re-detect dots on the flat
    image, and return a list of 6-bit binary strings in reading order
    (left-to-right, top-to-bottom). Bit order per cell: positions 1,4,2,5,3,6.
    """
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found.")
        return []

    inverted = _preprocess_for_blobs(img)
    detector = _make_blob_detector()
    raw_keypoints = detector.detect(inverted)

    # --- DYNAMIC SCALE-INVARIANT CLUSTERING ---
    valid_keypoints = []
    flat_img = None
    flat_keypoints = []
    binary_cells = []

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

                # Real braille dots are all the same size; wall/carpet noise
                # has wildly varying blob sizes.
                consistency = _size_consistency(cluster)

                # Real braille is on a fixed-pitch grid → nearest-neighbor
                # distances are very tight. Random texture noise has loose,
                # varied spacing. This is what separates a wall-texture cluster
                # of similar-sized bumps from a real braille cluster.
                regularity = _spacing_regularity(cluster)

                # Reject extreme aspect ratios — real braille plates are
                # roughly rectangular, not pencil-thin.
                aspect = max(w, h) / max(min(w, h), 1.0)
                if aspect > 12.0:
                    continue

                score = (density * math.sqrt(num_dots)
                         * (consistency ** 2)
                         * (regularity ** 2))

                if score > best_score:
                    best_score = score
                    best_cluster = cluster

        # 5. Deskew the winning cluster, then re-detect on the flat image
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

            # Deskew the *clean* original image so the flat image has no overlay.
            flat_img, warp_matrix = deskew_image(img.copy(), plate_corners)

            # Re-detect on the deskewed plate for cleaner, axis-aligned dots.
            flat_inverted = _preprocess_for_blobs(flat_img)
            redetected = detector.detect(flat_inverted)
            redetected = _filter_by_size_consistency(redetected, tolerance=0.4)
            redetected = _largest_spatial_cluster(redetected, search_radius_factor=5.0)

            # Fallback: if re-detection lost a significant fraction of the
            # original cluster's dots (happens when the deskewed crop is small
            # and the preprocessing params don't suit it — e.g. distant/dark
            # plates), reuse the original cluster's keypoints transformed into
            # the deskewed coordinate space. The original detection already
            # validated these as real dots.
            if len(redetected) < max(4, int(len(best_cluster) * 0.6)):
                flat_keypoints = _transform_keypoints(best_cluster, warp_matrix)
            else:
                flat_keypoints = redetected

            if flat_keypoints:
                flat_unit = _estimate_unit_spacing(flat_keypoints)
                binary_cells = keypoints_to_braille_binary(flat_keypoints, flat_unit)

            # Draw the plate outline for visualization (after deskewing).
            cv2.drawContours(img, [plate_corners], -1, (255, 0, 0), 2)

    # Draw ONLY the valid, filtered results
    img_with_keypoints = cv2.drawKeypoints(
        img, valid_keypoints, np.array([]), (0, 0, 255),
        cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )

    flat_with_keypoints = None
    if flat_img is not None:
        flat_with_keypoints = cv2.drawKeypoints(
            flat_img, flat_keypoints, np.array([]), (0, 0, 255),
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
    if flat_with_keypoints is not None:
        show_scaled("Deskewed Plate (Re-detected)", flat_with_keypoints)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return binary_cells

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = detect_3d_braille(sys.argv[1])
        print("Braille binary:", result)
    else:
        open_test_photo_dropdown()
