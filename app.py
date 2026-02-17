import streamlit as st
import pydicom
import pandas as pd
import os

st.set_page_config(page_title="HealthTech Analyzer", layout="wide")

st.title("🏥 DICOM Metadata Analyzer")
st.write("Ferramenta de Auditoria de Protocolos e Dose")

# Sidebar para configurações
st.sidebar.header("Configurações")
caminho_pasta = st.sidebar.text_input("Caminho da Pasta DICOM", r"D:\EXAMES\exame_dicon")

if st.button("Analisar Exames"):
    lista_dados = []

    # --- PASSO 1: Mapear todos os arquivos em subpastas ---
    caminhos_completos = []
    for raiz, subpastas, arquivos in os.walk(caminho_pasta):
        for f in arquivos:
            if f.lower().endswith('.dcm'):
                caminhos_completos.append(os.path.join(raiz, f))

    if not caminhos_completos:
        st.warning("Nenhum arquivo .dcm encontrado na pasta ou subpastas.")
    else:
        progresso = st.progress(0)
        status_text = st.empty()
        total = len(caminhos_completos)

        # --- PASSO 2: Processar a lista de caminhos encontrados ---
        for i, caminho in enumerate(caminhos_completos):
            try:
                ds = pydicom.dcmread(caminho)

                # Lógica para formatar a data
                data_bruta = ds.get("StudyDate", "")
                if data_bruta and len(data_bruta) == 8:
                    data_formatada = f"{data_bruta[6:8]}/{data_bruta[4:6]}/{data_bruta[0:4]}"
                else:
                    data_formatada = "N/A"

                info = {
                    "Arquivo": os.path.basename(caminho),
                    "Modalidade": ds.get("Modality", "N/A"),
                    "Descricao_Serie": ds.get("SeriesDescription", "N/A"),
                    "Protocolo": ds.get("ProtocolName", "N/A"),
                    "Espessura_Corte": ds.get("SliceThickness", "N/A"),
                    "KV": ds.get("KVP", "N/A"),
                    "mA": ds.get("XRayTubeCurrent", "N/A"),
                    "Data_Exame": data_formatada,
                    "Pasta": os.path.dirname(caminho).split(os.sep)[-1]  # Mostra a subpasta
                }
                lista_dados.append(info)

                # Atualiza progresso
                progresso.progress((i + 1) / total)
                status_text.text(f"Processando {i + 1} de {total}")

            except Exception as e:
                # Se um arquivo estiver corrompido, ele pula para o próximo
                continue

        df = pd.DataFrame(lista_dados)

        # Exibe métricas rápidas
        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Arquivos", len(df))
        col2.metric("Modalidades", ", ".join(df['Modalidade'].unique()))
        col3.metric("Protocolos Únicos", len(df['Protocolo'].unique()))

        # Mostra a tabela interativa
        st.dataframe(df, use_container_width=True)

        # Download formatado
        csv_formatado = df.to_csv(index=False, sep=';', encoding='utf-8-sig')
        st.download_button(
            label="📥 Baixar Relatório para Excel",
            data=csv_formatado,
            file_name='relatorio_dicom_completo.csv',
            mime='text/csv',
        )