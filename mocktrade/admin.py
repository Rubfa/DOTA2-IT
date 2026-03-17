from django.contrib import admin
from .models import UserAccount, Hero, MarketRecord, Cosmetic, MockTrading

class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'status', 'message_post_today')

class CosmeticAdmin(admin.ModelAdmin):
    list_display = ('id', 'item_name',)

class HeroAdmin(admin.ModelAdmin):
    list_display = ('id', 'hero_name', 'hero_type', 'item1', 'item2')

class MarketRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'date', 'price', 'quantity')

class MockTradingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'balance', 'asset1', 'asset2', 'asset3', 'asset4', 'asset5', 'asset6', 'asset7', 'asset8', 'asset9', 'asset10')

admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Hero, HeroAdmin)
admin.site.register(MarketRecord, MarketRecordAdmin)
admin.site.register(Cosmetic, CosmeticAdmin)
admin.site.register(MockTrading, MockTradingAdmin)
