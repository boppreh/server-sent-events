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

    def test_multiple(self):
        p = Publisher()
        s1 = p.subscribe()
        s2 = p.subscribe()
        s3 = p.subscribe()
        p.publish('test')
        p.close()
        self.assertEqual(self.read(s1), 'data: test')
        self.assertEqual(self.read(s2), 'data: test')
        self.assertEqual(self.read(s3), 'data: test')

    def test_channel(self):
        p = Publisher()
        s1 = p.subscribe('channel 1')
        s2 = p.subscribe('channel 2')
        s3 = p.subscribe(['channel 1', 'channel 2'])

        p.publish('test1', 'channel 1')
        p.publish('test2', 'channel 2')
        p.close()

        self.assertEqual(self.read(s1), 'data: test1')
        self.assertEqual(self.read(s2), 'data: test2')
        self.assertEqual(self.read(s3), 'data: test1\n\ndata: test2')

    def test_custom(self):
        p = Publisher()
        s1 = p.subscribe(properties=1)
        s2 = p.subscribe(properties=2)

        p.publish(lambda properties: properties)
        p.close()

        self.assertEqual(self.read(s1), 'data: 1')
        self.assertEqual(self.read(s2), 'data: 2')

    def test_initial_data(self):
        p = Publisher()
        s = p.subscribe(initial_data=['start 1', 'start 2'])
        p.publish('test')
        p.close()
        self.assertEqual(self.read(s),
                         'data: start 1\n\n'
                         'data: start 2\n\n'
                         'data: test')

    def test_multiline(self):
        p = Publisher()
        s = p.subscribe()
        p.publish('line 1\nline 2')
        p.close()
        self.assertEqual(self.read(s), 'data: line 1\ndata: line 2')

if __name__ == '__main__':
    unittest.main()
