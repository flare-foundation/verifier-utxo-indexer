import time

from django.core.management.base import BaseCommand

from utxo_indexer.indexer import get_indexer_client


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexer = get_indexer_client()

        start_s = time.time()

        index_blocks = range(
            5481872 - 500, 5481872
        )  #  [5463889, 5463890, 5463895, 5,481,872]  # // 2947814, 2947958, 2648059
        for block in index_blocks:
            start = time.time()
            indexer.process_block(block)
            print(f"indexing block {block} took: {time.time() - start}")

        print("All time: ", time.time() - start_s)
