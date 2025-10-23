import streamlit as st
import pandas as pd
import re
import json
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analisador de Conversas", layout="wide")

st.title("💬 Analisador Genérico de Conversas")
st.write("Envie um arquivo exportado do WhatsApp (.txt) e selecione as categorias que deseja pesquisar.")

# --- carregar palavras-chave ---
with open("keywords.json", "r", encoding="utf-8") as f:
    categorias = json.load(f)

# Mostrar categorias disponíveis
st.sidebar.header("⚙️ Configurações de análise")
todas_categorias = list(categorias.keys())

# --- escolher categorias ---
categorias_selecionadas = st.sidebar.multiselect(
    "Escolha as categorias que deseja analisar:",
    todas_categorias,
    default=todas_categorias  # todas marcadas por padrão
)

uploaded_file = st.file_uploader("📎 Envie o arquivo .txt da conversa", type="txt")

if uploaded_file:
    lines = uploaded_file.read().decode("utf-8", errors="ignore").splitlines()
    dados = []

    # Regex comum do WhatsApp
    padrao = r"^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2})\s+-\s+([^:]+):\s?(.*)$"

    for line in lines:
        m = re.match(padrao, line)
        if m:
            date, time, author, msg = m.groups()
            dados.append({"data": date, "hora": time, "autor": author.strip(), "mensagem": msg.strip()})

    df = pd.DataFrame(dados)
    st.success(f"{len(df)} mensagens carregadas de {df['autor'].nunique()} participantes.")
    st.dataframe(df.head(10))

    # --- função para classificar mensagens ---
    def classificar(msg):
        msg_lower = msg.lower()
        for cat in categorias_selecionadas:
            for palavra in categorias[cat]:
                if palavra in msg_lower:
                    return cat
        return "outros"

    df["categoria"] = df["mensagem"].apply(classificar)

    # --- contagem e exibição ---
    st.subheader("📊 Distribuição por categoria (filtradas)")
    contagem = df["categoria"].value_counts()

    if contagem.empty:
        st.warning("Nenhuma mensagem encontrada para as categorias selecionadas.")
    else:
        st.bar_chart(contagem)

        fig, ax = plt.subplots()
        ax.pie(contagem, labels=contagem.index, autopct="%1.1f%%")
        st.pyplot(fig)

    # --- mostrar mensagens filtradas ---
    st.subheader("📜 Mensagens filtradas")
    filtro = df[df["categoria"].isin(categorias_selecionadas)]
    st.dataframe(filtro)

    # --- botão para baixar CSV resultante ---
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Baixar CSV analisado", csv, "analise.csv", "text/csv")

else:
    st.info("Faça upload do arquivo de conversa para começar.")
