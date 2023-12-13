import numpy as np
from scipy.stats import norm

from statsmodels.sandbox.stats.runs import runstest_1samp

def runstest(seq: np.array):
    """

    :param seq: an one dim array
    :return: Pval
    """
    binary_sequence = [1 if x >= 0 else 0 for x in np.diff(seq)]

    n1 = sum(binary_sequence)
    n2 = len(binary_sequence) - n1

    mu = 2*n1*n2/(n1+n2) + 1
    sigma = np.sqrt((2*n1*n2*(2*n1*n2-n1-n2))/(((n1+n2)**2)*(n1+n2-1)))

    def count_runs(binary_sequence):
        """
        Count the number of runs in a binary sequence.
        A run is a sequence of adjacent elements with the same value.
        """
        runs = 1  # Start with 1 because the first element always starts a new run
        for i in range(1, len(binary_sequence)):
            if binary_sequence[i] != binary_sequence[i - 1]:
                runs += 1
        return runs

    if len(binary_sequence) < 20:
        z = count_runs(binary_sequence)
    else:
        z = (count_runs(binary_sequence) - mu) / sigma


    pVal = 2*norm.cdf(-abs(z))

    return  pVal

seq = np.array([1,2,3,4,5,6,7,84,3,21,3,4,5,6,4,21,2,4,5,7,5,2,12,312,32,3,4,5,6])
seq = np.array([1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1])

print(runstest(seq))
print(runstest_1samp(seq))

