from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название товара')

    def __str__(self):
        return self.name

    def display_clients(self):
        """Creates a string for the Clients. This is required to display products in Admin."""
        return ', '.join([suitable.client.name for suitable in ClientProduct.objects.filter(product=self)])
    display_clients.short_description = 'Клиенты, которым нужно разместить товар'

    def display_warehouses(self):
        """Creates a string for the Warehouses. This is required to display products in Admin."""
        return ', '.join([suitable.warehouse.name for suitable in WarehouseProduct.objects.filter(product=self)])
    display_warehouses.short_description = 'Склад, в которых можно разместить товар'

    class Meta:
        verbose_name = 'Товары'
        verbose_name_plural = 'Товары'
        ordering = ['name']


class Warehouse(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название склада')
    storage_limit = models.IntegerField(default=0, verbose_name='Общий лимит товаров к размещению(шт.)')
    products = models.ManyToManyField(Product, through='WarehouseProduct', verbose_name='Названия товаров, доступных к размещению')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Склады'
        verbose_name_plural = 'Склады'
        ordering = ['name']

    def display_products_to_store(self):
        """Creates a string for the Products. This is required to display products in Admin."""
        return ', '.join([product.name for product in self.products.all()[:10]])
    display_products_to_store.short_description = 'Названия товаров, доступных к размещению'


class WarehouseProduct(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    limit = models.IntegerField(default=0)
    tariff = models.FloatField()

    class Meta:
        unique_together = ('warehouse', 'product',)


class Client(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя клиента')
    products_in_use = models.ManyToManyField(Product, through='ClientProduct', verbose_name='Товары, которые нужно разместить')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Клиенты'
        verbose_name_plural = 'Клиенты'
        ordering = ['name']

    def display_products_in_use(self):
        """Creates a string for the Products. This is required to display products in Admin."""
        return ', '.join([product.name for product in self.products_in_use.all()[:10]])
    display_products_in_use.short_description = 'Товары, которые нужно разместить'


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

