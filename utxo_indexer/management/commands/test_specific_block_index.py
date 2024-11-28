import time

from django.core.management.base import BaseCommand

from utxo_indexer.indexer import get_indexer_client


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexer = get_indexer_client()

        start_s = time.time()

        index_blocks = [5463889, 5463890, 5463895, 5463900]  # // 2947814, 2947958, 2648059
        for block in index_blocks:
            start = time.time()
            print(f"indexing block {block}")

            indexer.process_block(block)
            print("Out: ", time.time() - start)

        print("All time: ", time.time() - start_s)
