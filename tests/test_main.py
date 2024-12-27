# TODO: Intialize tests for pytest


def my_func():
    return [1, 2, 3]


def test_pytest():
    expected_values = [1, 2, 3]
    actual_values = my_func()
    assert expected_values == actual_values
