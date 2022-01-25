# Generated by Django 3.2.11 on 2022-01-25 14:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40, verbose_name='Currency name')),
                ('symbol', models.CharField(max_length=3, verbose_name='Currency symbol')),
                ('is_base', models.BooleanField(default=False, verbose_name='Base currency')),
                ('is_deleted', models.BooleanField(verbose_name='Deleted')),
            ],
        ),
        migrations.CreateModel(
            name='CurrencyRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factor', models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Currency factor')),
                ('reference_date', models.DateTimeField(verbose_name='Reference date')),
                ('expire_date', models.DateTimeField(blank=True, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='currency', to='base.currency')),
            ],
        ),
        migrations.CreateModel(
            name='CodeTable',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('code', models.CharField(max_length=100)),
                ('desc', models.TextField()),
                ('is_deleted', models.BooleanField(default=True)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.codetable')),
            ],
        ),
    ]