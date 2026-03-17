from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from mocktrade.views import build_mocktrade_context
from messageboard.views import build_messageboard_context
from messageboard.forms import MessageForm
from messageboard.models import Message
from visualisation.views import build_visualisation_context

PANEL_TEMPLATES = {
    "messageboard": "includes/home_messageboard_panel.html",
    "mocktrade": "includes/home_mocktrade_panel.html",
}


def normalize_panel(panel):
    return panel if panel in PANEL_TEMPLATES else "messageboard"


def build_panel_context(request, panel):
    context = {"panel": panel}

    if panel == "mocktrade":
        context.update(build_mocktrade_context(request))
    else:
        context.update(build_messageboard_context(request))

    return context


def render_panel_html(request, panel, context=None):
    panel = normalize_panel(panel)
    panel_context = context if context is not None else build_panel_context(request, panel)
    return render_to_string(
        PANEL_TEMPLATES[panel],
        panel_context,
        request=request,
    )


def home(request):
    # Main homepage: upper visualisation + lower messageboard/mocktrade area.
    return redirect('/test/')


def home_test(request):
    panel = normalize_panel(request.GET.get("panel", "messageboard"))
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    if request.method == "GET" and is_ajax:
        context = build_panel_context(request, panel)
        html = render_panel_html(request, panel, context)
        return JsonResponse({"panel": panel, "html": html})

    if (
        request.method == "POST"
        and panel == "mocktrade"
        and is_ajax
    ):
        context = build_panel_context(request, panel)
        html = render_panel_html(request, panel, context)
        return JsonResponse({"panel": panel, "html": html})

    if request.method == "POST" and panel == "messageboard":
        if request.user.is_authenticated:
            delete_message_id = request.POST.get("delete_message_id")

            if delete_message_id:
                msg = get_object_or_404(Message, id=delete_message_id)

                if request.user.is_staff or msg.author_id == request.user.id:
                    msg.delete()

                return redirect("/test/?panel=messageboard")

            form = MessageForm(request.POST)
            if form.is_valid():
                topic_key = "home"
                parent_id = request.POST.get("parent_id") or None
                parent = None

                if parent_id:
                    parent = get_object_or_404(Message, id=parent_id, topic_key=topic_key)

                Message.objects.create(
                    author=request.user,
                    topic_key=topic_key,
                    parent=parent,
                    text=form.cleaned_data["text"]
                )

        return redirect("/test/?panel=messageboard")

    context = build_panel_context(request, panel)
    context.update(build_visualisation_context())

    return render(request, "hometesting.html", context)
