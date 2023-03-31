from random import randint, uniform
from typing import List, Dict, Union
from django.db.models import F

from django.db.models import QuerySet

from core.models import *


class ProductGenerator:
    def __init__(self, num_products: int):
        self.num_products = num_products

    def generate_products(self):
        for i in range(self.num_products):
            Product.objects.create(name=f'Товар {i + 1}')


class WarehouseGenerator:
    def __init__(self, num_warehouses: int):
        self.num_warehouses = num_warehouses

    def generate_warehouses(self):
        for i in range(self.num_warehouses):
            Warehouse.objects.create(
                name=f'Склад {i + 1}',
                storage_limit=randint(1, 100)
            )


class SupplyMarket:
    def __init__(self, products: QuerySet[Product], warehouses: QuerySet[Warehouse]):
        self.products = products
        self.warehouses = warehouses

    def generate_supply_market(self):
        for warehouse in self.warehouses:
            for product in self.products:
                if randint(0, 1) == 1:
                    warehouse.products.add(product, through_defaults={
                        'limit': randint(0, 250),
                        'tariff': round(uniform(1, 50), 2)
                    })


class ClientGenerator:
    def __init__(self, num_iterations: int):
        self.num_iterations = num_iterations

    def generate_clients(self):
        for i in range(self.num_iterations):
            client = Client.objects.create(name=f'Клиент {i + 1}')
            products = Product.objects.all()
            for product in products:
                quantity = randint(1, 500)
                if randint(0, 1) == 1:
                    client.products_in_use.add(product, through_defaults={
                        'quantity': quantity
                    })


class DistanceGenerator:
    @staticmethod
    def generate_distances(warehouses: QuerySet[Warehouse], client: Client):
        for warehouse in warehouses:
            distance: int = randint(1, 100)
            Distance.objects.create(
                client=client,
                warehouse=warehouse,
                distance=distance,
            )


class ScoresCounter:
    @staticmethod
    def calculating_scores(warehouses: QuerySet[Warehouse], client: Client) -> Dict[str, List[Union[int, float, Dict]]]:
        transport_tariff: float = 0.01
        products = client.products_in_use.all()

        result_dict: Dict[str, List[int, float, Dict]] = {}
        for warehouse in warehouses:
            products_in_result: Dict[str, int] = {}
            scores: int = 0
            total_cost: float = 0.0
            storage_limit: int = warehouse.storage_limit
            for product in products:
                if product not in warehouse.products.all():
                    continue
                else:
                    if storage_limit != 0:
                        product_to_store: int = min(
                            ClientProduct.objects.get(client=client, product=product).quantity,
                            storage_limit,
                            WarehouseProduct.objects.get(warehouse=warehouse,
                                                         product=product).limit)
                        scores += product_to_store
                        total_cost += product_to_store * transport_tariff * Distance.objects.get(
                            client=client, warehouse=warehouse
                        ).distance + product_to_store * WarehouseProduct.objects.get(
                            warehouse=warehouse,
                            product=product).tariff
                        storage_limit -= product_to_store
                        products_in_result[product.name] = product_to_store
                    result_dict[warehouse.name] = [scores, round(total_cost, 2), products_in_result]
        return result_dict


class Testing:
    @staticmethod
    def find_optimal_offers(testing_dict: Dict[str, List[Union[int, float, Dict]]], client: Client) -> List[Dict[str, Dict]]:
        result: Dict[str, Dict[str, Union[dict, int]]] = {}
        transport_tariff: float = 0.01
        product_dictionary: Dict[str, int] = {}
        for product in client.products_in_use.all():
            product_dictionary[product.name] = ClientProduct.objects.get(client=client, product=product).quantity
        for test_warehouse, test_value in testing_dict.items():
            storing_limit = Warehouse.objects.get(name=test_warehouse).storage_limit
            pre_result: Dict[str, Dict[str, Union[dict, int]]] = {
                test_warehouse: {
                    'Товары': {},
                    'Итоговая стоимость': 0
                }
            }
            for test_product, test_quantity in product_dictionary.items():
                if test_product in test_value[2].keys() and product_dictionary[test_product] != 0:
                    storing = min(test_value[2][test_product],
                                  product_dictionary[test_product], storing_limit)
                    product_dictionary[test_product] -= storing
                    pre_result[test_warehouse]['Товары'][test_product] = f'{storing}шт.'
                    storing_limit -= storing
                    pre_result[test_warehouse][
                        'Итоговая стоимость'] += storing * transport_tariff * Distance.objects.filter(
                        client=client,
                        warehouse__name=test_warehouse
                    ).first().distance + storing * WarehouseProduct.objects.filter(
                        warehouse__name=test_warehouse,
                        product__name=test_product).first().tariff
                    pre_result[test_warehouse]['Итоговая стоимость'] = round(
                        pre_result[test_warehouse]['Итоговая стоимость'], 2)
            if pre_result[test_warehouse]['Итоговая стоимость'] != 0:
                result.update(pre_result)
        print(product_dictionary)
        return [result, product_dictionary]

class TransactionHandler:
    @staticmethod
    def create_transaction(client, warehouse, stored_products, total_price, updated_products):
        trans = Transaction.objects.create(client=client, warehouse=warehouse, quantity=stored_products, total_price=total_price)
        for product in updated_products.keys():
            quant = int(updated_products[product][:-3])
            TransactionProductHandler.create_transaction_product(trans, product, quant)
            WarehouseProductHandler.update_warehouse_product(warehouse, product, quant)
        WarehouseHandler.update_warehouse_limit(warehouse, stored_products)

class WarehouseHandler:
    @staticmethod
    def update_warehouse_limit(warehouse, stored_products):
        Warehouse.objects.filter(name=warehouse.name).update(storage_limit=F('storage_limit') - stored_products)

class TransactionProductHandler:
    @staticmethod
    def create_transaction_product(transaction, product_name, quantity):
        product = Product.objects.get(name=product_name)
        tariff = WarehouseProductHandler.get_warehouse_product_tariff(transaction.warehouse, product)
        TransactionProduct.objects.create(transaction=transaction, product=product, quantity=quantity, price=tariff)

class WarehouseProductHandler:
    @staticmethod
    def get_warehouse_product_tariff(warehouse, product):
        return WarehouseProduct.objects.get(warehouse=warehouse, product=product).tariff

    @staticmethod
    def update_warehouse_product(warehouse, product_name, quantity):
        WarehouseProduct.objects.filter(warehouse=warehouse, product__name=product_name).update(limit=F('limit') - quantity)


