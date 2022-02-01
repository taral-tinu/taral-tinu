# Generated by Django 3.2.11 on 2022-01-29 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0010_auto_20220129_2236'),
        ('sales', '0007_auto_20220129_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customer.user'),
        ),
    ]
