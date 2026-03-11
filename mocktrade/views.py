from django.shortcuts import render
from django.http import HttpResponse

from .models import MockTrading, Cosmetic

def index(request):

    trading = MockTrading.objects.first()
    price = None

    if request.method == "POST":

        item_name = request.POST.get("item_name")
        action = request.POST.get("action")

        try:
            item = Cosmetic.objects.get(item_name=item_name)
            price = 100   # 暂时固定价格，之后可以从 MarketRecord 读取
        except Cosmetic.DoesNotExist:
            item = None

        if item:

            if action == "buy":

                if trading.balance >= price:

                    if trading.asset1 is None:
                        trading.asset1 = item
                    elif trading.asset2 is None:
                        trading.asset2 = item
                    elif trading.asset3 is None:
                        trading.asset3 = item
                    elif trading.asset4 is None:
                        trading.asset4 = item
                    elif trading.asset5 is None:
                        trading.asset5 = item

                    trading.balance -= price
                    trading.save()

            elif action == "sell":

                if trading.asset1 == item:
                    trading.asset1 = None
                elif trading.asset2 == item:
                    trading.asset2 = None
                elif trading.asset3 == item:
                    trading.asset3 = None
                elif trading.asset4 == item:
                    trading.asset4 = None
                elif trading.asset5 == item:
                    trading.asset5 = None

                trading.balance += price
                trading.save()

    assets = [
        trading.asset1,
        trading.asset2,
        trading.asset3,
        trading.asset4,
        trading.asset5,
    ]

    return render(request, "mocktrade/portfolio.html", {
        "balance": trading.balance,
        "assets": assets,
        "price": price
    })