from django.contrib import admin

from .models import Product, Warehouse, Client, WarehouseProduct, ClientProduct


class ProductInstanceInline(admin.TabularInline):
    model = WarehouseProduct


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_clients', 'display_warehouses')
    inlines = [ProductInstanceInline]


class WarehouseInstanceInline(admin.TabularInline):
    model = WarehouseProduct


class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'storage_limit', 'display_products_to_store')
    list_filter = ('storage_limit',)
    inlines = [WarehouseInstanceInline]


class ClientInstanceInline(admin.TabularInline):
    model = ClientProduct


class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_products_in_use')
    inlines = [ClientInstanceInline]


admin.site.register(Product, ProductAdmin)
admin.site.register(Warehouse, WarehouseAdmin)
admin.site.register(Client, ClientAdmin)
