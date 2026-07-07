.PHONY: install dev test lint format api dashboard notebooks
.PHONY: generate-data skill-vocab text-embeddings build-features split-data
.PHONY: train train-smoke evaluate ranking-metrics model-pipeline
.PHONY: export-onnx validate-onnx reports clean

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

dashboard:
	streamlit run app/dashboard.py

notebooks:
	jupyter notebook notebooks

generate-data:
	$(PYTHON) scripts/generate_synthetic_data.py

skill-vocab:
	$(PYTHON) src/features/skill_vectorizer.py

text-embeddings:
	$(PYTHON) src/features/text_embeddings.py

build-features:
	$(PYTHON) src/features/skill_vectorizer.py
	$(PYTHON) src/features/text_embeddings.py
	$(PYTHON) src/features/build_features.py

split-data:
	$(PYTHON) src/data/split_dataset.py

train:
	$(PYTHON) src/models/train.py

train-smoke:
	$(PYTHON) src/models/train.py --epochs 1 --batch-size 512

evaluate:
	$(PYTHON) src/models/evaluate.py

ranking-metrics:
	$(PYTHON) src/models/ranking_metrics.py

export-onnx:
	$(PYTHON) src/models/export_onnx.py

validate-onnx:
	$(PYTHON) src/models/onnx_inference.py

model-pipeline:
	$(PYTHON) src/models/train.py
	$(PYTHON) src/models/evaluate.py
	$(PYTHON) src/models/ranking_metrics.py
	$(PYTHON) src/models/export_onnx.py
	$(PYTHON) src/models/onnx_inference.py

reports:
	$(PYTHON) src/reports/generate_notebooks.py

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -prune -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -prune -exec rm -rf {} +

.PHONY: sandbox-start sandbox-stop sandbox-restart sandbox-test sandbox-clean

sandbox-start:
	bash sandbox_app/scripts/start.sh

sandbox-stop:
	bash sandbox_app/scripts/stop.sh

sandbox-restart:
	bash sandbox_app/scripts/restart.sh

sandbox-test:
	bash sandbox_app/scripts/smoke_test.sh

sandbox-clean:
	bash sandbox_app/scripts/clean_tmp.sh