build:
	pip install -r requirements.txt
start:
	python run.py
test-integration:
	python -m coverage run -m unittest tests/test_all_surveys.py
