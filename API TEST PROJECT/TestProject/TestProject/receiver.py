
from auditlog.models import UserStateAudit
from crequest.middleware import CrequestMiddleware
from django.contrib.auth.models import User
from django.dispatch import receiver

from .signals import state_audit_signal


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

@receiver(state_audit_signal)
def user_change_state_signal(sender, **kwargs):
    current_request = CrequestMiddleware.get_request()
    user_id = kwargs['user']
    old_state = kwargs['old_state']
    new_state = kwargs['new_state']
    user = User.objects.get(pk=user_id)
    username = user.username
    initiated_by = current_request.user.username if current_request else 'CLI'
    start_state = old_state
    end_state = new_state
    print("KKKKKKKKKKKKKKKKKK")
    ip = get_client_ip(current_request) if current_request else 'CLI'
    audit = UserStateAudit.objects.create(
        username=username,
        initiated_by=initiated_by,
        start_state=start_state,
        end_state=end_state,
        ip_address=ip
    )
    audit.save()
