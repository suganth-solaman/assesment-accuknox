from django.db import models


class TriggerModel(models.Model):
    name = models.CharField(max_length=100)

class TransactionProofModel(models.Model):
    created_by_signal = models.BooleanField(default=True)
