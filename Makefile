.PHONY: check format dev-check install

# install:
# 	python3 -m venv myenv
# 	source ./myenv/bin/activate
# 	pip install -r requirements.txt
# 	pip install black flake8 semgrep

# Only check style
check:
	ruff check src/

# Format
format:
	ruff format src/ && isort src/

dev-check:
	@grep -q "dev=True" src/shared.py && (echo "❌ dev=True found!" && exit 1) || echo "✅ OK"