build:
	pipenv install
start:
	pipenv run python run.py
integration-test:
	pipenv run python -Wi -m unittest discover -s integration_tests
eqv3-integration-test:
	pipenv run python -Wi -m unittest discover -s eqv3_integration_tests
performance-test-setup:
	pipenv run python -m unittest performance_tests.setup
performance-test:
	pipenv run python -m unittest performance_tests.test_performance
cleanup-test:
	pipenv run python -Wi -m unittest cleanup_tests.test_cleanup
comment-test:
	pipenv run python -Wi -m unittest comment_tests.test_comments
daily-comment-test:
	pipenv run python -Wi -m unittest comment_tests.test_daily
