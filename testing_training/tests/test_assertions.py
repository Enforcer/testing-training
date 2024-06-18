import math


def test_builtin_any() -> None:
    # Arrange
    bool_1 = False
    bool_2 = False
    bool_3 = True

    # Act
    result = any([bool_1, bool_2, bool_3])

    # Assert
    ...


def test_addition() -> None:
    # Arrange
    number_1 = 3
    number_2 = 5

    # Act
    total = number_1 + number_2

    # Assert
    ...


def test_adding_to_set() -> None:
    # Arrange
    set_ = {1, 2, 3}

    # Act
    set_.add(4)

    # Assert that 4 is now inside set
    ...


def test_10_times_pi_is_almost_31_using_pytest_approx() -> None:
    # Arrange
    pi = math.pi

    # Act
    result = 10 * pi

    # Assert
    ...


def test_dividing_by_zero() -> None:
    # Arrange
    number = 0

    # Act & Assert
    try:
        number / 0
    except ZeroDivisionError:
        pass
    else:
        assert False, "Expected ZeroDivisionError"
