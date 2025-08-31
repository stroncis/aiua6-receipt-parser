def normalize_entities(entities):
    """
    Normalize extracted entities (e.g., date format, amount as float).
    """
    normalized = dict(entities)
    # Normalize date to YYYY-MM-DD
    if 'date' in normalized:
        normalized['date'] = normalized['date'].replace('.', '-').replace('/', '-')
    # Normalize amount
    if 'amount' in normalized:
        normalized['amount'] = float(normalized['amount'].replace(',', '.'))
    return normalized
