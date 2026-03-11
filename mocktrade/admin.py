from django.contrib import admin
from .models import UserAccount, Hero, MarketRecord

admin.site.register(UserAccount)
admin.site.register(Hero)
admin.site.register(MarketRecord)
