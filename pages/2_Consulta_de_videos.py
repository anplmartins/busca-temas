import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
import re

# =====================
# CONFIGURAÇÃO DA PÁGINA
# =====================
st.set_page_config(
    page_title="Busca de temas",
    page_icon="📘",
    layout="wide"
)

# =====================
# ESTILO PARA DESTACAR ABAS
# =====================
st.markdown("""
<style>
div[data-baseweb="tab"] {
    font-size: 18px;
    padding: 12px 24px;
}
</style>
""", unsafe_allow_html=True)

# =====================
# FUNÇÕES AUXILIARES
# =====================
PREFIXOS = ["BT", "PRS", "RI", "CS", "FE", "PM", "CT", "CUR"]

def normalizar_titulo(texto):
    texto = texto.lower()
    texto = re.sub(rf'^({"|".join(PREFIXOS)})\s*[-:]\s*', '', texto)
    texto = texto.replace(":", " ").replace("-", " ")
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def similaridade(a, b):
    return SequenceMatcher(None, a, b).ratio()

# =====================
# DADOS DA PLANILHA (INDEX)
# =====================
SHEET_ID = "1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg"
GID_INDEX = "1373805871"

@st.cache_data
def carregar_index():
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID_INDEX}"
    return pd.read_csv(url)

df = carregar_index()

# Esperado no INDEX:
# UF | Ciclo | Produto | Tipo | Título | Jira

# =====================
# HOME
# =====================
st.title("📘 Busca de temas")

st.markdown("""
Está cansado de sugerir vídeos que **já foram feitos antes**  
ou de perder tempo tentando descobrir se um tema **já virou vídeo**?

**Seus problemas acabaram.**
""")

st.image(
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExazc5cjliNXNzaWs0NmZqODZmM2ZyZ282NW53ZDR0d3c0ZWR1NmI4bSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/g01ZnwAUvutuK8GIQn/giphy.gif"
)

# =====================
# ABAS
# =====================
tab1, tab2 = st.tabs([
    "🔎 Temas já produzidos",
    "🎯 Oportunidades de novos vídeos"
])

# ======================================================
# ABA 1 — TEMAS JÁ PRODUZIDOS
# ======================================================
with tab1:
    st.header("🔎 Temas já produzidos anteriormente")

    st.markdown("""
Use esta aba para **verificar rapidamente** se um tema (ou algo parecido)
já foi produzido em qualquer UF ou ciclo.
""")

    cliente = st.selectbox(
        "🎛️ Em qual cliente quer consultar?",
        sorted(df["UF"].dropna().unique())
    )

    texto_busca = st.text_input("✏️ Digite o tema para buscar")

    if texto_busca:
        termo = normalizar_titulo(texto_busca)

        resultados = []
        for _, row in df[df["UF"] == cliente].iterrows():
            titulo_base = normalizar_titulo(str(row["Título"]))
            score = similaridade(termo, titulo_base) * 100

            if score >= 70:
                resultados.append({
                    "UF_Ciclo": f'{row["UF"]}{row["Ciclo"]}',
                    "Produto": row["Produto"],
                    "Titulo": row["Título"],
                    "Jira": row.get("Jira", ""),
                    "Score": round(score, 1)
                })

        resultados.sort(key=lambda x: x["Score"], reverse=True)

        if resultados:
            for r in resultados:
                st.markdown(
                    f"- **{r['UF_Ciclo']} → {r['Produto']}** — _{r['Titulo']}_ — **{r['Score']}%**"
                )
                if r["Jira"]:
                    st.markdown(f"[🔗 Abrir Jira]({r['Jira']})")
        else:
            st.info("Nenhum tema semelhante encontrado.")

# ======================================================
# ABA 2 — OPORTUNIDADES DE NOVOS VÍDEOS
# ======================================================
with tab2:
    st.header("🎯 Oportunidades de novos vídeos")

    st.markdown("""
Use esta seção quando você já tem um título em mente e quer saber se ele  
**já foi utilizado em algum vídeo**, evitando retrabalho.

✏️ **Informe o título do vídeo exatamente como está no material base**
""")

    cliente = st.selectbox(
        "🎛️ Em qual cliente quer consultar?",
        sorted(df["UF"].dropna().unique()),
        key="cliente_video"
    )

    titulo_video = st.text_input("Título do vídeo")

    if titulo_video:
        termo_video = normalizar_titulo(titulo_video)

        df_cliente = df[df["UF"] == cliente]

        # Separar RI e Vídeos
        ris = df_cliente[df_cliente["Produto"].str.contains("RI", na=False)]
        videos = df_cliente[df_cliente["Produto"].str.contains("VD", na=False)]

        oportunidades = []

        for _, ri in ris.iterrows():
            titulo_ri = normalizar_titulo(str(ri["Título"]))

            ja_foi = False
            for _, vd in videos.iterrows():
                titulo_vd = normalizar_titulo(str(vd["Título"]))
                score = similaridade(titulo_ri, titulo_vd)

                if score >= 0.60:  # ✅ REGRA CORRIGIDA
                    ja_foi = True
                    break

            if not ja_foi:
                oportunidades.append(ri)

        if oportunidades:
            for o in oportunidades:
                st.markdown(
                    f"- **{o['UF']}{o['Ciclo']} → {o['Produto']}** — _{o['Título']}_"
                )
                if o.get("Jira"):
                    st.markdown(f"[🔗 Abrir Jira]({o['Jira']})")
        else:
            st.success("Nenhuma oportunidade nova encontrada — todos os temas já viraram vídeo.")

# =====================
# AVISO FINAL
# =====================
st.markdown("---")
st.markdown("""
⚠️ **Este app não substitui a planilha do cliente.**  
Sempre confirme as informações diretamente na base oficial.
""")

st.image(
    "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExOXNmcTI5eWtoZHZ5eDJoem15MHBscnVjNHB2czA4cHRycjd6MWE3cyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/VF65SrQlmClUc/giphy.gif"
)
