import unittest

class TestPublisher(unittest.TestCase):
    def test_single(self):
        p = Publisher()
        p.subscribe

if __name__ == '__main__':
    unittest.main()
