# Generated by Django 3.2.11 on 2022-03-15 11:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0019_auto_20220315_1631'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='street_name',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
