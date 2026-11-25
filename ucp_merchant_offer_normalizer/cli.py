"""CLI for UCP Merchant Offer Normalizer."""
import argparse
import json
from .core import OfferNormalizer


def main():
    parser = argparse.ArgumentParser(description="UCP Merchant Offer Normalizer CLI")
    parser.add_argument("--max-hours", type=int, default=72, help="Maximum delivery SLA hours")
    args = parser.parse_args()

    norm = OfferNormalizer()
    sample = [
        {"merchant": "FastMart", "sku": "NVME-1TB", "price": "79.00", "shipping": 0, "currency": "USD", "delivery_hours": 24},
        {"merchant": "BudgetShop", "sku": "NVME-1TB", "price": "69.50", "shipping": 14.0, "currency": "USD", "delivery_hours": 48},
    ]
    print(json.dumps(norm.normalize_and_rank(sample, max_delivery_hours=args.max_hours), indent=2))


if __name__ == "__main__":
    main()
