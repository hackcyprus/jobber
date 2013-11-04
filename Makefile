.PHONY: clean test

clean-pyc:
	echo 'Cleaning .pyc files'
	$(shell find * -name "*.pyc" | xargs rm -rf)

clean: clean-pyc

test: clean
	py.test tests/ -s