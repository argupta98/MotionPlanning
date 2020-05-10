""" Base class with useful timing functions. """

from time import time
import numpy as np 
import matplotlib.pyplot as plt
from collections import defaultdict

class Timer(object):
    """ Useful timing functions. """
    POLYGON = "polygon"
    def __init__(self, function):
        """
        Args:
            function: The function to time.
        """
        self.func = function

    def run_case(self, timing_case):
        times = []
        difficulty = []
        for i in range(50):
            start = time()
            true_difficulty, inp = self.make_input(timing_case)
            difficulty.append(true_difficulty)
            output = self.func(*inp)
            times.append(time() - start)
        return true_difficulty, times
    
    def make_input(self, case):
        raise NotImplementedError("Must be implemented by Base Class")

    def complex_fn(self, case):
        raise NotImplementedError("Must be implemented by Base Class")
    
    def run_suite(self, cases):
        """ Runs a suite of timing cases and plots the results.
            Assumes that the cases are increasing in complexity."""
        times = []
        complexity = [] 
        i = 0
        for timing_case in cases:
            i += 1
            print("[Timer] Running timing test {}...".format(i))
            true_difficulty, time = self.run_case(timing_case)
            complexity.extend(true_difficulty)
            times.extend(time)

        # Make complexity bins 
        complexity_bins = defaultdict(list)
        for index, value in enumerate(complexity):
           complexity_bins[value].append(times[index])

        avgs = [] 
        maxes = []
        for key, values in complexity_bins.items():
            arr = np.array(values)
            avg = arr.mean()
            max_val = arr.max()
            avgs.append(avg)
            maxes.append(max_val)


        complexity = np.array(complexity_bins.keys())
        complexity_fn = self.complex_fn(complexity)

        case_avgs = np.array(avgs)
        fit_coeffs_avg = np.polyfit(complexity_fn, case_avgs, 1)
        fit_avg = np.poly1d(fit_coeffs_avg)
        plt.scatter(complexity, case_avgs, color='green', label='mean runtime raw')
        plt.plot(complexity, fit_avg(complexity_fn), '--', color='green', label='{} fit to mean'.format(self.complexity_name))


        case_max = np.array(maxes)
        fit_coeffs_max = np.polyfit(complexity_fn, case_max, 1)
        fit_max = np.poly1d(fit_coeffs_max)
        # plt.scatter(complexity, case_medians, color='blue', label='median runtime')
        plt.scatter(complexity, case_max, color='red', label='worst-case runtime raw')
        plt.plot(complexity, fit_max(complexity_fn), '--', color='red', label='{} fit to worst-case'.format(self.complexity_name))
        
        plt.title("{} Runtime as a Function of Complexity".format(self.fn_name))
        plt.xlabel("Example Complexity")
        plt.ylabel("Runtime")
        plt.legend()
        plt.show()
        plt.close()

    