# MotionPlanning
A repository for a demonstration of motion planning based on a trapezoid decomposition of free-space.

## Instructions
To run the GUI interface run
```bash
$ python motion_planning.py
```

This will launch a GUI interface which will guide you through picking (or randomly generating) obstacles and planning a path. The interface additionally has options to do a step-by-step walkthrough for adding individual lines to the trapezoid decomposition.


We run asymptotic analysis on the code performance. We get the expected O(NlogN) runtime for building the trapezoid decomposition and point location datastructure:

We also get O(logN) query time:

For the minkowski sum, we have two algorithms. One runs in O(m + n), we call it `minkowski_sum_fast`. The other `minkowski_sum` runs in O(mn), but is far simpler and runs in 10x the speed.

To run the timer and get the timing results yourself, use the `timer.py` script.

```bash
$ python timer.py --help
usage: timer.py [-h] [--time_trap_building] [--time_trap_querying]
                [--time_minkowski] [--time_minkowski_slow]

optional arguments:
  -h, --help            show this help message and exit
  --time_trap_building  time the trapezoid and point-location building
                        algorithm
  --time_trap_querying  time the trapezoid and point-location query time
  --time_minkowski      time minkowski sum
  --time_minkowski_slow
                        time minkowski O(mn) sum

```
