from preprocessing import preprocess_image
from ocr import ocr_image
from parsing import extract_entities
from normalization import normalize_entities
import sys
import os

RECEIPT_DIR = os.path.join(os.path.dirname(__file__), '../receipts')

def process_receipt(image_path):
    print(f"Processing: {image_path}")
    preprocessed = preprocess_image(image_path)
    text = ocr_image(preprocessed)
    print("OCR Text:", text)
    entities = extract_entities(text)
    normalized = normalize_entities(entities)
    print("Extracted Data:", normalized)
    return normalized

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python main.py <receipt_image>")
        print(f"Or place images in {RECEIPT_DIR} and run without arguments.")
        for fname in os.listdir(RECEIPT_DIR):
            if '-processed' in fname:
                continue
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                process_receipt(os.path.join(RECEIPT_DIR, fname))
    else:
        process_receipt(sys.argv[1])
