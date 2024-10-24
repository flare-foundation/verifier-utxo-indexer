from django.core.management.base import BaseCommand

from utxo_indexer.indexer import get_indexer_client


class Command(BaseCommand):
    def handle(self, *args, **options):
        indexer = get_indexer_client()

        # start = time.time()
        # # Biggest doge block
        # indexer.process_block(4738722)
        # print("Out: ", time.time() - start)

        index_blocks = [2648059]  # // 2947814, 2947958, 2648059
        for block in index_blocks:
            print(f"indexing block {block}")

            indexer.process_block(block)
