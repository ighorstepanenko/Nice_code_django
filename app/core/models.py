from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Warehouse(models.Model):
    name = models.CharField(max_length=255)
    storage_limit = models.IntegerField(default=0)
    products = models.ManyToManyField(Product, through='WarehouseProduct')

    def __str__(self):
        return self.name


class WarehouseProduct(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    limit = models.IntegerField(default=0)
    tariff = models.FloatField()

    class Meta:
        unique_together = ('warehouse', 'product',)


class Client(models.Model):
    name = models.CharField(max_length=255)
    products_in_use = models.ManyToManyField(Product, through='ClientProduct')

    def __str__(self):
        return self.name


class ClientProduct(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)

    class Meta:
        unique_together = ('client', 'product',)


class Distance(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    distance = models.FloatField()

    class Meta:
        unique_together = ('client', 'warehouse',)

