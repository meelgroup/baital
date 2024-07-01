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

    def test_d4(self):
        self.assertTrue(os.path.exists("../bin/d4"), "d4 not found in ../bin/")

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
    

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_sampling_waps(self, mock_stdout):
        papprx = True
        apprx = False
        preprocess = False
        waps = True
        baital.run("test.cnf", 5, 2, 9, None, None, 3, "results/", "", True, "", papprx, 0.25, 0.25, 2, "", False, "", apprx, 0.05, 0.05, preprocess, waps, False)
        self.assertEqual(mock_stdout.getvalue().strip().split('\n')[-1], "(Approximate) number of combinations 376", "Baital sampling with waps failed")
         
if __name__ == '__main__':
    unittest.main()
