import unittest
import unittest.mock
import importlib.util
import baital
import baital_nf
import os
import utils
import random
import numpy as np
import io

class TestInstall(unittest.TestCase):

    #Common parameters
    #cnffile = "test.cnf"
    #smtfile = "test.smt"
    #strategy = 5
    #twise = 2
    #samples = 9
    #descoverage = None
    #spr = None
    #rounds = 3
    #outputdir = "results/"
    #outputfile = ""
    #outputfile1 = ""
    #outputfile2 = ""
    #nocomb = True 
    #combfile = ""
    #pdelta = 0.25
    #pepsilon = 0.25
    #funcnumber =2 
    #rescombfile = ""
    #nosampling = False
    #externalsamplefile = ""
    #epsilon = 0.05
    #delta = 0.05
    #generateMoreSamples = False

    def test_cmsgen(self):
        self.assertIsNotNone(importlib.util.find_spec("pycmsgen"), "pycmsgen not found")
        
    def test_approxmc(self):
        self.assertIsNotNone(importlib.util.find_spec("pyapproxmc"), "pyapproxmc not found") 
        
    def setUp(self):
        np.random.seed(1)
        random.seed(1)
        if not os.path.exists("results/"):
            os.makedirs("results/")
        
    def tearDown(self):
        utils.rmfile('results/test_2.comb')
        utils.rmfile('results/test_2.acomb')
        utils.rmfile('results/test_1.comb')
        utils.rmfile('results/test.nsamples')
        utils.rmfile('results/test.rsamples')
        utils.rmfile('results/test.samples')
        utils.rmfile('test.cnf.nnf')        
    
    def test_baital_preprocess(self):  
        papprx = False
        apprx = False
        preprocess = True
        waps = False
        baital.run("test.cnf", 5, 2, 9, None, None, 3, "results/", "", True, "", papprx, 0.25, 0.25, 2, "", False, "", apprx, 0.05, 0.05, preprocess, waps, False)
        self.assertTrue(os.path.exists('results/test_2.comb'), "Preprocess failed: result file not found")
        with open('results/test_2.comb') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 402, "Preprocess failed: wrong number of combinations")

    def test_baital_preprocess_approx(self):
        papprx = True
        apprx = False
        preprocess = True
        waps = False
        baital.run("test.cnf", 5, 2, 9, None, None, 3, "results/", "", True, "", papprx, 0.25, 0.25, 2, "", False, "", apprx, 0.05, 0.05, preprocess, waps, False)
        self.assertTrue(os.path.exists('results/test_2.acomb'), "Approximate preprocess failed: result file not found")
        with open('results/test_2.acomb') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 35, "Approximate preprocess failed: wrong number of lines")
            self.assertEqual(lines[-1].strip(), "-17 19", "Approximate preprocess failed: wrong number of combinations")


    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_sampling(self, mock_stdout):
        papprx = True
        apprx = False
        preprocess = False
        waps = False
        baital.run("test.cnf", 5, 2, 9, None, None, 3, "results/", "", True, "", papprx, 0.25, 0.25, 2, "", False, "", apprx, 0.05, 0.05, preprocess, waps, False)
        self.assertEqual(mock_stdout.getvalue().strip().split('\n')[-1], "(Approximate) number of combinations 363", "Baital sampling failed")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_approx_count(self, mock_stdout):
        papprx = False
        apprx = True
        preprocess = False
        waps = False
        baital.run("test.cnf", 5, 2, 9, None, None, 3, "results/", "", False, "", papprx, 0.25, 0.25, 2, "", False, "", apprx, 0.05, 0.05, preprocess, waps, False)
        self.assertEqual(mock_stdout.getvalue().strip().split('\n')[-1], "(Approximate) 2-wise coverage 0.9029850746268657", "Approximate coverage failed")
        
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_nf(self, mock_stdout):        
        papprx = True
        apprx = False
        preprocess = False
        waps = False
        seed = 1
        np.random.seed(1)
        random.seed(1)
        baital_nf.run("test.smt", 5, 2, 9, None, None, 3, "results/", "", "", True, "", papprx, 0.25, 0.25, 2, "", False, "", apprx, 0.05, 0.05, preprocess, waps, False, seed)
        self.assertEqual(mock_stdout.getvalue().strip().split('\n')[-1], "(Approximate) number of combinations 1567", "Baital_nb test failed")
        
if __name__ == '__main__':
    unittest.main()
