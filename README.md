![Pylint](https://github.com/fornstedt/registercalculator/actions/workflows/pylint.yml/badge.svg)
![Pytest](https://github.com/fornstedt/registercalculator/actions/workflows/pytest.yml/badge.svg)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# Register Calculator

The register calculator is a graphical tool intendend to view and manipulate individual bit fields in a data register. Arbitrary bit fields can be added and a value change in either a field or the main register is reflected everywhere.

![](https://fornstedt.eu/images/github/registercalculator.png)

### Binaries for latest release:
* [RegisterCalculator for MacOS](https://github.com/fornstedt/registercalculator/releases/latest/download/RegisterCalculator_MacOS.zip)
* [RegisterCalculator for Windows](https://github.com/fornstedt/registercalculator/releases/latest/download//RegisterCalculator_Windows.zip)

## Features

* Modify register/field using binary, hexadecimal or decimal values.
* Add any bit range as a new field by selecting the bits in the binary field and click the 'Add field' button.
* Export or import settings using a json-file.
* Choose bit number order, e.g from 31:0 or 0:31
* Choose a register bit size of 8, 16 or 32 bits.
* Swap bytes within the register to handle endianness.
