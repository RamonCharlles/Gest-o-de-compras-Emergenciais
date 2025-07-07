import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

DATA_FILE = "cadastro_compras.csv"

def carregar_dados():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, dtype={"ID": str})
        # Converter datas para datetime
        df["Data Solicitação"] = pd.to_datetime(df["Data Solicitação"], errors='coerce')
        df["Previsão Entrega"] = pd.to_datetime(df["Previsão Entrega"], errors='coerce')
        df["Lead Time"] = (df["Previsão Entrega"] - df["Data Solicitação"]).dt.days
        return df
    else:
        cols = [
            "ID", "Nome", "Registro", "OS", "RC", "TAG", "Descrição", "Tipo",
            "Data Solicitação", "Lead Time", "Status", "Previsão Entrega",
            "Motivo Atraso", "Ordem de Compra", "Prioridade", "Observações"
        ]
        return pd.DataFrame(columns=cols)

def salvar_dados(df):
    df.to_csv(DATA_FILE, index=False)

# Tela do Requisitante (Cadastro)
def tela_requisitante():
    st.title("📋 Cadastro de Compras Emergenciais - Requisitante")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome completo")
        registro = st.text_input("Registro / Matrícula")
        os_num = st.text_input("Número da OS")
        rc_num = st.text_input("Número da RC")
        tag = st.text_input("TAG do Equipamento")
        descricao = st.text_area("Descrição do item")
        tipo = st.selectbox("Tipo de solicitação", ["Material", "Serviço"])
        data_solicitacao = datetime.today().strftime("%Y-%m-%d")

        submit = st.form_submit_button("Cadastrar solicitação")
        if submit:
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
                "Data Solicitação": data_solicitacao,
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

# Tela do Comprador (Atualização)
def tela_comprador():
    st.title("📦 Painel do Comprador - Atualização de Solicitações")
    df = carregar_dados()
    if df.empty:
        st.warning("Nenhuma solicitação cadastrada.")
        return
    
    # Filtrar pendentes/andamento
    pendentes = df[df["Status"].isin(["Pendente", "Em Andamento", "Aguardando Fornecedor", "Em cotação", "Em aprovação no 14", "Em aprovação no 15", "Em Atraso"])]

    if pendentes.empty:
        st.info("Não há solicitações pendentes ou em andamento.")
        return

    # Separar Material e Serviço
    st.subheader("🧰 Materiais (Peças)")
    materiais = pendentes[pendentes["Tipo"] == "Material"]
    st.dataframe(materiais[["ID", "Descrição", "TAG", "Status", "Previsão Entrega", "Ordem de Compra"]])

    st.subheader("🛠️ Serviços")
    servicos = pendentes[pendentes["Tipo"] == "Serviço"]
    st.dataframe(servicos[["ID", "Descrição", "TAG", "Status", "Previsão Entrega", "Ordem de Compra"]])

    st.download_button("📥 Exportar solicitações pendentes para CSV", pendentes.to_csv(index=False).encode('utf-8'), file_name="solicitacoes_pendentes.csv", mime="text/csv")

    opcoes = (pendentes["ID"].astype(str) + " - " + pendentes["Descrição"]).tolist()
    selecionada = st.selectbox("Selecione uma solicitação para atualizar", opcoes)

    if selecionada:
        id_selecionado = selecionada.split(" - ")[0]
        linha = df[df["ID"] == id_selecionado].iloc[0]

        st.markdown("### Detalhes da solicitação")
        st.write(f"**Descrição:** {linha['Descrição']}")
        st.write(f"**TAG:** {linha['TAG']}")
        st.write(f"**Tipo:** {linha['Tipo']}")
        st.write(f"**Solicitante:** {linha['Nome']} ({linha['Registro']})")
        st.write(f"**Data da Solicitação:** {linha['Data Solicitação']}")
        st.write(f"**Status atual:** {linha['Status']}")
        st.write(f"**Previsão de entrega atual:** {linha['Previsão Entrega'] if pd.notna(linha['Previsão Entrega']) else '-'}")

        with st.form("form_atualizacao"):
            nova_previsao = st.date_input("Nova previsão de entrega", value=datetime.today())
            novo_status = st.selectbox("Status do processo", [
                "Pendente", "Em cotação", "Em aprovação no 14", "Em aprovação no 15",
                "Em Andamento", "Aguardando Fornecedor", "Cancelado", "Em Atraso"
            ], index=["Pendente", "Em cotação", "Em aprovação no 14", "Em aprovação no 15",
                     "Em Andamento", "Aguardando Fornecedor", "Cancelado", "Em Atraso"].index(linha["Status"]) if linha["Status"] in ["Pendente", "Em cotação", "Em aprovação no 14", "Em aprovação no 15", "Em Andamento", "Aguardando Fornecedor", "Cancelado", "Em Atraso"] else 0)
            
            ordem_compra = ""
            if novo_status in ["Em aprovação no 14", "Em aprovação no 15"]:
                ordem_compra = st.text_input("Número da Ordem de Compra", value=linha["Ordem de Compra"])
            
            motivo_atraso = st.text_area("Motivo do atraso (se houver alteração de prazo)", value=linha["Motivo Atraso"])

            enviar = st.form_submit_button("Atualizar solicitação")
            if enviar:
                idx = df[df["ID"] == id_selecionado].index[0]
                data_antiga = df.at[idx, "Previsão Entrega"]
                nova_data_str = nova_previsao.strftime("%Y-%m-%d")
                status_final = novo_status

                if pd.notna(data_antiga):
                    try:
                        data_antiga_dt = pd.to_datetime(data_antiga)
                        if nova_previsao > data_antiga_dt:
                            status_final = "Em Atraso"
                            if not motivo_atraso.strip():
                                st.error("Motivo do atraso é obrigatório quando a previsão é adiada!")
                                return
                    except:
                        pass

                df.at[idx, "Previsão Entrega"] = nova_data_str
                df.at[idx, "Status"] = status_final
                df.at[idx, "Motivo Atraso"] = motivo_atraso
                if novo_status in ["Em aprovação no 14", "Em aprovação no 15"]:
                    df.at[idx, "Ordem de Compra"] = ordem_compra

                salvar_dados(df)
                st.success("Solicitação atualizada com sucesso!")
                st.experimental_rerun()

# Tela do Administrador (Análise, filtros, gráficos, edição)
def tela_administrador():
    st.title("📊 Painel do Administrador - Análise e Gestão")
    df = carregar_dados()

    if df.empty:
        st.info("Nenhuma solicitação cadastrada.")
        return

    # Preparar dados
    df["Data Solicitação"] = pd.to_datetime(df["Data Solicitação"], errors='coerce')
    df["Previsão Entrega"] = pd.to_datetime(df["Previsão Entrega"], errors='coerce')
    df["Lead Time"] = (df["Previsão Entrega"] - df["Data Solicitação"]).dt.days

    with st.expander("🔎 Filtros de análise"):
        filtro_status = st.multiselect("Filtrar por Status:", options=df["Status"].dropna().unique(), default=df["Status"].dropna().unique())
        filtro_prioridade = st.multiselect("Filtrar por Prioridade:", options=df["Prioridade"].dropna().unique(), default=df["Prioridade"].dropna().unique())
        filtro_tipo = st.multiselect("Filtrar por Tipo (Material/Serviço):", options=df["Tipo"].dropna().unique(), default=df["Tipo"].dropna().unique())
        min_data = df["Data Solicitação"].min()
        max_data = df["Data Solicitação"].max()
        filtro_datas = st.date_input("Filtrar por intervalo de data da solicitação:", [min_data, max_data])

    df_filtrado = df[
        (df["Status"].isin(filtro_status)) &
        (df["Prioridade"].isin(filtro_prioridade)) &
        (df["Tipo"].isin(filtro_tipo)) &
        (df["Data Solicitação"] >= pd.Timestamp(filtro_datas[0])) &
        (df["Data Solicitação"] <= pd.Timestamp(filtro_datas[1]))
    ]

    st.markdown("### 📌 Indicadores Gerais")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Solicitações", len(df_filtrado))
    with col2:
        media_lead = int(df_filtrado["Lead Time"].mean(skipna=True)) if not df_filtrado["Lead Time"].isna().all() else "-"
        st.metric("Média Lead Time (dias)", media_lead)
    with col3:
        st.metric("Solicitações Pendentes", len(df_filtrado[df_filtrado["Status"] != "Processo Concluído"]))
    with col4:
        st.metric("Solicitações em Atraso", len(df_filtrado[df_filtrado["Status"] == "Em Atraso"]))

    st.markdown("### 📊 Gráficos")
    status_counts = df_filtrado["Status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Quantidade"]
    fig_status = px.bar(status_counts, x="Status", y="Quantidade", color="Status", text="Quantidade")
    st.plotly_chart(fig_status, use_container_width=True)

    leadtime_tipo = df_filtrado.groupby("Tipo")["Lead Time"].mean().reset_index()
    fig_lead_tipo = px.bar(leadtime_tipo, x="Tipo", y="Lead Time", color="Tipo", text="Lead Time",
                           title="Média de Lead Time por Tipo")
    st.plotly_chart(fig_lead_tipo, use_container_width=True)

    df_filtrado["Mes Solicitação"] = df_filtrado["Data Solicitação"].dt.to_period("M").dt.to_timestamp()
    evolucao = df_filtrado.groupby("Mes Solicitação").size().reset_index(name="Quantidade")
    fig_evolucao = px.line(evolucao, x="Mes Solicitação", y="Quantidade", title="Evolução Mensal de Solicitações")
    st.plotly_chart(fig_evolucao, use_container_width=True)

    st.markdown("### 📋 Solicitações Detalhadas")
    st.dataframe(df_filtrado.reset_index(drop=True))

    st.markdown("### ✏️ Gerenciar Solicitação")
    opcoes = (df_filtrado["ID"].astype(str) + " - " + df_filtrado["Descrição"]).tolist()
    selecionada = st.selectbox("Selecione uma solicitação para editar:", options=opcoes)

    if selecionada:
        id_sel = selecionada.split(" - ")[0]
        linha_sel = df_filtrado[df_filtrado["ID"] == id_sel]
        if not linha_sel.empty:
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
    perfil = st.sidebar.selectbox("Selecione o Perfil", ["Requisitante", "Comprador", "Administrador"])
    if perfil == "Requisitante":
        tela_requisitante()
    elif perfil == "Comprador":
        tela_comprador()
    elif perfil == "Administrador":
        tela_administrador()

if __name__ == "__main__":
    main()

