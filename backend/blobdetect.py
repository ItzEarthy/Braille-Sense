import cv2
import numpy as np
import math

CELL_STRIDE_X_U = 2.66
LINE_STRIDE_Y_U = 4.27

#translate vars
wordss = []
#alphabet
letters = {
    "100000" : "a",
    "110000" : "b",
    "100100" : "c",
    "100110" : "d",
    "100010" : "e",
    "110100" : "f",
    "110110" : "g",
    "110010" : "h",
    "010100" : "i",
    "010110" : "j",
    "101000" : "k",
    "111000" : "l",
    "101100" : "m",
    "101110" : "n",
    "101010" : "o",
    "111100" : "p",
    "111110" : "q",
    "111010" : "r",
    "011100" : "s",
    "011110" : "t",
    "101001" : "u",
    "111001" : "v",
    "010111" : "w",
    "101101" : "x",
    "101111" : "y",
    "101011" : "z",
    "010000" : ",",
    "001000" : "'",
    "001001" : "-",
    "010010" : ":",
    "011000" : ";",
    "010011" : ".",
    "011001" : "?",
    "011010" : "!",
    "011011" : "parenthesis",
    "001111" : "#",
    "000011" : "letterPrefix",
    "000001" : "capital",
    "000000" : " " 
}

numbers = {
    "a" : "1",
    "b" : "2",
    "c" : "3",
    "d" : "4",
    "e" : "5",
    "f" : "6",
    "g" : "7",
    "h" : "8",
    "i" : "9",
    "j" : "0"
}

captials = {
    "100000" : "A",
    "110000" : "B",
    "100100" : "C",
    "100110" : "D",
    "100010" : "E",
    "110100" : "F",
    "110110" : "G",
    "110010" : "H",
    "010100" : "I",
    "010110" : "J",
    "101000" : "K",
    "111000" : "L",
    "101100" : "M",
    "101110" : "N",
    "101010" : "O",
    "111100" : "P",
    "111110" : "Q",
    "111010" : "R",
    "011100" : "S",
    "011110" : "T",
    "101001" : "U",
    "111001" : "V",
    "010111" : "W",
    "101101" : "X",
    "101111" : "Y",
    "101011" : "Z"
}

#translate vars
wordss = []
#alphabet
letters = {
    "100000" : "a",
    "110000" : "b",
    "100100" : "c",
    "100110" : "d",
    "100010" : "e",
    "110100" : "f",
    "110110" : "g",
    "110010" : "h",
    "010100" : "i",
    "010110" : "j",
    "101000" : "k",
    "111000" : "l",
    "101100" : "m",
    "101110" : "n",
    "101010" : "o",
    "111100" : "p",
    "111110" : "q",
    "111010" : "r",
    "011100" : "s",
    "011110" : "t",
    "101001" : "u",
    "111001" : "v",
    "010111" : "w",
    "101101" : "x",
    "101111" : "y",
    "101011" : "z",
    "010000" : ",",
    "001000" : "'",
    "001001" : "-",
    "010010" : ":",
    "011000" : ";",
    "010011" : ".",
    "011001" : "?",
    "011010" : "!",
    "011011" : "parenthesis",
    "001111" : "#",
    "000011" : "letterPrefix",
    "000001" : "capital",
    "000000" : " " 
}

numbers = {
    "a" : "1",
    "b" : "2",
    "c" : "3",
    "d" : "4",
    "e" : "5",
    "f" : "6",
    "g" : "7",
    "h" : "8",
    "i" : "9",
    "j" : "0"
}

captials = {
    "100000" : "A",
    "110000" : "B",
    "100100" : "C",
    "100110" : "D",
    "100010" : "E",
    "110100" : "F",
    "110110" : "G",
    "110010" : "H",
    "010100" : "I",
    "010110" : "J",
    "101000" : "K",
    "111000" : "L",
    "101100" : "M",
    "101110" : "N",
    "101010" : "O",
    "111100" : "P",
    "111110" : "Q",
    "111010" : "R",
    "011100" : "S",
    "011110" : "T",
    "101001" : "U",
    "111001" : "V",
    "010111" : "W",
    "101101" : "X",
    "101111" : "Y",
    "101011" : "Z"
}

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
    warped = cv2.warpPerspective(img, matrix, (maxWidth, maxHeight))
    return warped, matrix

def _transform_keypoints(keypoints, matrix):
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
    params.maxArea = 8000
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
    if not keypoints or unit <= 0:
        return []

    pts = sorted([kp.pt for kp in keypoints], key=lambda p: (p[1], p[0]))
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

    lines = []
    if rows:
        current = [rows[0]]
        for r in rows[1:]:
            span = r['y'] - current[0]['y']
            gap = r['y'] - current[-1]['y']
            if span < 3.0 * unit and gap < 1.5 * unit:
                current.append(r)
            else:
                lines.append(current)
                current = [r]
        lines.append(current)

    if len(lines) > 1:
        line_sizes = [sum(len(r['pts']) for r in line) for line in lines]
        max_size = max(line_sizes)
        threshold = max(2, max_size * 0.25)
        lines = [line for line, size in zip(lines, line_sizes) if size >= threshold]

    cell_stride_x = unit * CELL_STRIDE_X_U
    result = []

    for line in lines:
        y_top = min(r['y'] for r in line)
        for r in line:
            dr = round((r['y'] - y_top) / unit)
            r['dotrow'] = max(0, min(2, dr))

        line_dots = [(p[0], r['dotrow']) for r in line for p in r['pts']]
        if not line_dots:
            continue
        line_dots.sort(key=lambda d: d[0])

        col_centers = _cluster_1d([d[0] for d in line_dots], unit * 0.5)
        col_dotrows = {ci: set() for ci in range(len(col_centers))}
        for x, dr in line_dots:
            ci = min(range(len(col_centers)), key=lambda i: abs(col_centers[i] - x))
            col_dotrows[ci].add(dr)

        cells = []
        ci = 0
        while ci < len(col_centers):
            cell = [ci]
            if (ci + 1 < len(col_centers) and col_centers[ci + 1] - col_centers[ci] < unit * 1.5):
                cell.append(ci + 1)
                ci += 2
            else:
                ci += 1
            cells.append(cell)

        prev_left_x = None
        for cell in cells:
            cell_left_x = col_centers[cell[0]]
            if prev_left_x is not None:
                n_steps = round((cell_left_x - prev_left_x) / cell_stride_x)
                for _ in range(max(0, n_steps - 1)):
                    result.append('000000')

            col_to_dotcol = {}
            for c in cell:
                dc = round((col_centers[c] - cell_left_x) / unit)
                col_to_dotcol[c] = max(0, min(1, dc))

            bits = []
            for dr in range(3):
                for dc in range(2):
                    hit = any(col_to_dotcol[c] == dc and dr in col_dotrows[c] for c in cell)
                    bits.append('1' if hit else '0')
            result.append(''.join(bits))
            prev_left_x = cell_left_x

    return result

def detect_3d_braille_from_image(img):
    inverted = _preprocess_for_blobs(img)
    detector = _make_blob_detector()
    raw_keypoints = detector.detect(inverted)

    valid_keypoints = []
    flat_img = None
    flat_keypoints = []
    binary_cells = []

    if raw_keypoints:
        pts = [kp.pt for kp in raw_keypoints]

        min_dists = []
        for i, p1 in enumerate(pts):
            dists = [math.hypot(p1[0]-p2[0], p1[1]-p2[1]) for j, p2 in enumerate(pts) if i != j]
            if dists:
                min_dists.append(min(dists))

        median_spacing = sorted(min_dists)[len(min_dists)//2] if min_dists else 10
        search_radius = max(median_spacing * 4.0, 25.0)

        clusters = []
        visited = set()

        for i, p in enumerate(pts):
            if i in visited:
                continue
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

        best_cluster = None
        best_score = 0

        for cluster in clusters:
            num_dots = len(cluster)
            if 4 <= num_dots <= 80:
                xs = [kp.pt[0] for kp in cluster]
                ys = [kp.pt[1] for kp in cluster]
                w = max(xs) - min(xs)
                h = max(ys) - min(ys)
                area = (w + 1) * (h + 1)
                density = num_dots / area
                consistency = _size_consistency(cluster)
                regularity = _spacing_regularity(cluster)
                aspect = max(w, h) / max(min(w, h), 1.0)
                if aspect > 12.0:
                    continue
                score = (density * math.sqrt(num_dots) * (consistency ** 2) * (regularity ** 2))
                if score > best_score:
                    best_score = score
                    best_cluster = cluster

        if best_cluster is not None:
            valid_keypoints = best_cluster
            cluster_pts = np.array([kp.pt for kp in best_cluster], dtype=np.float32)
            rect = cv2.minAreaRect(cluster_pts)
            (cx, cy), (w, h), angle = rect
            pad = median_spacing * 1.5
            padded_rect = ((cx, cy), (w + pad, h + pad), angle)
            corners = cv2.boxPoints(padded_rect)
            plate_corners = np.int32(corners)
            flat_img, warp_matrix = deskew_image(img.copy(), plate_corners)
            flat_inverted = _preprocess_for_blobs(flat_img)
            redetected = detector.detect(flat_inverted)
            redetected = _filter_by_size_consistency(redetected, tolerance=0.4)
            redetected = _largest_spatial_cluster(redetected, search_radius_factor=5.0)

            if len(redetected) < max(4, int(len(best_cluster) * 0.6)):
                flat_keypoints = _transform_keypoints(best_cluster, warp_matrix)
            else:
                flat_keypoints = redetected

            if flat_keypoints:
                flat_unit = _estimate_unit_spacing(flat_keypoints)
                binary_cells = keypoints_to_braille_binary(flat_keypoints, flat_unit)

            cv2.drawContours(img, [plate_corners], -1, (255, 0, 0), 2)

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
        
    return binary_cells

