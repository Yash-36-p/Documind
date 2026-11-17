from .models import AuditLog

def log_activity(action, user=None, document=None, details=None, request=None):
    """
    Utility helper to log system and user activity consistently.
    """
    user_name = 'System'
    if user and user.is_authenticated:
        user_name = user.get_full_name() or user.username

    ip_address = ''
    user_agent = ''
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '')
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:250]

    document_title = ''
    if document:
        document_title = document.title

    return AuditLog.objects.create(
        user=user if (user and user.is_authenticated) else None,
        user_name=user_name,
        action=action,
        document=document,
        document_title=document_title,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details or {}
    )

