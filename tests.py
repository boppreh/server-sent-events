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

    def test_single_multiple(self):
        p = Publisher()
        s1 = p.subscribe()
        s2 = p.subscribe()
        s3 = p.subscribe()
        p.publish('test')
        p.close()
        self.assertEqual(self.read(s1), 'data: test')
        self.assertEqual(self.read(s2), 'data: test')
        self.assertEqual(self.read(s3), 'data: test')

if __name__ == '__main__':
    unittest.main()
