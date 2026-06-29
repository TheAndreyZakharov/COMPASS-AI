.PHONY: install dev test lint format api notebooks train export-onnx reports generate-data build-features evaluate clean

PYTHON := python
PIP := pip

install:
	$(PIP) install -r requirements.txt

dev:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test:
	pytest

lint:
	ruff check src app scripts tests
	mypy src app scripts

format:
	black src app scripts tests
	ruff check src app scripts tests --fix

api:
	uvicorn app.api:app --reload --host 0.0.0.0 --port 8000

notebooks:
	jupyter notebook notebooks

generate-data:
	$(PYTHON) scripts/generate_synthetic_data.py

build-features:
	$(PYTHON) src/features/build_features.py

train:
	$(PYTHON) src/models/train.py

evaluate:
	$(PYTHON) src/models/evaluate.py

export-onnx:
	$(PYTHON) src/models/export_onnx.py

reports:
	$(PYTHON) src/reports/generate_notebooks.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +