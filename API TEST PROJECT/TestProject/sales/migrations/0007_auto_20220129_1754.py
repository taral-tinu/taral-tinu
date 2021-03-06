# Generated by Django 3.2.11 on 2022-01-29 12:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0006_auto_20220129_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectionaction',
            name='scheduler_item',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='action_scheduler', to='sales.scheduleritem'),
        ),
        migrations.AddField(
            model_name='scheduler',
            name='name',
            field=models.CharField(max_length=200, null=True, verbose_name='Scheduler Name'),
        ),
        migrations.AddField(
            model_name='scheduleritem',
            name='status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending'), ('call_due', 'Call due'), ('call_done', 'Call done'), ('finished', 'Finished'), ('legal_action', 'Legal Action')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='scheduleritem',
            name='total_invoice',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='SchedulerInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice', models.ManyToManyField(related_name='scheduler_invoice', to='sales.Invoice')),
                ('scheduler_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scheduler_item', to='sales.scheduleritem')),
            ],
        ),
    ]
