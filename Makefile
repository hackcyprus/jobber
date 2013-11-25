.PHONY: clean test test-unit test-integration

clean-pyc:
	echo 'Cleaning .pyc files'
	$(shell find * -name "*.pyc" | xargs rm -rf)

clean: clean-pyc

test: clean
	coverage run --source jobber -m py.test -s
	coverage report -m

test-unit: clean
	coverage run --source jobber -m py.test unit/ -s
	coverage report -m

test-integration: clean
	coverage run --source jobber -m py.test integration/ -s
	coverage report -m