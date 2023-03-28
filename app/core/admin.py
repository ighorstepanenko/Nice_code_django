from django.contrib import admin

from .models import Product, Warehouse, Client, WarehouseProduct, ClientProduct, TransactionProduct, Transaction


class ProductInstanceInline(admin.TabularInline):
    model = WarehouseProduct


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_clients', 'display_warehouses')
    inlines = [ProductInstanceInline]


class WarehouseInstanceInline(admin.TabularInline):
    model = WarehouseProduct


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'storage_limit', 'display_products_to_store')
    list_filter = ('name',)
    inlines = [WarehouseInstanceInline]


class ClientInstanceInline(admin.TabularInline):
    model = ClientProduct


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_products_in_use')
    inlines = [ClientInstanceInline]

class TransactionInstanceInline(admin.TabularInline):
    model = TransactionProduct

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'client', 'warehouse', 'quantity', 'total_price')
    list_filter = ('client', 'warehouse')
    inlines = [TransactionInstanceInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Transaction, TransactionAdmin)
