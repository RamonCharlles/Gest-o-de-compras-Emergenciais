import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

DATA_FILE = "cadastro_compras.csv"

def carregar_dados():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype={"ID": str})
        # Converter colunas de data para datetime, com coerção
        df["Data Solicitação"] = pd.to_datetime(df["Data Solicitação"], errors="coerce")
        df["Previsão Entrega"] = pd.to_datetime(df["Previsão Entrega"], errors="coerce")
        # Calcular lead time (dias)
        df["Lead Time"] = (df["Previsão Entrega"] - df["Data Solicitação"]).dt.days
        return df
    else:
        colunas = [
            "ID", "Nome", "Registro", "OS", "RC", "TAG", "Descrição", "Tipo",
            "Data Solicitação", "Lead Time", "Status", "Previsão Entrega",
            "Motivo Atraso", "Ordem de Compra", "Prioridade", "Observações"
        ]
        return pd.DataFrame(columns=colunas)

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

def tela_requisitante():
    st.title("📋 Cadastro de Compras Emergenciais")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo")
        registro = st.text_input("Registro / Matrícula")
        os_num = st.text_input("Número da OS")
        rc_num = st.text_input("Número da RC")
        tag = st.text_input("TAG do Equipamento")
        descricao = st.text_area("Descrição do item")
        tipo = st.selectbox("Tipo de solicitação", ["Material", "Serviço"])
        submit = st.form_submit_button("Cadastrar Solicitação")

        if submit:
            # Validação básica
            if not all([nome.strip(), registro.strip(), os_num.strip(), rc_num.strip(), tag.strip(), descricao.strip()]):
                st.error("Por favor, preencha todos os campos.")
                return
            df = carregar_dados()
            novo_id = str(len(df) + 1)
            novo_registro = {
                "ID": novo_id,
                "Nome": nome.strip(),
                "Registro": registro.strip(),
                "OS": os_num.strip(),
                "RC": rc_num.strip(),
                "TAG": tag.strip(),
                "Descrição": descricao.strip(),
                "Tipo": tipo,
                "Data Solicitação": datetime.today().strftime("%Y-%m-%d"),
                "Lead Time": None,
                "Status": "Pendente",
                "Previsão Entrega": None,
                "Motivo Atraso": "",
                "Ordem de Compra": "",
                "Prioridade": "Média",
                "Observações": ""
            }
            df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
            salvar_dados(df)
            st.success("Solicitação cadastrada com sucesso!")

def tela_comprador():
    st.title("📦 Painel do Comprador")
    df = carregar_dados()
    if df.empty:
        st.warning("Nenhuma solicitação cadastrada.")
        return

    # Filtra status relevantes para comprador
    status_validos = [
        "Pendente", "Em cotação", "Em aprovação no 14", "Em aprovação no 15",
        "Em Andamento", "Aguardando Fornecedor", "Em Atraso"
    ]
    df_pendentes = df[df["Status"].isin(status_validos)]

    if df_pendentes.empty:
        st.info("Não há solicitações para atualizar.")
        return

    st.subheader("Solicitações de Materiais")
    materiais = df_pendentes[df_pendentes["Tipo"] == "Material"]
    st.dataframe(materiais[["ID", "Descrição", "TAG", "Status", "Previsão Entrega", "Ordem de Compra"]])

    st.subheader("Solicitações de Serviços")
    servicos = df_pendentes[df_pendentes["Tipo"] == "Serviço"]
    st.dataframe(servicos[["ID", "Descrição", "TAG", "Status", "Previsão Entrega", "Ordem de Compra"]])

    st.download_button(
        label="Exportar solicitações pendentes para CSV",
        data=df_pendentes.to_csv(index=False).encode('utf-8'),
        file_name="solicitacoes_pendentes.csv",
        mime="text/csv"
    )

    opcoes = (df_pendentes["ID"].astype(str) + " - " + df_pendentes["Descrição"]).tolist()
    selecionada = st.selectbox("Selecione uma solicitação para atualizar", options=opcoes)

    if selecionada:
        id_sel = selecionada.split(" - ")[0]
        linha = df[df["ID"] == id_sel].iloc[0]

        st.markdown("### Dados da Solicitação")
        st.write(f"**Descrição:** {linha['Descrição']}")
        st.write(f"**TAG:** {linha['TAG']}")
        st.write(f"**Tipo:** {linha['Tipo']}")
        st.write(f"**Solicitante:** {linha['Nome']} ({linha['Registro']})")
        st.write(f"**Data Solicitação:** {linha['Data Solicitação']}")
        st.write(f"**Status atual:** {linha['Status']}")
        st.write(f"**Previsão de entrega:** {linha['Previsão Entrega'] if pd.notna(linha['Previsão Entrega']) else '-'}")

        with st.form("form_atualizacao"):
            nova_previsao = st.date_input("Nova previsão de entrega", value=datetime.today())
            novo_status = st.selectbox("Novo status", [
                "Pendente", "Em cotação", "Em aprovação no 14", "Em aprovação no 15",
                "Em Andamento", "Aguardando Fornecedor", "Cancelado", "Em Atraso"
            ], index=[
                "Pendente", "Em cotação", "Em aprovação no 14", "Em aprovação no 15",
                "Em Andamento", "Aguardando Fornecedor", "Cancelado", "Em Atraso"
            ].index(linha["Status"]) if linha["Status"] in [
                "Pendente", "Em cotação", "Em aprovação no 14", "Em aprovação no 15",
                "Em Andamento", "Aguardando Fornecedor", "Cancelado", "Em Atraso"] else 0)

            ordem_compra = ""
            if novo_status in ["Em aprovação no 14", "Em aprovação no 15"]:
                ordem_compra = st.text_input("Número da Ordem de Compra", value=linha["Ordem de Compra"])
            else:
                ordem_compra = ""

            motivo_atraso = st.text_area("Motivo do atraso (se houver alteração de prazo)", value=linha["Motivo Atraso"])

            enviar = st.form_submit_button("Atualizar")

            if enviar:
                idx = df[df["ID"] == id_sel].index[0]

                data_antiga = df.at[idx, "Previsão Entrega"]
                nova_data_str = nova_previsao.strftime("%Y-%m-%d")
                status_final = novo_status

                # Checar atraso e motivo
                if pd.notna(data_antiga):
                    try:
                        data_antiga_dt = pd.to_datetime(data_antiga)
                        if nova_previsao > data_antiga_dt:
                            status_final = "Em Atraso"
                            if not motivo_atraso.strip():
                                st.error("Informe o motivo do atraso.")
                                return
                    except:
                        pass

                df.at[idx, "Previsão Entrega"] = nova_data_str
                df.at[idx, "Status"] = status_final
                df.at[idx, "Motivo Atraso"] = motivo_atraso
                df.at[idx, "Ordem de Compra"] = ordem_compra

                salvar_dados(df)
                st.success("Solicitação atualizada com sucesso!")
                st.experimental_rerun()

def tela_administrador():
    st.title("📊 Painel do Administrador")

    df = carregar_dados()
    if df.empty:
        st.info("Nenhuma solicitação cadastrada.")
        return

    # Converter datas e calcular Lead Time
    df["Data Solicitação"] = pd.to_datetime(df["Data Solicitação"], errors="coerce")
    df["Previsão Entrega"] = pd.to_datetime(df["Previsão Entrega"], errors="coerce")
    df["Lead Time"] = (df["Previsão Entrega"] - df["Data Solicitação"]).dt.days

    # Filtros
    with st.expander("Filtros de análise"):
        status_sel = st.multiselect("Status", df["Status"].dropna().unique(), default=df["Status"].dropna().unique())
        prioridade_sel = st.multiselect("Prioridade", df["Prioridade"].dropna().unique(), default=df["Prioridade"].dropna().unique())
        tipo_sel = st.multiselect("Tipo", df["Tipo"].dropna().unique(), default=df["Tipo"].dropna().unique())
        data_min = df["Data Solicitação"].min()
        data_max = df["Data Solicitação"].max()
        datas_sel = st.date_input("Intervalo Data Solicitação", [data_min, data_max])

    # Aplicar filtros
    df_filtrado = df[
        (df["Status"].isin(status_sel)) &
        (df["Prioridade"].isin(prioridade_sel)) &
        (df["Tipo"].isin(tipo_sel)) &
        (df["Data Solicitação"] >= pd.Timestamp(datas_sel[0])) &
        (df["Data Solicitação"] <= pd.Timestamp(datas_sel[1]))
    ]

    # Indicadores
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de solicitações", len(df_filtrado))
    media_lead = int(df_filtrado["Lead Time"].mean()) if not df_filtrado["Lead Time"].isna().all() else "-"
    col2.metric("Média Lead Time (dias)", media_lead)
    col3.metric("Solicitações Pendentes", len(df_filtrado[df_filtrado["Status"] != "Processo Concluído"]))
    col4.metric("Solicitações em Atraso", len(df_filtrado[df_filtrado["Status"] == "Em Atraso"]))

    # Gráficos
    st.subheader("Distribuição por Status")
    status_counts = df_filtrado["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Quantidade"]
    fig_status = px.bar(status_counts, x="Status", y="Quantidade", color="Status", text="Quantidade")
    st.plotly_chart(fig_status, use_container_width=True)

    st.subheader("Média Lead Time por Tipo")
    lead_tipo = df_filtrado.groupby("Tipo")["Lead Time"].mean().reset_index()
    fig_lead_tipo = px.bar(lead_tipo, x="Tipo", y="Lead Time", color="Tipo", text="Lead Time")
    st.plotly_chart(fig_lead_tipo, use_container_width=True)

    # Tabela com detalhes
    st.subheader("Solicitações detalhadas")
    st.dataframe(df_filtrado.reset_index(drop=True))

    # Gerenciamento de solicitação individual
    st.subheader("Editar Solicitação")
    opcoes = (df_filtrado["ID"].astype(str) + " - " + df_filtrado["Descrição"]).tolist()
    selecionada = st.selectbox("Selecione uma solicitação para editar", options=opcoes)

    if selecionada:
        id_sel = selecionada.split(" - ")[0]
        linha_sel = df_filtrado[df_filtrado["ID"] == id_sel]
        if linha_sel.empty:
            st.error("Solicitação não encontrada.")
            return

        idx = linha_sel.index[0]

        st.markdown(f"**ID:** {linha_sel.at[idx, 'ID']}")
        st.markdown(f"**Nome:** {linha_sel.at[idx, 'Nome']} ({linha_sel.at[idx, 'Registro']})")
        st.markdown(f"**OS:** {linha_sel.at[idx, 'OS']}")
        st.markdown(f"**RC:** {linha_sel.at[idx, 'RC']}")
        st.markdown(f"**TAG:** {linha_sel.at[idx, 'TAG']}")
        st.markdown(f"**Descrição:** {linha_sel.at[idx, 'Descrição']}")
        st.markdown(f"**Tipo:** {linha_sel.at[idx, 'Tipo']}")
        st.markdown(f"**Data Solicitação:** {linha_sel.at[idx, 'Data Solicitação'].strftime('%Y-%m-%d') if pd.notna(linha_sel.at[idx, 'Data Solicitação']) else '-'}")
        st.markdown(f"**Previsão Entrega:** {linha_sel.at[idx, 'Previsão Entrega'].strftime('%Y-%m-%d') if pd.notna(linha_sel.at[idx, 'Previsão Entrega']) else '-'}")
        st.markdown(f"**Status:** {linha_sel.at[idx, 'Status']}")
        st.markdown(f"**Motivo do Atraso:** {linha_sel.at[idx, 'Motivo Atraso']}")
        st.markdown(f"**Ordem de Compra:** {linha_sel.at[idx, 'Ordem de Compra']}")
        st.markdown(f"**Prioridade:** {linha_sel.at[idx, 'Prioridade']}")
        st.markdown(f"**Observações:** {linha_sel.at[idx, 'Observações']}")
        st.markdown(f"**Lead Time:** {linha_sel.at[idx, 'Lead Time']} dias")

        st.markdown("---")
        nova_prioridade = st.selectbox("Alterar Prioridade", ["Baixa", "Média", "Alta", "Crítica"], index=["Baixa", "Média", "Alta", "Crítica"].index(linha_sel.at[idx, "Prioridade"]))
        nova_observacao = st.text_area("Atualizar Observações", value=linha_sel.at[idx, "Observações"])
        marcar_concluido = st.checkbox("Marcar como concluído")

        if st.button("Salvar Alterações"):
            df.at[idx, "Prioridade"] = nova_prioridade
            df.at[idx, "Observações"] = nova_observacao
            if marcar_concluido:
                df.at[idx, "Status"] = "Processo Concluído"
                try:
                    lead_time_total = (df.at[idx, "Previsão Entrega"] - df.at[idx, "Data Solicitação"]).days
                    df.at[idx, "Lead Time"] = lead_time_total
                except:
                    pass
            salvar_dados(df)
            st.success("Alterações salvas com sucesso!")
            st.experimental_rerun()

def main():
    st.sidebar.title("Menu")
    perfil = st.sidebar.selectbox("Selecione seu perfil:", ["Requisitante", "Comprador", "Administrador"])

    if perfil == "Requisitante":
        tela_requisitante()
    elif perfil == "Comprador":
        tela_comprador()
    else:
        tela_administrador()

if __name__ == "__main__":
    main()

