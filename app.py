import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="📘 Busca de temas", page_icon="📘")
st.title("📘 Busca de temas")

st.markdown("""
Este app permite buscar temas de três maneiras distintas, cada uma com seu próprio campo:

- 🔹 **Frase exata**: Digite algo como `"MEI para ME"` (com aspas) para encontrar apenas temas que contenham exatamente essa frase.
- 🔸 **Contém todas (AND)**: Digite palavras separadas por `AND`, como `MEI AND marketing`, para buscar temas que contenham todas essas palavras.
- 🔺 **Similaridade ≥ 40%**: Digite livremente para encontrar temas que se pareçam com a frase digitada.
""")

# Abas (UF + ciclo)
abas = {
    'RS25-26': '0',
    'RS24-25': '115275239',
    'RS23-24': '2138405098',
    'RS22-23': '1420824130',
    'SP25-26': '1513429512',
    'SP24-25': '205733653',
    'SP23-24': '205552520',
    'SP22-23': '80889',
    'SP21-22': '1993459611',
    'POLO25-26': '105220454',
    'POLO23-24': '2038651538',
    'MS22-23': '760527987',
    'MS23-24': '1270353981',
    'MS24-25': '410127937',
    'MS25-26': '1754281433'
}

sheet_id = '1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg'

@st.cache_data
def carregar_temas():
    registros = []

    for nome_aba, gid in abas.items():
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

        for header_row in [0, 1, 2]:
            try:
                df = pd.read_csv(url, header=header_row)

                col_titulo = next((c for c in df.columns if "título" in c.lower()), None)
                if not col_titulo:
                    continue

                col_produto = next((c for c in df.columns if "produto" in c.lower()), None)
                col_jira = next((c for c in df.columns if "jira" in c.lower()), None)

                for _, row in df.iterrows():
                    titulo = str(row[col_titulo]).strip() if pd.notna(row[col_titulo]) else ""
                    if not titulo:
                        continue

                    produto = str(row[col_produto]).strip() if col_produto and pd.notna(row[col_produto]) else ""
                    jira = str(row[col_jira]).strip() if col_jira and pd.notna(row[col_jira]) else ""

                    registros.append({
                        "UF_Ciclo": nome_aba,
                        "Produto": produto,
                        "Tema": titulo,
                        "Jira": jira
                    })
                break
            except:
                continue

    return pd.DataFrame(registros)

temas_df = carregar_temas()

def similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def render_resultado(uf, produto, tema, jira=None, score=None):
    linha = f"**{produto}** — _{tema}_" if produto else f"_{tema}_"
    if score is not None:
        linha += f" — {score}%"

    st.markdown(f"- **{uf}** → {linha}")

    if jira:
        st.markdown(f"🔗 [Abrir Jira]({jira})")

# 🔹 Frase exata
st.subheader("🔹 Buscar por frase exata")
frase = st.text_input("Digite a frase exata (com ou sem aspas)", key="exata")

if frase:
    frase = frase.strip('"').lower()
    encontrados = temas_df[temas_df["Tema"].str.lower().str.contains(frase, na=False)]

    if not encontrados.empty:
        for _, r in encontrados.iterrows():
            render_resultado(r["UF_Ciclo"], r["Produto"], r["Tema"], r["Jira"])
    else:
        st.info("Nenhum tema com essa frase exata.")

# 🔸 AND
st.subheader("🔸 Buscar por todas as palavras (AND)")
entrada_and = st.text_input("Digite com AND entre palavras, ex: MEI AND marketing", key="and")

if entrada_and:
    palavras = [p.strip().lower() for p in entrada_and.upper().split("AND")]

    resultados = temas_df[
        temas_df["Tema"].str.lower().apply(
            lambda t: all(p in t for p in palavras)
        )
    ]

    if not resultados.empty:
        for _, r in resultados.iterrows():
            render_resultado(r["UF_Ciclo"], r["Produto"], r["Tema"], r["Jira"])
    else:
        st.info("Nenhum tema contém todas essas palavras.")

# 🔺 Similaridade
st.subheader("🔺 Buscar por similaridade (≥ 40%)")
entrada_sim = st.text_input("Digite um tema para busca aproximada", key="sim")

if entrada_sim:
    achados = []

    for _, r in temas_df.iterrows():
        score = round(similaridade(entrada_sim, r["Tema"]) * 100, 1)
        if score >= 40:
            achados.append((r, score))

    if achados:
        for r, s in achados:
            render_resultado(r["UF_Ciclo"], r["Produto"], r["Tema"], r["Jira"], s)
    else:
        st.info("Nenhum tema semelhante com esse termo.")
