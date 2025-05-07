
import streamlit as st
import pandas as pd
from difflib import SequenceMatcher
import gspread
from google.oauth2.service_account import Credentials

# Configurações
SCOPE = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg'

# Autenticação
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPE)
gc = gspread.authorize(creds)
sh = gc.open_by_key(SPREADSHEET_ID)

# Função para detectar qual linha contém o cabeçalho
def get_header_and_data(worksheet):
    rows = worksheet.get_all_values()
    for i in range(2):  # verificar as duas primeiras linhas
        if "título" in [cell.lower() for cell in rows[i]]:
            header = rows[i]
            data = rows[i + 1:]
            df = pd.DataFrame(data, columns=header)
            return df
    return pd.DataFrame()

# Consolidar temas por UF
uf_temas = {}
for ws in sh.worksheets():
    title = ws.title
    if len(title) >= 7 and title[:2].isalpha():
        uf = title[:2]
        df = get_header_and_data(ws)
        if "Título" in df.columns:
            temas = df["Título"].dropna().astype(str).tolist()
            if uf not in uf_temas:
                uf_temas[uf] = []
            uf_temas[uf].extend(temas)

# Função de similaridade
def similarity(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_similar_titles(input_title, uf, threshold=0.6):
    temas = uf_temas.get(uf, [])
    similares = []
    for tema in temas:
        score = similarity(input_title, tema)
        if score >= threshold:
            similares.append((tema, round(score * 100, 1)))
    similares.sort(key=lambda x: x[1], reverse=True)
    return similares

# Interface
st.set_page_config(page_title="Busca de Temas por Similaridade", page_icon="🔍")
st.title("🔍 Busca de Temas por Similaridade")
st.markdown("Consulte se um tema (ou algo parecido) já foi feito para o Sebrae da UF selecionada.")

uf = st.selectbox("Selecione a UF:", sorted(uf_temas.keys()))
tema_novo = st.text_input("Digite o novo tema:")

if tema_novo and uf:
    resultados = find_similar_titles(tema_novo, uf)
    if resultados:
        st.subheader(f"Temas similares já feitos para {uf}:")
        for item in resultados:
            st.markdown(f"- **{item[0]}** — Similaridade: {item[1]}%")
    else:
        st.success("✅ Nenhum tema semelhante encontrado para esta UF.")
