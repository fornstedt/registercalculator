"""Script to run the RegisterCalculator package"""

import sys
from registercalculator import RegisterCalculator


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_window = RegisterCalculator(sys.argv[1])
    else:
        main_window = RegisterCalculator()

    main_window.show()
