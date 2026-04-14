import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURAÇÃO DE SEGURANÇA ---
# O script agora busca a chave automaticamente nos Secrets do Streamlit
try:
    CHAVE_MESTRA = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=CHAVE_MESTRA)
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.error("Erro: A chave API não foi configurada nos Secrets do Streamlit.")

# --- INTERFACE LIMPA ---
st.set_page_config(page_title="Agência Pro: Gerador de Keywords", layout="wide")
st.title("🎯 Gerador de Keywords Fundo de Funil")
st.write("Insira a URL abaixo para analisar a estratégia do cliente.")

# Apenas a URL como input
url_lp = st.text_input("URL da Landing Page ou Site:", placeholder="https://exemplo.com.br")

if st.button("Gerar Inteligência de Campanha"):
    if not url_lp:
        st.warning("Por favor, insira uma URL válida.")
    else:
        with st.spinner("A IA está analisando a página..."):
            try:
                # 1. Raspagem da página
                res = requests.get(url_lp, timeout=10)
                soup = BeautifulSoup(res.text, 'html.parser')
                texto = f"{soup.title.text if soup.title else ''} " + " ".join([p.text for p in soup.find_all('p')[:5]])
                
                # 2. Prompt Estruturado para a Agência
                prompt = f"""
                Analise esta Landing Page: '{texto}'
                Como um especialista em Google Ads focado em alta conversão:
                1. Liste 10 palavras-chave de 'Fundo de Funil' (intenção de compra imediata).
                2. Liste 15 palavras-chave 'Negativas' para evitar desperdício de verba.
                3. Sugira um título de anúncio magnético baseado na oferta principal.
                Responda com formatação clara usando Bullet Points.
                """
                
                response = model.generate_content(prompt)
                
                # 3. Exibição dos resultados
                st.divider()
                st.markdown(response.text)
                st.success("Análise finalizada com sucesso!")
                
            except Exception as e:
                st.error(f"Não conseguimos ler esta URL. Verifique se o site permite acesso ou tente outra. Erro: {e}")
