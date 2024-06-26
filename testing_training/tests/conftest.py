from _pytest.config.argparsing import Parser


def pytest_collection_modifyitems(session, config, items):
    for item in items:
        pass


def pytest_addoption(parser: Parser) -> None:
    # Example 1
    parser.addoption(
        "--example", # how it should be used
        action="store",  # what to do? Just save the value
        default="type1",  # default value
        help="my option: type1 or type2",  # help
    )
    # Use: pytest --example type2
    # Retrieve: request.config.getoption("--example") - returns 'type2'

    # Example 2
    parser.addoption(
        "--select",  # how it should be used
        nargs="+",  # what to do? Add all to a list, require at least one
    )
    # Use: pytest --select option1 option2
    # Retrieve: request.config.getoption("--example") - returns ['option1', 'option2']
