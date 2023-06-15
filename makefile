# commands I ran to get the tools installed into /usr/local/bin:
# sudo pip3 install pylint
# sudo pip3 install pylint3
# pip install --upgrade pip
# sudo pip3 install black
# sudo pip3 install coverage
# sudo pip3 install pytest

TEST_TARGETS:= test_format test_pylint test_pytest

.PHONY: test $(TEST_TARGETS)

test: $(TEST_TARGETS)

# path to python3,black,isort,pylint tools
BIN:=/Users/landonreese/miniconda3/bin/black

PY_FILES:=backend.py tests/test_backend.py
test_pylint: $(PY_FILES)
	$(BIN)/pylint --rcfile ./.pylintrc $^

test_pytest: $(PY_FILES)
	COVERAGE_FILE=tests/.coverage $(BIN)/coverage run --source=. -m pytest -v tests/test_backend.py 
	COVERAGE_FILE=tests/.coverage $(BIN)/coverage html
	COVERAGE_FILE=tests/.coverage $(BIN)/coverage report --fail-under 90  # require 90% code coverage
 
test_format: $(PY_FILES)
	$(BIN)/black --check -l 120 -t py310 .
	$(BIN)/isort --check -l 120 --profile black --force-sort-within-sections --py 310 .

# use this to autoformat (off by default) useful if make test_format fails
format: $(PY_FILES)
	$(BIN)/black -l 120 -t py310 .
	$(BIN)/isort -l 120 --profile black --force-sort-within-sections --py 310 .

