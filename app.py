
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="📘 Temas já produzidos anteriormente", page_icon="📘")
st.title("📘 Temas já produzidos anteriormente")

st.markdown("""
Este app permite buscar temas de três maneiras distintas, cada uma com seu próprio campo:

- 🔹 **Frase exata**: Digite algo como `"MEI para ME"` (com aspas) para encontrar apenas temas que contenham exatamente essa frase.
- 🔸 **Contém todas (AND)**: Digite palavras separadas por `AND`, como `MEI AND marketing`, para buscar temas que contenham todas essas palavras.
- 🔺 **Similaridade ≥ 40%**: Digite livremente para encontrar temas que se pareçam com a frase digitada.
""", unsafe_allow_html=True)

abas = {
    'RS25-26': '0',
    'RS24-25': '115275239',
    'RS23-24': '2138405098',
    'RS22-23': '1420824130',
    'SP24-25': '205733653',
    'SP23-24': '205552520',
    'SP22-23': '80889',
    'SP21-22': '1993459611',
    'POLO23-24': '2038651538'
}

sheet_id = '1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg'

@st.cache_data
def carregar_temas():
    todos = []
    for nome_aba, gid in abas.items():
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
        for header_row in [0, 1, 2]:
            try:
                df = pd.read_csv(url, header=header_row)
                col_titulo = [c for c in df.columns if "título" in c.lower()]
                if col_titulo:
                    col = col_titulo[0]
                    for t in df[col].dropna().astype(str):
                        todos.append({"UF_Ciclo": nome_aba, "Tema": t})
                    break
            except:
                continue
    return pd.DataFrame(todos)

temas_df = carregar_temas()

def similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

st.subheader("🔹 Buscar por frase exata")
frase = st.text_input("Digite a frase exata (com ou sem aspas)", key="exata")
if frase:
    frase = frase.strip('"').lower()
    encontrados = [(r["UF_Ciclo"], r["Tema"]) for _, r in temas_df.iterrows() if frase in r["Tema"].lower()]
    if encontrados:
        for uf, tema in encontrados:
            st.markdown(f"- **{uf}** → _{tema}_")
    else:
        st.info("Nenhum tema com essa frase exata.")

st.subheader("🔸 Buscar por todas as palavras (AND)")
entrada_and = st.text_input("Digite com AND entre palavras, ex: MEI AND marketing", key="and")
if entrada_and:
    palavras = [p.strip().lower() for p in entrada_and.upper().split("AND")]
    resultados = [(r["UF_Ciclo"], r["Tema"]) for _, r in temas_df.iterrows()
                  if all(p in r["Tema"].lower() for p in palavras)]
    if resultados:
        for uf, tema in resultados:
            st.markdown(f"- **{uf}** → _{tema}_")
    else:
        st.info("Nenhum tema contém todas essas palavras.")

st.subheader("🔺 Buscar por similaridade (≥ 40%)")
entrada_sim = st.text_input("Digite um tema para busca aproximada", key="sim")
if entrada_sim:
    lista = []
    for _, r in temas_df.iterrows():
        score = round(similaridade(entrada_sim, r["Tema"]) * 100, 1)
        if score >= 40:
            lista.append((r["UF_Ciclo"], r["Tema"], score))
    lista.sort(key=lambda x: x[2], reverse=True)
    if lista:
        for uf, tema, s in lista:
            st.markdown(f"- **{uf}** → _{tema}_ — {s}%")
    else:
        st.info("Nenhum tema semelhante com esse termo.")
