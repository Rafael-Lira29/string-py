import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. INICIALIZAÇÃO DO BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_registro TEXT,
            modelo TEXT,
            horas REAL,
            custo_material REAL,
            preco_venda REAL,
            lucro_liquido REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 2. CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="String.py", page_icon="🧵", layout="centered")

# Estilização CSS inspirada em terminais de código
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #00FF41; font-family: 'Courier New', monospace; }
    h1, h2, h3 { color: #00FF41; }
    .stButton>button { border: 1px solid #00FF41; color: #00FF41; background-color: transparent; }
    .stButton>button:hover { background-color: #00FF41; color: #0E1117; }
    </style>
    """, unsafe_allow_html=True)

st.title("> String.py_")
st.caption("Terminal de Precificação e Gestão | Ateliê Isabelle")

# --- 3. PARÂMETROS GLOBAIS (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Variáveis Globais")
    valor_hora = st.number_input("Valor da Hora Técnica (R$):", min_value=1.0, value=30.0, step=1.0)
    overhead = st.slider("Custos Fixos (Overhead) %:", 0, 30, 5) / 100

# --- 4. ENTRADA DE DADOS ---
st.subheader("📝 Novo Objeto (Bolsa)")

modelo = st.text_input("Identificador do Modelo (Ex: Bolsa Aurora):")

col1, col2, col3 = st.columns(3)
with col1:
    tempo = st.number_input("Horas Execução:", min_value=0.5, value=5.0, step=0.5)
with col2:
    custo_material = st.number_input("Custo Material (R$):", min_value=0.0, value=50.0, step=1.0)
with col3:
    markup = st.number_input("Markup (Lucro):", min_value=1.0, value=2.0, step=0.1)

# --- 5. LÓGICA DE PROCESSAMENTO ---
custo_base = (tempo * valor_hora) + custo_material
custo_total = custo_base * (1 + overhead)
preco_final = custo_total * markup
lucro_liquido = preco_final - custo_total

st.divider()

# --- 6. EXECUÇÃO E PERSISTÊNCIA ---
if st.button("EXECUTAR CÁLCULO E SALVAR"):
    if not modelo:
        st.warning("⚠️ O Identificador do Modelo não pode ficar vazio.")
    else:
        # Exibição dos resultados
        m1, m2, m3 = st.columns(3)
        m1.metric("Custo Total", f"R$ {custo_total:.2f}")
        m2.metric("Preço Sugerido", f"R$ {preco_final:.2f}")
        m3.metric("Lucro Líquido", f"R$ {lucro_liquido:.2f}")
        
        # Gravação no Banco de Dados
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        c.execute('''
            INSERT INTO vendas (data_registro, modelo, horas, custo_material, preco_venda, lucro_liquido)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data_atual, modelo, tempo, custo_material, preco_final, lucro_liquido))
        conn.commit()
        conn.close()
        
        st.success("💾 Dados gravados no banco de dados com sucesso.")

# --- 7. VISUALIZAÇÃO (DASHBOARD) ---
st.divider()
st.subheader("📊 Histórico de Registros")

conn = sqlite3.connect('database.db')
df = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("O banco de dados está aguardando o primeiro registro.")