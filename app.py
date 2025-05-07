
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher

st.set_page_config(page_title="🔍 Busca Inteligente de Temas", page_icon="📘")
st.title("📘 Busca Inteligente de Temas com Filtros")

st.markdown("""
Você pode digitar um tema e consultar os resultados com **três métodos diferentes**, exibidos lado a lado:

- 🔹 **Frase exata**: Encontre temas que contenham exatamente o texto digitado.  
  Exemplo: `"MEI para ME"` → retorna apenas temas com essa frase exata, na mesma ordem.

- 🔸 **Contém todas (AND)**: Encontre temas que incluam **todas as palavras digitadas**, em qualquer ordem.  
  Exemplo: `MEI AND marketing` → retorna temas que contenham tanto "MEI" quanto "marketing".

- 🔺 **Similaridade ≥ 40%**: Compara seu texto com todos os temas, mesmo com variações, e retorna os mais parecidos.  
  Exemplo: `Transformar MEI` → pode retornar "Quando migrar de MEI para ME?" ou "MEI e transição para ME".
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

entrada = st.text_input("Digite um tema para buscar:")

if entrada:
    entrada = entrada.strip()
    termo_exato = entrada.lower().strip('"')
    palavras_and = [p.strip().lower() for p in entrada.upper().split("AND")]
    
    exato = []
    and_results = []
    similares = []

    for _, row in temas_df.iterrows():
        tema = row["Tema"]
        tema_l = tema.lower()
        
        # Busca exata com aspas
        if termo_exato in tema_l:
            exato.append((row["UF_Ciclo"], tema))
        
        # Busca com AND
        if all(p.lower() in tema_l for p in palavras_and):
            and_results.append((row["UF_Ciclo"], tema))
        
        # Similaridade ≥ 40%
        score = round(similaridade(entrada, tema) * 100, 1)
        if score >= 40:
            similares.append((row["UF_Ciclo"], tema, score))

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🔹 Frase exata")
        if exato:
            for uf, t in exato:
                st.markdown(f"- **{uf}** → _{t}_")
        else:
            st.markdown("*Nenhum encontrado*")

    with col2:
        st.subheader("🔸 Contém todas (AND)")
        if and_results:
            for uf, t in and_results:
                st.markdown(f"- **{uf}** → _{t}_")
        else:
            st.markdown("*Nenhum encontrado*")

    with col3:
        st.subheader("🔺 Similaridade (≥40%)")
        if similares:
            for uf, t, s in sorted(similares, key=lambda x: x[2], reverse=True):
                st.markdown(f"- **{uf}** → _{t}_ — {s}%")
        else:
            st.markdown("*Nenhum encontrado*")
