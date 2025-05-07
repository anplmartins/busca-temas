
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="Consulta de Temas por UF", page_icon="📄")

st.title("📄 Consulta de Temas por UF")
st.markdown("Selecione a UF e o ciclo para consultar os temas já produzidos.")

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

# Seleção da aba
aba = st.selectbox("Selecione o ciclo:", list(abas.keys()))
gid = abas[aba]
csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'

@st.cache_data
def carregar_dados(url):
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

df = carregar_dados(csv_url)

if df is not None:
    # Detecta a coluna "Título"
    titulo_col = [col for col in df.columns if "título" in col.lower()]
    if titulo_col:
        st.success(f"Tema(s) encontrados na aba {aba}.")
        col = titulo_col[0]
        temas = df[col].dropna().astype(str).tolist()
        tema_input = st.text_input("Digite o novo tema para verificar similaridade:")

        def similaridade(a, b):
            return SequenceMatcher(None, a.lower(), b.lower()).ratio()

        if tema_input:
            resultados = []
            for tema in temas:
                score = round(similaridade(tema_input, tema) * 100, 1)
                if score >= 50:
                    resultados.append((tema, score))
            resultados.sort(key=lambda x: x[1], reverse=True)

            if resultados:
                st.subheader("Temas semelhantes encontrados:")
                for t, s in resultados:
                    st.markdown(f"- **{t}** — Similaridade: {s}%")
            else:
                st.info("Nenhum tema semelhante encontrado.")
    else:
        st.warning("Não foi possível localizar a coluna 'Título' nesta aba.")
else:
    st.error("Erro ao carregar os dados da planilha.")
