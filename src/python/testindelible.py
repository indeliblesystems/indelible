import indelible_log
import indelible_log.crypto
from base64 import standard_b64decode, standard_b64encode
import json
import unittest

class ValueTransformer(unittest.TestCase):

    def test_raw_mode(self):
        self.assertEqual(
            indelible_log.value_transformer("raw", key = None).encode("nonbase64;&"),
            "nonbase64;&")
        self.assertEqual(
            indelible_log.value_transformer("raw", key = None).decode("nonbase64;&"),
            "nonbase64;&")

    def test_json_mode(self):
        self.assertEqual(
            indelible_log.value_transformer("json", key = None).encode({"a":123}),
            "eyJhIjogMTIzfQ==")
        self.assertEqual(
            indelible_log.value_transformer("json", key = None).decode("eyJhIjogMTIzfQ=="),
            {"a":123})

    def test_string_mode(self):
        self.assertEqual(
            indelible_log.value_transformer("string", key = None).encode("foo"),
            "Zm9v")
        self.assertEqual(
            indelible_log.value_transformer("string", key = None).decode("Zm9v"),
            "foo")

    def test_binary_mode(self):
        self.assertEqual(
            indelible_log.value_transformer("binary", key = None).encode(b"foo"),
            "Zm9v")
        self.assertEqual(
            indelible_log.value_transformer("binary", key = None).decode("Zm9v"),
            b"foo")

test_key = standard_b64decode("UdHBz8klP8ze+cl+qP2zcFBOW952mo8DUc/tn59h6Rw=")
class Encryption(unittest.TestCase):

    def test_nonce(self):
        self.assertEqual(
            indelible_log.crypto.nonce(b"asdf" + test_key, indelible_log.crypto.encrypt_nonce_len),
            standard_b64decode("DuO9oCKfeLUrcIImvVH88Y67un3CFnRw"))

    def test_derive_key(self):
        self.assertEqual(
            indelible_log.crypto.derive_key(test_key, b"foo"),
            standard_b64decode("om8Kwi0iNWWfEcPcZcjVWA3WeV+vvLTj7NPM3yMvzpc="))

    def test_encrypt(self):
        self.assertEqual(
            standard_b64encode(indelible_log.crypto.encrypt(test_key, b"asdf")),
            b"DuO9oCKfeLUrcIImvVH88Y67un3CFnRwhZOvsmKMKFjTuKYsiLv0bwSBbjo=")

    def test_decrypt(self):
        self.assertEqual(
            indelible_log.crypto.decrypt(test_key, standard_b64decode("DuO9oCKfeLUrcIImvVH88Y67un3CFnRwhZOvsmKMKFjTuKYsiLv0bwSBbjo=")),
            b"asdf")

class PathEncoding(unittest.TestCase):

    def test_name_encoding_string(self):
        self.assertEqual(
            indelible_log.encode_name(
                name = json.dumps(["walkthrough", "Hello, World!", "v2"]),
                name_mode = "string"),
            b"""["walkthrough", "Hello, World!", "v2"]""")

    def test_name_encoding_raw(self):
        self.assertEqual(
            indelible_log.encode_name(
               name = b"WyJ3YWxrdGhyb3VnaCIsICJIZWxsbywgV29ybGQhIiwgInYyIl0=",
               name_mode = "raw"),
            b"WyJ3YWxrdGhyb3VnaCIsICJIZWxsbywgV29ybGQhIiwgInYyIl0=")

    def test_name_encoding_stringlist(self):
        self.assertEqual(
            standard_b64encode(
                indelible_log.encode_name(
                    name = ["walkthrough", "Hello, World!", "v2"],
                    name_mode = "stringlist")),
            b"AXdhbGt0aHJvdWdoAEhlbGxvLCBXb3JsZCEAdjIA")

if __name__ == "__main__":
    unittest.main()
