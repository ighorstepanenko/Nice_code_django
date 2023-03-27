from django.core.management import BaseCommand
from django.db.models import F

from core.logic import *


class Command(BaseCommand):
    help: str = 'Runs the supply market and customer generation logic'

    def add_arguments(self, parser):
        parser.add_argument('num_products', type=int, help='Number of products to generate.')
        parser.add_argument('num_warehouses', type=int, help='Number of warehouses to generate.')
        parser.add_argument('num_clients', type=int, help='Number of clients to run the algorithm.')

    def handle(self, *args, **options):
        # Generate products
        products = ProductGenerator(options['num_products'])
        products.generate_products()

        # Generate warehouses
        warehouses = WarehouseGenerator(options['num_warehouses'])
        warehouses.generate_warehouses()

        # Generate clients
        clients = ClientGenerator(options['num_clients'])
        clients.generate_clients()

        # Generate supply market
        supply_market = SupplyMarket(Product.objects.all(), Warehouse.objects.prefetch_related('products').all())
        supply_market.generate_supply_market()

        for client in Client.objects.all():
            print(f'Клиент: {client.name}\nТовары клиента: ', end='')
            for product, quantity in client.products_in_use.through.objects.filter(client=client).values_list(
                    'product', 'quantity'
            ):
                print(f'{Product.objects.get(id=product).name}({quantity}шт.)', end=', ')

            DistanceGenerator.generate_distances(Warehouse.objects.all(), client)
            result_dict = ScoresCounter.calculating_scores(Warehouse.objects.all(), client)
            most_convenient_offer_tuple: list[tuple] = sorted(
                result_dict.items(), key=lambda x: (x[1][0], -x[1][1]), reverse=True
            )
            most_convenient_offer_dict: dict = dict(most_convenient_offer_tuple)

            cheapest_offer_tuple: list[tuple] = sorted(result_dict.items(), key=lambda x: x[1][1])
            cheapest_offer_dict: dict = dict(cheapest_offer_tuple)

            most_convenient_offer, product_check1 = Testing.find_optimal_offers(most_convenient_offer_dict, client)
            cheapest_offer, product_check2 = Testing.find_optimal_offers(cheapest_offer_dict, client)

            def print_result(dictionary: dict):
                cost = []
                for ware, ware_result in dictionary.items():
                    self.stdout.write(f'{ware}: ')
                    for key, value in ware_result.items():
                        self.stdout.write(f'{key}: {value}')
                        if key == 'Итоговая стоимость':
                            cost.append(int(value))
                self.stdout.write(f'Стоимость за всю транспортировку: {sum(cost)}у.е')

            self.stdout.write(f'\nСамый удобный вариант:')
            print_result(most_convenient_offer)
            self.stdout.write(f'\nСамый дешёвый вариант:')
            print_result(cheapest_offer)

            for checked_product, value in product_check1.items():
                if value != 0:
                    self.stdout.write(f'Для товара {checked_product} не удалось найти вариант хранения, {value}шт.')

            if randint(0, 1) == 1:
                self.stdout.write(f'\nВыбран удобный вариант\n\n')
                transaction = most_convenient_offer
            else:
                self.stdout.write(f'\nВыбран дешёвый вариант\n\n')
                transaction = cheapest_offer

            for updated_warehouse in transaction.keys():
                updated_products = transaction[updated_warehouse]['Товары']
                Warehouse.objects.filter(name=updated_warehouse).update(
                    storage_limit=F('storage_limit') - sum([int(i[:-3]) for i in updated_products.values()]))
                for product in updated_products.keys():
                    WarehouseProduct.objects.filter(warehouse__name=updated_warehouse, product__name=product).update(
                        limit=F('limit') - int(updated_products[product][:-3]))
