def normalize_country(country: str) -> str:
    return country.strip().upper()


def calculate_tax(amount: float, country: str, rate: float) -> float:
    normalized = normalize_country(country)
    return amount * rate
