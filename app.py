import streamlit as st
import pandas as pd
import re
import json
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analisador de Conversas", layout="wide")

st.title("💬 Analisador de Conversas WhatsApp")
st.write("Envie um arquivo exportado do WhatsApp (.txt) e pesquise por qualquer palavra ou expressão.")

# --- carregar palavras-chave (opcional) ---
try:
    with open("keywords.json", "r", encoding="utf-8") as f:
        categorias = json.load(f)
except FileNotFoundError:
    categorias = {}

# upload do arquivo
uploaded_file = st.file_uploader("📎 Envie o arquivo .txt da conversa", type="txt")

if uploaded_file:
    lines = uploaded_file.read().decode("utf-8", errors="ignore").splitlines()
    dados = []

    padrao = r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s+-\s+([^:]+):\s?(.*)$"

    for line in lines:
        m = re.match(padrao, line)
        if m:
            date, time, author, msg = m.groups()
            dados.append({"data": date, "hora": time, "autor": author.strip(), "mensagem": msg.strip()})

    df = pd.DataFrame(dados)
    st.success(f"{len(df)} mensagens carregadas de {df['autor'].nunique()} participantes.")
    st.dataframe(df.head(10))

    # --- campo de busca ---
    st.sidebar.header("🔍 Pesquisa")
    termo = st.sidebar.text_input("Digite uma palavra ou expressão para buscar:")

    if termo:
        resultado = df[df["mensagem"].str.contains(termo, case=False, na=False)]
        st.subheader(f"📍 Resultados da busca por: '{termo}'")
        st.write(f"Mensagens encontradas: {len(resultado)}")
        if not resultado.empty:
            st.dataframe(resultado)
        else:
            st.warning("Nenhuma mensagem contém esse termo.")

    # --- estatísticas simples ---
    st.subheader("📊 Estatísticas gerais")
    contagem = df["autor"].value_counts()
    st.bar_chart(contagem)

    # --- gráfico de atividade por hora ---
    df["hora_int"] = pd.to_datetime(df["hora"], format="%H:%M", errors="coerce").dt.hour
    atividade = df.groupby("hora_int").size()
    st.subheader("⏰ Mensagens por hora do dia")
    st.bar_chart(atividade)

    # --- baixar CSV ---
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar conversa em CSV", csv, "conversa.csv", "text/csv")

else:
    st.info("Faça upload do arquivo de conversa para começar.")
