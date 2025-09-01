import os
from preprocessing import preprocess_image
from ocr import ocr_image
from parsing import extract_entities
from stored_data import save_receipt_data, load_receipt_data, load_addresses, add_address, fuzzy_match_address


def multipass_receipt_ocr(image_path, clip_limits=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5]):
    print(f"Multipass OCR for: {image_path}")
    qr_url = None
    results = []
    for clip_limit in clip_limits:
        print(f"Multipass: CLAHE clipLimit={clip_limit}")  # Debugging line
        img, qr_url = preprocess_image(image_path, clip_limit)
        if img is None:
            continue
        text = ocr_image(img)
        # print("OCR Text:", text)  # Debugging line
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


def proof_and_fill_fields(aggregated, tolerance=0.02):
    amount = aggregated.get('amount')
    liters = aggregated.get('fuel_liters')
    price = aggregated.get('fuel_price_per_liter')

    # Convert to float if possible
    try:
        amount_f = float(str(amount).replace(',', '.')) if amount else None
        liters_f = float(str(liters).replace(',', '.')) if liters else None
        price_f = float(str(price).replace(',', '.')) if price else None
    except Exception:
        amount_f = liters_f = price_f = None

    # Proof and fill missing fields
    if amount_f is not None and liters_f is not None and price_f is None:
        calc_price = amount_f / liters_f
        if calc_price > 0:
            aggregated['fuel_price_per_liter'] = round(calc_price, 3)
    elif amount_f is not None and price_f is not None and liters_f is None:
        calc_liters = amount_f / price_f
        if calc_liters > 0:
            aggregated['fuel_liters'] = round(calc_liters, 3)
    elif liters_f is not None and price_f is not None and amount_f is None:
        calc_amount = liters_f * price_f
        if calc_amount > 0:
            aggregated['amount'] = round(calc_amount, 2)

    # Optionally, check consistency
    if amount_f and liters_f and price_f:
        calc_amount = liters_f * price_f
        if abs(calc_amount - amount_f) > tolerance:
            print(f"Warning: Amount ({amount_f}) does not match liters*price ({calc_amount:.2f})")

    return aggregated


def process_receipt(image_path):
    print(f"Processing: {image_path}")
    fname = os.path.basename(image_path)
    aggregated, qr_url = multipass_receipt_ocr(image_path)
    aggregated = proof_and_fill_fields(aggregated)

    known_addresses = load_addresses()
    extracted_address = aggregated.get('address')
    matched_address_obj = fuzzy_match_address(extracted_address, known_addresses)
    if matched_address_obj:
        aggregated['address'] = matched_address_obj['address']
        aggregated['station'] = matched_address_obj['station']
        print(f"Matched address: {matched_address_obj['address']} (station: {matched_address_obj['station']})")
    else:
        print(f"Address not found in lookup. Please correct/add: {extracted_address}")
        corrected = input("Enter correct address: ")
        station = input("Enter station name: ")
        add_address(corrected, station)
        aggregated['address'] = corrected
        aggregated['station'] = station

    receipt_id = fname.split('.')[0]
    existing = load_receipt_data(receipt_id)
    if existing:
        print("Existing record found. Differences:")
        for k in aggregated:
            if existing.get(k) != aggregated[k]:
                print(f"  {k}: old={existing.get(k)}, new={aggregated[k]}")
        # update = input("Update record? (y/n): ")
        # if update.lower() == 'y':
        #     save_receipt_data(receipt_id, aggregated)
    else:
        save_receipt_data(receipt_id, aggregated)

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
