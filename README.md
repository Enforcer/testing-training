# Testing training

## Prerequisites

- Make sure ports 9090 and 8080 are free (applications used during the training use them)
- Install Python3.12
- Install [Poetry](https://python-poetry.org/)
- Install dependencies and the project using a command
```
poetry install --with=dev
```

## Verify installation

- Run dummy tests using command
```
poetry run pytest
```
This should open Firefox and Chrome, then you should see output similar to
```shell
============================================= test session starts ==============================================
platform darwin -- Python 3.12.1, pytest-7.2.2, pluggy-1.5.0
Using --randomly-seed=4173116174
rootdir: /Users/spb/Projects/bottega/testing-training, configfile: pyproject.toml
plugins: cov-5.0.0, hypothesis-6.103.1, mockito-0.0.4, randomly-3.15.0, Faker-25.8.0, asyncio-0.23.7, anyio-4.4.0, xdist-3.6.1, tavern-2.11.0
asyncio: mode=Mode.STRICT
collected 2 items

testing_training/tests/test_hello_world.py ..                                                            [100%]

============================================== 2 passed in 7.07s ===============================================
```

