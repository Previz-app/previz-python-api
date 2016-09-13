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
