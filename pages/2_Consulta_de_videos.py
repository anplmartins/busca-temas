import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
import re

# =============================
# Configuração da página
# =============================
st.set_page_config(
    page_title="🎥 Consulta de vídeos",
    page_icon="🎥"
)

# =============================
# HOME
# =============================
st.title("🎥 Consulta de vídeos já produzidos")

st.markdown("""
😩 **Cansado de sugerir vídeos que já foram feitos antes?**  
😵‍💫 **Ou de perder tempo tentando descobrir se aquele tema já virou vídeo para o cliente?**

Seus problemas acabaram.

Esta página foi criada para ajudar você a:
- evitar retrabalho
- ganhar tempo
- tomar decisões com mais segurança
""")

st.image(
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExazc5cjliNXNzaWs0NmZyZ282NW53ZDR0d3c0ZWR1NmI4bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/g01ZnwAUvutuK8GIQn/giphy.gif"
)

# =============================
# Configurações da planilha
# =============================
sheet_id = "1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg"
INDEX_GID = "1373805871"

PREFIXOS = ["BT", "PRS", "RI", "CS", "FE", "PM", "CT", "CUR", "VD 1.5", "VD 3"]

# =============================
# Funções auxiliares
# =============================
def normalizar_titulo(texto):
    if not texto:
        return ""
    texto = texto.lower().strip()
    for p in PREFIXOS:
        texto = re.sub(rf"^{p.lower()}[\s\-:]+", "", texto)
    return re.sub(r"\s+", " ", texto)

def similaridade(a, b):
    return SequenceMatcher(None, a, b).ratio()

# =============================
# Carregamento de dados
# =============================
@st.cache_data
def carregar_index():
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={INDEX_GID}"
    df = pd.read_csv(url)
    return dict(zip(df["UF_Ciclo"], df["GID"]))

@st.cache_data
def carregar_dados():
    registros = []
    abas = carregar_index()

    for uf_ciclo, gid in abas.items():
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

        for header_row in [0, 1, 2]:
            try:
                df = pd.read_csv(url, header=header_row)

                col_titulo = next((c for c in df.columns if "título" in c.lower()), None)
                col_produto = next((c for c in df.columns if "produto" in c.lower()), None)
                col_jira = next((c for c in df.columns if "jira" in c.lower()), None)

                if not col_titulo:
                    continue

                for _, row in df.iterrows():
                    titulo = str(row[col_titulo]).strip() if pd.notna(row[col_titulo]) else ""
                    if not titulo:
                        continue

                    produto = str(row[col_produto]).strip() if col_produto and pd.notna(row[col_produto]) else ""
                    jira = str(row[col_jira]).strip() if col_jira and pd.notna(row[col_jira]) else ""

                    registros.append({
                        "UF_Ciclo": uf_ciclo,
                        "UF": uf_ciclo[:2],
                        "Produto": produto,
                        "Titulo": titulo,
                        "Titulo_norm": normalizar_titulo(titulo),
                        "Jira": jira
                    })
                break
            except:
                continue

    return pd.DataFrame(registros)

df = carregar_dados()

# =============================
# ABAS
# =============================
aba1, aba2 = st.tabs(["🔍 Verificar vídeo", "🎯 Oportunidades de novos vídeos"])

# =============================
# ABA 1 — VERIFICAR VÍDEO
# =============================
with aba1:
    st.subheader("🔍 Verificar se um vídeo já foi produzido")

    uf_escolhida = st.radio(
        "🎛️ Em qual cliente quer consultar?",
        ["Todas as UFs", "RS", "SP", "MS", "POLO"],
        horizontal=True
    )

    titulo_busca = st.text_input(
        "✏️ Informe o título do vídeo exatamente como está no material base"
    )

    if titulo_busca:
        titulo_norm = normalizar_titulo(titulo_busca)

        base = df[df["Produto"].str.startswith("VD", na=False)]
        if uf_escolhida != "Todas as UFs":
            base = base[base["UF"] == uf_escolhida]

        encontrados = []

        for _, r in base.iterrows():
            score = round(similaridade(titulo_norm, r["Titulo_norm"]) * 100, 1)
            if score >= 40:
                encontrados.append((r, score))

        if encontrados:
            for r, s in encontrados:
                st.markdown(
                    f"- **{r['UF_Ciclo']}** → **{r['Produto']}** — _{r['Titulo']}_ — {s}%"
                )
                if r["Jira"]:
                    st.markdown(f"🔗 [Abrir Jira]({r['Jira']})")
        else:
            st.info("Nenhum vídeo encontrado para este cliente.")

# =============================
# ABA 2 — OPORTUNIDADES
# =============================
with aba2:
    st.subheader("🎯 Oportunidades de novos vídeos")

    uf_op = st.selectbox(
        "🎛️ Em qual cliente quer consultar?",
        ["RS", "SP", "MS", "POLO"]
    )

    base = df[~df["Produto"].str.startswith("VD", na=False)]
    videos = df[df["Produto"].str.startswith("VD", na=False)]

    base = base[base["UF"] == uf_op]

    titulos_video = set(videos["Titulo_norm"])

    oportunidades = base[~base["Titulo_norm"].isin(titulos_video)]

    if oportunidades.empty:
        st.success("Nenhuma oportunidade encontrada para este cliente.")
    else:
        for _, r in oportunidades.iterrows():
            st.markdown(
                f"- **{r['UF_Ciclo']}** → **{r['Produto']}** — _{r['Titulo']}_"
            )
            if r["Jira"]:
                st.markdown(f"🔗 [Abrir Jira]({r['Jira']})")

# =============================
# AVISO FINAL
# =============================
st.markdown("---")

st.warning("""
⚠️ **Importante**

Este app **não substitui a planilha oficial do cliente**.  
Use-o como apoio à análise, mas **sempre confirme as informações diretamente na planilha do cliente** antes de fechar qualquer encaminhamento.
""")

st.image(
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXNmcTI5eWtoZHZ5eDJoem15MHBscnVjNHB2czA4cHRycjd6MWE3cyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VF65SrQlmClUc/giphy.gif"
)
