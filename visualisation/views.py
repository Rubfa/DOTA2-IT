from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from mocktrade.models import Cometics, Heros, Maket_records

HERO_IMAGE_BASE = "https://cdn.cloudflare.steamstatic.com/apps/dota2/images/dota_react/heroes"

HERO_SLUGS = {
    "CK": "chaos_knight",
    "DK": "dragon_knight",
    "先知": "furion",
    "冰女": "crystal_maiden",
    "剧毒": "venomancer",
    "大牛": "elder_titan",
    "天怒": "skywrath_mage",
    "女王": "queenofpain",
    "小Y": "shadow_shaman",
    "小小": "tiny",
    "小牛": "earthshaker",
    "小鱼": "slark",
    "小鹿": "enchantress",
    "小黑": "drow_ranger",
    "尸王": "undying",
    "屠夫": "pudge",
    "拉比克": "rubick",
    "拍拍": "ursa",
    "斧王": "axe",
    "斯温": "sven",
    "水人": "morphling",
    "海民": "tusk",
    "潮汐": "tidehunter",
    "火女": "lina",
    "火猫": "ember_spirit",
    "电棍": "razor",
    "蓝猫": "storm_spirit",
    "谜团": "enigma",
    "酒仙": "brewmaster",
    "龙骑": "dragon_knight",
}


def build_visualisation_context():
    default_icon = (
        "data:image/svg+xml;utf8,"
        "<svg xmlns='http://www.w3.org/2000/svg' width='60' height='60'>"
        "<rect width='100%' height='100%' fill='%23e5e7eb'/>"
        "<text x='50%' y='55%' font-size='12' text-anchor='middle' fill='%23374151'>Hero</text>"
        "</svg>"
    )

    def get_hero_icon(hero_name):
        hero_slug = HERO_SLUGS.get(hero_name)
        if hero_slug:
            return f"{HERO_IMAGE_BASE}/{hero_slug}.png"
        return default_icon

    heroes = Heros.objects.select_related("item1", "item2").all().order_by("hero_name")
    hero_cards = [
        {
            "id": hero.id,
            "name": hero.hero_name,
            "type": hero.hero_type,
            "icon": get_hero_icon(hero.hero_name),
            "fallback_icon": default_icon,
        }
        for hero in heroes
    ]
    search_items = []

    for hero in heroes:
        seen_ids = set()
        for cosmetic in (hero.item1, hero.item2):
            if cosmetic and cosmetic.id not in seen_ids:
                seen_ids.add(cosmetic.id)
                search_items.append(
                    {
                        "id": cosmetic.id,
                        "name": cosmetic.item_name,
                        "hero_id": hero.id,
                        "hero_name": hero.hero_name,
                        "hero_type": hero.hero_type,
                    }
                )

    return {
        "heroes": hero_cards,
        "search_items": search_items,
    }


def index(request):
    return render(request, "index.html", build_visualisation_context())


def get_cosmetics(request, hero_id):
    hero = get_object_or_404(Heros, id=hero_id)
    cosmetics = []
    seen_ids = set()

    for cosmetic in (hero.item1, hero.item2):
        if cosmetic and cosmetic.id not in seen_ids:
            seen_ids.add(cosmetic.id)
            cosmetics.append({"id": cosmetic.id, "name": cosmetic.item_name})

    return JsonResponse(cosmetics, safe=False)


def linear_trend(values):
    n = len(values)
    if n < 2:
        return values[:]

    xs = list(range(n))
    sum_x = sum(xs)
    sum_y = sum(values)
    sum_x2 = sum(x * x for x in xs)
    sum_xy = sum(x * y for x, y in zip(xs, values))
    denom = n * sum_x2 - sum_x * sum_x

    if denom == 0:
        return values[:]

    a = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - a * sum_x) / n
    return [a * x + b for x in xs]


def build_dense_window_series(item, anchor_date, days):
    full_records = list(
        Maket_records.objects
        .filter(item=item, date__lte=anchor_date)
        .order_by("date")
    )
    if not full_records:
        return [], [], []

    start_date = anchor_date - timedelta(days=days)
    labels = []
    prices = []
    quantities = []

    index = 0
    current_price = float(full_records[0].price)
    current_quantity = full_records[0].quantity

    while index < len(full_records) and full_records[index].date <= start_date:
        current_price = float(full_records[index].price)
        current_quantity = full_records[index].quantity
        index += 1

    point_date = start_date
    while point_date <= anchor_date:
        while index < len(full_records) and full_records[index].date <= point_date:
            current_price = float(full_records[index].price)
            current_quantity = full_records[index].quantity
            index += 1

        labels.append(point_date.isoformat())
        prices.append(current_price)
        quantities.append(current_quantity)
        point_date += timedelta(days=1)

    return labels, prices, quantities


def item_history_api(request, item_id):
    item = get_object_or_404(Cometics, id=item_id)

    qs = Maket_records.objects.filter(item=item)
    r = request.GET.get("range", "30d")
    latest_record = qs.order_by("-date").first()
    labels = []
    prices = []
    quantities = []

    if latest_record and r in {"7d", "30d"}:
        days = {"7d": 7, "30d": 30}[r]
        labels, prices, quantities = build_dense_window_series(item, latest_record.date, days)
    elif latest_record and r == "365d":
        days = 365
        anchor_date = latest_record.date
        qs = qs.filter(date__gte=anchor_date - timedelta(days=days))
        records = list(qs.order_by("date"))
        labels = [x.date.isoformat() for x in records]
        prices = [float(x.price) for x in records]
        quantities = [x.quantity for x in records]

    if not labels:
        records = list(qs.order_by("date"))
        labels = [x.date.isoformat() for x in records]
        prices = [float(x.price) for x in records]
        quantities = [x.quantity for x in records]

    return JsonResponse(
        {
            "labels": labels,
            "prices": prices,
            "quantities": quantities,
            "trend_price": linear_trend(prices),
            "trend_qty": linear_trend(quantities),
        }
    )


def item_chart_page(request, item_id):
    return render(request, "items/item_chart.html", {"item_id": item_id})
