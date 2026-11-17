import logging
from django.conf import settings
from .tasks import process_document_task, run_document_processing

logger = logging.getLogger(__name__)

def queue_document_processing(document_id: str, async_mode: bool = True):
    """
    Intelligently dispatch processing:
    Tries Celery background task first. If Celery/Redis broker is not reachable
    or settings.CELERY_TASK_ALWAYS_EAGER is True, runs synchronously without failing.
    """
    if getattr(settings, 'CELERY_TASK_ALWAYS_EAGER', False) or not async_mode:
        return run_document_processing(document_id)

    try:
        # Try sending to Celery worker
        task = process_document_task.delay(document_id)
        return task.id
    except Exception as e:
        logger.warning(f"Could not dispatch to Celery broker ({e}). Falling back to in-process execution.")
        return run_document_processing(document_id)
