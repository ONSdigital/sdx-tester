build:
	pipenv install
start:
	pipenv run python run.py
integration-test:
	pipenv run python -Wi -m unittest discover -s integration_tests
performance-test-setup:
	pipenv run python -m unittest performance_tests.setup
performance-test:
	pipenv run python -m unittest performance_tests.test_performance
cleanup-test:
	pipenv run python -Wi -m unittest cleanup_tests.test_cleanup
comment-test:
	pipenv run python -Wi -m unittest discover -s comment_tests
