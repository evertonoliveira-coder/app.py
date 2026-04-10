import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# Título da Ferramenta
st.set_page_config(page_title="Agência Pro: Ads Tool")
st.title("🎯 Gerador de Keywords Fundo de Funil")

# Inputs na barra lateral
with st.sidebar:
    st.header("Configurações")
    gemini_key = st.text_input("Chave API do Gemini:", type="password")
    url_lp = st.text_input("URL da Landing Page do Cliente:")

if st.button("Analisar Landing Page"):
    if not gemini_key or not url_lp:
        st.error("Por favor, preencha a chave do Gemini e a URL.")
    else:
        with st.spinner("Lendo a página e gerando ideias..."):
            try:
                # 1. Tenta ler o conteúdo da URL
                res = requests.get(url_lp, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                texto = f"{soup.title.text if soup.title else ''} " + " ".join([p.text for p in soup.find_all('p')[:3]])
                
                # 2. Configura a IA
                genai.configure(api_key=gemini_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"Com base neste conteúdo de Landing Page: '{texto}', gere 10 palavras-chave de fundo de funil (foco em conversão) e 10 palavras negativas."
                
                response = model.generate_content(prompt)
                
                # 3. Exibe o resultado
                st.subheader("🚀 Sugestões da IA")
                st.write(response.text)
                st.success("Análise concluída!")
                
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
