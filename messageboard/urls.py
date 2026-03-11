from django.urls import path
from . import views

app_name = "messageboard"

urlpatterns = [
    path("t/<str:topic_key>/", views.thread, name="thread"),
    path("t/<str:topic_key>/post/", views.post_message, name="post"),
    path("delete/<int:message_id>/", views.delete_message, name="delete_message"),
]