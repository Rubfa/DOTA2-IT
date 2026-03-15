from datetime import date, timedelta

from django.test import TestCase
from django.urls import reverse

from .models import Cosmetic, Hero, Item, PriceRecord


class IndexPageTests(TestCase):
    def test_index_contains_search_box_and_hero_entries(self):
        hero = Hero.objects.create(
            name="Axe",
            icon="https://example.com/axe.png",
            type="Strength",
        )

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="searchHero"')
        self.assertContains(response, 'placeholder="search hero"')
        self.assertContains(response, hero.name)
        self.assertContains(response, "function searchHero()")
        self.assertContains(response, '<canvas id="chart"')


class ItemHistoryApiTests(TestCase):
    def test_history_api_returns_linear_trend_series(self):
        item = Item.objects.create(name="Bladeform Legacy")
        hero = Hero.objects.create(
            name="Juggernaut",
            icon="https://example.com/jugg.png",
            type="Agility",
        )
        cosmetic = Cosmetic.objects.create(
            hero=hero,
            item=item,
            name="Bladeform Legacy",
        )

        today = date.today()
        for index, (price, quantity) in enumerate(((10, 2), (20, 4), (30, 6))):
            PriceRecord.objects.create(
                item=item,
                date=today - timedelta(days=2 - index),
                price=price,
                quantity=quantity,
            )

        response = self.client.get(
            reverse("item_history_api", args=[cosmetic.id]),
            {"range": "30d"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(len(payload["labels"]), 3)
        self.assertEqual(payload["prices"], [10.0, 20.0, 30.0])
        self.assertEqual(payload["quantities"], [2, 4, 6])
        self.assertEqual(len(payload["trend_price"]), 3)
        self.assertEqual(len(payload["trend_qty"]), 3)
        self.assertEqual(payload["trend_price"], [10.0, 20.0, 30.0])
        self.assertEqual(payload["trend_qty"], [2.0, 4.0, 6.0])
