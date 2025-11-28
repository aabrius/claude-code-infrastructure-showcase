#!/bin/bash

# Cores para saída
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Configurando ambiente para Google Ad Manager API ===${NC}"

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python 3 não encontrado. Por favor, instale o Python 3.7 ou superior.${NC}"
    exit 1
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 --version | cut -d " " -f 2)
echo -e "${GREEN}Usando Python versão: ${PYTHON_VERSION}${NC}"

# Criar ambiente virtual
echo -e "${GREEN}Criando ambiente virtual...${NC}"
python3 -m venv venv

# Ativar ambiente virtual
echo -e "${GREEN}Ativando ambiente virtual...${NC}"
source venv/bin/activate

# Instalar pacote
echo -e "${GREEN}Instalando pacote GAM-API...${NC}"
pip install --upgrade pip
pip install -e .

# Verificar se o arquivo .env existe
if [ ! -f .env ]; then
    echo -e "${GREEN}Criando arquivo .env a partir do exemplo...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Por favor, edite o arquivo .env com suas credenciais.${NC}"
else
    echo -e "${GREEN}Arquivo .env já existe.${NC}"
fi

# Verificar se o arquivo googleads.yaml existe
if [ ! -f googleads.yaml ]; then
    echo -e "${GREEN}Criando arquivo googleads.yaml a partir do exemplo...${NC}"
    cp googleads.yaml.example googleads.yaml
    echo -e "${YELLOW}Por favor, edite o arquivo googleads.yaml com suas credenciais.${NC}"
else
    echo -e "${GREEN}Arquivo googleads.yaml já existe.${NC}"
fi

echo -e "${GREEN}=== Ambiente configurado com sucesso! ===${NC}"
echo -e "${YELLOW}Para ativar o ambiente virtual, execute:${NC}"
echo -e "    source venv/bin/activate"
echo -e "${YELLOW}Para gerar um token de atualização OAuth2, execute:${NC}"
echo -e "    python generate_new_token.py"
echo -e "${YELLOW}Usar as interfaces disponíveis:${NC}"
echo -e "    # REST API"
echo -e "    make api"
echo -e "    # FastMCP Server" 
echo -e "    make mcp"
echo -e "    # Exemplos Python SDK"
echo -e "    python examples/sdk_quick_start.py"