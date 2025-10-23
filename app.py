import streamlit as st
import pandas as pd
import re
import json
from collections import Counter
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analisador de Conversas", layout="wide")

st.title("💬 Analisador Genérico de Conversas")
st.write("Envie um arquivo exportado do WhatsApp (.txt) e veja análises automáticas com base em palavras-chave configuráveis.")

# --- carregar palavras-chave ---
with open("keywords.json", "r", encoding="utf-8") as f:
    categorias = json.load(f)

# upload
uploaded_file = st.file_uploader("📎 Envie o arquivo .txt da conversa", type="txt")

if uploaded_file:
    lines = uploaded_file.read().decode("utf-8", errors="ignore").splitlines()
    dados = []

    for line in lines:
        m = re.match(r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s+-\s+([^:]+):\s?(.*)$", line)
        if m:
            date, time, author, msg = m.groups()
            dados.append({"data": date, "hora": time, "autor": author.strip(), "mensagem": msg.strip()})

    df = pd.DataFrame(dados)
    st.success(f"{len(df)} mensagens carregadas de {df['autor'].nunique()} participantes.")
    st.dataframe(df.head(10))

    # --- classificação por palavras-chave ---
    def classificar(msg):
        msg_lower = msg.lower()
        for cat, palavras in categorias.items():
            if any(p in msg_lower for p in palavras):
                return cat
        return "outros"

    df["categoria"] = df["mensagem"].apply(classificar)

    # --- contagem e exibição ---
    st.subheader("📊 Distribuição por categoria")
    contagem = df["categoria"].value_counts()
    st.bar_chart(contagem)

    fig, ax = plt.subplots()
    ax.pie(contagem, labels=contagem.index, autopct="%1.1f%%")
    st.pyplot(fig)

    # --- baixar CSV resultante ---
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV analisado", csv, "analise.csv", "text/csv")

else:
    st.info("Faça upload do arquivo de conversa para começar.")
