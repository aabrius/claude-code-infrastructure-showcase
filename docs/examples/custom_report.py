#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Exemplo de relatório personalizado utilizando a API do Ad Manager

from reports import generate_report
import sys
import os
import pandas as pd
import logging
from datetime import datetime, timedelta

# Adicionar o diretório pai ao path para importar os módulos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def generate_performance_by_device_report(start_date=None, end_date=None, days_back=30):
    """
    Gera um relatório de desempenho por dispositivo

    Args:
        start_date: Data de início no formato 'AAAA-MM-DD'
        end_date: Data de fim no formato 'AAAA-MM-DD'
        days_back: Número de dias para olhar para trás (usado se start_date/end_date não forem fornecidos)

    Returns:
        DataFrame pandas com os dados do relatório
    """
    # Definir as dimensões do relatório
    dimensions = [
        'DATE',
        'DEVICE_CATEGORY_NAME',
        'COUNTRY_NAME',
        'ADVERTISER'
    ]

    # Definir as métricas/colunas do relatório
    columns = [
        'TOTAL_IMPRESSIONS',
        'TOTAL_CLICKS',
        'TOTAL_REVENUE',
        'CTR',
        'TOTAL_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS',
        'ACTIVE_VIEW_VIEWABLE_IMPRESSION_RATE'
    ]

    # Gerar o relatório usando a função do módulo reports
    df = generate_report(
        report_type='HISTORICAL',
        dimensions=dimensions,
        columns=columns,
        start_date=start_date,
        end_date=end_date,
        days_back=days_back
    )

    return df


def analyze_device_performance(df):
    """
    Analisa os dados de desempenho por dispositivo

    Args:
        df: DataFrame pandas com os dados do relatório

    Returns:
        DataFrame pandas com a análise
    """
    # Agrupar por dispositivo e calcular as médias/totais
    if df is not None and not df.empty:
        analysis = df.groupby('DEVICE_CATEGORY_NAME').agg({
            'TOTAL_IMPRESSIONS': 'sum',
            'TOTAL_CLICKS': 'sum',
            'TOTAL_REVENUE': 'sum',
            'CTR': 'mean',
            'ACTIVE_VIEW_VIEWABLE_IMPRESSION_RATE': 'mean'
        }).reset_index()

        # Calcular o CTR manualmente como confirmação
        analysis['CALCULATED_CTR'] = (
            analysis['TOTAL_CLICKS'] / analysis['TOTAL_IMPRESSIONS']) * 100

        # Calcular a distribuição percentual de impressões por dispositivo
        total_impressions = analysis['TOTAL_IMPRESSIONS'].sum()
        analysis['IMPRESSION_SHARE'] = (
            analysis['TOTAL_IMPRESSIONS'] / total_impressions) * 100

        # Calcular a receita por mil impressões (RPM)
        analysis['RPM'] = (analysis['TOTAL_REVENUE'] /
                           analysis['TOTAL_IMPRESSIONS']) * 1000

        return analysis
    else:
        logger.error("Sem dados para análise")
        return None


def main():
    # Calcular datas para os últimos 30 dias
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Formatar as datas para o formato 'AAAA-MM-DD'
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    logger.info(
        f"Gerando relatório de desempenho por dispositivo de {start_date_str} a {end_date_str}")

    # Gerar o relatório
    df = generate_performance_by_device_report(
        start_date=start_date_str,
        end_date=end_date_str
    )

    # Analisar os dados
    analysis = analyze_device_performance(df)

    if analysis is not None:
        # Exibir a análise
        pd.set_option('display.float_format', '{:.2f}'.format)
        print("\n=== Análise de Desempenho por Dispositivo ===")
        print(analysis)

        # Salvar a análise em um arquivo CSV
        output_file = f"device_performance_{end_date.strftime('%Y%m%d')}.csv"
        analysis.to_csv(output_file, index=False)
        logger.info(f"Análise salva em {output_file}")

        # Salvar o relatório completo
        if df is not None:
            detailed_file = f"device_performance_detailed_{end_date.strftime('%Y%m%d')}.csv"
            df.to_csv(detailed_file, index=False)
            logger.info(f"Relatório detalhado salvo em {detailed_file}")


if __name__ == "__main__":
    main()
