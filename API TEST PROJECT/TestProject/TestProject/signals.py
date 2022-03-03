import inspect
import os

from api.models import UserProfile
from django.db.models.signals import post_delete, post_save, pre_save
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


from django.dispatch import Signal

state_audit_signal = Signal(providing_args=["user", "old_state", "new_state"])


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


# @receiver(post_save, sender=CollectionActionReport)
# # @receiver(post_save, sender=OrderLineProductItem)
# def update_on_save(sender, instance, created, **kwargs):
#     """Update order total on lineproductitem and
#     lineticketitem update/create
#     """

#     print('Hello, signals here!',sender._meta,sender)
#     apps = str(sender._meta).split(".")
#     print(apps,"apps")
#     print(instance.id)

#     # if request:
#     #     print(request)
#     # upload("sales", "collectionactionattachment", serializer.data["id"], request.FILES.get("attachment"), None, c_ip, "-", user, False, "")
#     #upload(_app_name, _model_name, _object_id, _docfile, _file_type, _ip_addr, _checksum, _user_id, is_public, source_doc, _name=None, _size=None, doc_type="gen"):

# # works fine and, when called, updates everything accordingly
# @receiver(post_delete, sender=CollectionActionReport)
# # @receiver(post_delete, sender=OrderLineProductItem)
# def update_on_delete(sender, instance, **kwargs):
#     """Update order total on lineproductitem and
#     lineticketitem delete"""

#     print('Hello, signals here!',sender)
#     print(instance.id)
