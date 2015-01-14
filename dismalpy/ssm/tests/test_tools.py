"""
Tests for tools

Author: Chad Fulton
License: Simplified-BSD
"""
from __future__ import division, absolute_import, print_function

import numpy as np
import pandas as pd

from dismalpy.ssm import tools
# from .results import results_sarimax
from numpy.testing import (
    assert_equal, assert_array_equal, assert_almost_equal, assert_raises,
    assert_raises_regex
)

class TestCompanionMatrix(object):

    cases = [
        (2, np.array([[0,1],[0,0]])),
        ([1,-1,-2], np.array([[1,1],[2,0]])),
        ([1,-1,-2,-3], np.array([[1,1,0],[2,0,1],[3,0,0]]))
    ]

    def test_cases(self):
        for polynomial, result in self.cases:
            assert_equal(tools.companion_matrix(polynomial), result)

class TestDiff(object):

    x = np.arange(10)
    cases = [
        # diff = 1
        ([1,2,3], 1, None, 1, [1, 1]),
        # diff = 2
        (x, 2, None, 1, [0]*8),
        # diff = 1, seasonal_diff=1, k_seasons=4
        (x, 1, 1, 4, [0]*5),
        (x**2, 1, 1, 4, [8]*5),
        (x**3, 1, 1, 4, [60, 84, 108, 132, 156]),
        # diff = 1, seasonal_diff=2, k_seasons=2
        (x, 1, 2, 2, [0]*5),
        (x**2, 1, 2, 2, [0]*5),
        (x**3, 1, 2, 2, [24]*5),
        (x**4, 1, 2, 2, [240, 336, 432, 528, 624]),
    ]

    def test_cases(self):
        # Basic cases
        for series, diff, seasonal_diff, k_seasons, result in self.cases:
            
            # Test numpy array
            x = tools.diff(series, diff, seasonal_diff, k_seasons)
            assert_almost_equal(x, result)

            # Test as Pandas Series
            series = pd.Series(series)

            # Rewrite to test as n-dimensional array
            series = np.c_[series, series]
            result = np.c_[result, result]

            # Test Numpy array
            x = tools.diff(series, diff, seasonal_diff, k_seasons)
            assert_almost_equal(x, result)

            # Test as Pandas Dataframe
            series = pd.DataFrame(series)
            x = tools.diff(series, diff, seasonal_diff, k_seasons)
            assert_almost_equal(x, result)

class TestConcat(object):

    x = np.arange(10)
    
    valid = [
        (((1,2,3),(4,)), (1,2,3,4)),
        (((1,2,3),[4]), (1,2,3,4)),
        (([1,2,3],np.r_[4]), (1,2,3,4)),
        ((np.r_[1,2,3],pd.Series([4])), 0, True, (1,2,3,4)),
        ((pd.Series([1,2,3]),pd.Series([4])), 0, True, (1,2,3,4)),
        ((np.c_[x[:2],x[:2]], np.c_[x[2:3],x[2:3]]), np.c_[x[:3],x[:3]]),
        ((np.c_[x[:2],x[:2]].T, np.c_[x[2:3],x[2:3]].T), 1, np.c_[x[:3],x[:3]].T),
        ((pd.DataFrame(np.c_[x[:2],x[:2]]), np.c_[x[2:3],x[2:3]]), 0, True, np.c_[x[:3],x[:3]]),
    ]

    invalid = [
        (((1,2,3), pd.Series([4])), ValueError),
        (((1,2,3), np.array([[1,2]])), ValueError)
    ]

    def test_valid(self):
        for args in self.valid:
            assert_array_equal(tools.concat(*args[:-1]), args[-1])

    def test_invalid(self):
        for args in self.invalid:
            assert_raises(args[-1], tools.concat, *args[:-1])

class TestIsInvertible(object):

    cases = [
        ([1, -0.5], True),
        ([1, 1-1e-9], True),
        ([1, 1], False),
        ([1, 0.9,0.1], True),
        (np.array([1,0.9,0.1]), True),
        (pd.Series([1,0.9,0.1]), True)
    ]

    def test_cases(self):
        for polynomial, invertible in self.cases:
            assert_equal(tools.is_invertible(polynomial), invertible)

class TestConstrainStationaryUnivariate(object):

    cases = [
        (np.array([2.]), -2./((1+2.**2)**0.5))
    ]

    def test_cases(self):
        for unconstrained, constrained in self.cases:
            result = tools.constrain_stationary_univariate(unconstrained)
            assert_equal(result, constrained)

class TestValidateMatrixShape(object):
    # name, shape, nrows, ncols, nobs
    valid = [
        ('TEST', (5,2), 5, 2, None),
        ('TEST', (5,2), 5, 2, 10),
        ('TEST', (5,2,10), 5, 2, 10),
    ]
    invalid = [
        ('TEST', (5,), 5, None, None),
        ('TEST', (5,1,1,1), 5, 1, None),
        ('TEST', (5,2), 10, 2, None),
        ('TEST', (5,2), 5, 1, None),
        ('TEST', (5,2,10), 5, 2, None),
        ('TEST', (5,2,10), 5, 2, 5),
    ]

    def test_valid_cases(self):
        for args in self.valid:
            # Just testing that no exception is raised
            tools.validate_matrix_shape(*args)

    def test_invalid_cases(self):
        for args in self.invalid:
            assert_raises_regex(
                ValueError, args[0], tools.validate_matrix_shape, *args
            )

class TestValidateVectorShape(object):
    # name, shape, nrows, ncols, nobs
    valid = [
        ('TEST', (5,), 5, None),
        ('TEST', (5,), 5, 10),
        ('TEST', (5,10), 5, 10),
    ]
    invalid = [
        ('TEST', (5,2,10), 5, 10),
        ('TEST', (5,), 10, None),
        ('TEST', (5,10), 5, None),
        ('TEST', (5,10), 5, 5),
    ]

    def test_valid_cases(self):
        for args in self.valid:
            # Just testing that no exception is raised
            tools.validate_vector_shape(*args)

    def test_invalid_cases(self):
        for args in self.invalid:
            assert_raises_regex(
                ValueError, args[0], tools.validate_vector_shape, *args
            )