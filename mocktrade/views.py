from collections import defaultdict
from decimal import Decimal

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import MockTrading, Cosmetic, MarketRecord, UserAccount

COSMETIC_NAME_ALIASES = {
    "chaos knight": "CK",
    "dragon knight": "DK",
    "nature's prophet": "先知",
    "crystal maiden": "冰女",
    "venomancer": "剧毒",
    "elder titan": "大牛",
    "skywrath mage": "天怒",
    "queen of pain": "女王",
    "shadow shaman": "小Y",
    "tiny": "小小",
    "earthshaker": "小牛",
    "slark": "小鱼",
    "enchantress": "小鹿",
    "drow ranger": "小黑",
    "undying": "尸王",
    "pudge": "屠夫",
    "rubick": "拉比克",
    "ursa": "拍拍",
    "axe": "斧王",
    "sven": "斯温",
    "morphling": "水人",
    "tusk": "海民",
    "tidehunter": "潮汐",
    "lina": "火女",
    "ember spirit": "火猫",
    "razor": "电棍",
    "storm spirit": "蓝猫",
    "enigma": "谜团",
    "brewmaster": "酒仙",
}

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

def get_item_by_name(item_name: str) -> Cosmetic:
    if not item_name:
        return None

    query = item_name.strip()

    exact_match = Cosmetic.objects.filter(item_name__iexact=query).first()
    if exact_match:
        return exact_match

    alias_name = COSMETIC_NAME_ALIASES.get(query.lower())
    if alias_name:
        alias_match = Cosmetic.objects.filter(item_name__iexact=alias_name).first()
        if alias_match:
            return alias_match

    partial_match = Cosmetic.objects.filter(item_name__icontains=query).first()
    if partial_match:
        return partial_match

    return None

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

    price = get_item_price(item)
    if price is None:
        return "No market history available"

    return price

def handle_buy(trading, item):
    if not item:
        return "Not Found"

    price = get_item_price(item)
    if price is None:
        return "No market history available"

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
    if price is None:
        return "No market history available"

    removed = remove_item_from_slot(trading, item)

    if not removed:
        return "You do not own this item"

    trading.balance += price
    trading.save()
    return price


def format_price_value(value):
    if isinstance(value, Decimal):
        return f"{value:.2f}"
    return str(value)


def build_trade_feedback(action, item_name, result):
    if not action:
        return (
            "Search a cosmetic to view the latest market price, then buy or sell without leaving the page.",
            "info",
        )

    display_name = item_name or "this cosmetic"
    is_price = isinstance(result, Decimal)

    if action == "search":
        if is_price:
            return (f"Loaded the latest recorded price for {display_name}.", "success")
        if result == "Not Found":
            return (f"{display_name} was not found in the cosmetic list.", "warning")
        if result == "No market history available":
            return (f"{display_name} exists, but it has no market history yet.", "warning")

    if action == "buy":
        if is_price:
            return (f"Purchased {display_name} for {format_price_value(result)}.", "success")
        if result == "Not enough balance":
            return ("Your balance is too low for this purchase.", "error")
        if result == "No empty slot":
            return ("Your inventory is full. Sell an item before buying another one.", "warning")

    if action == "sell":
        if is_price:
            return (f"Sold {display_name} for {format_price_value(result)}.", "success")
        if result == "You do not own this item":
            return (f"You cannot sell {display_name} because it is not in your inventory.", "warning")

    if result == "Not Found":
        return (f"{display_name} was not found in the cosmetic list.", "warning")

    if result == "No market history available":
        return (f"{display_name} exists, but it has no market history yet.", "warning")

    return ("The requested trading action could not be completed.", "error")


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
    action = None

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
    trade_status_message, trade_status_tone = build_trade_feedback(action, item_name, price)

    return {
        "username": request.user.username,
        "balance": trading.balance,
        "assets": assets,
        "portfolio_chart_data": chart_data,
        "asset_chart_data": asset_chart_data,
        "price": price,
        "item_name": item_name,
        "trade_status_message": trade_status_message,
        "trade_status_tone": trade_status_tone,
        "current_page": "mocktrade",
    }

@login_required
def index(request):
    context = build_mocktrade_context(request)
    return render(request, "mocktrade/portfolio.html", context)
