from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class CodeTable(models.Model):
    parent = models.ForeignKey("self", on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=100,null=True,blank=True)
    code = models.CharField(max_length=100,unique=True)
    desc = models.TextField()
    is_deleted = models.BooleanField(default=False)


class Currency(models.Model):

    name = models.CharField(max_length=40, null=False, verbose_name="Currency name")
    symbol = models.CharField(max_length=3, null=False, verbose_name="Currency symbol")
    is_base = models.BooleanField(default=False, verbose_name="Base currency")
    is_deleted = models.BooleanField(verbose_name="Deleted")

    def __str__(self):
        return "%s" % (self.name)

class CurrencyRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, null=False, related_name="currency")
    factor = models.DecimalField(null=False, max_digits=10, decimal_places=3, verbose_name="Currency factor")
    reference_date = models.DateTimeField(verbose_name="Reference date", null=False)
    expire_date = models.DateTimeField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT)

class SysParameter(models.Model):
    para_code = models.CharField(max_length=60, verbose_name="Parameter code", null=False)
    descr = models.CharField(max_length=250, verbose_name="Description", null=True, blank=True)
    para_value = models.CharField(max_length=1000, verbose_name="Parameter value", null=False, blank=True)
    para_group = models.CharField(max_length=30, verbose_name="Parameter Group", null=True, blank=True)
    for_system = models.BooleanField(default=True)
