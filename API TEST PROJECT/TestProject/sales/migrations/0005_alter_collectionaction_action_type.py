# Generated by Django 3.2.11 on 2022-01-26 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0004_alter_invoice_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionaction',
            name='action_type',
            field=models.CharField(choices=[('call', 'Call'), ('chat', 'Chat'), ('offline_message', 'Offline message'), ('ticket', 'Ticket'), ('plan_follow_up', 'Plan Follow up')], max_length=100),
        ),
    ]