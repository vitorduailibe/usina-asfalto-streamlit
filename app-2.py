
import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- Inicializa arquivos CSV se não existirem ---
ARQUIVOS = {
    "tickets": "tickets.csv",
    "estoque": "estoque.csv",
    "tracos": "tracos.csv",
    "producao": "producao.csv",
    "clientes": "clientes.csv",
    "motoristas": "motoristas.csv",
    "fornecedores": "fornecedores.csv"
}

for nome, caminho in ARQUIVOS.items():
    if not os.path.exists(caminho):
        pd.DataFrame().to_csv(caminho, index=False)

# --- Carregar dados ---
def carregar_csv(nome):
    caminho = ARQUIVOS[nome]
    try:
        df = pd.read_csv(caminho)
        return df
    except:
        return pd.DataFrame()

def salvar_csv(nome, df):
    df.to_csv(ARQUIVOS[nome], index=False)

# --- Menu lateral ---
st.set_page_config(page_title="Usina de Asfalto", layout="wide")
menu = st.sidebar.selectbox("Menu", [
    "Tickets de Saída",
    "Controle de Estoque",
    "Controle de Traço",
    "Controle de Produção",
    "Cadastros"
])

# --- Tickets ---
if menu == "Tickets de Saída":
    st.title("📤 Geração de Ticket de Saída")
    with st.form("ticket_form"):
        col1, col2 = st.columns(2)
        with col1:
            motorista = st.text_input("Motorista")
            cpf = st.text_input("CPF")
            rg = st.text_input("RG")
            placa = st.text_input("Placa Cavalo")
        with col2:
            cliente = st.text_input("Cliente")
            material = st.text_input("Material")
            quantidade = st.number_input("Quantidade (t)", min_value=0.0, step=0.1)
            operador = st.text_input("Operador")
        submitted = st.form_submit_button("Gerar Ticket")

    if submitted:
        df = carregar_csv("tickets")
        novo = {
            "ID": len(df) + 1,
            "Data": datetime.now().strftime("%d/%m/%Y"),
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Motorista": motorista,
            "CPF": cpf,
            "RG": rg,
            "Placa": placa,
            "Cliente": cliente,
            "Material": material,
            "Quantidade": quantidade,
            "Operador": operador
        }
        df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
        salvar_csv("tickets", df)
        st.success(f"Ticket gerado com sucesso! Número: {novo['ID']}")

    st.subheader("📄 Tickets Emitidos")
    st.dataframe(carregar_csv("tickets"))

# --- Estoque ---
elif menu == "Controle de Estoque":
    st.title("📦 Controle de Estoque")
    df = carregar_csv("estoque")

    with st.expander("Adicionar ou Atualizar Estoque"):
        nome = st.text_input("Nome do Insumo")
        tipo = st.text_input("Tipo")
        saldo = st.number_input("Saldo (kg)", min_value=0.0)
        salvar = st.button("Salvar/Atualizar")
        if salvar:
            df = df[df["Nome"] != nome]
            novo = pd.DataFrame([[nome, tipo, saldo]], columns=["Nome", "Tipo", "Saldo"])
            df = pd.concat([df, novo], ignore_index=True)
            salvar_csv("estoque", df)
            st.success("Estoque atualizado.")

    st.subheader("📊 Estoque Atual")
    st.dataframe(df)

# --- Traço ---
elif menu == "Controle de Traço":
    st.title("🧪 Controle de Traços")
    df = carregar_csv("tracos")
    with st.expander("Cadastrar Novo Traço"):
        nome = st.text_input("Nome do Traço")
        areia = st.number_input("Areia Média (kg/t)", min_value=0.0)
        brita1 = st.number_input("Brita 1 (kg/t)", min_value=0.0)
        brita0 = st.number_input("Brita 0 (kg/t)", min_value=0.0)
        cap = st.number_input("CAP 50/70 (kg/t)", min_value=0.0)
        salvar = st.button("Salvar Traço")
        if salvar:
            novo = pd.DataFrame([[nome, areia, brita1, brita0, cap]], columns=["Traço", "Areia", "Brita1", "Brita0", "CAP"])
            df = pd.concat([df, novo], ignore_index=True)
            salvar_csv("tracos", df)
            st.success("Traço salvo com sucesso.")
    st.subheader("🔍 Traços Cadastrados")
    st.dataframe(df)

# --- Produção ---
elif menu == "Controle de Produção":
    st.title("🏭 Controle de Produção")
    df_traco = carregar_csv("tracos")
    df_estoque = carregar_csv("estoque")
    df_producao = carregar_csv("producao")

    with st.form("producao_form"):
        traco_escolhido = st.selectbox("Selecionar Traço", df_traco["Traço"] if not df_traco.empty else [])
        toneladas = st.number_input("Quantidade Produzida (t)", min_value=0.0)
        registrar = st.form_submit_button("Registrar Produção")

    if registrar and traco_escolhido:
        linha = df_traco[df_traco["Traço"] == traco_escolhido].iloc[0]
        consumo = {
            "Areia": linha["Areia"] * toneladas,
            "Brita1": linha["Brita1"] * toneladas,
            "Brita0": linha["Brita0"] * toneladas,
            "CAP": linha["CAP"] * toneladas
        }
        for insumo, usado in consumo.items():
            df_estoque.loc[df_estoque["Nome"] == insumo, "Saldo"] -= usado

        salvar_csv("estoque", df_estoque)
        novo = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y"), traco_escolhido, toneladas]], columns=["Data", "Traço", "Toneladas"])
        df_producao = pd.concat([df_producao, novo], ignore_index=True)
        salvar_csv("producao", df_producao)
        st.success("Produção registrada e estoque atualizado.")

    st.subheader("📈 Produção Realizada")
    st.dataframe(df_producao)

# --- Cadastros ---
elif menu == "Cadastros":
    st.title("📋 Cadastros")
    aba = st.radio("Selecione", ["Clientes", "Motoristas", "Fornecedores"])
    df = carregar_csv(aba.lower())
    with st.expander("Adicionar Novo"):
        nome = st.text_input("Nome")
        doc = st.text_input("Documento (CNPJ ou CPF)")
        tipo = st.text_input("Tipo de Insumo / Contato")
        salvar = st.button("Salvar Cadastro")
        if salvar:
            novo = pd.DataFrame([[nome, doc, tipo]], columns=["Nome", "Documento", "Tipo"])
            df = pd.concat([df, novo], ignore_index=True)
            salvar_csv(aba.lower(), df)
            st.success("Cadastro salvo com sucesso.")

    st.subheader(f"📄 Lista de {aba}")
    st.dataframe(df)
