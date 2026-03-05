from datetime import date, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from .models import Item, PriceRecord

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
    item = Item.objects.get(id=item_id)
    qs = PriceRecord.objects.filter(item=item)

    r = request.GET.get("range", "30d")
    if r == "7d":
        qs = qs.filter(recorded_date__gte=date.today() - timedelta(days=7))
    elif r == "30d":
        qs = qs.filter(recorded_date__gte=date.today() - timedelta(days=30))
    # all 不筛选

    records = qs.order_by("recorded_date")
    labels = [x.recorded_date.isoformat() for x in records]
    prices = [float(x.price) for x in records]
    quantities = [x.quantity for x in records]

    trend_price = linear_trend(prices)
    trend_qty = linear_trend(quantities)

    return JsonResponse({
        "labels": labels,
        "prices": prices,
        "quantities": quantities,
        "trend_price": trend_price,
        "trend_qty": trend_qty,
    })

def item_chart_page(request, item_id):
    return render(request, "items/item_chart.html", {"item_id": item_id})