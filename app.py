import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="📘 Busca de temas", page_icon="📘")
st.title("📘 Busca de temas")

st.markdown("""
Este app permite buscar temas de três maneiras distintas:

- 🔹 **Frase exata**
- 🔸 **AND**
- 🔺 **Similaridade ≥ 40%**
""")

# IDs da planilha
sheet_id = "1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg"
INDEX_GID = "1373805871"  # GID da aba INDEX

@st.cache_data
def carregar_index():
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={INDEX_GID}"
    df = pd.read_csv(url)
    return dict(zip(df["UF_Ciclo"], df["GID"]))

abas = carregar_index()

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
frase = st.text_input("Digite a frase exata", key="exata")

if frase:
    frase = frase.strip('"').lower()
    resultados = temas_df[temas_df["Tema"].str.lower().str.contains(frase, na=False)]
    for _, r in resultados.iterrows():
        render_resultado(r["UF_Ciclo"], r["Produto"], r["Tema"], r["Jira"])

# 🔸 AND
st.subheader("🔸 Buscar por todas as palavras (AND)")
entrada_and = st.text_input("Digite com AND entre palavras", key="and")

if entrada_and:
    palavras = [p.strip().lower() for p in entrada_and.upper().split("AND")]
    resultados = temas_df[
        temas_df["Tema"].str.lower().apply(lambda t: all(p in t for p in palavras))
    ]
    for _, r in resultados.iterrows():
        render_resultado(r["UF_Ciclo"], r["Produto"], r["Tema"], r["Jira"])

# 🔺 Similaridade
st.subheader("🔺 Buscar por similaridade (≥ 40%)")
entrada_sim = st.text_input("Digite um tema", key="sim")

if entrada_sim:
    for _, r in temas_df.iterrows():
        score = round(similaridade(entrada_sim, r["Tema"]) * 100, 1)
        if score >= 40:
            render_resultado(r["UF_Ciclo"], r["Produto"], r["Tema"], r["Jira"], score)
