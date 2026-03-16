from collections import defaultdict
from decimal import Decimal

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import MockTrading, Cosmetic, MarketRecord, UserAccount

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


def build_portfolio_chart_data(trading):
    assets = [asset for asset in get_user_assets(trading) if asset]
    if not assets:
        return {"labels": [], "cash": [], "asset_values": [], "total_values": [], "asset_names": []}

    history_by_item = defaultdict(list)
    all_dates = set()

    records = (
        MarketRecord.objects
        .filter(item__in=assets)
        .order_by("item_id", "date")
        .values_list("item_id", "date", "price")
    )

    for item_id, point_date, price in records:
        history_by_item[item_id].append((point_date, price))
        all_dates.add(point_date)

    sorted_dates = sorted(all_dates)
    item_indices = {item.id: 0 for item in assets}
    item_prices = {item.id: None for item in assets}
    cash_balance = Decimal(trading.balance)

    labels = []
    cash_values = []
    asset_values = []
    total_values = []

    for current_date in sorted_dates:
        total_asset_value = Decimal("0")

        for item in assets:
            item_history = history_by_item.get(item.id, [])
            idx = item_indices[item.id]

            while idx < len(item_history) and item_history[idx][0] <= current_date:
                item_prices[item.id] = item_history[idx][1]
                idx += 1

            item_indices[item.id] = idx

            if item_prices[item.id] is not None:
                total_asset_value += Decimal(item_prices[item.id])

        labels.append(current_date.isoformat())
        cash_values.append(float(cash_balance))
        asset_values.append(float(total_asset_value))
        total_values.append(float(cash_balance + total_asset_value))

    return {
        "labels": labels,
        "cash": cash_values,
        "asset_values": asset_values,
        "total_values": total_values,
        "asset_names": [asset.item_name for asset in assets],
    }


def build_asset_chart_data(trading):
    assets = []
    seen_ids = set()

    for asset in get_user_assets(trading):
        if asset and asset.id not in seen_ids:
            seen_ids.add(asset.id)
            assets.append(asset)

    asset_payload = {
        str(asset.id): {
            "id": asset.id,
            "name": asset.item_name,
            "labels": [],
            "prices": [],
            "quantities": [],
        }
        for asset in assets
    }

    records = (
        MarketRecord.objects
        .filter(item__in=assets)
        .order_by("item_id", "date")
        .values_list("item_id", "date", "price", "quantity")
    )

    for item_id, point_date, price, quantity in records:
        entry = asset_payload[str(item_id)]
        entry["labels"].append(point_date.isoformat())
        entry["prices"].append(float(price))
        entry["quantities"].append(quantity)

    return asset_payload

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


def get_or_create_trading_for_user(request_user):
    username = request_user.username if request_user.is_authenticated else "guest"
    user_account, _ = UserAccount.objects.get_or_create(
        username=username,
        defaults={"password": "", "status": True},
    )
    trading, _ = MockTrading.objects.get_or_create(
        user=user_account,
        defaults={"balance": Decimal("10000.00")},
    )
    return trading

def build_mocktrade_context(request):
    trading = get_or_create_trading_for_user(request.user)
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
    chart_data = build_portfolio_chart_data(trading)
    asset_chart_data = build_asset_chart_data(trading)

    return {
        "username": request.user.username,
        "balance": trading.balance,
        "assets": assets,
        "portfolio_chart_data": chart_data,
        "asset_chart_data": asset_chart_data,
        "price": price,
        "item_name": item_name,
        "current_page": "mocktrade",
    }

@login_required
def index(request):
    context = build_mocktrade_context(request)
    return render(request, "mocktrade/portfolio.html", context)
