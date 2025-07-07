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

# Tela de cadastro

def tela_cadastro():
    # ... (mesma função)
    pass

# Tela do comprador

def tela_comprador():
    # ... (mesma função)
    pass

# Tela do administrador

def tela_admin():
    st.title("🛠️ Painel do Administrador")
    df = carregar_dados()

    if df.empty:
        st.info("Nenhum dado cadastrado.")
        return

    with st.expander("🔍 Ver todas as solicitações"):
        st.dataframe(df)

    st.markdown("### ✏️ Edição Individual de Solicitação")
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

    st.markdown("### 🔄 Atualizar Status em Massa")
    status_alvo = st.selectbox("Novo status para aplicar em massa", [
        "Pendente", "Em Andamento", "Aguardando Fornecedor",
        "Em cotação", "Em aprovação no 14", "Em aprovação no 15",
        "Processo Concluído", "Cancelado"
    ])
    filtro_prioridade = st.multiselect("Filtrar por Prioridade (opcional)", options=df["Prioridade"].unique())

    if filtro_prioridade:
        df_filtrado = df[df["Prioridade"].isin(filtro_prioridade)]
    else:
        df_filtrado = df.copy()

    selecionados = st.multiselect(
        "Selecione as solicitações para alterar o status",
        options=(df_filtrado["ID"] + " - " + df_filtrado["Descrição"]).tolist()
    )

    if st.button("Aplicar Status em Massa") and selecionados:
        ids_para_alterar = [s.split(" - ")[0] for s in selecionados]
        df.loc[df["ID"].isin(ids_para_alterar), "Status"] = status_alvo
        salvar_dados(df)
        st.success(f"Status atualizado para '{status_alvo}' em {len(ids_para_alterar)} solicitações.")

# Menu principal

def main():
    menu = st.sidebar.selectbox("Selecione o Perfil", ["Requisitante", "Comprador", "Administrador"])

    if menu == "Requisitante":
        tela_cadastro()
    elif menu == "Comprador":
        tela_comprador()
    elif menu == "Administrador":
        tela_admin()

if __name__ == "__main__":
    main()
