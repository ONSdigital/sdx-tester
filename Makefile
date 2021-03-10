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
cleanup-test:
	python -m unittest cleanup_tests.test_setup
	python -m unittest cleanup_tests.test_publish_receipt
	python -m unittest cleanup_tests.test_cleanup
