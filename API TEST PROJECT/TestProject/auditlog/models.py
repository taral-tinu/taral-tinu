from django.db import models


# Create your models here.
class UserStateAudit(models.Model):
    username = models.TextField(null=False, blank=False)
    initiated_by = models.TextField(null=False, blank=False)
    start_state = models.TextField(null=False, blank=False)
    end_state = models.TextField(null=False, blank=False)
    datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    ip_address = models.TextField()
