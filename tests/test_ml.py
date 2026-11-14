import unittest
import numpy as np
from science.train_ml import train, fit, predict

class ModelTests(unittest.TestCase):
    def records(self):
        dates=[f"{2001+i//12}-{i%12+1:02}" for i in range(300)]
        t=np.arange(300)
        return 26+np.sin(t/6)+t*.002, 6+np.cos(t/3), dates
    def test_test_targets_do_not_affect_fit_or_selection(self):
        temp,rain,dates=self.records()
        a=train(temp,rain,"Test",dates)
        temp[240:]+=20
        b=train(temp,rain,"Test",dates)
        for x,y in zip(a,b):
            for key in ["weights","mean","scale","alpha","intercept","candidates"]:
                self.assertEqual(x[key],y[key])
            self.assertEqual(x["training_count"],228)
            self.assertEqual(x["test_count"],60)
    def test_exported_prediction_matches_holdout(self):
        temp,rain,dates=self.records()
        for m in train(temp,rain,"Test",dates):
            for sample in m["test"]:
                self.assertAlmostEqual(float(predict(m,np.array(sample["inputs"]))),sample["predicted"],places=10)
    def test_invalid_records_rejected(self):
        temp,rain,dates=self.records()
        temp[0]=np.nan
        with self.assertRaises(ValueError): train(temp,rain,"Test",dates)
if __name__=="__main__": unittest.main()
