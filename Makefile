.PHONY: setup auth api mcp mcp-http test clean help install-dev inspector inspector-cli inspector-http

# Definir variáveis
PYTHON = python3
PORT = 8000
MCP_PORT = 8080

help:
	@echo "Comandos disponíveis:"
	@echo "  make setup        - Instala as dependências"
	@echo "  make install-dev  - Instala com todas as dependências de desenvolvimento"
	@echo "  make auth         - Gera um token de atualização OAuth2"
	@echo "  make api          - Inicia o servidor REST API"
	@echo "  make mcp          - Inicia o servidor FastMCP local (stdio)"
	@echo "  make mcp-http     - Inicia o servidor FastMCP com HTTP transport"
	@echo "  make test         - Executa os testes"
	@echo "  make test-unit    - Executa apenas testes unitários"
	@echo "  make test-cov     - Executa testes com cobertura"
	@echo "  make clean        - Remove arquivos temporários e logs"
	@echo "  make env          - Configura ambiente inicial"
	@echo ""
	@echo "MCP Inspector:"
	@echo "  make inspector      - Abre MCP Inspector UI (modo interativo)"
	@echo "  make inspector-cli  - Executa testes CLI automatizados"
	@echo "  make inspector-http - Testa servidor HTTP com Inspector"
	@echo ""
	@echo "Automated MCP Tests:"
	@echo "  make test-mcp       - Run automated MCP server tests"
	@echo "  make test-mcp-quick - Quick smoke tests (metadata only)"
	@echo "  make test-mcp-full  - Full tests with report generation"
	@echo "  make test-mcp-cloud - Include Cloud Run tests"
	@echo "  make test-mcp-pytest - Run pytest integration tests"
	@echo ""
	@echo "Variáveis:"
	@echo "  PORT              - Porta para o servidor API (padrão: 8000)"
	@echo "  MCP_PORT          - Porta para o servidor MCP HTTP (padrão: 8080)"

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
	cd applications/mcp-server && $(PYTHON) main.py

mcp-http:
	cd applications/mcp-server && MCP_TRANSPORT=http MCP_AUTH_ENABLED=false MCP_PORT=$(MCP_PORT) $(PYTHON) main.py

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

# MCP Inspector targets
inspector:
	./scripts/test_with_inspector.sh

inspector-cli:
	./scripts/test_with_inspector.sh --cli

inspector-http:
	./scripts/test_with_inspector.sh --http

inspector-cloud:
	./scripts/test_with_inspector.sh --cloud

# Automated MCP Server Tests
test-mcp:
	./scripts/test_mcp_automated.sh

test-mcp-quick:
	./scripts/test_mcp_automated.sh --quick

test-mcp-full:
	./scripts/test_mcp_automated.sh --full --report

test-mcp-cloud:
	./scripts/test_mcp_automated.sh --cloud

test-mcp-pytest:
	$(PYTHON) -m pytest tests/integration/test_mcp_server_real.py -v --tb=short
