from django.shortcuts import render, redirect, get_object_or_404
from mocktrade.views import build_mocktrade_context
from messageboard.views import build_messageboard_context
from messageboard.forms import MessageForm
from messageboard.models import Message
from visualisation.views import build_visualisation_context


def home(request):
    # Main homepage: upper visualisation + lower messageboard/mocktrade area.
    return redirect('/test/')


def home_test(request):
    panel = request.GET.get("panel", "messageboard")

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

    context = {"panel": panel}
    context.update(build_visualisation_context())

    if panel == "mocktrade":
        context.update(build_mocktrade_context(request))
    elif panel == "messageboard":
        context.update(build_messageboard_context(request))

    return render(request, "hometesting.html", context)
