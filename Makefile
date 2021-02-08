build:
	pip install -r requirements.txt
start:
	python run.py
test:
	python -m unittest
test-good:
	python -m coverage run -m unittest test/test_all_surveys.py
test-routes:
	python -m coverage run -m unittest test/test_routes.py