.PHONY: setup auth api mcp test clean help install-dev

# Definir variáveis
PYTHON = python3
PORT = 8000

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup        - Instala as dependências"
	@echo "  make install-dev  - Instala com todas as dependências de desenvolvimento"
	@echo "  make auth         - Gera um token de atualização OAuth2"
	@echo "  make api          - Inicia o servidor REST API"
	@echo "  make mcp          - Inicia o servidor FastMCP local"
	@echo "  make test         - Executa os testes"
	@echo "  make test-unit    - Executa apenas testes unitários"
	@echo "  make test-cov     - Executa testes com cobertura"
	@echo "  make clean        - Remove arquivos temporários e logs"
	@echo "  make env          - Configura ambiente inicial"
	@echo ""
	@echo "Variáveis:"
	@echo "  PORT              - Porta para o servidor API (padrão: 8000)"

setup:
	$(PYTHON) -m pip install -e .

install-dev:
	$(PYTHON) -m pip install -e ".[dev,test,all]"

auth:
	$(PYTHON) generate_new_token.py

env:
	./scripts/setup_env.sh

test-credentials:
	$(PYTHON) scripts/test_credentials.py

api:
	cd applications/api-server && $(PYTHON) -m uvicorn main:app --reload --port $(PORT)

mcp:
	cd applications/mcp-server && $(PYTHON) fastmcp_server.py

test:
	$(PYTHON) -m pytest

test-unit:
	$(PYTHON) -m pytest -m unit

test-integration:
	$(PYTHON) -m pytest -m integration

test-journeys:
	$(PYTHON) -m pytest -m journeys

test-cov:
	$(PYTHON) -m pytest --cov=packages --cov=applications --cov-report=html --cov-report=term

coverage-report:
	$(PYTHON) scripts/run_coverage_report.py

clean:
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f *.log
	rm -f *.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

lint:
	$(PYTHON) -m flake8 packages/ applications/ tests/

format:
	$(PYTHON) -m black packages/ applications/ tests/

typecheck:
	$(PYTHON) -m mypy packages/ applications/
