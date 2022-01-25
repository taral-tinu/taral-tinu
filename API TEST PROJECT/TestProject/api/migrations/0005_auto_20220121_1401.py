# Generated by Django 3.2.11 on 2022-01-21 08:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20220120_1115'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduler',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='scheduler_invoices', to='api.invoice'),
        ),
        migrations.AlterField(
            model_name='collectionaction',
            name='scheduler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='scheduler', to='api.scheduler'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='invoice_number',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]