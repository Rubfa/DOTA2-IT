from datetime import date, timedelta

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Cosmetic, Hero, Item, PriceRecord


def index(request):
    heroes = Hero.objects.all()
    return render(request, "index.html", {"heroes": heroes})


def get_cosmetics(request, hero_id):
    cosmetics = Cosmetic.objects.filter(hero_id=hero_id)
    data = [{"id": c.id, "name": c.name} for c in cosmetics]
    return JsonResponse(data, safe=False)


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


def item_history_api(request, item_id):
    try:
        cosmetic = Cosmetic.objects.get(id=item_id)
        item = cosmetic.item if cosmetic.item else get_object_or_404(Item, id=item_id)
    except Cosmetic.DoesNotExist:
        item = get_object_or_404(Item, id=item_id)

    qs = PriceRecord.objects.filter(item=item)
    r = request.GET.get("range", "30d")

    if r == "7d":
        qs = qs.filter(date__gte=date.today() - timedelta(days=7))
    elif r == "30d":
        qs = qs.filter(date__gte=date.today() - timedelta(days=30))
    elif r == "365d":
        qs = qs.filter(date__gte=date.today() - timedelta(days=365))

    records = qs.order_by("date")
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
