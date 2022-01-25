from datetime import datetime
from uuid import uuid4

from django.contrib.auth.models import Group, User
from django.core.files.storage import FileSystemStorage
from django.db import models
from TestProject.util import Util

profile_image_storage = FileSystemStorage()
# from base.models import *

from TestProject.choices import *

# Create your models here.


def get_profile_image_name(instance, filename):
    resource_img_path = Util.get_resource_path('profile', '')
    profile_image_storage.location = resource_img_path
    newfilename = str(uuid4()) + "." + filename.split(".")[-1]
    return newfilename


class MainMenu(models.Model):# base
    name = models.CharField(max_length=150, verbose_name="Menu name")
    url = models.CharField(max_length=1000, verbose_name="Url")
    icon = models.CharField(max_length=500, verbose_name="Icon")
    parent_id = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    sequence = models.IntegerField(verbose_name="Sequence", default=0)
    is_active = models.BooleanField(default=True)
    menu_code = models.CharField(max_length=200, verbose_name="Menu Code", null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
            return "%s" % (str(self.name) + " - " + str(self.name))


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    theme = models.CharField(max_length=15, verbose_name="Color", null=True, blank=True)
    display_row = models.IntegerField(verbose_name="Display row", null=True, blank=True)
    default_page = models.TextField(max_length=250, null=True, blank=True, verbose_name="Default page loaded after login")
    profile_image = models.ImageField(storage=profile_image_storage, upload_to=get_profile_image_name, null=True, blank=True)
    def __str__(self):
        return str(self.user.username)

class ContentPermission(models.Model):
    content_group = models.CharField(max_length=150)
    content_name = models.CharField(max_length=150)
    sequence = models.IntegerField(default=0)

    def __str__(self):
        return "%s" % (str(self.content_group) + " - " + str(self.content_name))

class PagePermission(models.Model):
    menu = models.ForeignKey(MainMenu, null=True, on_delete=models.PROTECT)
    content = models.ForeignKey(ContentPermission, null=True, on_delete=models.PROTECT)
    act_name = models.CharField(max_length=30)
    act_code = models.CharField(max_length=200)

    def __str__(self):
        return "%s" % (str(self.menu.name) + " - " + str(self.act_name))

class GroupPermission(models.Model):
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.PROTECT)
    page_permission = models.ForeignKey(PagePermission, blank=True, null=True, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return "%s" % (self.group)

class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT,related_name="usergroup")
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.PROTECT)

class CodeTable(models.Model):#base
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=100)
    desc = models.TextField()
    is_deleted = models.BooleanField(default=True)

class Country(models.Model):#base
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=5, verbose_name="Code", null=True, blank=True)

class State(models.Model):#base
    name = models.CharField(max_length=200)
    country = models.ForeignKey(Country, null=True, on_delete=models.PROTECT)
    code = models.CharField(max_length=20, verbose_name="Code", null=True, blank=True)

class Currency(models.Model):#base

    name = models.CharField(max_length=40, null=False, verbose_name="Currency name")
    symbol = models.CharField(max_length=3, null=False, verbose_name="Currency symbol")
    is_base = models.BooleanField(default=False, verbose_name="Base currency")
    is_deleted = models.BooleanField(verbose_name="Deleted")

    def __str__(self):
        return "%s" % (self.name)

class CurrencyRate(models.Model): # base
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=False, related_name="currency")
    factor = models.DecimalField(null=False, max_digits=10, decimal_places=3, verbose_name="Currency factor")
    reference_date = models.DateTimeField(verbose_name="Reference date", null=False)
    expire_date = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

class Contact(models.Model): # customers
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    create_on = models.DateTimeField(auto_now_add=True)
    job_title = models.CharField(max_length=100, null=True)
    is_deleted = models.BooleanField(default=False)
    # responsibility = models.ForeignKey()


class Customer(models.Model): # customers
    ec_customer_id = models.IntegerField(null=True, blank=True, verbose_name="EC customer Id")
    name = models.CharField(max_length=200, default="")
    email = models.EmailField(null=True)
    contact_person = models.CharField(max_length=200, default="")
    contact_number = models.CharField(max_length=200, default="")
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name="Country", null=True)
    account_manager = models.ForeignKey(Contact, verbose_name="Account manager", blank=True, null=True, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=30, verbose_name="Account number", null=True, help_text="Number assigned by Accounting")
    initials = models.CharField(max_length=30,null=True, blank=True)
    customer_type = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="customer_type")
    tax_number_type = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="taxt_number_type")
    vat_no = models.CharField(max_length=100,blank=True, null=True)
    invoice_prefrence = models.CharField(max_length=100,blank=True, null=True)
    invoice_postage = models.CharField(max_length=100,blank=True, null=True)
    is_sales_review = models.BooleanField(default=False)
    is_vat_verified = models.BooleanField(default=False)
    currency = models.ForeignKey(Currency,on_delete=models.PROTECT)
    # sa_company_competence = models.CharField(max_length=500,blank=True, null=True)
    # sa_ec_customer = models.CharField(max_length=500,blank=True, null=True)
    peppol_address = models.CharField(max_length=500,blank=True, null=True)
    status = models.ForeignKey(CodeTable,on_delete=models.PROTECT)
    last_order_date = models.DateTimeField()
    is_allow_send_mail = models.BooleanField(default=False)
    invoice_lang = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="invoice_language")
    is_deleted = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    is_exclude_vat = models.BooleanField(default=False)
    is_deliver_invoice_by_post = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_peppol_verfied = models.BooleanField(default=False)
    Is_always_vat = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_student_team = models.BooleanField(default=False)
    is_call_report_attached = models.BooleanField(default=False)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="Currency", null=True)

    def __str__(self):
        return self.name
class ECUser(models.Model): # customers
    company = models.ForeignKey(Customer,on_delete=models.PROTECT)
    username = models.CharField(max_length=200)
    password = models.CharField(max_length=200)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT)
    language = models.ForeignKey(CodeTable, on_delete=models.PROTECT)
    is_power_user = models.BooleanField(default=False)
    is_deleted =  models.BooleanField(default=False)
    is_active =  models.BooleanField(default=False)
    # sa_user_responsibilities = models.TextField()

class Address(models.Model): # customers
    street_name = models.CharField(max_length=100, default="")
    company = models.ForeignKey(Customer, null=True, on_delete=models.PROTECT)
    street_no = models.CharField(max_length=100, default="")
    street_address1 = models.CharField(max_length=300, default="")
    street_address2 = models.CharField(max_length=300, default="")
    note = models.TextField(null=True, blank=True)
    zip = models.CharField(max_length=40,null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.SET_NULL, blank=True, null=True)
    city = models.CharField(max_length=300, null=True, blank=True)
    state = models.ForeignKey(CodeTable, verbose_name="State", null=True, on_delete=models.PROTECT)
    other_state = models.CharField(max_length=100)
    country = models.ForeignKey(Country, verbose_name="Country", null=True, on_delete=models.PROTECT)
    is_primary = models.BooleanField(default=True)
    created_by = models.ForeignKey(ECUser,on_delete=models.PROTECT,null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    box_no = models.CharField(max_length=300,null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

class Invoice(models.Model): # sales
    invoice_number = models.CharField(max_length=100,unique=True)
    status = models.ForeignKey(CodeTable,on_delete=models.PROTECT)
    company = models.ForeignKey(Customer, on_delete=models.PROTECT,related_name="customer")
    outstanding_amount = models.DecimalField(max_digits=12, decimal_places=3)
    currency_outstanding_amount = models.DecimalField(max_digits=12, decimal_places=3)
    invoice_created_on = models.DateTimeField()
    invoice_due_date = models.DateTimeField()
    invoice_close_date = models.DateTimeField()
    hand_company = models.ForeignKey(Customer, on_delete=models.PROTECT,related_name="hand_company")
    invoice_value = models.DecimalField(max_digits=12, decimal_places=3)
    vat_percentage = models.DecimalField(max_digits=12, decimal_places=3)
    vat_value = models.DecimalField(max_digits=12, decimal_places=3)
    order_net_value = models.DecimalField(max_digits=12, decimal_places=3)
    invoice_type = models.ForeignKey(CodeTable,on_delete=models.PROTECT, related_name="invoice_type")
    transport_cost = models.DecimalField(max_digits=12, decimal_places=3)
    weight = models.DecimalField(max_digits=12, decimal_places=3)
    custom_value = models.DecimalField(max_digits=12, decimal_places=3)
    cust_account_no = models.CharField(max_length=100,null=True, blank=True)
    delivery_condition = models.CharField(max_length=100,null=True, blank=True)
    intrastat = models.CharField(max_length=100,null=True, blank=True)
    packing = models.IntegerField()
    country_of_origin = models.IntegerField()
    trans_port_serivice = models.IntegerField()
    service_type = models.IntegerField()
    packing = models.IntegerField()
    is_invoiced = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(ECUser,on_delete=models.PROTECT)
    last_rem_date = models.DateTimeField()
    remark = models.TextField()
    meta_data = models.CharField(max_length=200,null=True, blank=True)
    currency_invoice_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_vat_value= models.DecimalField(max_digits=12, decimal_places=3)
    currency_order_net_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency_transport_cost = models.DecimalField(max_digits=12, decimal_places=3)
    currency_custome_value = models.DecimalField(max_digits=12, decimal_places=3)
    currency = models.ForeignKey(Currency,on_delete=models.PROTECT)
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
    payment_date = models.DateTimeField()
    secondry_status = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="invoice_secondry_status")
    is_einv_sign_scheduled = models.BooleanField(default=False)
    original_invoice_number = models.CharField(max_length=100,null=True, blank=True)
    is_downpayment = models.BooleanField(default=False)
    is_peppol_invoice = models.BooleanField(default=False)
    is_peppol_verified = models.BooleanField(default=False)
    payment_tracking_number = models.IntegerField()

    def __str__(self):
        return self.invoice_number


class Scheduler(models.Model): # sales
    scheduler_name = models.CharField(max_length=200,verbose_name="Scheduler Name")
    created_on = models.DateTimeField(auto_now_add=True)
    is_legal_action = models.BooleanField(default=False)
    # status = models.CharField(max_length=100,choices=action_status,default="pending")
    status = models.ForeignKey(CodeTable,on_delete=models.PROTECT)


    def __str__(self):
        return self.scheduler_name


class SchedulerItem(models.Model): # sales
    scheduler = models.ForeignKey(Scheduler,on_delete=models.PROTECT,related_name="scheduler_item")
    invoice = models.ManyToManyField(Invoice,related_name="scheduler_invoice")
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT,related_name="scheduler_customer",null=True)
    def __str__(self):
        return str(self.scheduler)

class CollectionAction(models.Model): # sales
    scheduler = models.ForeignKey(Scheduler, on_delete=models.PROTECT,related_name="scheduler")
    action_by = models.ForeignKey(User, on_delete=models.PROTECT)
    # action_by = models.ForeignKey(ECUser, on_delete=models.PROTECT)
    # action_type = models.CharField(max_length=100,choices=action_types,null=True,blank=True)
    action_type = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="action_type")
    action_date = models.DateTimeField(null=True,blank=True)
    summary = models.TextField(blank=True)
    reference = models.CharField(max_length=100, null=True,blank=True)
    attachment = models.TextField(default="")
    # next_action_type = models.CharField(max_length=100,choices=action_types,null=True,blank=True)
    next_action_type = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="next_action_type")
    next_action_date = models.DateTimeField(null=True,blank=True)
    note = models.TextField(blank=True)
    next_reference = models.CharField(max_length=100, null=True,blank=True)
    next_attachment = models.TextField(default="")
    is_legal_action = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

