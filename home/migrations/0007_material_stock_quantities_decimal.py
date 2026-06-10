from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_order_detail_parts_quantity_required_decimal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='material_stock',
            name='stock_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='material_stock',
            name='reserved_quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='purchase_item',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
