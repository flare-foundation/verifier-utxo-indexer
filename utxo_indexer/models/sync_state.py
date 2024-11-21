import time

from django.db import models


class TipSyncStateChoices(models.TextChoices):
    created = "created", "Created"
    syncing = "sync", "Syncing"
    up_to_date = "up_to_date", "Up to date"
    error = "error", "Error"


class TipSyncState(models.Model):
    TIP_STATE_ID = 1

    sync_state = models.CharField(max_length=10, choices=TipSyncStateChoices.choices)
    latest_tip_height = models.PositiveIntegerField()
    latest_indexed_height = models.PositiveIntegerField()

    # timestamp of latest update
    timestamp = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"Sync state: {self.sync_state} - latest tip height: {self.latest_tip_height} - latest indexed height: {self.latest_indexed_height}"

    @classmethod
    def instance(cls):
        _instance, _ = cls.objects.get_or_create(
            pk=cls.TIP_STATE_ID,
            defaults={
                "sync_state": TipSyncStateChoices.created,
                "latest_tip_height": 0,
                "latest_indexed_height": 0,
                "timestamp": int(time.time()),
            },
        )
        return _instance


class PruneSyncState(models.Model):
    TIP_STATE_ID = 1

    latest_indexed_tail_height = models.PositiveIntegerField()

    # timestamp of latest update
    timestamp = models.PositiveIntegerField()

    def __str__(self) -> str:
        return f"Tail pruning state: bottom indexed height: {self.latest_indexed_tail_height} (at {self.timestamp})"

    @classmethod
    def instance(cls):
        _instance, _ = cls.objects.get_or_create(
            pk=cls.TIP_STATE_ID,
            defaults={
                "latest_indexed_tail_height": 0,
                "timestamp": int(time.time()),
            },
        )
        return _instance
