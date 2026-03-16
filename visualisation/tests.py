from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from mocktrade.models import Cosmetic, Hero, MarketRecord


class IndexPageTests(TestCase):
    def test_index_contains_search_box_and_hero_entries(self):
        item1 = Cosmetic.objects.create(item_name="Axe of Phractos")
        item2 = Cosmetic.objects.create(item_name="Axe Unleashed")
        hero = Hero.objects.create(
            hero_name="Axe",
            hero_type="Strength",
            item1=item1,
            item2=item2,
        )

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="searchHero"')
        self.assertContains(response, 'placeholder="search hero or cosmetic"')
        self.assertContains(response, hero.hero_name)
        self.assertContains(response, "function searchHero()")
        self.assertContains(response, '<canvas id="chart"')


class ItemHistoryApiTests(TestCase):
    def test_history_api_returns_dense_window_and_trend_series(self):
        item = Cosmetic.objects.create(item_name="Bladeform Legacy")

        today = date.today()
        for index, (price, quantity) in enumerate(((10, 2), (20, 4), (30, 6))):
            MarketRecord.objects.create(
                item=item,
                date=today - timedelta(days=2 - index),
                price=price,
                quantity=quantity,
            )

        response = self.client.get(
            reverse("item_history_api", args=[item.id]),
            {"range": "30d"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(len(payload["labels"]), 31)
        self.assertEqual(payload["labels"][0], (today - timedelta(days=30)).isoformat())
        self.assertEqual(payload["labels"][-1], today.isoformat())
        self.assertEqual(payload["prices"][-3:], [10.0, 20.0, 30.0])
        self.assertEqual(payload["quantities"][-3:], [2, 4, 6])
        self.assertEqual(len(payload["trend_price"]), 31)
        self.assertEqual(len(payload["trend_qty"]), 31)
