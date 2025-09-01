
import cv2
import numpy as np
from PIL import Image

# === Preprocessing mode controls ===
PREPROCESS_MODE = 'otsu'  # Options: 'otsu', 'mean', 'gaussian', 'manual'
MANUAL_THRESHOLD_VALUE = 210  # Used only if PREPROCESS_MODE == 'manual'
APPLY_EQUALIZE = False
APPLY_CLAHE = True
CLAHE_CLIP_LIMIT = 4.0
CLAHE_TILE_GRID_SIZE = (16, 16)
APPLY_DESKEW = True
APPLY_PERSPECTIVE_CORRECTION = True
APPLY_MEDIAN_BLUR = True
MEDIAN_BLUR_KSIZE = 3
APPLY_MORPH_OPEN = True
MORPH_KERNEL_SIZE = 2
APPLY_DENOISE = True
FAST_NL_MEANS_PARAMS = dict(h=30, templateWindowSize=7, searchWindowSize=21)


def preprocess_image(image_path):
    """
    Load and preprocess the image for OCR.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not found or unable to read: {image_path}")

    # --- QR code detection (OpenCV) ---
    qr_url = None
    qr_detector = cv2.QRCodeDetector()
    qr_data, points, _ = qr_detector.detectAndDecode(image)
    if qr_data and 'kvitas.vmi.lt' in qr_data:
        qr_url = qr_data
        print(f"QR code found: {qr_url}")
    else:
        print("No valid QR code found.")

    # --- Deskewing ---
    if APPLY_DESKEW:
        print("Applying deskewing")
        image = deskew_image(image)
        if image is None:
            print("Warning: Deskewing failed, image is None.")
            return None, qr_url

    # # --- Perspective Correction ---
    # if APPLY_PERSPECTIVE_CORRECTION:
    #     print("Applying perspective correction")
    #     image = perspective_correction(image)
    #     if image is None:
    #         print("Warning: Perspective correction failed, image is None.")
    #         return None, qr_url

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    img = gray

    if APPLY_CLAHE:
        print(f"Applying CLAHE (clipLimit={CLAHE_CLIP_LIMIT}, tileGridSize={CLAHE_TILE_GRID_SIZE})")
        clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_GRID_SIZE)
        img = clahe.apply(img)
    elif APPLY_EQUALIZE:
        print("Applying histogram equalization")
        img = cv2.equalizeHist(img)

    if APPLY_MEDIAN_BLUR:
        print(f"Applying median blur with ksize={MEDIAN_BLUR_KSIZE}")
        img = cv2.medianBlur(img, MEDIAN_BLUR_KSIZE)

    print(f"Applying {PREPROCESS_MODE} thresholding")
    if PREPROCESS_MODE == 'otsu':
        # Otsu ignores the threshold value, always computes its own
        _, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif PREPROCESS_MODE == 'manual':
        _, img = cv2.threshold(img, MANUAL_THRESHOLD_VALUE, 255, cv2.THRESH_BINARY)
    elif PREPROCESS_MODE == 'mean':
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 31, 10)
    elif PREPROCESS_MODE == 'gaussian':
        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 10)

    if APPLY_MORPH_OPEN:
        print(f"Applying morphological opening with kernel size={MORPH_KERNEL_SIZE}")
        kernel = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE), np.uint8)
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

    if APPLY_DENOISE:
        print(f"Applying fastNlMeansDenoising with params={FAST_NL_MEANS_PARAMS}")
        img = cv2.fastNlMeansDenoising(img, None, **FAST_NL_MEANS_PARAMS)

    # Save preprocessed image for inspection
    processed_path = image_path.rsplit('.', 1)
    if len(processed_path) == 2:
        processed_path = processed_path[0] + '-processed.' + processed_path[1]
    else:
        processed_path = image_path + '-processed'
    print(f"Saving preprocessed image to: {processed_path}")
    cv2.imwrite(processed_path, img)

    return img, qr_url


def deskew_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # Extracting edges for Hough Line Transform
    edges = cv2.Canny(thresh, 50, 150, apertureSize=3)
    cv2.imwrite("receipts/canny_edges_visualization.jpg", edges)
    print("Saved Canny edges visualization as canny_edges_visualization.jpg")

    # Hough Line Transform
    lines = cv2.HoughLines(edges, 1, np.pi / 180, 250)
    angles = []
    vis = image.copy()
    if lines is not None:
        for line in lines:
            rho, theta = line[0]
            angle_deg = np.rad2deg(theta)
            # Only lines near horizontal (within ±30° of 0° or 180°)
            deviation = min(abs(angle_deg), abs(angle_deg - 180))
            if deviation < 30:
                deskew_angle = angle_deg if angle_deg < 90 else angle_deg - 180
                angles.append(deskew_angle)
                # Debug: draw the line for visualization
                a = np.cos(theta)
                b = np.sin(theta)
                x0 = a * rho
                y0 = b * rho
                x1 = int(x0 + 1000 * (-b))
                y1 = int(y0 + 1000 * (a))
                x2 = int(x0 - 1000 * (-b))
                y2 = int(y0 - 1000 * (a))
                cv2.line(vis, (x1, y1), (x2, y2), (0, 0, 255), 2)
        # Debug: save visualization image
        cv2.imwrite("receipts/hough_lines_visualization.jpg", vis)
        print("Saved Hough lines visualization as hough_lines_visualization.jpg")

        if angles:
            avg_angle = np.mean(angles)
            print(f"Hough deskew detected angle: {avg_angle:.2f}")
            # Rotate by -avg_angle to deskew
            if abs(avg_angle) > 0.5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, float(avg_angle), 1.0)
                rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                return rotated
            else:
                print("Deskew angle too small, skipping rotation.")
                return image
        else:
            print("No suitable lines found for deskewing, fallback to minAreaRect.")

    # Fallback to minAreaRect
    coords = np.column_stack(np.where(thresh > 0))
    if coords.size == 0:
        print("Warning: No nonzero pixels found for deskewing.")
        return None
    angle = cv2.minAreaRect(coords)[-1]
    print(f"Initial deskew angle: {angle}")

    if abs(angle) > 45:
        print(f"Deskew skipped: detected angle {angle} is too large (likely vertical receipt or misdetection)")
        return image
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    print(f"Corrected deskew angle: {angle}")

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    if rotated is None:
        print("Warning: cv2.warpAffine failed during deskewing.")
    print(f"Deskew angle: {angle:.2f}")
    return rotated


def perspective_correction(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blur, 50, 200)

    contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]
    pts = None
    for c in contours:
        min_area = 0.2 * image.shape[0] * image.shape[1]
        if cv2.contourArea(c) < min_area:
            continue
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            break
    if pts is None:
        print("No 4-point contour found for perspective correction, skipping.")
        return image
        # return None

    # Order points
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    maxWidth = max(int(widthA), int(widthB))
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)
    maxHeight = max(int(heightA), int(heightB))

    if maxWidth < 0.5 * image.shape[1] or maxHeight < 0.5 * image.shape[0]:
        print("Perspective correction skipped: detected contour too small compared to input image.")
        return image

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    if warped is None:
        print("Warning: cv2.warpPerspective failed during perspective correction.")
    print("Perspective correction applied.")
    return warped


def order_points(pts):
    # Order points: top-left, top-right, bottom-right, bottom-left
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect
