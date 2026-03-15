from django.contrib import admin

from .models import Cosmetic, Hero, Item, PriceRecord


@admin.register(Hero)
class HeroAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "icon")
    search_fields = ("name", "type")
    list_filter = ("type",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Cosmetic)
class CosmeticAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "hero", "item", "price", "quantity")
    search_fields = ("name", "hero__name", "item__name")
    list_filter = ("hero__type",)


@admin.register(PriceRecord)
class PriceRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "date", "price", "quantity")
    search_fields = ("item__name",)
    list_filter = ("date",)
