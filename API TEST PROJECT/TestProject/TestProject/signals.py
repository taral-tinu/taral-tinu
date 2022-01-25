import os

from api.models import UserProfile
from django.db.models.signals import pre_save
from django.dispatch import Signal, receiver

# auditlog_signal = Signal(providing_args=["app_name", "model_name", "object_ids", "action_id", "action_by_id", "ip_addr", "descr"])

@receiver(pre_save,sender=UserProfile)
def delete_old_file(sender, instance, **kwargs):
    if instance._state.adding and not instance.pk:
        return False
    try:
        old_file = sender.objects.get(pk=instance.pk).profile_image
    except sender.DoesNotExist:
        return False
    file = instance.profile_image
    if not old_file == file:
        if old_file:
            if os.path.isfile(old_file.path):
                os.remove(old_file.path)

# pre_save.connect(delete_old_file, sender=UserProfile)


# class DeleteOldFile():

#=================comman class for delete unwanted file data ====================#

# def deletefile(action,model,obj):
#     @receiver(action,sender=model)
#     def delete_old_file(sender, instance, **kwargs):
#         if instance._state.adding and not instance.pk:
#             return False
#         try:
#             old_file = sender.objects.get(pk=instance.pk)
#             old_file = getattr(old_file, obj)

#         except sender.DoesNotExist:
#             return False
#         # file = instance.profile_image
#         file = getattr(instance, obj)

#         if not old_file == file:
#             if old_file:
#                 if os.path.isfile(old_file.path):
#                     os.remove(old_file.path)
# deletefile(pre_save,UserProfile,'profile_image')


#========================= log history ================================
