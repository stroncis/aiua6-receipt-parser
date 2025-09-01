import os
import json

ADDRESS_FILE = os.path.join(os.path.dirname(__file__), '../data/addresses.json')
RECEIPT_DATA_DIR = os.path.join(os.path.dirname(__file__), '../data/receipts_data')
os.makedirs(RECEIPT_DATA_DIR, exist_ok=True)


def save_receipt_data(receipt_id, data):
    path = os.path.join(RECEIPT_DATA_DIR, f"{receipt_id}.json")
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved receipt data to {path}")


def load_receipt_data(receipt_id):
    path = os.path.join(RECEIPT_DATA_DIR, f"{receipt_id}.json")
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None


def load_addresses():
    if os.path.exists(ADDRESS_FILE):
        with open(ADDRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_addresses(addresses):
    with open(ADDRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(addresses, f, ensure_ascii=False, indent=2)


def fuzzy_match_address(address, known_addresses, threshold=3):
    # Simple Levenshtein distance (can use rapidfuzz or python-Levenshtein for speed)
    def levenshtein(a, b):
        if len(a) < len(b):
            return levenshtein(b, a)
        if len(b) == 0:
            return len(a)
        previous_row = range(len(b) + 1)
        for i, c1 in enumerate(a):
            current_row = [i + 1]
            for j, c2 in enumerate(b):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        return previous_row[-1]
    matches = [
        (entry, levenshtein(address, entry["address"]))
        for entry in known_addresses if "address" in entry
    ]
    matches.sort(key=lambda x: x[1])
    if matches and matches[0][1] <= threshold:
        return matches[0][0]
    return None


def add_address(address, station):
    addresses = load_addresses()
    addresses.append({"address": address, "station": station})
    save_addresses(addresses)
    print(f"Added address: {address} (station: {station})")
