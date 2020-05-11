from timing.time_pointlocation import DecompositionCases
from timing.time_query import QueryCases
from timing.time_minkowski import MinkowskiCases
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--time_trap_building", action="store_true", help="time the trapezoid and point-location building algorithm")
parser.add_argument("--time_trap_querying", action="store_true", help="time the trapezoid and point-location query time")
parser.add_argument("--time_minkowski", action="store_true", help="time minkowski sum")

if __name__ == "__main__":
    args = parser.parse_args()
    if args.time_trap_building:
        timer = DecompositionCases()
    elif args.time_trap_querying:
        timer = QueryCases()
    elif args.time_minkowski:
        timer = MinkowskiCases()
    timer.run()

