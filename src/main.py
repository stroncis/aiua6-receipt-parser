import sys
import os
from process_receipt import process_receipt

RECEIPT_DIR = os.path.join(os.path.dirname(__file__), '../receipts')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python main.py <receipt_image>")
        print(f"Or place images in {RECEIPT_DIR} and run without arguments.")
        for fname in os.listdir(RECEIPT_DIR):
            if '-processed' in fname or '_visualization' in fname:
                continue
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                process_receipt(os.path.join(RECEIPT_DIR, fname))
    else:
        process_receipt(sys.argv[1])
