from django.shortcuts import render
from mocktrade.views import build_mocktrade_context

def home(request):
    return render(request, 'home.html', {
        'current_page': 'home'
    })

def home_test(request):
    panel = request.GET.get("panel", "messageboard")

    context = {
        "panel": panel,
    }

    if panel == "mocktrade":
        context.update(build_mocktrade_context(request))
    # elif panel == "messageboard":
        # context.update(function(request))

    return render(request, "hometesting.html", context)