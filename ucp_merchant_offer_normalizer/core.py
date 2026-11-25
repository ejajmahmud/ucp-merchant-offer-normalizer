"""Core merchant offer normalizer for Universal Commerce Protocol pipelines."""
from typing import Any, Dict, List


class OfferNormalizer:
    """Converts heterogeneous merchant pricing/SLA payloads into canonical UCP offers."""

    def __init__(self, fx_rates: Dict[str, float] = None, default_tax_rate: float = 0.0):
        self.fx_rates = dict(fx_rates or {"USD": 1.0, "EUR": 1.08, "GBP": 1.27})
        self.default_tax_rate = default_tax_rate

    def _to_cents(self, val: Any, currency: str) -> int:
        rate = self.fx_rates.get(currency.upper())
        if rate is None:
            raise ValueError(f"Unsupported currency: {currency}")
        amount = float(str(val).replace("$", "").replace(",", "").strip())
        return int(round(amount * rate * 100))

    def normalize(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        currency = offer.get("currency", "USD").upper()
        base_cents = self._to_cents(offer["price"], currency)
        ship_cents = self._to_cents(offer.get("shipping", 0.0), currency)
        tax_rate = float(offer.get("tax_rate", self.default_tax_rate))
        tax_cents = int(round(base_cents * tax_rate)) if not offer.get("tax_included", False) else 0
        landed = base_cents + ship_cents + tax_cents

        return {
            "merchant": offer["merchant"],
            "sku": offer.get("sku", "unknown"),
            "currency": "USD",
            "base_usd_cents": base_cents,
            "shipping_usd_cents": ship_cents,
            "tax_usd_cents": tax_cents,
            "landed_usd_cents": landed,
            "delivery_hours": int(offer.get("delivery_hours", 72)),
            "return_days": int(offer.get("return_days", 0)),
        }

    def normalize_and_rank(self, offers: List[Dict[str, Any]], max_delivery_hours: int = None) -> List[Dict[str, Any]]:
        normalized = [self.normalize(o) for o in offers]
        if max_delivery_hours is not None:
            normalized = [o for o in normalized if o["delivery_hours"] <= max_delivery_hours]
        return sorted(normalized, key=lambda o: (o["landed_usd_cents"], o["delivery_hours"]))
