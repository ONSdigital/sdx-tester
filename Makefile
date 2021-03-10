build:
	pip install -r requirements.txt
start:
	python run.py
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
#comment-test:
#	python -m unittest comment_tests.test_setup
#	# Placeholder for triggering cronjob with code
#	python -m unittest comment_tests.test_comments
