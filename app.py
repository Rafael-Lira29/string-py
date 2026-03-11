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

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #00FF41; font-family: 'Courier New', monospace; }
    h1, h2, h3 { color: #00FF41; }
    .stButton>button { border: 1px solid #00FF41; color: #00FF41; background-color: transparent; }
    .stButton>button:hover { background-color: #00FF41; color: #0E1117; }
    </style>
    """, unsafe_allow_html=True)

st.title("> String.py_")
st.caption("Terminal de Produção | Ateliê Isabelle")

# --- 3. MODO ROOT (ACESSO DO RAFAEL) ---
with st.sidebar:
    st.header("🔐 Modo Root")
    senha = st.text_input("Chave de Acesso:", type="password")
    
    # A senha padrão está definida como "SextaFeira". Você pode alterar aqui no código.
    if senha == "SextaFeira":
        st.success("Acesso Liberado, Rafael.")
        valor_hora = st.number_input("Valor da Hora Técnica (R$):", min_value=1.0, value=15.0, step=1.0)
        overhead = st.slider("Custos Fixos (Overhead) %:", 0, 30, 5) / 100
        markup = st.number_input("Markup (Lucro):", min_value=1.0, value=1.4, step=0.1)
    else:
        # Se a senha não for inserida, o sistema roda com os valores fixos (Ideais para a Isabelle)
        valor_hora = 15.0
        overhead = 0.05
        markup = 1.4
        st.info("Interface otimizada para produção. Parâmetros de cálculo operando em Background.")

# --- 4. ENTRADA DE DADOS (INTERFACE ISABELLE) ---
st.subheader("📝 Detalhes da Nova Peça")

modelo = st.text_input("Identificador do Modelo (Ex: Bolsa Aurora):")
tempo = st.number_input("Horas de Execução Focada:", min_value=0.5, value=4.0, step=0.5)

st.divider()

# --- 5. TABELA DINÂMICA DE MATERIAIS ---
st.subheader("🧶 Insumos Utilizados")
st.write("Adicione os materiais e seus custos. A tabela soma automaticamente.")

# Cria uma tabela vazia inicial na memória do sistema
if 'tabela_materiais' not in st.session_state:
    st.session_state.tabela_materiais = pd.DataFrame([{"Item/Material": "Fio de Malha (Exemplo)", "Custo (R$)": 0.0}])

# O data_editor permite que a Isabelle adicione ou exclua linhas dinamicamente
df_materiais = st.data_editor(
    st.session_state.tabela_materiais, 
    num_rows="dynamic", 
    use_container_width=True,
    hide_index=True
)

# O Python soma a coluna de Custo automaticamente
custo_material = df_materiais["Custo (R$)"].sum()
st.info(f"**Custo Total de Insumos Calculado: R$ {custo_material:.2f}**")

# --- 6. LÓGICA DE PROCESSAMENTO ---
custo_base = (tempo * valor_hora) + custo_material
custo_total = custo_base * (1 + overhead)
preco_final = custo_total * markup
lucro_liquido = preco_final - custo_total

st.divider()

# --- 7. EXECUÇÃO E PERSISTÊNCIA ---
if st.button("PROCESSAR E SALVAR NO BANCO"):
    if not modelo:
        st.warning("⚠️ O Identificador do Modelo não pode ficar vazio.")
    elif custo_material == 0:
        st.warning("⚠️ Adicione pelo menos um valor de material na tabela acima.")
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric("Custo Total", f"R$ {custo_total:.2f}")
        m2.metric("Preço Sugerido", f"R$ {preco_final:.2f}")
        m3.metric("Lucro Líquido", f"R$ {lucro_liquido:.2f}")
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
        c.execute('''
            INSERT INTO vendas (data_registro, modelo, horas, custo_material, preco_venda, lucro_liquido)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (data_atual, modelo, tempo, custo_material, preco_final, lucro_liquido))
        conn.commit()
        conn.close()
        
        st.success("💾 Dados gravados com sucesso.")

# --- 8. VISUALIZAÇÃO (DASHBOARD) ---
st.divider()
st.subheader("📊 Histórico de Produção")

conn = sqlite3.connect('database.db')
df = pd.read_sql_query("SELECT * FROM vendas ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.caption("O banco de dados está aguardando o primeiro registro.")