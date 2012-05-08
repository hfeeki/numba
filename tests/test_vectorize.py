#! /usr/bin/env python
# ______________________________________________________________________

from math import sin, pi

from numba.decorators import vectorize
from numba.translate import Translate

from numpy import array, linspace

import sys
import unittest

# ______________________________________________________________________

def sinc(x):
    if x==0.0:
        return 1.0
    else:
        return sin(x*pi)/(pi*x)

# ______________________________________________________________________

@vectorize
def vsinc(x):
    if x==0.0:
        return 1.0
    else:
        return sin(x*pi)/(pi*x)

# ______________________________________________________________________

class TestVectorize(unittest.TestCase):
    def __init__(self, *args, **kws):
        super(TestVectorize, self).__init__(*args, **kws)
        self.vsinc1 = vsinc
        #self.vsinc2 = vectorize(sinc)

    def test_manual_vectorization(self):
        x = linspace(-5,5,1001)
        t = Translate(sinc)
        t.translate()
        vsinc0 = t.make_ufunc()
        y = vsinc0(x)
        self.assertTrue((y == array([sinc(x_elem) for x_elem in x])).all())

    @unittest.skip("Generated ufunc causes segfault")
    def test_decorator(self):
        x = linspace(-5,5,1001)
        y = vsinc(x)
        self.assertTrue((y == array([sinc(x_elem) for x_elem in x])).all())

    @unittest.skip("Generated ufunc causes segfault")
    def test_manual_decoration(self):
        x = linspace(-5,5,1001)
        y = vectorize(sinc)(x)
        self.assertTrue((y == array([sinc(x_elem) for x_elem in x])).all())

# ______________________________________________________________________

def main(*args, **kws):
    unittest.main(*args, **kws)

if __name__ == "__main__":
    main(*sys.argv[1:])

# ______________________________________________________________________
# End of test_vectorize.py