default: build test

.PHONY: build
build:
	pip install -e .

.PHONY: test
test:

.PHONY: clean
clean:
	true