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
        self.fn_name = None
        self.complexity_name = None

    def run_case(self, timing_case):
        times = []
        difficulty = []
        for i in range(50):
            true_difficulty, inp = self.make_input(timing_case)
            difficulty.append(true_difficulty)
            start = time()
            output = self.func(*inp)
            times.append(time() - start)
        return difficulty, times
    
    def make_input(self, case):
        raise NotImplementedError("Must be implemented by Child Class")

    def complex_fn(self, case):
        raise NotImplementedError("Must be implemented by Child Class")

    def plot_complexity(self, values):
        raise NotImplementedError("Must be implemented by Child Class")
    
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
        plot_complexity = self.plot_complexity(complexity)
        complexity_sorted_indices = np.argsort(plot_complexity)
        complexity = complexity[complexity_sorted_indices]
        plot_complexity = plot_complexity[complexity_sorted_indices]
        complexity_fn = self.complex_fn(complexity)

        case_avgs = np.array(avgs)[complexity_sorted_indices]

        fit_coeffs_avg = np.polyfit(complexity_fn, case_avgs, 1)
        fit_avg = np.poly1d(fit_coeffs_avg)
        plt.scatter(plot_complexity, case_avgs, color='green', label='mean runtime raw')
        plt.plot(plot_complexity, fit_avg(complexity_fn), '--', color='green', label='{} fit to mean'.format(self.complexity_name))

        """
        case_max = np.array(maxes)[complexity_sorted_indices]
        fit_coeffs_max = np.polyfit(complexity_fn, case_max, 1)
        fit_max = np.poly1d(fit_coeffs_max)
        # plt.scatter(complexity, case_medians, color='blue', label='median runtime')
        plt.scatter(plot_complexity, case_max, color='red', label='worst-case runtime raw')
        plt.plot(plot_complexity, fit_max(complexity_fn), '--', color='red', label='{} fit to worst-case'.format(self.complexity_name))
        """
        
        plt.ylim(0, case_avgs.max())
        plt.title("{} Runtime as a Function of Complexity".format(self.fn_name))
        plt.xlabel("Example Complexity")
        plt.ylabel("Runtime")
        plt.legend()
        plt.show()
        plt.close()

    