import unittest

from previz import *

class TestPrevizProject(unittest.TestCase):
    def setUp(self):
        self.p = PrevizProject('https://example.com/api',
                               'aaa',
                               1)
        
    def test_url_elems(self):
        self.assertEqual(self.p.url_elems,
                         {
                             'root': 'https://example.com/api',
                             'project_id': 1
                         })

    def test_headers(self):
        self.assertEqual(self.p.headers,
                         {
                             'Authorization': 'Bearer aaa'
                         })


class TestUtils(unittest.TestCase):
    def test_flat_list(self):
        l = [
            [
                [1, 2, 3],
                [range(4, 6+1), range(7, 9+1)]
            ],
            [
                {
                    (10, 11, 12): 'dummy',
                    13: 'dummy'
                }
            ]
        ]
        self.assertListEqual(flat_list(l),
                             [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

    def test_UuidBuilder(self):
        b = UuidBuilder()
        self.assertEqual(b('SomeString'), b('SomeString'))
        self.assertEqual(b('SomeString'), b('SomeString').upper())
        self.assertNotEqual(b(), b())
