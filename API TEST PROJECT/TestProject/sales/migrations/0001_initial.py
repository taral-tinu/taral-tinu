# Generated by Django 3.2.11 on 2022-01-25 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0001_initial'),
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=100, unique=True)),
                ('outstanding_amount', models.DecimalField(decimal_places=3, max_digits=12)),
                ('currency_outstanding_amount', models.DecimalField(decimal_places=3, max_digits=12)),
                ('invoice_created_on', models.DateTimeField()),
                ('invoice_due_date', models.DateTimeField()),
                ('invoice_close_date', models.DateTimeField()),
                ('invoice_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('vat_percentage', models.DecimalField(decimal_places=3, max_digits=12)),
                ('vat_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('order_net_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('transport_cost', models.DecimalField(decimal_places=3, max_digits=12)),
                ('weight', models.DecimalField(decimal_places=3, max_digits=12)),
                ('custom_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('cust_account_no', models.CharField(blank=True, max_length=100, null=True)),
                ('delivery_condition', models.CharField(blank=True, max_length=100, null=True)),
                ('intrastat', models.CharField(blank=True, max_length=100, null=True)),
                ('country_of_origin', models.IntegerField()),
                ('trans_port_serivice', models.IntegerField()),
                ('service_type', models.IntegerField()),
                ('packing', models.IntegerField()),
                ('is_invoiced', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('last_rem_date', models.DateTimeField()),
                ('remark', models.TextField()),
                ('meta_data', models.CharField(blank=True, max_length=200, null=True)),
                ('currency_invoice_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('currency_vat_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('currency_order_net_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('currency_transport_cost', models.DecimalField(decimal_places=3, max_digits=12)),
                ('currency_custome_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('curr_rate', models.DecimalField(decimal_places=8, max_digits=12)),
                ('is_invoice_deliver', models.BooleanField(default=False)),
                ('is_invoice_send', models.BooleanField(default=False)),
                ('is_invoice_by_post', models.BooleanField(default=False)),
                ('is_e_invoice', models.BooleanField(default=False)),
                ('ots_vat_percentage', models.DecimalField(decimal_places=3, max_digits=12)),
                ('ots_vat_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('currency_ots_vat_value', models.DecimalField(decimal_places=3, max_digits=12)),
                ('order_nrs', models.CharField(max_length=100)),
                ('amount_paid', models.DecimalField(decimal_places=3, max_digits=12)),
                ('cust_amount_paid', models.DecimalField(decimal_places=3, max_digits=12)),
                ('payment_date', models.DateTimeField()),
                ('is_einv_sign_scheduled', models.BooleanField(default=False)),
                ('original_invoice_number', models.CharField(blank=True, max_length=100, null=True)),
                ('is_downpayment', models.BooleanField(default=False)),
                ('is_peppol_invoice', models.BooleanField(default=False)),
                ('is_peppol_verified', models.BooleanField(default=False)),
                ('payment_tracking_number', models.IntegerField()),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='customer', to='customer.customer')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customer.user')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.currency')),
                ('hand_company', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='hand_company', to='customer.customer')),
                ('invoice_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_type', to='base.codetable')),
                ('secondry_status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_secondry_status', to='base.codetable')),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.codetable')),
            ],
        ),
        migrations.CreateModel(
            name='Scheduler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduler_name', models.CharField(max_length=200, verbose_name='Scheduler Name')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('is_legal_action', models.BooleanField(default=False)),
                ('status', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.codetable')),
            ],
        ),
        migrations.CreateModel(
            name='SchedulerItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='scheduler_customer', to='customer.customer')),
                ('invoice', models.ManyToManyField(related_name='scheduler_invoice', to='sales.Invoice')),
                ('scheduler', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='scheduler_item', to='sales.scheduler')),
            ],
        ),
        migrations.CreateModel(
            name='CollectionAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_date', models.DateTimeField(blank=True, null=True)),
                ('summary', models.TextField(blank=True)),
                ('reference', models.CharField(blank=True, max_length=100, null=True)),
                ('attachment', models.TextField(default='')),
                ('next_action_date', models.DateTimeField(blank=True, null=True)),
                ('note', models.TextField(blank=True)),
                ('next_reference', models.CharField(blank=True, max_length=100, null=True)),
                ('next_attachment', models.TextField(default='')),
                ('is_legal_action', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('action_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='customer.user')),
                ('action_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='action_type', to='base.codetable')),
                ('next_action_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='next_action_type', to='base.codetable')),
                ('scheduler', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='scheduler', to='sales.scheduler')),
            ],
        ),
    ]
