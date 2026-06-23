import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_material_stock_quantities_decimal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stock_movement',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='stock_movement',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_movements', to='home.orders'),
        ),
        migrations.AlterField(
            model_name='stock_movement',
            name='purchase',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='stock_movements', to='home.purchase'),
        ),
    ]
