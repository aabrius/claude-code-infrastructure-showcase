# CODE_TO_PRESERVE.md - Essential Code Mapping for Simplification

Este documento mapeia todo o código essencial que deve ser preservado durante o processo de simplificação do GAM-API. O código está organizado por categoria e inclui justificativas para preservação.

## 1. MCP Server - Código Completo para Preservar

### 1.1 Ferramentas MCP (Tools)

#### `applications/mcp-server/tools/metadata.py`
**Preservar completamente** - Contém funções essenciais para:
- `handle_get_dimensions_metrics`: Retorna dimensões e métricas disponíveis
- `handle_get_common_combinations`: Fornece combinações validadas
- Funções auxiliares de categorização (`_categorize_dimensions`, `_categorize_metrics`)

#### `applications/mcp-server/tools/reports.py` 
**Preservar completamente** - Implementa todos os handlers de relatórios:
- `handle_quick_report`: Relatórios rápidos pré-configurados
- `handle_create_report`: Criação de relatórios customizados
- `handle_list_reports`: Listagem de relatórios existentes
- `handle_get_quick_report_types`: Tipos de relatórios disponíveis
- `_extract_value`: Função auxiliar para extração de valores

### 1.2 Servidor FastMCP

#### `applications/mcp-server/fastmcp_server.py`
**Preservar parcialmente** - Extrair e simplificar:

```python
# Essencial: Importações e configuração
from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair

# Essencial: Classe de métricas de performance
@dataclass
class PerformanceMetrics:
    # Manter implementação completa
    
# Essencial: Circuit breaker simples
class CircuitBreaker:
    # Manter implementação completa

# Essencial: MCPError para respostas de erro estruturadas
class MCPError:
    # Manter todos os métodos estáticos de formatação de erro

# Essencial: Decoradores
@with_graceful_degradation  # Manter completo
@track_performance         # Manter completo

# Essencial: Todas as ferramentas MCP decoradas com @mcp.tool
@mcp.tool
async def gam_quick_report(...)
@mcp.tool
async def gam_create_report(...)
@mcp.tool
async def gam_list_reports(...)
@mcp.tool
async def gam_get_dimensions_metrics(...)
@mcp.tool
async def gam_get_common_combinations(...)
@mcp.tool
async def gam_get_quick_report_types(...)
@mcp.tool
async def gam_run_report(...)
@mcp.tool
async def gam_get_performance_stats(...)
```

## 2. Utilities Essenciais - Código Parcial

### 2.1 Formatadores

#### `packages/shared/src/gam_shared/formatters.py`
**Preservar parcialmente** - Extrair apenas:

```python
# Classes essenciais
class JSONFormatter(ReportFormatter):
    def format(self, result: ReportResult) -> str
    def _format_row(self, row: Dict[str, Any], ...) -> Dict[str, Any]
    def _extract_value(self, value_obj: Dict[str, Any]) -> Any

class CSVFormatter(ReportFormatter):
    def format(self, result: ReportResult) -> str
    def _format_row(self, row: Dict[str, Any], ...) -> List[Any]
    def _extract_value(self, value_obj: Dict[str, Any]) -> Any

class SummaryFormatter(ReportFormatter):
    def format(self, result: ReportResult) -> str

# Função factory essencial
def get_formatter(format_type: Union[str, ExportFormat], **kwargs) -> ReportFormatter

# Funções de compatibilidade para fastmcp_server
def format_as_json(data)
def format_as_csv(data)
```

### 2.2 Validadores

#### `packages/shared/src/gam_shared/validators.py`
**Preservar parcialmente** - Extrair apenas:

```python
# Conjuntos de validação essenciais (manter como estão)
VALID_DIMENSIONS = {
    # Time dimensions
    "DATE", "WEEK", "MONTH", "YEAR",
    # Inventory dimensions
    "AD_UNIT_ID", "AD_UNIT_NAME", "AD_UNIT_CODE",
    # ... (manter lista completa)
}

VALID_METRICS = {
    # Impression metrics
    "TOTAL_LINE_ITEM_LEVEL_IMPRESSIONS",
    # ... (manter lista completa)
}

REACH_ONLY_METRICS = {
    "UNIQUE_REACH_IMPRESSIONS",
    "UNIQUE_REACH_FREQUENCY", 
    "UNIQUE_REACH"
}

# Funções de validação essenciais
def validate_dimensions_list(dimensions: List[str]) -> List[str]
def validate_metrics_list(metrics: List[str]) -> List[str]
def validate_report_type_compatibility(report_type: ReportType, metrics: List[str]) -> bool

# Funções de compatibilidade para fastmcp_server
def validate_dimensions(dimensions)
def validate_metrics(metrics)
```

## 3. Models - Apenas Enums

#### `packages/core/src/gam_api/models.py`
**Preservar apenas enums** - Extrair:

```python
from enum import Enum

class ReportType(str, Enum):
    """Report type enumeration."""
    DELIVERY = "delivery"
    INVENTORY = "inventory"
    SALES = "sales" 
    REACH = "reach"
    PROGRAMMATIC = "programmatic"

class DateRangeType(str, Enum):
    """Date range type enumeration."""
    LAST_WEEK = "LAST_WEEK"
    LAST_MONTH = "LAST_MONTH"
    CUSTOM = "CUSTOM"
    LAST_N_DAYS = "LAST_N_DAYS"

class ReportStatus(str, Enum):
    """Report status enumeration."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class ExportFormat(str, Enum):
    """Export format enumeration."""
    JSON = "json"
    CSV = "csv"
    XLSX = "xlsx"
```

## 4. Configuração - Preservar Estrutura

### 4.1 Arquivo de Configuração

#### `googleads.yaml`
**Preservar estrutura completa** - Manter como referência:

```yaml
ad_manager:
  # Autenticação via OAuth2 com credenciais de usuário
  client_id: <CLIENT_ID>
  client_secret: <CLIENT_SECRET>
  refresh_token: <REFRESH_TOKEN>
  
  # Código da rede do Ad Manager
  network_code: "<NETWORK_CODE>"
  
  # Nome da aplicação
  application_name: Ad Manager Data Extractor
  
  # Configurações de logging
  logging:
    level: INFO
```

## 5. Lógica de Autenticação OAuth - Simplificada

### 5.1 Autenticação Essencial

Extrair da `packages/core/src/gam_api/auth.py` apenas o essencial:

```python
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class SimpleAuthManager:
    """Gerenciador simplificado de autenticação OAuth."""
    
    def __init__(self, config):
        self.config = config
        self._credentials = None
    
    def get_oauth2_credentials(self) -> Credentials:
        """Obter credenciais OAuth2."""
        if self._credentials is None:
            # Criar objeto de credenciais
            self._credentials = Credentials(
                None,  # No access token yet
                refresh_token=self.config['refresh_token'],
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.config['client_id'],
                client_secret=self.config['client_secret']
            )
            # Atualizar token
            self._credentials.refresh(Request())
        
        # Verificar se precisa atualizar
        if self._credentials.expired:
            self._credentials.refresh(Request())
        
        return self._credentials
```

## 6. Estrutura Simplificada Proposta

```
gam-api-simplified/
├── mcp_server/
│   ├── __init__.py
│   ├── server.py         # fastmcp_server.py simplificado
│   ├── tools.py          # metadata.py + reports.py combinados
│   └── errors.py         # MCPError extraído
├── core/
│   ├── __init__.py
│   ├── auth.py           # SimpleAuthManager
│   ├── models.py         # Apenas enums
│   ├── validators.py     # Validadores essenciais
│   └── formatters.py     # Formatadores essenciais
├── config/
│   └── googleads.yaml    # Configuração preservada
└── requirements.txt      # Dependências mínimas
```

## 7. Funcionalidades a Remover

- **NÃO preservar**:
  - API REST (applications/api-server/)
  - SDK Python (packages/sdk/)
  - Scripts legados (legacy/)
  - Infraestrutura de deployment complexa
  - Sistema de cache elaborado
  - Logging estruturado complexo
  - Testes (podem ser recriados)
  - Documentação extensa (criar nova simplificada)

## 8. Dependências Mínimas

```txt
# requirements.txt simplificado
fastmcp>=0.1.0
google-auth>=2.0.0
google-auth-oauthlib>=0.4.0
pyyaml>=5.0
```

## 9. Notas de Migração

1. **Circuit Breaker**: Manter implementação simples para resiliência
2. **Performance Metrics**: Preservar para monitoramento
3. **Graceful Degradation**: Essencial para disponibilidade
4. **Error Handling**: Manter MCPError para respostas estruturadas
5. **Validação**: Preservar listas completas de dimensões/métricas válidas

## 10. Próximos Passos

1. Criar nova estrutura de diretórios simplificada
2. Copiar código essencial identificado
3. Simplificar importações e dependências
4. Testar funcionalidade do MCP Server
5. Documentar nova estrutura simplificada