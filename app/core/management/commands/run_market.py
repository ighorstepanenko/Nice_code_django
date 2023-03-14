from random import randint, uniform

from django.core.management import BaseCommand
from django.db.models import F

from core.models import Product, Warehouse, Client, Distance, WarehouseProduct, ClientProduct


class Command(BaseCommand):
    help = 'Runs the supply market and customer generation logic'

    def add_arguments(self, parser):
        parser.add_argument('num_products', type=int, help='Number of products to generate.')
        parser.add_argument('num_warehouses', type=int, help='Number of warehouses to generate.')
        parser.add_argument('num_iterations', type=int, help='Number of iterations to run the algorithm.')

    def handle(self, *args, **options):
        # Generate products
        for i in range(options['num_products']):
            Product.objects.create(
                name=f'Товар {i + 1}'
            )

        # Generate warehouses
        for i in range(options['num_warehouses']):
            Warehouse.objects.create(
                name=f'Склад {i + 1}',
                storage_limit=randint(1, 100)
            )

        # Load products
        products = Product.objects.all()

        # Load warehouses
        warehouses = Warehouse.objects.prefetch_related('products').all()

        # Generate supply market
        for warehouse in warehouses:
            for product in products:
                if randint(0, 1) == 1:
                    warehouse.products.add(product, through_defaults={
                        'limit': randint(0, 250),
                        'tariff': round(uniform(1, 50), 2)
                    })

        # Find optimal offers
        for i in range(options['num_iterations']):
            # Generate client with random products
            client = Client.objects.create(
                name=f'Client {i + 1}'
            )
            products = Product.objects.all()
            for product in products:
                quantity = randint(1, 500)
                if randint(0, 1) == 1:
                    client.products_in_use.add(product, through_defaults={
                        'quantity': quantity
                    })
            print(f'Клиент: {client.name}\nТовары клиента: ', end='')
            for product, quantity in client.products_in_use.through.objects.filter(client=client).values_list('product',
                                                                                                              'quantity'):
                print(f'{Product.objects.get(id=product).name}({quantity}шт.)', end=', ')

            # Generate distances
            for warehouse in warehouses:
                distance = randint(1, 100)
                Distance.objects.create(
                    client=client,
                    warehouse=warehouse,
                    distance=distance,
                )

            transport_tariff = 0.01
            products = client.products_in_use.all()

            result_dict = {}
            for warehouse in warehouses:
                products_in_result = {}
                scores = 0
                total_cost = 0
                storage_limit = warehouse.storage_limit
                for product in products:
                    if product not in warehouse.products.all():
                        continue
                    else:
                        if storage_limit != 0:
                            product_to_store = min(ClientProduct.objects.get(client=client, product=product).quantity,
                                                   storage_limit,
                                                   WarehouseProduct.objects.get(warehouse=warehouse,
                                                                                product=product).limit)
                            scores += product_to_store
                            total_cost += product_to_store * transport_tariff * Distance.objects.get(client=client,
                                                                                                     warehouse=warehouse).distance + product_to_store * WarehouseProduct.objects.get(
                                warehouse=warehouse,
                                product=product).tariff
                            storage_limit -= product_to_store
                            products_in_result[product.name] = product_to_store
                result_dict[warehouse.name] = [scores, round(total_cost, 2), products_in_result]
            most_convenient_offer_tuple = sorted(result_dict.items(), key=lambda x: (x[1][0], -x[1][1]), reverse=True)
            most_convenient_offer_dict = dict(most_convenient_offer_tuple)

            cheapest_offer_tuple = sorted(result_dict.items(), key=lambda x: x[1][1])
            cheapest_offer_dict = dict(cheapest_offer_tuple)

            products_dict = {}
            for product in products:
                products_dict[product.name] = ClientProduct.objects.get(client=client, product=product).quantity

            def testing(testing_dict: dict):
                result = {}
                product_dictionary = products_dict.copy()
                for test_warehouse, test_value in testing_dict.items():
                    storing_limit = Warehouse.objects.get(name=test_warehouse).storage_limit
                    pre_result: dict = {
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
                                warehouse__name=test_warehouse).first().distance + storing * WarehouseProduct.objects.filter(
                                warehouse__name=test_warehouse,
                                product__name=test_product).first().tariff
                            pre_result[test_warehouse]['Итоговая стоимость'] = round(
                                pre_result[test_warehouse]['Итоговая стоимость'], 2)
                    if pre_result[test_warehouse]['Итоговая стоимость'] != 0:
                        result.update(pre_result)
                print(product_dictionary)
                return result, product_dictionary

            most_convenient_offer, product_check1 = testing(most_convenient_offer_dict)
            cheapest_offer, product_check2 = testing(cheapest_offer_dict)

            def print_result(dictionary: dict, prod_check: dict):
                cost = []
                for ware, ware_result in dictionary.items():
                    self.stdout.write(f'{ware}: ')
                    for key, value in ware_result.items():
                        self.stdout.write(f'{key}: {value}')
                        if key == 'Итоговая стоимость':
                            cost.append(int(value))
                self.stdout.write(f'Стоимость за всю транспортировку: {sum(cost)}у.е')

            self.stdout.write(f'\nСамый удобный вариант:')
            print_result(most_convenient_offer, product_check1)
            self.stdout.write(f'\nСамый дешёвый вариант:')
            print_result(cheapest_offer, product_check2)

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
