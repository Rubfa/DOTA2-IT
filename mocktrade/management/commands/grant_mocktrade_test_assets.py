from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from mocktrade.models import Cosmetic, MarketRecord, MockTrading, UserAccount


class Command(BaseCommand):
    help = "Grant a user a set of mock trading assets that already have market history."

    def add_arguments(self, parser):
        parser.add_argument("username", help="Username/UserAccount username to populate.")
        parser.add_argument(
            "--balance",
            default="10000.00",
            help="Balance to set after populating the account.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=5,
            help="Number of assets to assign.",
        )

    def handle(self, *args, **options):
        username = options["username"]
        balance = Decimal(options["balance"])
        limit = max(1, min(options["limit"], 10))

        user_account, _ = UserAccount.objects.get_or_create(
            username=username,
            defaults={"password": "", "status": True},
        )
        trading, _ = MockTrading.objects.get_or_create(
            user=user_account,
            defaults={"balance": balance},
        )

        cosmetics = list(
            Cosmetic.objects.filter(marketrecord__isnull=False)
            .distinct()
            .order_by("id")[:limit]
        )
        if not cosmetics:
            raise CommandError("No cosmetics with market history are available.")

        for index in range(1, 11):
            setattr(trading, f"asset{index}", None)

        for index, cosmetic in enumerate(cosmetics, start=1):
            setattr(trading, f"asset{index}", cosmetic)

        trading.balance = balance
        trading.save()

        summary = ", ".join(item.item_name for item in cosmetics)
        self.stdout.write(
            self.style.SUCCESS(
                f"Assigned {len(cosmetics)} assets to {username}: {summary}"
            )
        )
