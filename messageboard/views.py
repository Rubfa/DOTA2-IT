from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import MessageForm
from .models import Message


def thread(request, topic_key):
    form = MessageForm()

    # Fetch all messages in this topic
    qs = (
        Message.objects
        .filter(topic_key=topic_key)
        .select_related("author")
        .order_by("created_at")
    )
    all_msgs = list(qs)

    # Build a tree in memory: node = {"msg": Message, "children": []}
    nodes = {m.id: {"msg": m, "children": []} for m in all_msgs}
    roots = []

    for m in all_msgs:
        node = nodes[m.id]
        if m.parent_id and m.parent_id in nodes:
            nodes[m.parent_id]["children"].append(node)
        else:
            roots.append(node)

    return render(request, "messageboard/thread.html", {
        "topic_key": topic_key,
        "form": form,
        "roots": roots,   # tree roots
    })


@login_required
def post_message(request, topic_key):
    if request.method != "POST":
        return redirect("messageboard:thread", topic_key=topic_key)

    form = MessageForm(request.POST)
    if not form.is_valid():
        return redirect("messageboard:thread", topic_key=topic_key)

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

    return redirect("messageboard:thread", topic_key=topic_key)


@login_required
def delete_message(request, message_id):
    msg = get_object_or_404(Message, id=message_id)

    if not (request.user.is_staff or msg.author_id == request.user.id):
        return HttpResponseForbidden("Not allowed")

    topic_key = msg.topic_key

    if request.method == "POST":
        msg.delete()

    return redirect("messageboard:thread", topic_key=topic_key)