# compras_emergenciais_app.py

import streamlit as streamlit_app
import pandas as pandas_lib
import plotly.express as plotly_express
from datetime import datetime as data_hora
import os as sistema_operacional

# Caminho do arquivo CSV
CAMINHO_ARQUIVO_DADOS = "cadastro_compras.csv"

# Carrega os dados
def carregar_dados():
    if sistema_operacional.path.exists(CAMINHO_ARQUIVO_DADOS):
        return pandas_lib.read_csv(CAMINHO_ARQUIVO_DADOS, dtype={"ID": str})
    else:
        return pandas_lib.DataFrame(columns=[
            "ID", "Nome", "Registro", "OS", "RC", "TAG", "Descrição", "Tipo",
            "Data Solicitação", "Lead Time", "Status", "Previsão Entrega",
            "Motivo Atraso", "Ordem de Compra", "Prioridade", "Observações"
        ])

# Salva os dados
def salvar_dados(dataframe):
    dataframe.to_csv(CAMINHO_ARQUIVO_DADOS, index=False)

# Tela do administrador aprimorada
def tela_administrador():
    streamlit_app.title("📊 Painel do Administrador - Visão Geral e Gestão")
    dataframe = carregar_dados()

    if dataframe.empty:
        streamlit_app.info("Nenhuma solicitação cadastrada.")
        return

    # Conversão de datas para cálculo de lead time
    dataframe["Data Solicitação"] = pandas_lib.to_datetime(dataframe["Data Solicitação"], errors='coerce')
    dataframe["Previsão Entrega"] = pandas_lib.to_datetime(dataframe["Previsão Entrega"], errors='coerce')

    dataframe["Lead Time"] = (dataframe["Previsão Entrega"] - dataframe["Data Solicitação"]).dt.days

    streamlit_app.markdown("### 📌 Indicadores Gerais")
    coluna_1, coluna_2, coluna_3 = streamlit_app.columns(3)
    with coluna_1:
        streamlit_app.metric("Total de Solicitações", len(dataframe))
    with coluna_2:
        streamlit_app.metric("Média de Lead Time", int(dataframe["Lead Time"].mean(skipna=True)) if not dataframe["Lead Time"].isna().all() else "-")
    with coluna_3:
        streamlit_app.metric("Pendentes", len(dataframe[dataframe["Status"] != "Processo Concluído"]))

    streamlit_app.markdown("### 📈 Lead Time por Solicitação")
    streamlit_app.dataframe(dataframe[["ID", "Descrição", "Data Solicitação", "Previsão Entrega", "Lead Time", "Status"]])

    streamlit_app.markdown("### 📊 Gráfico de Status")
    grafico_status = dataframe["Status"].value_counts().reset_index()
    grafico_status.columns = ["Status", "Quantidade"]
    grafico_gerado = plotly_express.bar(grafico_status, x="Status", y="Quantidade", color="Status", text="Quantidade")
    streamlit_app.plotly_chart(grafico_gerado, use_container_width=True)

    streamlit_app.markdown("### ✏️ Edição de Solicitação")
    opcoes_solicitacao = (dataframe["ID"].astype(str) + " - " + dataframe["Descrição"]).tolist()
    selecionada = streamlit_app.selectbox("Selecione a solicitação para editar", opcoes_solicitacao)

    if selecionada and " - " in selecionada:
        identificador = selecionada.split(" - ")[0].strip()
        linha_selecionada = dataframe[dataframe["ID"] == identificador]
        if not linha_selecionada.empty:
            indice = linha_selecionada.index[0]
            prioridade_atual = dataframe.at[indice, "Prioridade"]
            nova_prioridade = streamlit_app.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Crítica"], index=["Baixa", "Média", "Alta", "Crítica"].index(prioridade_atual))
            novas_observacoes = streamlit_app.text_area("Observações", value=dataframe.at[indice, "Observações"])
            marcar_concluido = streamlit_app.checkbox("Marcar como Concluído")

            if streamlit_app.button("Salvar Alterações"):
                dataframe.at[indice, "Prioridade"] = nova_prioridade
                dataframe.at[indice, "Observações"] = novas_observacoes
                if marcar_concluido:
                    dataframe.at[indice, "Status"] = "Processo Concluído"
                    try:
                        tempo_total = (dataframe.at[indice, "Previsão Entrega"] - dataframe.at[indice, "Data Solicitação"]).days
                        dataframe.at[indice, "Lead Time"] = tempo_total
                    except:
                        pass
                salvar_dados(dataframe)
                streamlit_app.success("Alterações salvas com sucesso!")

# Telas mantidas
def tela_cadastro():
    pass

def tela_comprador():
    pass

# Execução principal
def executar_aplicativo():
    perfil_selecionado = streamlit_app.sidebar.selectbox("Selecione o Perfil", ["Requisitante", "Comprador", "Administrador"])

    if perfil_selecionado == "Requisitante":
        tela_cadastro()
    elif perfil_selecionado == "Comprador":
        tela_comprador()
    elif perfil_selecionado == "Administrador":
        tela_administrador()

if __name__ == "__main__":
    executar_aplicativo()
