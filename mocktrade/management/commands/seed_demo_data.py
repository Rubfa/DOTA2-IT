from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from mocktrade.models import Cosmetic, Hero, MarketRecord, MockTrading, UserAccount


class Command(BaseCommand):
    help = "Seed integrated demo data for mocktrade + visualisation pages."

    def handle(self, *args, **options):
        cosmetics = {}
        for item_name in [
            "Axe of Phractos",
            "Molten Claw",
            "Bladeform Legacy",
            "Fireborn Odachi",
        ]:
            item, _ = Cosmetic.objects.get_or_create(item_name=item_name)
            cosmetics[item_name] = item

        Hero.objects.update_or_create(
            hero_name="Axe",
            defaults={
                "hero_type": "Strength",
                "item1": cosmetics["Axe of Phractos"],
                "item2": cosmetics["Molten Claw"],
            },
        )
        Hero.objects.update_or_create(
            hero_name="Juggernaut",
            defaults={
                "hero_type": "Agility",
                "item1": cosmetics["Bladeform Legacy"],
                "item2": cosmetics["Fireborn Odachi"],
            },
        )

        today = date.today()
        base_prices = {
            "Axe of Phractos": Decimal("38.00"),
            "Molten Claw": Decimal("22.00"),
            "Bladeform Legacy": Decimal("55.00"),
            "Fireborn Odachi": Decimal("41.00"),
        }

        for item_name, item in cosmetics.items():
            for days_ago in range(29, -1, -1):
                point_date = today - timedelta(days=days_ago)
                trend = Decimal(str((29 - days_ago) * 0.45))
                price = base_prices[item_name] + trend
                quantity = 120 + (29 - days_ago) * 3
                MarketRecord.objects.update_or_create(
                    item=item,
                    date=point_date,
                    defaults={"price": price, "quantity": quantity},
                )

        user, _ = UserAccount.objects.get_or_create(
            username="demo_user",
            defaults={"password": "demo1234", "status": True},
        )
        MockTrading.objects.get_or_create(
            user=user,
            defaults={"balance": Decimal("10000.00")},
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
