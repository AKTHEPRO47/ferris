import unittest
from science.analyze import analyze
class Tests(unittest.TestCase):
    def test_slope(self): self.assertAlmostEqual(analyze([1,2,3,4,5],[2,4,6,8,10])["slope"],2)
    def test_constant(self): self.assertEqual(analyze([1,2,3,4],[2,2,2,2])["p"],1)
    def test_missing(self): self.assertEqual(analyze([1,2,3,4,5],[1,None,3,4,5])["missing"],1)
    def test_small(self):
        with self.assertRaises(ValueError): analyze([1,2],[1,2])
    def test_duplicate(self):
        with self.assertRaises(ValueError): analyze([1,1,2,3],[1,2,3,4])
