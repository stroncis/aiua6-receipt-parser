from preprocessing import preprocess_image
from ocr import ocr_image
from parsing import extract_entities
import sys
import os
import requests
import re

RECEIPT_DIR = os.path.join(os.path.dirname(__file__), '../receipts')


def fetch_html(url, timeout=10):
    """
    Fetch HTML content from a URL. Returns HTML string or None.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"Failed to fetch {url}, status: {resp.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_vmi_content(qr_url):
    """
    Scrape kvitas.vmi.lt
    Extract relevant content from the HTML.
    """
    print(f"Scraping data from: {qr_url}")
    if not qr_url:
        print("No QR URL provided.")
        return None, None
    sum_match = ''
    address_match = ''
    try:
        html = fetch_html(qr_url)
        if html is None:
            print("Failed to retrieve QR page.")
            return None, None
        sum_match = re.search(r'Suma.*?(\d+[.,]\d+)', html)
        address_match = re.search(r'Adresas.*?<td[^>]*>(.*?)<', html, re.DOTALL)
    except Exception as e:
        print(f"Error scraping QR page: {e}")
    return sum_match, address_match


def multipass_receipt_ocr(image_path, clip_limits=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]):
    qr_url = None
    results = []
    for clip_limit in clip_limits:
        print(f"Multipass: CLAHE clipLimit={clip_limit}")
        # Set CLAHE_CLIP_LIMIT for this pass
        from preprocessing import preprocess_image
        img, qr_url = preprocess_image(image_path, clip_limit)
        if img is None:
            continue
        from ocr import ocr_image
        text = ocr_image(img)
        print("OCR Text:", text)
        from parsing import extract_entities
        entities = extract_entities(text)
        results.append(entities)
    # Aggregate results (example: majority vote for each field)
    aggregated = {}
    keys = set().union(*(r.keys() for r in results if r))
    for key in keys:
        values = [r[key] for r in results if r and key in r]
        if values:
            # Majority vote
            aggregated[key] = max(set(values), key=values.count)
    print("Aggregated entities:", aggregated)
    return aggregated, qr_url


def process_receipt(image_path):
    print(f"Processing: {image_path}")
    fname = os.path.basename(image_path)
    # Use multipass CLAHE for robust OCR
    aggregated, qr_url = multipass_receipt_ocr(image_path)
    print(f"Processed {fname}:")
    for key, value in aggregated.items():
        print(f"    {key}: {value}")
    print(f"    QR URL: {qr_url}")
    # if qr_url:
    #     sum_match, address_match = extract_vmi_content(qr_url)
    #     if sum_match:
    #         print(f"Extracted sum: {sum_match.group(1)}")
    #     if address_match:
    #         print(f"Extracted address: {address_match.group(1).strip()}")
    return aggregated, qr_url


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
