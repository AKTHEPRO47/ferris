import unittest
import numpy as np
from science.advanced import bh_adjust,hac_trend,kalman_step
class AdvancedTests(unittest.TestCase):
    def test_bh_reference(self):
        np.testing.assert_allclose(bh_adjust([.01,.04,.03]),[.03,.04,.04])
    def test_paired_contrast(self):
        years=np.arange(20)
        shared=np.sin(years)
        first=2*years+shared
        second=-years+shared
        self.assertAlmostEqual(hac_trend(years,first-second)["slope"],3)
    def test_constant_contrast(self):
        result=hac_trend(np.arange(20),np.zeros(20))
        self.assertEqual(result["p"],1)
    def test_kalman_covariance(self):
        updated,covariance,_,_=kalman_step(np.zeros(2),np.eye(2),np.array([1.,2.]),.7*np.eye(2),.2*np.eye(2),.1*np.eye(2))
        self.assertTrue(np.all(np.linalg.eigvalsh(covariance)>0))
        self.assertTrue(np.all(updated>0))
