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
    # Join lines around address keywords
    address_lines = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(r'(g\.|sav\.|k\.)', line):
            # Collect previous, current, and next lines for context
            start = max(i-1, 0)
            end = min(i+2, len(lines))
            address_chunk = ' '.join(lines[start:end]).strip()
            address_lines.append(address_chunk)
    if address_lines:
        # Choose the longest chunk as the likely address
        entities['address'] = max(address_lines, key=len)

    # Date extraction
    date_match = re.search(r'(\d{4}[./-]\d{2}[./-]\d{2})', text)
    if date_match:
        entities['date'] = date_match.group(1)

    # Time extraction, only valid times
    time_matches = re.findall(r'(\d{2}):(\d{2})(?::(\d{2}))?', text)
    for match in time_matches:
        hh, mm, ss = int(match[0]), int(match[1]), int(match[2] or 0)
        if 0 <= hh < 24 and 0 <= mm < 60 and 0 <= ss < 60:
            entities['time'] = f"{hh:02d}:{mm:02d}:{ss:02d}" if match[2] else f"{hh:02d}:{mm:02d}"
            break

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
