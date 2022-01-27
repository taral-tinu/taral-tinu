from base.models import CodeTable, Currency
from django.db import models

# Create your models here.

class Country(models.Model):#customer
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=5, verbose_name="Code", null=True, blank=True)

class State(models.Model):#customer
    name = models.CharField(max_length=200)
    country = models.ForeignKey(Country, null=True, on_delete=models.PROTECT)
    code = models.CharField(max_length=20, verbose_name="Code", null=True, blank=True)

class Contact(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True)
    ec_contact_id = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)


class Customer(models.Model): # customers
    ec_customer_id = models.IntegerField(null=True, blank=True, verbose_name="EC customer Id")
    company_name = models.CharField(max_length=200, default="")
    # email = models.EmailField(null=True)
    # contact_person = models.CharField(max_length=200, default="")
    # contact_number = models.CharField(max_length=200, default="")
    # country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name="Country", null=True)
    account_manager = models.ForeignKey(Contact, verbose_name="Account manager", blank=True, null=True, on_delete=models.PROTECT)
    account_number = models.CharField(max_length=30, verbose_name="Account number", null=True, help_text="Number assigned by Accounting")
    initials = models.CharField(max_length=30,null=True, blank=True)
    customer_type = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="customer_type",blank=True, null=True)
    tax_number_type = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="taxt_number_type",blank=True, null=True)
    vat_no = models.CharField(max_length=100,blank=True, null=True)
    invoice_prefrence = models.CharField(max_length=100,blank=True, null=True)
    invoice_postage = models.CharField(max_length=100,blank=True, null=True)
    is_sales_review = models.BooleanField(default=False)
    is_vat_verified = models.BooleanField(default=False)
    sa_company_competence = models.CharField(max_length=500,blank=True, null=True)
    sa_ec_customer = models.CharField(max_length=500,blank=True, null=True)
    peppol_address = models.CharField(max_length=500,blank=True, null=True)
    status = models.ForeignKey(CodeTable,on_delete=models.PROTECT,blank=True, null=True)
    last_order_date = models.DateTimeField(blank=True, null=True)
    is_allow_send_mail = models.BooleanField(default=False)
    invoice_lang = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="invoice_language",blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    is_exclude_vat = models.BooleanField(default=False)
    is_deliver_invoice_by_post = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_peppol_verfied = models.BooleanField(default=False)
    is_always_vat = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_student_team = models.BooleanField(default=False)
    is_call_report_attached = models.BooleanField(default=False)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, verbose_name="Currency", null=True,blank=True)
    invoice_delivery = models.ForeignKey(CodeTable,on_delete=models.PROTECT,related_name="invoice_delivery",blank=True, null=True)

    def __str__(self):
        return self.company_name



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
    ec_address_id = models.IntegerField(null=True,blank=True)
    company = models.ForeignKey(Customer, null=True, on_delete=models.PROTECT)
    street_no = models.CharField(max_length=100, default="")
    street_address1 = models.CharField(max_length=300, default="")
    street_address2 = models.CharField(max_length=300, default="")
    postal_code = models.CharField(max_length=40,null=True, blank=True)
    city = models.CharField(max_length=300, null=True, blank=True)
    state = models.ForeignKey(CodeTable, verbose_name="State", null=True, on_delete=models.PROTECT)
    other_state = models.CharField(max_length=100,null=True,blank=True)
    address_name = models.CharField(max_length=200,null=True,blank=True)
    contact_name = models.CharField(max_length=200,null=True,blank=True)
    country = models.ForeignKey(Country, verbose_name="Country", null=True, on_delete=models.PROTECT)
    address_type = models.ForeignKey(CodeTable,null=True, on_delete=models.PROTECT,related_name="address_type")
    email = models.CharField(max_length=200,null=True,blank=True)
    phone = models.CharField(max_length=50,null=True,blank=True)
    fax = models.CharField(max_length=50,null=True,blank=True)
    box_no = models.CharField(max_length=300,null=True, blank=True)
    is_primary = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

