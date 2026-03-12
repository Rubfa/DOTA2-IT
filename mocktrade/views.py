from django.shortcuts import render
from .models import MockTrading, Cosmetic, MarketRecord


def get_user_assets(trading):
    return [
        trading.asset1,
        trading.asset2,
        trading.asset3,
        trading.asset4,
        trading.asset5,
        trading.asset6,
        trading.asset7,
        trading.asset8,
        trading.asset9,
        trading.asset10,
    ]

def get_item_by_name(item_name : str) -> Cosmetic:
    return Cosmetic.objects.filter(item_name__iexact=item_name).first()

def get_item_price(item: Cosmetic) -> int:
    if not item:
        return None
    latest_record = (
        MarketRecord.objects
        .filter(item=item)
        .order_by("-date")
        .first()
    )
    if not latest_record:
        return None
    return latest_record.price

def add_item_to_empty_slot(trading, item: Cosmetic):
    for i in range(1, 11):
        field = f"asset{i}"

        if getattr(trading, field) is None:
            setattr(trading, field, item)
            break
    else:
        return False

    trading.save()
    return True

def remove_item_from_slot(trading, item):
    for i in range(10, 0, -1):
        field = f"asset{i}"

        if getattr(trading, field) == item:
            setattr(trading, field, None)
            trading.save()
            return True

    return False

def handle_search(item):
    if not item:
        return "Not Found"
    return get_item_price(item)

def handle_buy(trading, item):
    if not item:
        return "Not Found"

    price = get_item_price(item)

    if trading.balance < price:
        return "Not enough balance"

    added = add_item_to_empty_slot(trading, item)

    if not added:
        return "No empty slot"

    trading.balance -= price
    trading.save()
    return price

def handle_sell(trading, item):
    if not item:
        return "Not Found"

    price = get_item_price(item)

    removed = remove_item_from_slot(trading, item)

    if not removed:
        return "You do not own this item"

    trading.balance += price
    trading.save()
    return price


def index(request):
    trading = MockTrading.objects.first()
    item_name = ""
    price = None

    if request.method == "POST":
        item_name = request.POST.get("item_name", "").strip()
        action = request.POST.get("action")
        item = get_item_by_name(item_name)

        if action == "search":
            price = handle_search(item)

        elif action == "buy":
            price = handle_buy(trading, item)

        elif action == "sell":
            price = handle_sell(trading, item)

    assets = get_user_assets(trading)

    return render(request, "mocktrade/portfolio.html", {
        "username": request.user.username,
        "balance": trading.balance,
        "assets": assets,
        "price": price,
        "item_name": item_name,
        "current_page": "mocktrade",
    })