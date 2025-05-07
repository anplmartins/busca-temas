
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="🔍 Diagnóstico de Leitura de Abas", page_icon="🛠️")
st.title("🛠️ Diagnóstico de Leitura de Abas")
st.markdown("Esta versão mostra quantos temas estão sendo carregados por aba e de qual linha vem o cabeçalho.")

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
def diagnosticar_abas():
    resultados = []
    for nome_aba, gid in abas.items():
        url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}'
        encontrou = False
        for header_row in [0, 1, 2]:
            try:
                df = pd.read_csv(url, header=header_row)
                titulo_col = [col for col in df.columns if "título" in col.lower()]
                if titulo_col:
                    col = titulo_col[0]
                    temas = df[col].dropna().astype(str).tolist()
                    resultados.append({
                        "Aba": nome_aba,
                        "Header": f"Linha {header_row + 1}",
                        "Total Temas": len(temas),
                        "Exemplo": temas[:2]
                    })
                    encontrou = True
                    break
            except Exception as e:
                continue
        if not encontrou:
            resultados.append({
                "Aba": nome_aba,
                "Header": "❌ Não encontrado",
                "Total Temas": 0,
                "Exemplo": []
            })
    return resultados

resumo = diagnosticar_abas()

st.subheader("Resumo por aba:")
for r in resumo:
    st.markdown(f"**{r['Aba']}** — {r['Header']} — {r['Total Temas']} tema(s)")
    if r["Exemplo"]:
        for ex in r["Exemplo"]:
            st.markdown(f"• _{ex}_")
    st.markdown("---")
