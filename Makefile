default: build test

.PHONY: build
build:
	python ./setup.py build develop;
.PHONY: test
test:

.PHONY: clean
clean:
