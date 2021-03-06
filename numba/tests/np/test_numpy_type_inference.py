import numpy as np

import numba
from numba import *
from numba import typesystem

tup_t = typesystem.TupleType

#------------------------------------------------------------------------
# Test functions
#------------------------------------------------------------------------

@autojit
def array(value):
    return numba.typeof(np.array(value))

@autojit
def nonzero(value):
    return numba.typeof(np.nonzero(value))

@autojit
def where(value):
    return numba.typeof(np.where(value))

@autojit
def where3(value, x, y):
    return numba.typeof(np.where(value, x, y))

@autojit
def numba_dot(A, B):
    result = np.dot(A, B)
    return numba.typeof(result), result

@autojit
def numba_vdot(A, B):
    result = np.vdot(A, B)
    return numba.typeof(result), result

@autojit
def numba_inner(a, b):
    result = np.inner(a, b)
    return numba.typeof(result), result

# ------------- Test sum ------------

@autojit
def sum_(a):
    return numba.typeof(np.sum(a))

@autojit
def sum_axis(a, axis):
    return numba.typeof(np.sum(a, axis=axis))

@autojit
def sum_dtype(a, dtype):
    return numba.typeof(np.sum(a, dtype=dtype))

@autojit
def sum_out(a, out):
    return numba.typeof(np.sum(a, out=out))

@autojit
def add_reduce(a):
    return numba.typeof(np.add.reduce(a))

@autojit
def add_reduce_axis(a, axis):
    return numba.typeof(np.add.reduce(a, axis=axis))


#------------------------------------------------------------------------
# Tests
#------------------------------------------------------------------------

def equals(a, b):
    assert a == b, (a, b, type(a), type(b),
                    a.comparison_type_list, b.comparison_type_list)

def test_array():
    equals(array(np.array([1, 2, 3], dtype=np.double)), float64[:])
    equals(array(np.array([[1, 2, 3]], dtype=np.int32)), int32[:, :])
    equals(array(np.array([[1, 2, 3],
                           [4, 5, 6]], dtype=np.int32).T), int32[:, :])

def test_nonzero():
    equals(nonzero(np.array([1, 2, 3], dtype=np.double)),
           tup_t(npy_intp[:], 1))
    equals(nonzero(np.array([[1, 2, 3]], dtype=np.double)),
           tup_t(npy_intp[:], 2))
    equals(nonzero(np.array((((1, 2, 3),),), dtype=np.double)),
           tup_t(npy_intp[:], 3))

def test_where():
    equals(where(np.array([1, 2, 3], dtype=np.double)),
           tup_t(npy_intp[:], 1))

    equals(where3(np.array([True, False, True]),
                  np.array([1, 2, 3], dtype=np.double),
                  np.array([1, 2, 3], dtype=np.complex128)),
           complex128[:])

    equals(where3(np.array([True, False, True]),
                  np.array([1, 2, 3], dtype=np.float32),
                  np.array([1, 2, 3], dtype=np.int64)),
           float64[:])

def test_numba_dot():
    A = np.array(1)
    B = np.array(2)

    dtype = typesystem.from_numpy_dtype(A.dtype).dtype

    for i in range(1, 10):
        for j in range(1, 10):
            # print i, j

            shape_A = (1,) * i
            shape_B = (1,) * j

            x = A.reshape(*shape_A)
            y = B.reshape(*shape_B)

            result_type, result = numba_dot(x, y)

            assert result == np.dot(x, y)
            if i + j - 2 > 0:
                assert result.ndim == result_type.ndim
            else:
                assert result_type == dtype

def test_numba_vdot():
    for a, b in ((np.array([1+2j,3+4j]),
                  np.array([5+6j,7+8j])),
                 (np.array([[1, 4], [5, 6]]),
                  np.array([[4, 1], [2, 2]]))):
        result_type, result = numba_vdot(a, b)
        assert result == np.vdot(a, b)
        assert result_type == typesystem.from_numpy_dtype(a.dtype).dtype
        result_type, result = numba_vdot(b, a)
        assert result == np.vdot(b, a)
        assert result_type == typesystem.from_numpy_dtype(b.dtype).dtype

def test_numba_inner():
    # Note these tests assume that the lhs' type is the same as the
    # promotion type for both arguments.  They will fail if additional
    # test data doesn't adhere to this policy.
    for a, b in ((np.array([1,2,3]), np.array([0,1,0])),
                 (np.arange(24).reshape((2,3,4)), np.arange(4)),
                 (np.eye(2), 7)):
        result_type, result = numba_inner(a, b)
        if result_type.is_array:
            assert (result == np.inner(a, b)).all()
            assert (result_type.dtype ==
                    typesystem.from_numpy_dtype(result.dtype).dtype)
            assert (result_type.dtype ==
                    typesystem.from_numpy_dtype(a.dtype).dtype)
        else:
            assert result == np.inner(a, b)
            assert result_type == typesystem.from_numpy_dtype(a.dtype).dtype

def test_sum():
    a = np.array([1, 2, 3], dtype=np.int32)
    b = np.array([[1, 2], [3, 4]], dtype=np.int64)

    equals(sum_(a), int32)
    equals(sum_axis(a, 0), int32)
    equals(sum_dtype(a, np.double), double)
    equals(sum_out(b, a), int32[:]) # Not a valid call to sum :)

def test_ufunc_reduce():
    a = np.array([1, 2, 3], dtype=np.int32)
    b = np.array([[1, 2], [3, 4]], dtype=np.int64)

    equals(add_reduce(a), int32)
    equals(add_reduce_axis(b, 1), int64[:])

if __name__ == "__main__":
    test_array()
    test_nonzero()
    test_where()
    test_numba_dot()
    test_numba_vdot()
    test_numba_inner()
    test_sum()
    test_ufunc_reduce()
