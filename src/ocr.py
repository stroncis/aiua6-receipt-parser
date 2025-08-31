import pytesseract
from PIL import Image
import cv2

def ocr_image(image):
    """
    Run Tesseract OCR on a preprocessed image (numpy array).
    """
    pil_img = Image.fromarray(image)
    # psm 6 - assume a uniform block of text
    # oem 1 - LSTM engine
    custom_config = r'--oem 1 --psm 6'

    print(pytesseract.get_languages(config=''))
    try:
        text = pytesseract.image_to_string(pil_img, lang='lit', config=custom_config)
    except pytesseract.TesseractError:
        print("Lithuanian language data not found, falling back to English.")
        text = pytesseract.image_to_string(pil_img, lang='eng', config=custom_config)
    return text