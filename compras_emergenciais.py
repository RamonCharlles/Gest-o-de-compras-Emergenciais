# compras_emergenciais_app.py

import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
import os

# Caminho do arquivo CSV
DATA_FILE = "cadastro_compras.csv"

# Carrega os dados

def carregar_dados():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, dtype={"ID": str})
    else:
        return pd.DataFrame(columns=[
            "ID", "Nome", "Registro", "OS", "RC", "TAG", "Descrição", "Tipo",
            "Data Solicitação", "Lead Time", "Status", "Previsão Entrega",
            "Motivo Atraso", "Ordem de Compra", "Prioridade", "Observações"
        ])

# Salva os dados

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

# Tela do administrador com painel dinâmico

def tela_admin():
    st.title("📊 Painel do Administrador - Visão Geral")
    df = carregar_dados()

    if df.empty:
        st.info("Nenhum dado cadastrado.")
        return

    # Métricas principais
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Solicitações", len(df))
    col2.metric("Solicitações Pendentes", len(df[df["Status"] == "Pendente"]))
    col3.metric("Solicitações Concluídas", len(df[df["Status"] == "Processo Concluído"]))

    # Filtros dinâmicos
    with st.expander("🔍 Filtrar Solicitações"):
        status_filtro = st.multiselect("Filtrar por Status", options=df["Status"].unique(), default=df["Status"].unique())
        tipo_filtro = st.multiselect("Filtrar por Tipo", options=df["Tipo"].unique(), default=df["Tipo"].unique())
        prioridade_filtro = st.multiselect("Filtrar por Prioridade", options=df["Prioridade"].unique(), default=df["Prioridade"].unique())

        df_filtrado = df[
            df["Status"].isin(status_filtro) &
            df["Tipo"].isin(tipo_filtro) &
            df["Prioridade"].isin(prioridade_filtro)
        ]

    st.markdown("### 📋 Solicitações Filtradas")
    st.dataframe(df_filtrado)
    st.download_button("📥 Exportar Relatório", df_filtrado.to_csv(index=False).encode("utf-8"), file_name="relatorio_compras.csv", mime="text/csv")

    st.markdown("### ✏️ Edição de Solicitação")
    opcoes = (df["ID"].astype(str) + " - " + df["Descrição"]).tolist()
    if not opcoes:
        st.warning("Nenhuma solicitação disponível.")
        return

    selecionada = st.selectbox("Selecione uma solicitação para gerenciar", opcoes)

    if selecionada and " - " in selecionada:
        id_str = selecionada.split(" - ")[0].strip()
        linha = df[df["ID"] == id_str]
        if linha.empty:
            st.error("Solicitação não encontrada.")
            return
        idx = linha.index[0]

        st.markdown(f"### 📄 Gerenciar Solicitação")
        prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Crítica"], index=["Baixa", "Média", "Alta", "Crítica"].index(df.at[idx, "Prioridade"]))
        observacoes = st.text_area("Observações", value=df.at[idx, "Observações"])
        concluir = st.checkbox("Marcar como Concluído")

        if st.button("Salvar Alterações"):
            df.at[idx, "Prioridade"] = prioridade
            df.at[idx, "Observações"] = observacoes
            if concluir:
                df.at[idx, "Status"] = "Processo Concluído"
                try:
                    data_solicitacao = datetime.strptime(df.at[idx, "Data Solicitação"], "%Y-%m-%d")
                    data_entrega = datetime.strptime(df.at[idx, "Previsão Entrega"], "%Y-%m-%d")
                    df.at[idx, "Lead Time"] = (data_entrega - data_solicitacao).days
                except:
                    pass
            salvar_dados(df)
            st.success("Solicitação atualizada com sucesso!")

