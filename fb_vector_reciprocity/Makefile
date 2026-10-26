# Makefile for VectorWing Fan-Shaped Body Connectomics Pipeline
# Hardware baseline: Dell Inspiron 5558 (Core i5-4210U, 8 GB RAM, Ubuntu 24.04 LTS)

VENV_PYTHON := $(wildcard ../.venv/bin/python .venv/bin/python)
PYTHON ?= $(if $(VENV_PYTHON),$(firstword $(VENV_PYTHON)),python3)

.PHONY: all demo test audit validate setup analysis figures reproduce extract clean

all: demo

setup:
	@echo "=== Checking Python Environment and Packages ==="
	@$(PYTHON) -c "import pyarrow, cairo; print('Environment OK: Python, PyArrow, and Cairo available.')"

validate: test audit
	@echo "=== Validation Suite Passed Successfully! ==="

demo:
	@$(PYTHON) demo.py

test:
	@echo "=== Running Full Automated Unit & Algorithmic Test Suite ==="
	@$(PYTHON) -m unittest discover -s tests -v

audit:
	@echo "=== Running Forensic Audit & Stress Tests ==="
	@$(PYTHON) scripts/audit_and_diagnose_mcmc.py
	@$(PYTHON) scripts/stress_test_dynamics.py
	@$(PYTHON) scripts/run_sensitivity_and_controls.py

analysis:
	@echo "=== Running Primary Controlled Study ==="
	@$(PYTHON) scripts/run_fb_controlled_study.py
	@echo "=== Running Continuous Degree k-NN Benchmark ==="
	@$(PYTHON) scripts/run_continuous_degree_model.py
	@echo "=== Running Cellular & Layer Anatomy Mapping ==="
	@$(PYTHON) scripts/analyze_layer_column_anatomy.py
	@echo "=== Running Rate-Based Dynamics Simulation ==="
	@$(PYTHON) scripts/simulate_vector_steering_dynamics.py

figures:
	@echo "=== Rendering Presentation Figures (SVG & PNG) ==="
	@$(PYTHON) scripts/generate_fb_figures.py

reproduce: analysis audit figures test
	@echo "=== Full Reproduction Complete! Running Demo ==="
	@$(PYTHON) demo.py

extract:
	@echo "=== Streaming Raw FAFB v783 Feather Connectome (16.8M rows) ==="
	@$(PYTHON) scripts/extract_fb_subgraph.py --threshold 5

clean:
	@rm -rf __pycache__ scripts/__pycache__ tests/__pycache__
