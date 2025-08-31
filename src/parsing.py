import re

def extract_entities(text):
    """
    Extract entities from OCR text (date, amount, fuel type, etc.).
    """
    entities = {}

    # Fuel price and liters extraction (e.g., 1,560 X 12.820)
    fuel_amount_match = re.search(r'(\d+[.,]\d+)\s*[xX*]\s*(\d+[.,]\d+)', text)
    if fuel_amount_match:
        entities['fuel_price_per_liter'] = fuel_amount_match.group(1)
        entities['fuel_liters'] = fuel_amount_match.group(2)

    # Address extraction (look for lines with 'g.', 'sav.', 'k.', etc.)
    address_match = re.search(r'([A-Za-zėūųįšžąč .,-]+g\.|sav\.|k\.[^\n]*)', text)
    if address_match:
        entities['address'] = address_match.group(0).strip()

    # Date extraction
    date_match = re.search(r'(\d{4}[./-]\d{2}[./-]\d{2})', text)
    if date_match:
        entities['date'] = date_match.group(1)

    # Time extraction (HH:MM or HH:MM:SS)
    time_match = re.search(r'(\d{2}:\d{2}(?::\d{2})?)', text)
    if time_match:
        entities['time'] = time_match.group(1)

    # Amount extraction: look for lines with Moketi, Moketa, Moket, etc.
    amount_match = re.search(r'(?:Mok[eė]ti|Mok[eė]ta|Moket|Hoxeta|Moket)[^\d]*(\d+[.,]\d{2})', text, re.IGNORECASE)
    if not amount_match:
        # Fallback: any standalone number with 2 decimals
        amount_match = re.search(r'(\d+[.,]\d{2})', text)
    if amount_match:
        entities['amount'] = amount_match.group(1)

    # Fuel type extraction (add Lithuanian)
    fuel_match = re.search(r'(Diesel|Petrol|Gasoline|Dyzelinas|Benzinas|Dujos)', text, re.IGNORECASE)
    if fuel_match:
        entities['fuel_type'] = fuel_match.group(1)

    # Simple Lithuanian keyword detection
    lt_keywords = ['Mokėti', 'Kortelės', 'Kvito', 'Saugos', 'Dokumento', 'PVM']
    entities['language'] = 'lt' if any(word.lower() in text.lower() for word in lt_keywords) else 'unknown'

    return entities
