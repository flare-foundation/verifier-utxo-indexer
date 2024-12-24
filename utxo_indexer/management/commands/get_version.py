from django.conf import settings
from django.core.management.base import BaseCommand

from configuration.config import config
from utxo_indexer.indexer import get_indexer_client
from utxo_indexer.models.config import Version


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexer = get_indexer_client()
        node_version = indexer._get_network_info(indexer.toplevel_worker)

        Version.objects.update_or_create(
            id=1,
            defaults={
                "node_version": node_version,
                "git_tag": settings.PROJECT_VERSION,
                "git_hash": settings.PROJECT_COMMIT_HASH,
                "build_date": settings.PROJECT_BUILD_DATE.timestamp(),
                "num_confirmations": config.NUMBER_OF_BLOCK_CONFIRMATIONS,
                "history_seconds": config.PRUNE_KEEP_DAYS * 24 * 60 * 60,
            },
            create_defaults={
                "node_version": node_version,
                "git_tag": settings.PROJECT_VERSION,
                "git_hash": settings.PROJECT_COMMIT_HASH,
                "build_date": settings.PROJECT_BUILD_DATE.timestamp(),
                "num_confirmations": config.NUMBER_OF_BLOCK_CONFIRMATIONS,
                "history_seconds": config.PRUNE_KEEP_DAYS * 24 * 60 * 60,
            },
        )
