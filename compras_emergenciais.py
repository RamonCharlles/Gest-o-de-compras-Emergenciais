import streamlit as streamlit_app
import pandas as pandas_lib
import plotly.express as plotly_express
from datetime import datetime as data_hora
import os as sistema_operacional

# Caminho do arquivo CSV
CAMINHO_ARQUIVO_DADOS = "cadastro_compras.csv"

def carregar_dados():
    if sistema_operacional.path.exists(CAMINHO_ARQUIVO_DADOS):
        return pandas_lib.read_csv(CAMINHO_ARQUIVO_DADOS, dtype={"ID": str})
    else:
        return pandas_lib.DataFrame(columns=[
            "ID", "Nome", "Registro", "OS", "RC", "TAG", "Descrição", "Tipo",
            "Data Solicitação", "Lead Time", "Status", "Previsão Entrega",
            "Motivo Atraso", "Ordem de Compra", "Prioridade", "Observações"
        ])

def salvar_dados(dataframe):
    dataframe.to_csv(CAMINHO_ARQUIVO_DADOS, index=False)

def tela_administrador():
    streamlit_app.title("📊 Painel do Administrador - Análise e Gestão")
    dataframe = carregar_dados()
    
    if dataframe.empty:
        streamlit_app.info("Nenhuma solicitação cadastrada.")
        return
    
    # Converter datas para datetime
    dataframe["Data Solicitação"] = pandas_lib.to_datetime(dataframe["Data Solicitação"], errors='coerce')
    dataframe["Previsão Entrega"] = pandas_lib.to_datetime(dataframe["Previsão Entrega"], errors='coerce')
    
    # Calcular Lead Time
    dataframe["Lead Time"] = (dataframe["Previsão Entrega"] - dataframe["Data Solicitação"]).dt.days
    
    # --- FILTROS ---
    with streamlit_app.expander("🔎 Filtros de análise"):
        filtro_status = streamlit_app.multiselect("Filtrar por Status:", options=dataframe["Status"].unique(), default=dataframe["Status"].unique())
        filtro_prioridade = streamlit_app.multiselect("Filtrar por Prioridade:", options=dataframe["Prioridade"].unique(), default=dataframe["Prioridade"].unique())
        filtro_tipo = streamlit_app.multiselect("Filtrar por Tipo (Material/Serviço):", options=dataframe["Tipo"].unique(), default=dataframe["Tipo"].unique())
        filtro_data_inicio, filtro_data_fim = streamlit_app.date_input("Filtrar por intervalo de data de solicitação:", [dataframe["Data Solicitação"].min(), dataframe["Data Solicitação"].max()])
    
    # Aplicar filtros
    df_filtrado = dataframe[
        (dataframe["Status"].isin(filtro_status)) &
        (dataframe["Prioridade"].isin(filtro_prioridade)) &
        (dataframe["Tipo"].isin(filtro_tipo)) &
        (dataframe["Data Solicitação"] >= pandas_lib.Timestamp(filtro_data_inicio)) &
        (dataframe["Data Solicitação"] <= pandas_lib.Timestamp(filtro_data_fim))
    ]
    
    # --- INDICADORES GERAIS ---
    streamlit_app.markdown("### 📌 Indicadores Gerais")
    col1, col2, col3, col4 = streamlit_app.columns(4)
    with col1:
        streamlit_app.metric("Total de Solicitações", len(df_filtrado))
    with col2:
        media_lead_time = int(df_filtrado["Lead Time"].mean(skipna=True)) if not df_filtrado["Lead Time"].isna().all() else "-"
        streamlit_app.metric("Média de Lead Time (dias)", media_lead_time)
    with col3:
        streamlit_app.metric("Solicitações Pendentes", len(df_filtrado[df_filtrado["Status"] != "Processo Concluído"]))
    with col4:
        atraso_qtd = len(df_filtrado[df_filtrado["Status"] == "Em Atraso"])
        streamlit_app.metric("Solicitações em Atraso", atraso_qtd)
    
    # --- GRÁFICOS ---
    streamlit_app.markdown("### 📊 Visualizações Gráficas")
    # Status count
    status_contagem = df_filtrado["Status"].value_counts().reset_index()
    status_contagem.columns = ["Status", "Quantidade"]
    fig_status = plotly_express.bar(status_contagem, x="Status", y="Quantidade", color="Status", text="Quantidade")
    streamlit_app.plotly_chart(fig_status, use_container_width=True)
    
    # Lead time por tipo
    leadtime_tipo = df_filtrado.groupby("Tipo")["Lead Time"].mean().reset_index()
    fig_leadtime_tipo = plotly_express.bar(leadtime_tipo, x="Tipo", y="Lead Time", color="Tipo", text="Lead Time", title="Média de Lead Time por Tipo")
    streamlit_app.plotly_chart(fig_leadtime_tipo, use_container_width=True)
    
    # Evolução de solicitações por data
    df_filtrado["Data Solicitação Mês"] = df_filtrado["Data Solicitação"].dt.to_period('M').dt.to_timestamp()
    evolucao = df_filtrado.groupby("Data Solicitação Mês").size().reset_index(name="Quantidade")
    fig_evolucao = plotly_express.line(evolucao, x="Data Solicitação Mês", y="Quantidade", title="Evolução Mensal de Solicitações")
    streamlit_app.plotly_chart(fig_evolucao, use_container_width=True)
    
    # --- TABELA DETALHADA ---
    streamlit_app.markdown("### 📋 Solicitações Detalhadas")
    streamlit_app.dataframe(df_filtrado.reset_index(drop=True))
    
    # --- DETALHES DA SOLICITAÇÃO ---
    streamlit_app.markdown("### ✏️ Gerenciar Solicitação")
    opcoes_solicitacao = (df_filtrado["ID"].astype(str) + " - " + df_filtrado["Descrição"]).tolist()
    selecionada = streamlit_app.selectbox("Selecione uma solicitação para analisar e editar:", options=opcoes_solicitacao)
    
    if selecionada and " - " in selecionada:
        id_selecionado = selecionada.split(" - ")[0].strip()
        linha_selecionada = df_filtrado[df_filtrado["ID"] == id_selecionado]
        if not linha_selecionada.empty:
            indice = linha_selecionada.index[0]
            
            # Mostrar informações
            streamlit_app.markdown(f"**ID:** {linha_selecionada.at[indice, 'ID']}")
            streamlit_app.markdown(f"**Solicitante:** {linha_selecionada.at[indice, 'Nome']} ({linha_selecionada.at[indice, 'Registro']})")
            streamlit_app.markdown(f"**OS:** {linha_selecionada.at[indice, 'OS']}")
            streamlit_app.markdown(f"**RC:** {linha_selecionada.at[indice, 'RC']}")
            streamlit_app.markdown(f"**TAG do Equipamento:** {linha_selecionada.at[indice, 'TAG']}")
            streamlit_app.markdown(f"**Descrição:** {linha_selecionada.at[indice, 'Descrição']}")
            streamlit_app.markdown(f"**Tipo:** {linha_selecionada.at[indice, 'Tipo']}")
            streamlit_app.markdown(f"**Data da Solicitação:** {linha_selecionada.at[indice, 'Data Solicitação'].strftime('%Y-%m-%d') if not pandas_lib.isna(linha_selecionada.at[indice, 'Data Solicitação']) else '-'}")
            streamlit_app.markdown(f"**Previsão de Entrega:** {linha_selecionada.at[indice, 'Previsão Entrega'].strftime('%Y-%m-%d') if not pandas_lib.isna(linha_selecionada.at[indice, 'Previsão Entrega']) else '-'}")
            streamlit_app.markdown(f"**Status Atual:** {linha_selecionada.at[indice, 'Status']}")
            streamlit_app.markdown(f"**Motivo do Atraso:** {linha_selecionada.at[indice, 'Motivo Atraso']}")
            streamlit_app.markdown(f"**Ordem de Compra:** {linha_selecionada.at[indice, 'Ordem de Compra']}")
            streamlit_app.markdown(f"**Prioridade:** {linha_selecionada.at[indice, 'Prioridade']}")
            streamlit_app.markdown(f"**Observações:** {linha_selecionada.at[indice, 'Observações']}")
            streamlit_app.markdown(f"**Lead Time (dias):** {linha_selecionada.at[indice, 'Lead Time']}")
            
            streamlit_app.markdown("---")
            streamlit_app.markdown("### Atualizar Solicitação")
            
            nova_prioridade = streamlit_app.selectbox("Alterar Prioridade", ["Baixa", "Média", "Alta", "Crítica"], index=["Baixa", "Média", "Alta", "Crítica"].index(linha_selecionada.at[indice, "Prioridade"]))
            nova_observacao = streamlit_app.text_area("Atualizar Observações", value=linha_selecionada.at[indice, "Observações"])
            marcar_concluido = streamlit_app.checkbox("Marcar processo como concluído")
            
            if streamlit_app.button("Salvar Alterações"):
                dataframe.at[indice, "Prioridade"] = nova_prioridade
                dataframe.at[indice, "Observações"] = nova_observacao
                if marcar_concluido:
                    dataframe.at[indice, "Status"] = "Processo Concluído"
                    try:
                        lead_time_total = (dataframe.at[indice, "Previsão Entrega"] - dataframe.at[indice, "Data Solicitação"]).days
                        dataframe.at[indice, "Lead Time"] = lead_time_total
                    except:
                        pass
                salvar_dados(dataframe)
                streamlit_app.success("Alterações salvas com sucesso!")
                streamlit_app.experimental_rerun()

# Tela de cadastro e tela do comprador podem ser inseridas aqui, ou importadas

def main():
    perfil_selecionado = streamlit_app.sidebar.selectbox("Selecione o Perfil", ["Requisitante", "Comprador", "Administrador"])

    if perfil_selecionado == "Requisitante":
        # chamar função tela_cadastro()
        pass
    elif perfil_selecionado == "Comprador":
        # chamar função tela_comprador()
        pass
    elif perfil_selecionado == "Administrador":
        tela_administrador()

if __name__ == "__main__":
    main()

