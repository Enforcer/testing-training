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
This should open Firefox and Chrome, then you should see output

