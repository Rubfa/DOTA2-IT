from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Cosmetic, MarketRecord, MockTrading, UserAccount


class MocktradeHomePanelTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="trader1", password="pass12345")
        self.client.force_login(self.user)
        self.url = f"{reverse('home_test')}?panel=mocktrade"

        self.cosmetic = Cosmetic.objects.create(item_name="电棍")
        MarketRecord.objects.create(
            item=self.cosmetic,
            date=date(2026, 3, 1),
            price=Decimal("5100.00"),
            quantity=8,
        )

    def test_ajax_search_returns_price_payload(self):
        response = self.client.post(
            self.url,
            {"item_name": "电棍", "action": "search"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["action"], "search")
        self.assertEqual(payload["item_name"], "电棍")
        self.assertEqual(payload["price"], "5100.00")

    def test_buy_assigns_asset_and_updates_balance(self):
        cheap_item = Cosmetic.objects.create(item_name="测试饰品")
        MarketRecord.objects.create(
            item=cheap_item,
            date=date(2026, 3, 1),
            price=Decimal("100.00"),
            quantity=3,
        )

        response = self.client.post(
            self.url,
            {"item_name": "测试饰品", "action": "buy"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        trading = MockTrading.objects.get(user__username="trader1")

        self.assertEqual(trading.balance, Decimal("9900.00"))
        self.assertEqual(trading.asset1, cheap_item)
        self.assertIn("home-mocktrade-panel", response.json()["html"])

    def test_sell_restores_balance_and_clears_owned_asset(self):
        user_account = UserAccount.objects.create(username="seller1", password="", status=True)
        trading = MockTrading.objects.create(
            user=user_account,
            balance=Decimal("4800.00"),
            asset1=self.cosmetic,
        )
        self.user.username = "seller1"
        self.user.save(update_fields=["username"])

        response = self.client.post(
            self.url,
            {"item_name": "电棍", "action": "sell"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        trading.refresh_from_db()
        self.assertEqual(trading.balance, Decimal("9900.00"))
        self.assertIsNone(trading.asset1)

    def test_search_returns_not_found_for_unknown_item(self):
        response = self.client.post(
            self.url,
            {"item_name": "不存在", "action": "search"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["price"], "Not Found")
