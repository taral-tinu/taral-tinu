# Generated by Django 3.2.11 on 2022-01-26 06:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_auto_20220126_1145'),
        ('sales', '0003_auto_20220126_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customer.ecuser'),
        ),
    ]
