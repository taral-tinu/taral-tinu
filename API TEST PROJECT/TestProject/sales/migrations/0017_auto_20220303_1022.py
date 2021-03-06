# Generated by Django 3.2.11 on 2022-03-03 04:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0013_rename_company_name_customer_name'),
        ('sales', '0016_auto_20220302_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_customer', to='customer.customer'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='hand_company',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_hand_company', to='customer.customer'),
        ),
    ]
