# Generated by Django 3.2.11 on 2022-03-15 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0018_alter_customer_customer_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='street_address1',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='street_address2',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='street_no',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
