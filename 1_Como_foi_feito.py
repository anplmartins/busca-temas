
import streamlit as st

st.set_page_config(page_title="ℹ️ Como o app foi construído", page_icon="ℹ️")

st.title("ℹ️ Como o app foi construído")
st.markdown("""
Este app foi desenvolvido para facilitar a consulta de temas **já produzidos** pelos SEBRAEs das UFs **RS** e **SP**.

---

### 🗂 Fonte de dados:
Os dados vêm de uma única planilha do Google Sheets:
- [Planilha consolidada](https://docs.google.com/spreadsheets/d/1W3SXFXuUtbYbvYN5xJBzGZVbxEA9iXx5ZQDVSv6SkSg)

Ela possui várias abas, uma por UF e ciclo contratual.

---

### 🧭 Abas utilizadas:
| Aba       | GID         | UF / Ciclo      |
|-----------|-------------|-----------------|
| RS25-26   | 0           | SEBRAE RS 2025–2026 |
| RS24-25   | 115275239   | SEBRAE RS 2024–2025 |
| RS23-24   | 2138405098  | SEBRAE RS 2023–2024 |
| RS22-23   | 1420824130  | SEBRAE RS 2022–2023 |
| SP24-25   | 205733653   | SEBRAE SP 2024–2025 |
| SP23-24   | 205552520   | SEBRAE SP 2023–2024 |
| SP22-23   | 80889       | SEBRAE SP 2022–2023 |
| SP21-22   | 1993459611  | SEBRAE SP 2021–2022 |

---

### 🔍 Funcionalidades:
- Busca por **frase exata**
- Busca por **palavras obrigatórias (AND)**
- Busca por **similaridade ≥ 40%**

---

### 🔧 Técnicas usadas:
- Leitura direta do CSV público exportado de cada aba (`export?format=csv&gid=...`)
- Identificação automática da linha de cabeçalho (1, 2 ou 3)
- Filtro da coluna “Título”
- Cálculo de similaridade com `difflib.SequenceMatcher`

---

### 📌 Atualizações futuras:
Você pode editar a planilha original, adicionar novas abas, ou atualizar os GIDs aqui na explicação para refletir novos ciclos.
""", unsafe_allow_html=True)
