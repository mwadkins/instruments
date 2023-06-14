SET_PYTHON:=PKW_python3=3.10.2_rel02

TEST_TARGETS:= test_format test_pylint test_pytest

.PHONY: test $(TEST_TARGETS)

test: $(TEST_TARGETS)


PY_FILES:=backend.py tests/test_backend.py
test_pylint: $(PY_FILES)
	pkw_pylint1.7.2 --rcfile ./.pylintrc $^

test_pytest:
	$(SET_PYTHON) coverage run -m pytest -v tests/test_backend.py 
	$(SET_PYTHON) coverage html
	$(SET_PYTHON) coverage report --fail-under 40

test_format: $(PY_FILES)
	$(SET_PYTHON) black --check -l 120 -t py310 .
	$(SET_PYTHON) isort --check -l 120 --profile black --force-sort-within-sections --py 310 .

format: $(PY_FILES)
	$(SET_PYTHON) black -l 120 -t py310 .
	$(SET_PYTHON) isort -l 120 --profile black --force-sort-within-sections --py 310 .

