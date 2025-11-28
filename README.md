# Google Ad Manager API Integration

**AI-friendly Google Ad Manager API integration with MCP Server, REST API, and Python SDK for automated report generation.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP](https://img.shields.io/badge/MCP-Server-purple.svg)](https://modelcontextprotocol.io/)

---

## 🚀 Features

- **🤖 MCP Server** - 7 tools for AI assistants (Claude, etc.) with JWT authentication
- **🌐 REST API** - FastAPI with 17 endpoints for web applications
- **🐍 Python SDK** - Fluent API with builders pattern for programmatic access
- **📊 Report Types** - Delivery, Inventory, Sales, Reach, Programmatic
- **🔄 Multi-API Support** - SOAP (legacy) + REST API v1 (beta) with automatic fallback
- **⚡ Performance** - Multi-level caching (memory + file) with TTL
- **🛡️ Error Handling** - Circuit breaker pattern with graceful degradation
- **☁️ Cloud Ready** - Deployed to Google Cloud Run with auto-scaling

---

## 📦 Quick Start

### Installation

```bash
# Complete environment setup
./scripts/setup_env.sh

# Install dependencies
pip install -e ".[all]"

# Generate OAuth token
python generate_new_token.py
```

### Configuration

Create `googleads.yaml` from template:
```bash
cp googleads.yaml.example googleads.yaml
# Edit with your OAuth2 credentials and network code
```

### Running Services

```bash
# REST API (port 8000)
make api

# MCP Server (local)
make mcp

# Run tests
make test
```

---

## 🎯 Available Commands

### Setup & Environment
```bash
make env               # Configure initial environment
make setup             # Install basic dependencies
make install-dev       # Install all dev dependencies
make auth              # Generate OAuth2 token
make test-credentials  # Validate GAM credentials
```

### Development
```bash
make api               # Start REST API server (port 8000)
make mcp               # Start MCP server locally
```

### Testing
```bash
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make test-journeys     # Run journey tests only
make test-cov          # Run tests with coverage report
make coverage-report   # Generate detailed coverage report
```

### Code Quality
```bash
make lint              # Run linting (flake8)
make format            # Format code (black)
make typecheck         # Type checking (mypy)
```

### Cleanup
```bash
make clean             # Remove cache and temp files
```

### Help
```bash
make help              # Show all available commands
```

---

## 🏗️ Architecture

### Monorepo Structure

```
gam-api/
├── packages/                    # Reusable components
│   ├── core/                   # GAM API functionality (gam_api package)
│   ├── sdk/                    # Python SDK (gam_sdk package)
│   └── shared/                 # Utilities (gam_shared package)
├── applications/               # Deployable services
│   ├── api-server/            # FastAPI REST API
│   └── mcp-server/            # FastMCP server with 7 tools
├── tests/                     # Unit, integration, journeys, performance
├── scripts/                   # Utility scripts
├── infrastructure/            # Deployment scripts
└── docs/                      # Comprehensive documentation
```

### Production Interfaces

- **MCP Server**: https://gam-mcp-server-183972668403.us-central1.run.app
  - 7 tools for AI assistants
  - JWT authentication
  - Native HTTP transport

- **REST API**: `http://localhost:8000/api/v1`
  - 17 endpoints
  - API key authentication
  - OpenAPI/Swagger docs at `/docs`

- **Python SDK**: Fluent API for direct integration
  ```python
  from gam_api import GAMClient

  client = GAMClient()
  report = client.quick_report("delivery", days_back=7)
  ```

---

## 📊 Report Types

### 1. Delivery Reports
Impressions, clicks, CTR, CPM, revenue

### 2. Inventory Reports
Ad requests, fill rate, matched requests

### 3. Sales Reports
Revenue, eCPM by advertiser/order

### 4. Reach Reports
Unique reach, frequency by country/device

### 5. Programmatic Reports
Programmatic channel performance

---

## 🔧 Configuration

### Environment Variables

```bash
# Google Ad Manager
GAM_NETWORK_CODE=123456789
GOOGLE_OAUTH_CLIENT_ID=your-client-id
GOOGLE_OAUTH_CLIENT_SECRET=your-client-secret
GOOGLE_OAUTH_REFRESH_TOKEN=your-refresh-token

# Optional
GAM_APPLICATION_NAME="GAM API"
GAM_TIMEZONE="America/New_York"
```

### Configuration Files

- **`googleads.yaml`** - OAuth2 credentials, network code (legacy SOAP format)
- **`config/agent_config.yaml`** - Multi-interface configuration
- **`pyproject.toml`** - Monorepo workspace configuration
- **`.env`** - Environment variables (gitignored)

---

## 🧪 Testing

```bash
# All tests
make test

# Specific test categories
make test-unit          # Fast unit tests
make test-integration   # Integration tests with mocking
make test-journeys      # End-to-end journey tests

# With coverage
make test-cov           # HTML + terminal report
make coverage-report    # Detailed coverage analysis

# Test credentials
make test-credentials   # Validate OAuth and network access
```

---

## 📚 Documentation

- **[API Reference](docs/api-reference.md)** - Complete API documentation
- **[SDK Guide](docs/SDK_USAGE_GUIDE.md)** - Python SDK usage examples
- **[Deployment Guide](docs/deployment.md)** - Cloud Run deployment
- **[Testing Guide](docs/testing/)** - Testing strategies and examples
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions
- **[Examples](docs/examples/)** - Code examples and patterns

---

## 🚀 Deployment

### Google Cloud Run (Production)

```bash
# Setup credentials
./infrastructure/deploy/setup-secrets.sh

# Deploy MCP server
./infrastructure/deploy/cloud-run-deploy.sh

# Or use Cloud Build
gcloud builds submit --config cloudbuild-simple.yaml
```

### Local Development

```bash
# API Server
cd applications/api-server
python main.py

# MCP Server
cd applications/mcp-server
python fastmcp_server.py
```

---

## 🔑 Authentication

### OAuth 2.0 Setup

1. **Get credentials** from Google Cloud Console
2. **Create `googleads.yaml`** from template
3. **Generate refresh token**:
   ```bash
   python generate_new_token.py
   ```
4. **Test credentials**:
   ```bash
   make test-credentials
   ```

### MCP Server Authentication

Production MCP server uses JWT authentication with RSA key pairs.

```json
{
  "mcpServers": {
    "gam-api-cloud": {
      "url": "https://gam-mcp-server-183972668403.us-central1.run.app/mcp",
      "transport": "http",
      "headers": {
        "Authorization": "Bearer <jwt-token>"
      }
    }
  }
}
```

---

## 🛠️ Development

### Prerequisites

- Python 3.8+
- Google Ad Manager account
- OAuth 2.0 credentials

### Setup Development Environment

```bash
# Clone repository
git clone <repository-url>
cd gam-api

# Setup environment
./scripts/setup_env.sh

# Install dev dependencies
make install-dev

# Generate OAuth token
make auth

# Test credentials
make test-credentials

# Run tests
make test
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
make typecheck
```

---

## 📈 Performance Features

- **Multi-level caching** - Memory + file cache with TTL
- **Circuit breaker** - Graceful degradation when API unavailable
- **Connection pooling** - Efficient API connections
- **Performance monitoring** - Request tracking and metrics
- **Structured logging** - JSON logging with request IDs

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

- **Documentation**: [docs/](docs/)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)
- **Issues**: GitHub Issues

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- MCP support via [FastMCP](https://github.com/jlowin/fastmcp)
- Google Ad Manager API by Google
- Deployed on [Google Cloud Run](https://cloud.google.com/run)

---

**Made with ❤️ for AI-assisted development**
