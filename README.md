# Fuel Receipt Reader

A Python project for reading and extracting structured data from fuel receipts using computer vision and OCR.

## Project Structure
- `src/` - Source code
  - `preprocessing.py` - Image preprocessing (OpenCV)
  - `ocr.py` - OCR logic (Tesseract)
  - `parsing.py` - Entity extraction and parsing
  - `normalization.py` - Data normalization
- `data/` - Sample and test data
- `receipts/` - Raw receipt images
- `tests/` - Unit tests
- `requirements.txt` - Python dependencies

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place receipt images in `receipts/`.
3. Run the main pipeline (to be implemented).

## Flow
1. **Preprocessing**: Enhance image quality for OCR.
2. **OCR**: Extract text using Tesseract.
3. **Parsing**: Extract entities (date, amount, fuel type, etc.).
4. **Normalization**: Standardize extracted data.

## Testing
Run tests with:
```bash
pytest
```

## Notes

Most recent receipts have QR codes with an URL to basic information: date and time, spent sum, receipt issuer and transaction location address.
