import threading
from signals_app import signals
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import TriggerModel, TransactionProofModel
from .rectangle import Rectangle


def _reset_signal_state():
    """Reset module-level state used by signal demos."""
    signals.execution_order.clear()
    signals.receiver_thread_id = None


class ProofSynchronousView(APIView):
    """
    Q1: Prove signals run synchronously.
    If they were async, the receiver would run later and "receiver_ran" would
    not appear between "before_save" and "after_save".

    Answer: Synchronously. Django default behavior is to run signals synchronously.
    Proof: We append 'before_save', then save (which runs the receiver), then 'after_save'.
    If async, receiver would run later and order would be before_save, after_save, receiver_ran.

    """

    def get(self, request):
        _reset_signal_state()
        signals.execution_order.append("before_save")
        TriggerModel.objects.create(name="sync_demo")
        signals.execution_order.append("after_save")

        return Response({
            "execution_order": list(signals.execution_order),
        })


class ProofSameThreadView(APIView):
    """
    Q2: Prove signals run in the same thread as the caller.

    Answer: Yes. We compare threading.current_thread().ident in the view vs in the receiver.
    example:
        "caller_thread_id": 139949697398336,
        "receiver_thread_id": 139949697398336
    """

    def get(self, request):
        _reset_signal_state()
        caller_thread_id = threading.current_thread().ident
        TriggerModel.objects.create(name="thread_demo")

        rec_tid = signals.receiver_thread_id

        return Response({
            "caller_thread_id": caller_thread_id,
            "receiver_thread_id": rec_tid,
        })


class ProofSameTransactionView(APIView):
    """
    Q3: Prove signals run in the same database transaction as the caller.
    We start a transaction, save a model (receiver creates another row), then raise.
    After rollback, both tables must have no new rows.

    Answer: Yes.
    Proof: Inside transaction.atomic() we save TriggerModel (receiver creates TransactionProofModel),
    then we raise to rollback. If signal ran in a different transaction, TransactionProofModel would still have a row.
    """

    def get(self, request):

        TriggerModel.objects.filter(name="transaction_demo").delete()
        TransactionProofModel.objects.all().delete()

        try:
            with transaction.atomic():
                TriggerModel.objects.create(name="transaction_demo")
                # Receiver already ran and created a TransactionProofModel
               
                raise Exception("intentional_rollback")
        except Exception:
            pass

        trigger_count = TriggerModel.objects.filter(name="transaction_demo").count()
        proof_count = TransactionProofModel.objects.count()

        return Response({
            
            "after_rollback_trigger_count": trigger_count,
            "after_rollback_proof_count": proof_count,
        })


class RectangleDemoView(APIView):
    """
    Demonstrate Rectangle:
    - init with length/width (int)
    - iteration yields length then width.
    """

    def get(self, request):
        request_length = request.GET.get("length", 5)
        request_width = request.GET.get("width", 3)
        rect = Rectangle(length=int(request_length), width=int(request_width))
        collection = []
        iterator = rect.dimensions_generator()
        collection.append(next(iterator))
        collection.append(next(iterator))
        return Response({
            "collection": collection,
        })
