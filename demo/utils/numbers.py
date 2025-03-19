def parse_quotation(quotation):
    """Преобразует units и nano в float."""
    return float(quotation['units']) + float(quotation['nano']) / 1e9