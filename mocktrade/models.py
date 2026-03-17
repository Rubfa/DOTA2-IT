from django.db import models

class UserAccount(models.Model):
    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20)
    status = models.BooleanField(default=True)
    message_post_today = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Cosmetic(models.Model):
    item_name = models.CharField(max_length=20)

    def __str__(self):
        return self.item_name


class Hero(models.Model):
    hero_name = models.CharField(max_length=20, unique=True)
    hero_type = models.CharField(max_length=20)
    item1 = models.ForeignKey(
        Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='hero_item1'
    )
    item2 = models.ForeignKey(
        Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='hero_item2'
    ) 

    def __str__(self):
        return self.hero_name


class MarketRecord(models.Model):
    item = models.ForeignKey(Cosmetic, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.item.item_name} - {self.date}"


class MockTrading(models.Model):
    user = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)

    asset1 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset1_users')
    asset2 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset2_users')
    asset3 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset3_users')
    asset4 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset4_users')
    asset5 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset5_users')
    asset6 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset6_users')
    asset7 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset7_users')
    asset8 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset8_users')
    asset9 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset9_users')
    asset10 = models.ForeignKey(Cosmetic, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset10_users')

    def __str__(self):
        return f"{self.user.username} Trading Account"


# Compatibility aliases used by teammates in existing code.
Cometics = Cosmetic
Heros = Hero
Maket_records = MarketRecord
Mock_tradings = MockTrading
