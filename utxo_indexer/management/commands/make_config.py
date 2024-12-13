from django.conf import settings
from django.core.management.base import BaseCommand

from utxo_indexer.indexer import get_indexer_client
from utxo_indexer.models.config import Config


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexer = get_indexer_client()
        node_version = indexer._get_network_info(indexer.toplevel_worker)

        Config.objects.update_or_create(
            id=1,
            defaults={
                "node_version": node_version,
                "git_tag": settings.PROJECT_VERSION,
                "git_hash": settings.PROJECT_COMMIT_HASH,
                "build_date": settings.PROJECT_BUILD_DATE.timestamp(),
            },
            create_defaults={
                "node_version": node_version,
                "git_tag": settings.PROJECT_VERSION,
                "git_hash": settings.PROJECT_COMMIT_HASH,
                "build_date": settings.PROJECT_BUILD_DATE.timestamp(),
            },
        )
