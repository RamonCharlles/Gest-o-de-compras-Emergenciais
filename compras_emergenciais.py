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
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=[
            "ID", "Nome", "Registro", "OS", "RC", "Descrição", "Tipo",
            "Data Solicitação", "Lead Time", "Status", "Previsão Entrega",
            "Motivo Atraso", "Prioridade", "Observações"
        ])

# Salva os dados

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

# Tela de cadastro

def tela_cadastro():
    st.title("📋 Cadastro de Compras Emergenciais")

    with st.form("cadastro_form"):
        nome = st.text_input("Nome do Requisitante")
        registro = st.text_input("Registro / Matrícula")
        os_num = st.text_input("Número da OS")
        rc_num = st.text_input("Número da RC")
        descricao = st.text_area("Descrição do Item")
        tipo = st.selectbox("Tipo de Solicitação", ["Material", "Serviço"])
        data_solicitacao = datetime.today().strftime("%Y-%m-%d")

        submitted = st.form_submit_button("Cadastrar Solicitação")

        if submitted:
            if not (nome and registro and os_num and rc_num and descricao):
                st.error("Todos os campos devem ser preenchidos.")
            else:
                df = carregar_dados()
                novo_registro = {
                    "ID": str(uuid.uuid4()),
                    "Nome": nome,
                    "Registro": registro,
                    "OS": os_num,
                    "RC": rc_num,
                    "Descrição": descricao,
                    "Tipo": tipo,
                    "Data Solicitação": data_solicitacao,
                    "Lead Time": "",
                    "Status": "Pendente",
                    "Previsão Entrega": "",
                    "Motivo Atraso": "",
                    "Prioridade": "Média",
                    "Observações": ""
                }
                df = df.append(novo_registro, ignore_index=True)
                salvar_dados(df)
                st.success("Solicitação cadastrada com sucesso!")

# Tela do comprador

def tela_comprador():
    st.title("📦 Painel do Comprador - Atualização de Solicitações")

    df = carregar_dados()

    if df.empty:
        st.warning("Nenhuma solicitação registrada ainda.")
        return

    pendentes = df[df["Status"].isin(["Pendente", "Em Andamento", "Aguardando Fornecedor"])]

    if pendentes.empty:
        st.info("Não há solicitações pendentes ou em andamento.")
        return

    opcoes = pendentes["ID"] + " - " + pendentes["Descrição"]
    selecionada = st.selectbox("Selecione a solicitação para atualizar", options=opcoes)

    if selecionada:
        id_selecionado = selecionada.split(" - ")[0]
        linha = df[df["ID"] == id_selecionado].iloc[0]

        st.markdown("### Informações da Solicitação")
        st.write(f"**Descrição:** {linha['Descrição']}")
        st.write(f"**Solicitante:** {linha['Nome']} - Matrícula: {linha['Registro']}")
        st.write(f"**Data da Solicitação:** {linha['Data Solicitação']}")
        st.write(f"**Status Atual:** {linha['Status']}")

        with st.form("form_comprador"):
            nova_previsao = st.date_input("Previsão de Entrega", value=datetime.today())
            novo_status = st.selectbox("Status do Processo", [
                "Em Andamento", "Aguardando Fornecedor", "Cancelado", "Pendente"
            ])
            motivo_atraso = st.text_area("Motivo do Atraso (se houver alteração de prazo)")

            enviado = st.form_submit_button("Atualizar Solicitação")

            if enviado:
                df_copy = df.copy()
                idx = df_copy[df_copy["ID"] == id_selecionado].index[0]
                data_antiga = df_copy.at[idx, "Previsão Entrega"]
                nova_data_str = nova_previsao.strftime("%Y-%m-%d")
                status_final = novo_status

                if data_antiga:
                    try:
                        data_antiga_dt = datetime.strptime(data_antiga, "%Y-%m-%d")
                        if nova_previsao > data_antiga_dt:
                            status_final = "Em Atraso"
                            if not motivo_atraso.strip():
                                st.error("Motivo do atraso é obrigatório!")
                                return
                    except:
                        pass

                df_copy.at[idx, "Previsão Entrega"] = nova_data_str
                df_copy.at[idx, "Status"] = status_final
                df_copy.at[idx, "Motivo Atraso"] = motivo_atraso

                if status_final == "Processo Concluído":
                    data_solicitacao = datetime.strptime(df_copy.at[idx, "Data Solicitação"], "%Y-%m-%d")
                    lead_time = (nova_previsao - data_solicitacao).days
                    df_copy.at[idx, "Lead Time"] = lead_time

                salvar_dados(df_copy)
                st.success("Solicitação atualizada com sucesso!")

# Tela do administrador

def tela_admin():
    st.title("🛠️ Painel do Administrador")
    df = carregar_dados()

    if df.empty:
        st.info("Nenhum dado cadastrado.")
        return

    with st.expander("🔍 Ver todas as solicitações"):
        st.dataframe(df)

    opcoes = df["ID"] + " - " + df["Descrição"]
    selecionada = st.selectbox("Selecione uma solicitação para gerenciar", opcoes)

    if selecionada:
        id_selecionado = selecionada.split(" - ")[0]
        idx = df[df["ID"] == id_selecionado].index[0]

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
