"""Tests for UCP Merchant Offer Normalizer."""
import unittest
from ucp_merchant_offer_normalizer.core import OfferNormalizer


class TestOfferNormalizer(unittest.TestCase):
    def setUp(self):
        self.norm = OfferNormalizer(fx_rates={"USD": 1.0, "EUR": 1.1}, default_tax_rate=0.1)

    def test_ranks_by_true_landed_cost(self):
        offers = [
            {"merchant": "HiddenShip", "price": "$50.00", "shipping": 20.0, "currency": "USD", "delivery_hours": 24},
            {"merchant": "FreeShip", "price": "$60.00", "shipping": 0.0, "currency": "USD", "delivery_hours": 48},
        ]
        ranked = self.norm.normalize_and_rank(offers)
        self.assertEqual(ranked[0]["merchant"], "FreeShip")
        self.assertEqual(ranked[0]["landed_usd_cents"], 6600)

    def test_currency_and_sla_filter(self):
        offers = [
            {"merchant": "Slow", "price": "10.00", "currency": "USD", "delivery_hours": 120},
            {"merchant": "EuroFast", "price": "20.00", "currency": "EUR", "delivery_hours": 24, "tax_included": True},
        ]
        ranked = self.norm.normalize_and_rank(offers, max_delivery_hours=48)
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["landed_usd_cents"], 2200)

    def test_unsupported_currency_raises(self):
        with self.assertRaises(ValueError):
            self.norm.normalize({"merchant": "X", "price": "10", "currency": "ZZZ"})
