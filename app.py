import streamlit as st
import pandas as pd
import numpy as np
import requests
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Valuation: Graham & Bazin",
    page_icon="📈",
    layout="wide"
)


# --- FUNÇÃO DE EXTRAÇÃO E CÁLCULO (COM CACHE) ---
@st.cache_data(ttl=3600)  # Atualiza a cada 1 hora
def carregar_e_calcular_dados():
    # 1. Fazendo a extração diretamente do site (Substitui a lib fundamentus)
    url = "https://www.fundamentus.com.br/resultado.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    resposta = requests.get(url, headers=headers)

    # Lendo o HTML nativamente pelo Pandas (o site usa vírgula para decimal e ponto para milhar)
    df = pd.read_html(io.StringIO(resposta.text), decimal=",", thousands=".")[0]

    # 2. Limpeza básica para bater com o padrão anterior
    # Renomear "Cotação" para "Cotacao"
    df.rename(columns={'Cotação': 'Cotacao', 'Papel': 'Ativo'}, inplace=True)

    # Limpar a coluna Div.Yield que vem como texto (ex: "5,50%")
    # Mantemos o valor em formato de porcentagem (ex: 5.50 em vez de 0.055) para formatar no Streamlit
    df['Div.Yield'] = df['Div.Yield'].astype(str).str.replace('%', '', regex=False)
    df['Div.Yield'] = df['Div.Yield'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
    df['Div.Yield'] = pd.to_numeric(df['Div.Yield'], errors='coerce')

    # Garantir que as colunas essenciais sejam numéricas
    colunas_numericas = ['Cotacao', 'P/L', 'P/VP', 'Liq.2meses']
    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Cálculos de Valuation
    # Remover ativos com cotação zerada
    df = df[df['Cotacao'] > 0].copy()

    # Tratamento de zeros para evitar divisão por zero
    df['P/L'] = df['P/L'].replace(0, np.nan)
    df['P/VP'] = df['P/VP'].replace(0, np.nan)

    # Derivando VPA e LPA
    df['VPA'] = df['Cotacao'] / df['P/VP']
    df['LPA'] = df['Cotacao'] / df['P/L']

    # Graham: Exige VPA e LPA positivos
    graham_mask = (df['VPA'] > 0) & (df['LPA'] > 0)
    df['Preco_Justo_Graham'] = np.nan
    df.loc[graham_mask, 'Preco_Justo_Graham'] = np.sqrt(22.5 * df.loc[graham_mask, 'VPA'] * df.loc[graham_mask, 'LPA'])

    # Bazin: Baseado em dividendos (Meta de 6% ou 0.06).
    # Div.Yield está como número inteiro percentual (ex: 6.00), então dividimos por 100 no cálculo do dividendo absoluto.
    df['Dividendos_12m'] = df['Cotacao'] * (df['Div.Yield'] / 100.0)
    df['Preco_Teto_Bazin'] = df['Dividendos_12m'] / 0.06

    # Margens de Segurança
    df['Margem_Graham_%'] = ((df['Preco_Justo_Graham'] / df['Cotacao']) - 1) * 100
    df['Margem_Bazin_%'] = ((df['Preco_Teto_Bazin'] / df['Cotacao']) - 1) * 100

    return df


# --- INTERFACE DO USUÁRIO ---
st.title("📈 Dashboard de Valuation: Graham e Bazin")
st.markdown("Analise o Preço Justo e Preço Teto de ações da B3 com base nas fórmulas clássicas.")

# Carrega os dados
with st.spinner("Buscando dados no Fundamentus..."):
    df_completo = carregar_e_calcular_dados()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.header("Filtros de Análise")

filtro_liquidez = st.sidebar.number_input(
    "Liquidez Diária Mínima (R$)",
    min_value=0,
    value=200000,
    step=100000,
    help="Filtra empresas com baixa negociação na bolsa."
)

filtro_margem_graham = st.sidebar.slider(
    "Margem de Segurança Mínima - Graham (%)",
    min_value=-100, max_value=100, value=0, step=5
)

filtro_margem_bazin = st.sidebar.slider(
    "Margem de Segurança Mínima - Bazin (%)",
    min_value=-100, max_value=100, value=0, step=5
)

# Aplicando os filtros no dataframe
df_filtrado = df_completo[
    (df_completo['Liq.2meses'] >= filtro_liquidez) &
    (df_completo['Margem_Graham_%'] >= filtro_margem_graham) &
    (df_completo['Margem_Bazin_%'] >= filtro_margem_bazin)
    ].copy()

# Configurando o "Ativo" como o índice para a tabela do Streamlit ficar mais limpa
df_filtrado.set_index('Ativo', inplace=True)

# Colunas para exibir
colunas_exibicao = [
    'Cotacao', 'Div.Yield', 'Preco_Justo_Graham', 'Margem_Graham_%',
    'Preco_Teto_Bazin', 'Margem_Bazin_%'
]

# --- CONFIGURAÇÃO DE COLUNAS (Formatação Visual) ---
# Usamos o column_config do Streamlit para aplicar R$ e % sem converter os dados para strings.
# Isso preserva a ordenação numérica correta nas tabelas.
configuracao_colunas = {
    "Cotacao": st.column_config.NumberColumn(
        "Cotação",
        format="R$ %.2f"
    ),
    "Div.Yield": st.column_config.NumberColumn(
        "Dividend Yield",
        format="%.2f%%"
    ),
    "Preco_Justo_Graham": st.column_config.NumberColumn(
        "Preço Justo (Graham)",
        format="R$ %.2f"
    ),
    "Margem_Graham_%": st.column_config.NumberColumn(
        "Margem Graham",
        format="%.2f%%"
    ),
    "Preco_Teto_Bazin": st.column_config.NumberColumn(
        "Preço Teto (Bazin)",
        format="R$ %.2f"
    ),
    "Margem_Bazin_%": st.column_config.NumberColumn(
        "Margem Bazin",
        format="%.2f%%"
    )
}

# --- EXIBIÇÃO DOS DADOS ---
st.subheader(f"Ativos Encontrados: {len(df_filtrado)}")

tab1, tab2 = st.tabs(["Foco em Graham (Valor)", "Foco em Bazin (Dividendos)"])

with tab1:
    st.markdown("**Top Ativos com Maior Margem de Segurança (Fórmula de Graham)**")
    df_graham = df_filtrado.sort_values(by='Margem_Graham_%', ascending=False)[colunas_exibicao]
    st.dataframe(
        df_graham,
        column_config=configuracao_colunas,
        use_container_width=True,
        height=500
    )

with tab2:
    st.markdown("**Top Ativos com Maior Margem de Segurança (Fórmula de Bazin)**")
    df_bazin = df_filtrado.sort_values(by='Margem_Bazin_%', ascending=False)[colunas_exibicao]
    st.dataframe(
        df_bazin,
        column_config=configuracao_colunas,
        use_container_width=True,
        height=500
    )

# Rodapé explicativo
st.markdown("---")
st.caption(
    "⚠️ **Aviso Legal:** Esta ferramenta é apenas para fins de estudo e análise técnica. Não constitui recomendação de compra ou venda de ativos financeiros.")