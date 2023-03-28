# Generated by Django 4.1.7 on 2023-03-28 10:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_transaction_transactionproduct_transaction_products_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'ordering': ['pk'], 'verbose_name': 'Транзакции', 'verbose_name_plural': 'Транзакции'},
        ),
        migrations.AlterField(
            model_name='clientproduct',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.client', verbose_name='Имя клиента'),
        ),
        migrations.AlterField(
            model_name='clientproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product', verbose_name='Название товара'),
        ),
        migrations.AlterField(
            model_name='clientproduct',
            name='quantity',
            field=models.IntegerField(default=0, verbose_name='Количество имеющегося товара'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.client', verbose_name='Имя клиента'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='quantity',
            field=models.PositiveIntegerField(default=0, verbose_name='Количество размещённого товара (шт.)'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='total_price',
            field=models.PositiveIntegerField(default=0, verbose_name='Итоговая стоимость размещения товаров'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.warehouse', verbose_name='Склад'),
        ),
        migrations.AlterField(
            model_name='transactionproduct',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=6, verbose_name='Стоимость размещения единицы товара'),
        ),
        migrations.AlterField(
            model_name='transactionproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product', verbose_name='Название товара'),
        ),
        migrations.AlterField(
            model_name='transactionproduct',
            name='quantity',
            field=models.PositiveIntegerField(verbose_name='Количество размещённого товара'),
        ),
        migrations.AlterField(
            model_name='transactionproduct',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.transaction', verbose_name='Транзакция'),
        ),
        migrations.AlterField(
            model_name='warehouseproduct',
            name='limit',
            field=models.IntegerField(default=0, verbose_name='Лимит товара на складе'),
        ),
        migrations.AlterField(
            model_name='warehouseproduct',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product', verbose_name='Название товара'),
        ),
        migrations.AlterField(
            model_name='warehouseproduct',
            name='tariff',
            field=models.FloatField(verbose_name='Стоимость размещения единицы товара'),
        ),
        migrations.AlterField(
            model_name='warehouseproduct',
            name='warehouse',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.warehouse', verbose_name='Склад'),
        ),
    ]
