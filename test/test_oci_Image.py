import unittest

from decoap.oci import Image as Image

class TestOciImage(unittest.TestCase):

    def test_invalid_format(self):
        with self.assertRaises(Exception):
            Image("http://invalid.format")

    def test_full(self):
        image = Image("docker.io/library/decoap:latest")
        self.assertEqual(image.registry, "docker.io")
        self.assertEqual(image.scope, "library")
        self.assertEqual(image.name, "decoap")
        self.assertEqual(image.tag, "latest")

    def test_no_exists(self):
        image = Image("doesnotexist.noexist/library/doesnotexist:doesnotexist")
        self.assertFalse(image.exists())

if __name__ == '__main__':
    unittest.main()
