build:
	pip install -r requirements.txt
start:
	python run.py
integration-test:
	python -m unittest discover -s integration_tests
performance-test:
	python -m unittest performance_tests.setup
	python -m unittest performance_tests.test_performance
cleanup-test:
	python -m unittest cleanup_tests.test_setup
	python -m unittest cleanup_tests.test_publish_receipt
	python -m unittest cleanup_tests.test_cleanup
comment-test:
	python -m unittest comment_tests.test_setup
	kubectl create job --from=cronjob/sdx-collate test-collate
	sleep 5
	python -m unittest comment_tests.test_comments
	kubectl delete job test-collate
