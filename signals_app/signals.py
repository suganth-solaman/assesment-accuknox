import threading
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TriggerModel, TransactionProofModel


execution_order = []
receiver_thread_id = None

@receiver(post_save, sender=TriggerModel)
def trigger_model_post_save(sender, instance, created, **kwargs):
    execution_order.append("receiver_ran")

    global receiver_thread_id
    receiver_thread_id = threading.current_thread().ident

    TransactionProofModel.objects.create(created_by_signal=True)
