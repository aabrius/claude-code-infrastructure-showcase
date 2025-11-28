# 📋 Issues Prontas para Linear - Copy & Paste

## Como Usar Este Documento

1. Abra o Linear
2. Copie cada issue abaixo (título + descrição)
3. Cole no Linear mantendo a formatação Markdown
4. Adicione as labels sugeridas
5. Defina as estimativas indicadas

---

## 🎯 Epic: Simplificação Radical do GAM API

### Descrição do Epic
Transformar o projeto de uma arquitetura enterprise (34,405 linhas) para uma ferramenta pessoal eficiente (<500 linhas), mantendo apenas o essencial: MCP server para IA e utilities básicas.

**Objetivo**: 98% menos código, 100% do valor

---

## FASE 1: PREPARAÇÃO E BACKUP

### 📌 Issue #1
**Título**: [SIMPLIFICATION] Preparar ambiente para simplificação radical

**Descrição**:
Criar branch de segurança e backup antes de iniciar simplificação

**Tarefas**:
- [ ] Criar branch `radical-simplification`
- [ ] Fazer backup completo em `gam-api-backup-{date}.tar.gz`
- [ ] Criar novo diretório `gam-mcp-simple/` para versão simplificada
- [ ] Documentar estado atual: 109 arquivos Python, 34,405 linhas

**Labels**: `simplification`, `preparation`, `high-priority`
**Estimativa**: 1 ponto

---

### 📌 Issue #2  
**Título**: [SIMPLIFICATION] Mapear código essencial para preservar

**Descrição**:
Identificar e documentar código que será preservado na simplificação

**Código a preservar**:

**1. MCP Server**:
- `applications/mcp-server/tools/metadata.py`
- `applications/mcp-server/tools/reports.py`
- `applications/mcp-server/fastmcp_server.py` (parcial)

**2. Utilities essenciais**:
- `packages/shared/src/gam_shared/formatters.py` (parcial)
- `packages/shared/src/gam_shared/validators.py` (parcial)
- `packages/core/src/gam_api/models.py` (enums apenas)

**3. Configuração**:
- `googleads.yaml` (manter)
- Lógica de autenticação OAuth (simplificada)

**Criar**: `CODE_TO_PRESERVE.md`

**Labels**: `simplification`, `analysis`
**Estimativa**: 2 pontos

---

## FASE 2: CRIAÇÃO DA NOVA ESTRUTURA

### 📌 Issue #3
**Título**: [SIMPLIFICATION] Consolidar MCP server em arquivo único

**Descrição**:
Criar mcp_server.py unificado com todas as ferramentas

**Tarefas**:
- [ ] Criar `gam-mcp-simple/mcp_server.py`
- [ ] Migrar 7 tools do MCP atual:
  - `gam_quick_report`
  - `gam_create_report`  
  - `gam_list_reports`
  - `gam_get_dimensions_metrics`
  - `gam_get_common_combinations`
  - `gam_get_quick_report_types`
  - `gam_run_report`
- [ ] Integrar com `google-ads-admanager` oficial
- [ ] Remover todas as dependências desnecessárias
- [ ] Adicionar configuração mínima via `config.yaml`

**Resultado esperado**: ~200-300 linhas de código

**Labels**: `simplification`, `mcp`, `core`, `high-priority`
**Estimativa**: 5 pontos

---

### 📌 Issue #4
**Título**: [SIMPLIFICATION] Criar gam_utils.py com funções essenciais

**Descrição**:
Consolidar utilities essenciais em arquivo único

**Conteúdo do gam_utils.py**:
- [ ] `format_to_excel()` - do formatters.py
- [ ] `format_to_csv()` - do formatters.py  
- [ ] `validate_dimensions_metrics()` - do validators.py
- [ ] `simple_memory_cache()` - versão mínima do cache.py
- [ ] `quick_report_templates()` - templates comuns

**Ignorar**:
- Logger complexo (usar print ou logging básico)
- Cache em arquivo
- Formatters para BI tools específicas

**Resultado esperado**: ~100 linhas de código

**Labels**: `simplification`, `utilities`
**Estimativa**: 3 pontos

---

### 📌 Issue #5
**Título**: [SIMPLIFICATION] Criar pasta examples/ com casos de uso reais

**Descrição**:
Criar exemplos práticos e diretos

**Criar em gam-mcp-simple/examples/**:
- [ ] `daily_revenue_check.py` - Script simples para checar receita
- [ ] `weekly_report.ipynb` - Notebook com análise semanal
- [ ] `common_queries.md` - Queries mais usadas em markdown
- [ ] `mcp_usage.md` - Como usar com Claude/outros agentes

**Fonte dos exemplos**:
- `tests/journeys/` (extrair casos práticos)
- `docs/examples/` (simplificar)

**Labels**: `simplification`, `documentation`, `examples`
**Estimativa**: 2 pontos

---

## FASE 3: REMOÇÃO E LIMPEZA

### 📌 Issue #6
**Título**: [SIMPLIFICATION] Remover API REST Server completamente

**Descrição**:
Deletar toda a estrutura do API server

**Arquivos a deletar**:
```
applications/api-server/ (toda a pasta)
├── Dockerfile
├── main.py
├── auth.py
├── models.py
├── requirements.txt
└── routes/
    ├── health.py
    ├── metadata.py
    └── reports.py
```

**Motivo**: Sem usuários externos, requests via browser são suficientes

**Labels**: `simplification`, `deletion`
**Estimativa**: 1 ponto

---

### 📌 Issue #7
**Título**: [SIMPLIFICATION] Remover arquitetura monorepo packages/

**Descrição**:
Deletar toda estrutura de packages

**Pastas a deletar completamente**:
- `packages/core/`
- `packages/sdk/`  
- `packages/shared/`

**Total**: ~60 arquivos

**Motivo**: Overengineering para projeto pessoal
**Nota**: Código essencial já extraído nas issues #3 e #4

**Labels**: `simplification`, `deletion`
**Estimativa**: 1 ponto

---

### 📌 Issue #8
**Título**: [SIMPLIFICATION] Remover configurações de deployment complexas

**Descrição**:
Deletar infraestrutura desnecessária

**Deletar**:
- `infrastructure/` (toda a pasta)
- `.github/workflows/` (manter apenas básico se necessário)
- `Makefile` (criar novo minimalista)
- `docker-compose.yml`
- `cloudbuild.yaml`

**Manter apenas**:
- Dockerfile simples (10 linhas) para MCP se necessário

**Labels**: `simplification`, `deletion`, `infrastructure`
**Estimativa**: 1 ponto

---

### 📌 Issue #9
**Título**: [SIMPLIFICATION] Remover todo código legacy

**Descrição**:
Remover compatibilidade desnecessária

**Deletar**:
- `legacy/` (pasta completa)
- Todos os `migration_examples.py`
- Código de retrocompatibilidade

**Motivo**: Sem usuários = sem necessidade de compatibilidade

**Labels**: `simplification`, `deletion`
**Estimativa**: 1 ponto

---

### 📌 Issue #10
**Título**: [SIMPLIFICATION] Manter apenas testes essenciais

**Descrição**:
Simplificar estrutura de testes

**Manter**:
- `tests/test_mcp.py` (criar novo, simples)
- `tests/test_utils.py` (criar novo, simples)

**Deletar**:
- `tests/unit/` (todos)
- `tests/integration/` (todos)
- `tests/performance/` (todos)
- `tests/journeys/` (já extraímos exemplos)
- Configurações complexas de pytest

**Resultado**: 2 arquivos de teste, ~100 linhas total

**Labels**: `simplification`, `tests`
**Estimativa**: 2 pontos

---

## FASE 4: DOCUMENTAÇÃO E FINALIZAÇÃO

### 📌 Issue #11
**Título**: [SIMPLIFICATION] Documentação simples e direta

**Descrição**:
Criar README.md focado no essencial

**Seções**:
1. O que é (2 linhas)
2. Setup (5 passos máximo)
3. Uso com MCP (exemplo)
4. Exemplos práticos (links)

**Deletar**:
- `docs/` (pasta inteira exceto documentos de simplificação)
- Documentação de API
- Guias de deployment complexos

**Resultado**: README.md com <100 linhas

**Labels**: `simplification`, `documentation`
**Estimativa**: 2 pontos

---

### 📌 Issue #12
**Título**: [SIMPLIFICATION] Setup em um comando

**Descrição**:
Criar setup.py ou setup.sh minimalista

**Funcionalidades**:
- [ ] Instalar `google-ads-admanager`
- [ ] Instalar `fastmcp`
- [ ] Criar `config.yaml` de exemplo
- [ ] Verificar `googleads.yaml`
- [ ] Rodar teste básico

**Substituir**:
- `setup_env.sh` complexo
- `requirements.txt` múltiplos
- `pyproject.toml` monorepo

**Labels**: `simplification`, `setup`
**Estimativa**: 1 ponto

---

### 📌 Issue #13
**Título**: [SIMPLIFICATION] Validar simplificação e limpar restos

**Descrição**:
Verificação final da simplificação

**Checklist**:
- [ ] MCP server funciona com todas as 7 tools
- [ ] Exemplos rodam sem erros
- [ ] Setup completo em <5 minutos
- [ ] Código total <500 linhas
- [ ] Arquivos totais <10
- [ ] Deletar arquivos órfãos (`.pyc`, `__pycache__`, etc)
- [ ] Atualizar `.gitignore` para novo estrutura

**Métricas finais**:
- LOC antes: 34,405 → depois: <500
- Arquivos antes: 109 → depois: <10
- Tempo de setup antes: 30min → depois: 5min

**Labels**: `simplification`, `validation`
**Estimativa**: 2 pontos

---

## FASE 5: MIGRAÇÃO E ARQUIVO

### 📌 Issue #14
**Título**: [SIMPLIFICATION] Criar arquivo do projeto original

**Descrição**:
Preservar versão antiga para referência

**Tarefas**:
- [ ] Criar `gam-api-enterprise-archived/`
- [ ] Mover código antigo preservando histórico git
- [ ] Criar README explicando o arquivo
- [ ] Tag final: `v1.0.0-enterprise-final`

**Novo repo principal**: `gam-mcp-simple/`

**Labels**: `simplification`, `archive`
**Estimativa**: 1 ponto

---

## 📊 Resumo para o Board

**Total de Issues**: 14
**Estimativa Total**: 28 pontos
**Impacto**: 98% redução de código, 100% valor mantido

**Sugestão de Sprints**:
- **Sprint 1** (Preparação): Issues #1-2 (3 pontos)
- **Sprint 2** (Construção): Issues #3-5 (10 pontos)
- **Sprint 3** (Demolição): Issues #6-10 (6 pontos)
- **Sprint 4** (Finalização): Issues #11-14 (9 pontos)

**Milestone**: Simplificação Completa - 2 semanas