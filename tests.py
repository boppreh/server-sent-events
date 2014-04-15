import unittest
from sse import Publisher

class TestPublisher(unittest.TestCase):
    def read(self, generator):
        return ''.join(generator).strip()

    def test_single(self):
        p = Publisher()
        s = p.subscribe()
        p.publish('test')
        p.close()
        self.assertEqual(self.read(s), 'data: test')

if __name__ == '__main__':
    unittest.main()
