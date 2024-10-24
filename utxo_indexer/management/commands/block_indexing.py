from django.core.management.base import BaseCommand

from utxo_indexer.indexer import get_indexer_client


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexer = get_indexer_client()
        indexer.run()
