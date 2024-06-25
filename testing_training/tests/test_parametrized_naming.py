import pytest


# 1. using ids kwarg to parametrize
@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("3+5", 8),
        ("2+4", 6),
        ("6*9", 54)
    ],
    ids=[
        "add 3 and 5",
        "add 2 and 4",
        "multiply 6 by 9"
    ]
)
def test_(test_input, expected):
    result = eval(test_input)
    assert result == expected


# 2. using formatter
def formatter(*args, **kwargs):
    # this function guts SINGLE argument
    # and returns it as a string
    # if it returns None, default formatting is preserved
    # could be also written as:
    # def formatter(arg):
    #     return f"argument {arg}"
    return f"arg is {args[0]} "


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("3+5", 8),
        ("2+4", 6),
        ("6*9", 54)
    ],
    ids=formatter
)
def test_2(test_input, expected):
    result = eval(test_input)
    assert result == expected


# pytest.param
@pytest.mark.parametrize(
    "test_input, expected",
    [
        pytest.param("3+5", 8, id="add 3 and 5"),
        pytest.param("2+4", 6, id="add 2 and 4"),
        pytest.param("6*9", 54, id="multiply 6 by 9"),
    ]
)
def test_3(test_input, expected):
    result = eval(test_input)
    assert result == expected
