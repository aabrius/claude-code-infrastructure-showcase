# 📋 Issues para Simplificação Radical - GAM API

## Sequência de Execução

### FASE 1: PREPARAÇÃO E BACKUP (Prioridade: Urgente)

#### Issue #1: Criar branch e backup completo
**Título**: [SIMPLIFICATION] Preparar ambiente para simplificação radical
**Descrição**:
```
Criar branch de segurança e backup antes de iniciar simplificação

Tarefas:
- [ ] Criar branch `radical-simplification`
- [ ] Fazer backup completo em `gam-api-backup-{date}.tar.gz`
- [ ] Criar novo diretório `gam-mcp-simple/` para versão simplificada
- [ ] Documentar estado atual (LOC, número de arquivos, complexidade)

Arquivos afetados:
- Todo o projeto (backup)
```
**Labels**: simplification, preparation
**Estimate**: 1

---

#### Issue #2: Análise e mapeamento de código essencial
**Título**: [SIMPLIFICATION] Mapear código essencial para preservar
**Descrição**:
```
Identificar e documentar código que será preservado na simplificação

Código a preservar:
1. MCP Server:
   - applications/mcp-server/tools/metadata.py
   - applications/mcp-server/tools/reports.py
   - applications/mcp-server/fastmcp_server.py (parcial)

2. Utilities essenciais:
   - packages/shared/src/gam_shared/formatters.py (parcial)
   - packages/shared/src/gam_shared/validators.py (parcial)
   - packages/core/src/gam_api/models.py (enums apenas)

3. Configuração:
   - googleads.yaml (manter)
   - Lógica de autenticação OAuth (simplificada)

Criar documento: CODE_TO_PRESERVE.md
```
**Labels**: simplification, analysis
**Estimate**: 2

---

### FASE 2: CRIAÇÃO DA NOVA ESTRUTURA (Prioridade: Alta)

#### Issue #3: Criar novo MCP server consolidado
**Título**: [SIMPLIFICATION] Consolidar MCP server em arquivo único
**Descrição**:
```
Criar mcp_server.py unificado com todas as ferramentas

Tarefas:
- [ ] Criar gam-mcp-simple/mcp_server.py
- [ ] Migrar 7 tools do MCP atual:
  - gam_quick_report
  - gam_create_report  
  - gam_list_reports
  - gam_get_dimensions_metrics
  - gam_get_common_combinations
  - gam_get_quick_report_types
  - gam_run_report
- [ ] Integrar com google-ads-admanager oficial
- [ ] Remover todas as dependências desnecessárias
- [ ] Adicionar configuração mínima via config.yaml

Resultado esperado: ~200-300 linhas de código
```
**Labels**: simplification, mcp, core
**Estimate**: 5

---

#### Issue #4: Criar utilities consolidadas
**Título**: [SIMPLIFICATION] Criar gam_utils.py com funções essenciais
**Descrição**:
```
Consolidar utilities essenciais em arquivo único

Conteúdo do gam_utils.py:
- [ ] format_to_excel() - do formatters.py
- [ ] format_to_csv() - do formatters.py  
- [ ] validate_dimensions_metrics() - do validators.py
- [ ] simple_memory_cache() - versão mínima do cache.py
- [ ] quick_report_templates() - templates comuns

Ignorar:
- Logger complexo (usar print ou logging básico)
- Cache em arquivo
- Formatters para BI tools específicas

Resultado esperado: ~100 linhas de código
```
**Labels**: simplification, utilities
**Estimate**: 3

---

#### Issue #5: Migrar exemplos práticos
**Título**: [SIMPLIFICATION] Criar pasta examples/ com casos de uso reais
**Descrição**:
```
Criar exemplos práticos e diretos

Criar em gam-mcp-simple/examples/:
- [ ] daily_revenue_check.py - Script simples para checar receita
- [ ] weekly_report.ipynb - Notebook com análise semanal
- [ ] common_queries.md - Queries mais usadas em markdown
- [ ] mcp_usage.md - Como usar com Claude/outros agentes

Fonte dos exemplos:
- tests/journeys/ (extrair casos práticos)
- docs/examples/ (simplificar)
```
**Labels**: simplification, documentation, examples
**Estimate**: 2

---

### FASE 3: REMOÇÃO E LIMPEZA (Prioridade: Alta)

#### Issue #6: Deletar applications/api-server
**Título**: [SIMPLIFICATION] Remover API REST Server completamente
**Descrição**:
```
Deletar toda a estrutura do API server

Arquivos a deletar:
- applications/api-server/ (toda a pasta)
  - Dockerfile
  - main.py
  - auth.py
  - models.py
  - requirements.txt
  - routes/
    - health.py
    - metadata.py
    - reports.py

Motivo: Sem usuários externos, requests via browser são suficientes
```
**Labels**: simplification, deletion
**Estimate**: 1

---

#### Issue #7: Deletar estrutura de packages
**Título**: [SIMPLIFICATION] Remover arquitetura monorepo packages/
**Descrição**:
```
Deletar toda estrutura de packages

Pastas a deletar completamente:
- packages/core/
- packages/sdk/  
- packages/shared/

Total de arquivos a deletar: ~60 arquivos

Motivo: Overengineering para projeto pessoal
Código essencial já foi extraído nas issues #3 e #4
```
**Labels**: simplification, deletion
**Estimate**: 1

---

#### Issue #8: Deletar infrastructure e deployment
**Título**: [SIMPLIFICATION] Remover configurações de deployment complexas
**Descrição**:
```
Deletar infraestrutura desnecessária

Deletar:
- infrastructure/ (toda a pasta)
  - deploy/
  - docker/
  - scripts/
- .github/workflows/ (manter apenas básico se necessário)
- Makefile (criar novo minimalista)
- docker-compose.yml
- cloudbuild.yaml

Manter apenas:
- Dockerfile simples (10 linhas) para MCP se necessário
```
**Labels**: simplification, deletion, infrastructure
**Estimate**: 1

---

#### Issue #9: Deletar legacy code
**Título**: [SIMPLIFICATION] Remover todo código legacy
**Descrição**:
```
Remover compatibilidade desnecessária

Deletar:
- legacy/ (pasta completa)
- Todos os migration_examples.py
- Código de retrocompatibilidade

Motivo: Sem usuários = sem necessidade de compatibilidade
```
**Labels**: simplification, deletion
**Estimate**: 1

---

#### Issue #10: Simplificar tests
**Título**: [SIMPLIFICATION] Manter apenas testes essenciais
**Descrição**:
```
Simplificar estrutura de testes

Manter:
- tests/test_mcp.py (criar novo, simples)
- tests/test_utils.py (criar novo, simples)

Deletar:
- tests/unit/ (todos)
- tests/integration/ (todos)
- tests/performance/ (todos)
- tests/journeys/ (já extraímos exemplos)
- Configurações complexas de pytest

Resultado: 2 arquivos de teste, ~100 linhas total
```
**Labels**: simplification, tests
**Estimate**: 2

---

### FASE 4: DOCUMENTAÇÃO E FINALIZAÇÃO (Prioridade: Média)

#### Issue #11: Criar novo README.md minimalista
**Título**: [SIMPLIFICATION] Documentação simples e direta
**Descrição**:
```
Criar README.md focado no essencial

Seções:
1. O que é (2 linhas)
2. Setup (5 passos máximo)
3. Uso com MCP (exemplo)
4. Exemplos práticos (links)

Deletar:
- docs/ (pasta inteira exceto essencial)
- Documentação de API
- Guias de deployment complexos

Resultado: README.md com <100 linhas
```
**Labels**: simplification, documentation
**Estimate**: 2

---

#### Issue #12: Criar script de setup simples
**Título**: [SIMPLIFICATION] Setup em um comando
**Descrição**:
```
Criar setup.py ou setup.sh minimalista

Funcionalidades:
- [ ] Instalar google-ads-admanager
- [ ] Instalar fastmcp
- [ ] Criar config.yaml de exemplo
- [ ] Verificar googleads.yaml
- [ ] Rodar teste básico

Substituir:
- setup_env.sh complexo
- requirements.txt múltiplos
- pyproject.toml monorepo
```
**Labels**: simplification, setup
**Estimate**: 1

---

#### Issue #13: Validação final e limpeza
**Título**: [SIMPLIFICATION] Validar simplificação e limpar restos
**Descrição**:
```
Verificação final da simplificação

Checklist:
- [ ] MCP server funciona com todas as 7 tools
- [ ] Exemplos rodam sem erros
- [ ] Setup completo em <5 minutos
- [ ] Código total <500 linhas
- [ ] Arquivos totais <10
- [ ] Deletar arquivos órfãos (.pyc, __pycache__, etc)
- [ ] Atualizar .gitignore para novo estrutura

Métricas finais:
- LOC antes vs depois
- Número de arquivos antes vs depois
- Tempo de setup antes vs depois
```
**Labels**: simplification, validation
**Estimate**: 2

---

### FASE 5: MIGRAÇÃO E ARQUIVO (Prioridade: Baixa)

#### Issue #14: Arquivar projeto antigo
**Título**: [SIMPLIFICATION] Criar arquivo do projeto original
**Descrição**:
```
Preservar versão antiga para referência

Tarefas:
- [ ] Criar gam-api-enterprise-archived/
- [ ] Mover código antigo preservando histórico git
- [ ] Criar README explicando o arquivo
- [ ] Tag final: v1.0.0-enterprise-final

Novo repo principal: gam-mcp-simple/
```
**Labels**: simplification, archive
**Estimate**: 1

---

## Resumo da Execução

**Total de Issues**: 14
**Estimativa Total**: 28 pontos
**Arquivos a Deletar**: ~95% do projeto atual
**Código Final**: <500 linhas (vs 5000+ atual)

## Ordem de Execução Recomendada

1. **Dia 1**: Issues #1-2 (Preparação)
2. **Dia 2-3**: Issues #3-5 (Nova estrutura)
3. **Dia 4**: Issues #6-10 (Deletar tudo)
4. **Dia 5**: Issues #11-14 (Finalização)

## Princípio Guia

> "Perfection is achieved not when there is nothing more to add, but when there is nothing left to take away." - Antoine de Saint-Exupéry

Delete sem piedade. Mantenha apenas o essencial.