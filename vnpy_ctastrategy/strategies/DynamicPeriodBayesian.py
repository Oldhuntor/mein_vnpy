"""
Sometimes if the long term period is a fixed number, when it encounters a short fluctuation
It would be broken down into different kinds of scenarios
example:
[++++ --- +++++] is different from [+++++++++ ---]
so we should take the repetitive pattern into consideration
the first one is 4 + 3 + 5 , the second one is 9 + 3
although they has the same prior probability but info they contain is different

method:
* 1
we use the mean value of repetitive pattern
4 + 3 + 5 / 3 = 4

9 + 3 / 2 = 6

if the mean value is higher we assign a more higher signal

* 2 Maybe we can use run test?

when the run test P value is smaller than a thershold

and when they P value is above 0.05, close position
"""

from queue import Queue

myQueue = Queue(10)