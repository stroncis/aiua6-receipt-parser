
import cv2
import numpy as np
from PIL import Image

# === Preprocessing mode controls ===
PREPROCESS_MODE = 'otsu'  # Options: 'otsu', 'mean', 'gaussian', 'manual'
MANUAL_THRESHOLD_VALUE = 210  # Used only if PREPROCESS_MODE == 'manual'
APPLY_EQUALIZE = False
APPLY_CLAHE = True
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)
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

    # Thresholding
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

    return img
