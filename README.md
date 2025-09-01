# Fuel Receipt Reader

A Python project for reading and extracting structured data from fuel receipts using computer vision and OCR. Goal is to automate tracking of fuel expenses.

## Flow
1. **Preprocessing**: Enhance image quality for OCR.
2. **OCR**: Extract text using Tesseract.
3. **Parsing**: Extract entities (date, amount, fuel type, etc.).
4. **Normalization**: Standardize extracted data.

## Notes

### Preprocessing
All receipt pictures have a barely or not at all perceivable to the naked eye gradient. That gradient is sometimes hard to cope even in Photoshop to make a clear text mask. Making it fully automated is a challenge of a next level. CLAHE (Contrast Limited AHE (Adaptive Histogram Equalization)) solves this by splitting an image to the grid and applying AHE for each part separatedly. This way darker corner on one side will be treated differently, than another (if there still is enough data, f.e. pixel values are not clipped).

There is constant inconsistency in light and contrast, to fight or at least compensate that, I use the central part of ant image to measure conditions. This is based on assumption, that receipt is positioned in te center of the screen.

Going further, uneven light, shadows and overall luminosity affect how readable are different parts of an image. To cope with this problem, OCR can be fed with the same image multiple times but with different clipping thresholds in CLAHE. So added multi -pass OCR readings.

### Data integrity

For some values we can get proof or fallback fill missing fields. A perfect candidate is amount to pay, amount of fuel and fuel price triangle. It should match or be very close (as we can't be sure, how rounding is done before receipt). Also potentially could fill missing field if it's impossible to extract value.

Another way is to check QR code, if there is one with an URL to a receipt verification, which containt receipt summary. This is an EU initiative to make taxing transparent. In Lithuania it leads to https://kvitas.vmi.lt/?NR=[receipt id]&SM=[security module id]&RS=[receipt signature]&RC=[receipt code]. Though it is behind the CloudFlare bot wall and requires JS. If one of the project goals is being offline and mobile, this option is off the table.

### Scraping information

Most recent receipts have QR codes with an URL to basic information: date and time, spent sum, receipt issuer and transaction location address.

Some do not have QR code, only codes to be entered into kvitas.vmi.lt form, though such are very rare.

OpenCV QR algorithm is quite fragile, fails quite often even if the code is a little bit deformed. Google Lens reads without a problem most, even if they are cropped a little bit. One way to fix is to straighten QR code or use more versatile library.

## Setup

### Tesseract
Tesseract needs a correct language, get the language model from [https://github.com/tesseract-ocr/tessdata](https://github.com/tesseract-ocr/tessdata) and in case you installed tesseract with Brew, move is to `/opt/homebrew/Cellar/tesseract/5.5.0_1/share/tessdata`.

For making it to a locally running mobile ap model, it will require serious dataset and training.

## Challenges
* To capture address is insanely hard. My solution is to use fuzzy string searching (Levenstein etc) in lookup tables. If it is entered once into database and approved, then all the incorrect OCR readings could be easily fixed with a lookup table for that data cathegory. Though this requires a lot of considerations, as addresses are too mangled to be usable. A small language model could help here?
* Creating IDs for receipts based on filename is not the best idea, but should work for now, later should check for date, time, pay amount?
* So far so good for smaller chunks of text, though there are issues with reading some characters, especially "3" "8" and "9" being confused a lot.
* Having thousands of labeled receipts could help with Tesseract finetuning, though this is a major task, not for a hobby project. Outsourcing neighboor kiddos for candies.
* Reading car mileage from dashboard. Sounds easy, but so far attempt results are very poor due to infinite variations of light, refrections, characters having backlight, LCD or other variations. This could require even more preprocessing, than receipts.

## Project Structure
- `src/` - Source code
  - `preprocessing.py` - Image preprocessing (OpenCV)
  - `ocr.py` - OCR logic (Tesseract)
  - `parsing.py` - Entity extraction and parsing
  - `normalization.py` - Data normalization
- `data/` - Sample, test and output data
- `receipts/` - Raw receipt images
- `requirements.txt` - Python dependencies

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Place receipt images in `receipts/`.
3. Run the main pipeline (to be implemented).
