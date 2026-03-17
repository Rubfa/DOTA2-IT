from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path("get_cosmetics/<int:hero_id>/", views.get_cosmetics, name="get_cosmetics"),
    path("api/items/<int:item_id>/history/", views.item_history_api, name="item_history_api"),
    path("items/<int:item_id>/chart/", views.item_chart_page, name="item_chart_page"),
]
