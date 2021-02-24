build:
	pip install -r requirements.txt
start:
	python run.py
test:
	python -m unittest
integration-test:
	python -m unittest discover -s integration_tests
setup-performance:
	python -m unittest performance_tests.setup
performance-test:
	python -m unittest performance_tests.test_performance