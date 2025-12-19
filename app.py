import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

# =============================
# Configuração da página
# =============================
st.set_page_config(
    page_title="📘 Busca de temas",
    page_icon="📘"
)

st.title("📘 Busca de temas")

st.markdown("""
Este app permite consultar **temas já produzidos anteriormente** pelos SEBRAEs,
evitando duplicidade de pautas entre ciclos e UFs.

Você pode pesquisar de **três formas diferentes**, escolhendo a que faz mais sentido
para cada situação:

---

### 🔹 Frase exata
Use quando quiser saber se **um título específico já foi produzido**.

Exemplo:  
`"MEI para ME"`

Retorna apenas temas que contenham **exatamente essa frase**, na mesma ordem.

---

### 🔸 Contém todas as palavras (AND)
Use quando quiser verificar se **conceitos combinados já apareceram juntos**,
mesmo que em frases diferentes.

Exemplo:  
`MEI AND marketing`

Retorna temas que contenham **todas as palavras**, em qualquer ordem.

---

### 🔺 Similaridade (≥ 40%)
Use quando tiver **uma ideia ainda em formulação**.

Exemplo:  
`Transformar MEI`

Pode retornar temas como:
- “Quando é hora de passar de MEI para ME?”
- “MEI e transição para ME”

---

ℹ️ A busca é feita automaticamente em **todas as UFs e ciclos contratuais disponíveis**,
com base na planilha consolidada.
""")

# =============================
# Configurações da planilha
# =============================
sheet_id = "1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg"
INDEX_GID = "1373805871"  # aba INDEX

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

# =============================
# Funções auxiliares
# =============================
def similaridade(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def render_resultado(uf, produto, tema, jira=None, score=None):
    linha = f"**{produto}** — _{tema}_" if produto else f"_{tema}_"
    if score is not None:
        linha += f" — {score}%"

    st.markdown(f"- **{uf}** → {linha}")
    if jira:
        st.markdown(f"🔗 [Abrir Jira]({jira})")

# =============================
# 🔹 Frase exata
# =============================
st.subheader("🔹 Buscar por frase exata")
frase = st.text_input("Digite a frase exata (com ou sem aspas)")

if frase:
    frase = frase.strip('"').lower()
    resultados = temas_df[
        temas_df["Tema"].str.lower().str.contains(frase, na=False)
    ]

    if not resultados.empty:
        for _, r in resultados.iterrows():
            render_resultado(r["UF_Ciclo"], r["Produto"], r["Tema"], r["Jira"])
    else:
        st.info("Nenhum tema com essa frase exata.")

# =============================
# 🔸 AND
# =============================
st.subheader("🔸 Buscar por todas as palavras (AND)")
entrada_and = st.text_input("Digite com AND entre palavras (ex: MEI AND marketing)")

if entrada_and:
    palavras = [p.strip().lower() for p in entrada_and.upper().split("AND")]
    resultados = temas_df[
        temas_df["Tema"].str.lower().apply(lambda t: all(p in t for p in palavras))
    ]

    if not resultados.empty:
        for _, r in resultados.iterrows():
            render_resultado(r["UF_Ciclo"], r["Produto"], r["Tema"], r["Jira"])
    else:
        st.info("Nenhum tema contém todas essas palavras.")

# =============================
# 🔺 Similaridade
# =============================
st.subheader("🔺 Buscar por similaridade (≥ 40%)")
entrada_sim = st.text_input("Digite um tema para busca aproximada")

if entrada_sim:
    encontrou = False
    for _, r in temas_df.iterrows():
        score = round(similaridade(entrada_sim, r["Tema"]) * 100, 1)
        if score >= 40:
            encontrou = True
            render_resultado(
                r["UF_Ciclo"],
                r["Produto"],
                r["Tema"],
                r["Jira"],
                score
            )

    if not encontrou:
        st.info("Nenhum tema semelhante encontrado.")
