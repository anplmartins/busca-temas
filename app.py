
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="Busca de Temas em Todas as UFs", page_icon="🔎")
st.title("🔎 Busca de Temas em Todas as UFs")
st.markdown("Digite um novo tema e veja se ele (ou algo semelhante) já foi produzido em qualquer UF/ciclo.")

# Dicionário de abas e GIDs
abas = {
    'RS25-26': '0',
    'RS24-25': '115275239',
    'RS23-24': '2138405098',
    'RS22-23': '1420824130',
    'SP24-25': '205733653',
    'SP23-24': '205552520',
    'SP22-23': '80889',
    'SP21-22': '1993459611',
}

sheet_id = '1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg'

@st.cache_data
def carregar_temas_de_todas_as_abas():
    temas_por_aba = []
    for nome_aba, gid in abas.items():
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
        for header_row in [1, 2]:
            try:
                df = pd.read_csv(url, header=header_row)
                titulo_col = [col for col in df.columns if "título" in col.lower()]
                if titulo_col:
                    col = titulo_col[0]
                    for tema in df[col].dropna().astype(str):
                        temas_por_aba.append({"UF_Ciclo": nome_aba, "Tema": tema})
                    break
            except:
                continue
    return pd.DataFrame(temas_por_aba)

temas_df = carregar_temas_de_todas_as_abas()

def similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

tema_input = st.text_input("Digite o novo tema:")

if tema_input:
    resultados = []
    for _, row in temas_df.iterrows():
        score = round(similaridade(tema_input, row["Tema"]) * 100, 1)
        if score >= 30:
            resultados.append((row["UF_Ciclo"], row["Tema"], score))
    resultados.sort(key=lambda x: x[2], reverse=True)

    if resultados:
        st.subheader("Temas semelhantes encontrados:")
        for uf, tema, score in resultados:
            st.markdown(f"- **{uf}** → _{tema}_ — Similaridade: **{score}%**")
    else:
        st.info("Nenhum tema semelhante encontrado em nenhuma aba.")
