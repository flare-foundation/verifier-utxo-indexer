from django.test import TestCase

from utxo_indexer.utils import is_valid_bytes_32_hex, un_prefix_0x


class UtilsTest(TestCase):
    def test_un_prefix_0x(self):
        """Test for un_prefix_0x function"""
        string1 = "r43rt34tk34tjok4t4"
        string2 = "0x3rt34tk34tjok4t4"
        self.assertEqual(un_prefix_0x(string1), string1)
        self.assertEqual(un_prefix_0x(string2), "3rt34tk34tjok4t4")

    def test_is_valid_bytes_32_hex(self):
        """Test for is_valid_bytes_32_hex function"""
        string1 = "0123456789abcdef000000000000000000000000000000000000000000000000"
        string2 = "0x0123456789abcdef000000000000000000000000000000000000000000000000"
        string3 = "0123456789abcdef00000000000000000000000000000000000000000000000"
        string4 = "0123456789abcdefg00000000000000000000000000000000000000000000000"
        self.assertEqual(is_valid_bytes_32_hex(string1), True)
        self.assertEqual(is_valid_bytes_32_hex(string2), True)
        self.assertEqual(is_valid_bytes_32_hex(string3), False)
        self.assertEqual(is_valid_bytes_32_hex(string4), False)
