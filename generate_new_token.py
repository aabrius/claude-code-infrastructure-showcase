#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Script para gerar uma nova URL de autorização e processar o código

import os
import re
import json
import webbrowser
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

# Caminho para o arquivo de credenciais JSON
CLIENT_SECRET_FILE = 'client_secret_640670014752-u5lnbkslujd482j3rs8jvm6fng4q1nbf.apps.googleusercontent.com.json'

# Escopos necessários para a API do Ad Manager
SCOPES = ['https://www.googleapis.com/auth/admanager']


def main():
    # Verificar se o arquivo de credenciais existe
    if not os.path.exists(CLIENT_SECRET_FILE):
        print(
            f"Erro: Arquivo de credenciais '{CLIENT_SECRET_FILE}' não encontrado.")
        return

    try:
        # Carregar o arquivo JSON para extrair os URIs de redirecionamento configurados
        with open(CLIENT_SECRET_FILE, 'r') as f:
            client_config = json.load(f)

        # Verificar se é um cliente web
        if 'web' not in client_config:
            print("Erro: O arquivo de credenciais não é do tipo 'web'.")
            return

        # Obter os URIs de redirecionamento configurados
        redirect_uris = client_config['web']['redirect_uris']
        if not redirect_uris:
            print("Erro: Nenhum URI de redirecionamento configurado nas credenciais.")
            return

        # Usar o primeiro URI de redirecionamento configurado
        redirect_uri = redirect_uris[0]
        print(f"Usando URI de redirecionamento: {redirect_uri}")

        # Criar o fluxo de autorização OAuth2 diretamente do arquivo JSON
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=redirect_uri)

        # Gerar URL de autorização
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            prompt='consent',
            include_granted_scopes='true'
        )

        print(f'\nPor favor, acesse este URL para autorizar o aplicativo:')
        print(auth_url)
        print('\nApós autorizar, você será redirecionado para {}.'.format(redirect_uri))
        print('Como esse redirecionamento pode não funcionar localmente, você precisará copiar a URL completa da barra de endereços após o redirecionamento.')

        # Tentar abrir o navegador automaticamente
        webbrowser.open(auth_url)

        print('\nCole a URL completa após o redirecionamento:')
        redirect_response = input('URL de redirecionamento: ').strip()

        # Extrair o código da URL de redirecionamento
        code_match = re.search(r'code=([^&]+)', redirect_response)
        if not code_match:
            print("Erro: Não foi possível encontrar o código na URL de redirecionamento.")
            return

        code = code_match.group(1)
        print(f"Código extraído: {code}")

        # Extrair os escopos da URL de redirecionamento (se houver)
        scope_match = re.search(r'scope=([^&]+)', redirect_response)
        if scope_match:
            scope_str = scope_match.group(1)
            # Substituir '+' por espaços para obter o formato correto
            scope_str = scope_str.replace('+', ' ')
            # Dividir em uma lista de escopos
            scopes = scope_str.split()
            print(f"Escopos extraídos: {scopes}")

            # Atualizar o fluxo com os novos escopos
            flow = Flow.from_client_secrets_file(
                CLIENT_SECRET_FILE,
                scopes=scopes,
                redirect_uri=redirect_uri)

        # Trocar o código pelo token
        try:
            flow.fetch_token(authorization_response=redirect_response)
            credentials = flow.credentials
        except Exception as e:
            print(f"Erro ao trocar o código pelo token: {e}")
            print("Tentando método alternativo...")

            try:
                flow.fetch_token(code=code)
                credentials = flow.credentials
            except Exception as e:
                print(f"Erro no método alternativo: {e}")
                return

        # Exibir os tokens
        print(f'\nToken de Acesso: {credentials.token}')
        print(f'Token de Atualização: {credentials.refresh_token}')

        # Adicionar o token ao arquivo .env
        with open('.env', 'r') as f:
            env_content = f.read()

        if 'REFRESH_TOKEN=' in env_content:
            # Substituir o token existente
            env_lines = env_content.split('\n')
            for i, line in enumerate(env_lines):
                if line.startswith('REFRESH_TOKEN='):
                    env_lines[i] = f'REFRESH_TOKEN={credentials.refresh_token}'
                    break
            env_content = '\n'.join(env_lines)
        else:
            # Adicionar o token ao final do arquivo
            env_content += f'\nREFRESH_TOKEN={credentials.refresh_token}\n'

        with open('.env', 'w') as f:
            f.write(env_content)

        print('\nToken de atualização adicionado ao arquivo .env')

        # Adicionar o token ao arquivo googleads.yaml
        try:
            with open('googleads.yaml', 'r') as f:
                yaml_content = f.read()

            if 'refresh_token:' in yaml_content and '# refresh_token:' not in yaml_content:
                # Substituir o token existente
                yaml_lines = yaml_content.split('\n')
                for i, line in enumerate(yaml_lines):
                    if line.strip().startswith('refresh_token:'):
                        yaml_lines[i] = f'  refresh_token: {credentials.refresh_token}'
                        break
                yaml_content = '\n'.join(yaml_lines)
            else:
                # Descomente e adicione o token
                yaml_lines = yaml_content.split('\n')
                for i, line in enumerate(yaml_lines):
                    if '# refresh_token:' in line:
                        yaml_lines[i] = f'  refresh_token: {credentials.refresh_token}'
                        break
                yaml_content = '\n'.join(yaml_lines)

            with open('googleads.yaml', 'w') as f:
                f.write(yaml_content)

            print('Token de atualização adicionado ao arquivo googleads.yaml')
        except Exception as e:
            print(f'Erro ao atualizar googleads.yaml: {e}')

    except Exception as e:
        print(f"Erro durante o processo de autenticação: {e}")


if __name__ == '__main__':
    main()
