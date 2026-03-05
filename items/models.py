from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class PriceRecord(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="records")
    recorded_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ("item", "recorded_date")
        ordering = ["recorded_date"]
