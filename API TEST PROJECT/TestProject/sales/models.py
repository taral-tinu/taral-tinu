from base.models import CodeTable, Currency
from customer.models import Customer
from customer.models import User as ECUser
from django.contrib.auth.models import User
from django.db import models
from TestProject.choices import action_status, action_types, scheduler_status
from TestProject.signals import state_audit_signal


# Create your models here.
class Invoice(models.Model):
    invoice_number = models.CharField(max_length=100,unique=True)
    status = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="%(class)s_status")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT,related_name="%(class)s_customer")
    outstanding_amount = models.DecimalField(max_digits=12, decimal_places=3,null=True, blank=True)
    currency_outstanding_amount = models.DecimalField(max_digits=12, decimal_places=3,null=True, blank=True)
    invoice_created_on = models.DateTimeField(null=True, blank=True)
    invoice_due_date = models.DateTimeField(null=True, blank=True)
    invoice_close_date = models.DateTimeField(null=True, blank=True)
    hand_company = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="%(class)s_hand_company",null=True, blank=True)
    invoice_value = models.DecimalField(max_digits=12, decimal_places=3)
    vat_percentage = models.DecimalField(max_digits=12, decimal_places=3)
    vat_value = models.DecimalField(max_digits=12, decimal_places=3)
    order_net_value = models.DecimalField(max_digits=12, decimal_places=3)
    ec_invoice_type_id = models.IntegerField(null=True, blank=True)
    transport_cost = models.DecimalField(max_digits=12, decimal_places=3)
    weight = models.DecimalField(max_digits=12, decimal_places=3)
    custom_value = models.DecimalField(max_digits=12, decimal_places=3)
    cust_account_no = models.CharField(max_length=100,null=True, blank=True)
    delivery_condition = models.CharField(max_length=100,null=True, blank=True)
    intrastat = models.CharField(max_length=100,null=True, blank=True)
    packing = models.IntegerField(null=True, blank=True)
    country_of_origin = models.IntegerField(null=True, blank=True)
    trans_port_serivice = models.IntegerField(null=True, blank=True)
    is_invoiced = models.BooleanField(default=False)
    created_on = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(ECUser,on_delete=models.PROTECT,null=True, blank=True)
    last_rem_date = models.DateTimeField(null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    meta_data = models.TextField(null=True, blank=True)
    currency_invoice_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_vat_value= models.DecimalField(max_digits=12, decimal_places=3)
    currency_order_net_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_transport_cost = models.DecimalField(max_digits=12, decimal_places=3)
    currency_custome_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency = models.ForeignKey(Currency,on_delete=models.PROTECT,null=True, blank=True)
    curr_rate = models.DecimalField(max_digits=12, decimal_places=8)
    is_invoice_deliver = models.BooleanField(default=False)
    is_invoice_send = models.BooleanField(default=False)
    is_invoice_by_post = models.BooleanField(default=False)
    is_e_invoice = models.BooleanField(default=False)
    ots_vat_percentage = models.DecimalField(max_digits=12, decimal_places=3)
    ots_vat_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_ots_vat_value = models.DecimalField(max_digits=12, decimal_places=3)
    order_nrs = models.CharField(max_length=100)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=3)
    cust_amount_paid = models.DecimalField(max_digits=12, decimal_places=3)
    payment_date = models.DateTimeField(null=True, blank=True)
    secondry_status = models.ForeignKey(CodeTable,on_delete=models.PROTECT,null=True, blank=True, related_name="%(class)s_secondry_status")
    is_einv_sign_scheduled = models.BooleanField(default=False)
    original_invoice_number = models.CharField(max_length=100,null=True, blank=True)
    is_downpayment = models.BooleanField(default=False)
    is_peppol_invoice = models.BooleanField(default=False)
    is_peppol_verified = models.BooleanField(default=False)
    payment_tracking_number = models.IntegerField(null=True, blank=True)
    ec_invoice_address_id = models.IntegerField(null=True, blank=True) #changed column name
    # invoice_iddress = models.ForeignKey(Address,on_delete=models.PROTECT)
    ec_delivery_id = models.IntegerField(null=True, blank=True)
    is_legal = models.BooleanField(default=False)
    is_finished = models.BooleanField(default=False)

    def __str__(self):
        return self.invoice_number

class InvoiceOrder(models.Model):
    invoice = models.ForeignKey(Invoice,on_delete=models.PROTECT,related_name="invoice")
    order_numbre = models.IntegerField(null=True,blank=True)
    order_number = models.CharField(max_length=100,null=True,blank=True)
    order_unit_value = models.DecimalField(max_digits=12, decimal_places=3,null=True,blank=True)
    quantity = models.IntegerField(null=True,blank=True)
    invoice_amount = models.DecimalField(max_digits=12, decimal_places=3,null=True,blank=True)
    ord_trp_value = models.DecimalField(max_digits=12, decimal_places=3,null=True,blank=True)
    order_vnit_value_Curr = models.DecimalField(max_digits=12, decimal_places=3,null=True,blank=True)
    ord_trp_value_curr = models.DecimalField(max_digits=12, decimal_places=3,null=True,blank=True)
    invoice_amount_curr = models.DecimalField(max_digits=12, decimal_places=3,null=True,blank=True)
    is_reduce_vat = models.BooleanField(default=False)
    invoice_ref = models.CharField(max_length=100,null=True,blank=True)


class Scheduler(models.Model):
    name = models.CharField(max_length=200,verbose_name="Scheduler Name")
    created_on = models.DateTimeField(auto_now=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT,related_name="customer_scheduler")
    total_invoice = models.IntegerField(null=True,blank=True)
    invoice = models.ManyToManyField(Invoice,related_name="%(class)s_invoice")
    def __str__(self):
        return str(self.name)
class ActionReport(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.PROTECT, related_name="%(class)s_customer")
    invoice = models.ManyToManyField(Invoice,related_name="%(class)s_invoice")
    action_by = models.ForeignKey(User, on_delete=models.PROTECT)
    action_type = models.CharField(max_length=100,choices=action_types,null=True,blank=True)
    action_status = models.CharField(max_length=100,choices=action_status,default="pending")
    action_date = models.DateTimeField(null=True,blank=True)
    summary = models.TextField(blank=True)
    reference = models.CharField(max_length=100, null=True,blank=True)
    # attachment = models.TextField(default="",null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    is_legal = models.BooleanField(default=False)

