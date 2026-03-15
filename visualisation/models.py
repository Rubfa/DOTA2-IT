from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=200)

    class Meta:
        db_table = "items_item"

    def __str__(self):
        return self.name


class PriceRecord(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.FloatField()
    quantity = models.IntegerField()

    class Meta:
        db_table = "items_pricerecord"


class Hero(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=200)
    type = models.CharField(max_length=50)

    class Meta:
        db_table = "items_hero"

    def __str__(self):
        return self.name


class Cosmetic(models.Model):
    hero = models.ForeignKey(Hero, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    price = models.FloatField(default=0)
    quantity = models.IntegerField(default=0)

    class Meta:
        db_table = "items_cosmetic"

    def __str__(self):
        return self.name
