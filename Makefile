test:
	python -m pytest tests/ -v --ignore=tests/integration

test-integration:
	python -m pytest tests/integration/ -v -m integration

test-all:
	python -m pytest tests/ -v

backtest:
	python main.py --backtest
