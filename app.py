import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURAÇÃO DE SEGURANÇA E MODELO ---
try:
    # Busca a chave nos Secrets do Streamlit
    CHAVE_MESTRA = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=CHAVE_MESTRA)
    
    # Usar 'gemini-1.5-flash-latest' resolve o erro 404 em chaves gratuitas
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"Erro na configuração: Verifique se a chave está nos Secrets. Detalhes: {e}")

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Agência Pro: Ads Tool", layout="wide", page_icon="🎯")

# CSS para esconder o menu do Streamlit e focar no conteúdo (bom para embed)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Gerador de Keywords Fundo de Funil")
st.write("Insira a URL abaixo para extrair inteligência de campanha diretamente da Landing Page.")

# --- INPUT DO USUÁRIO ---
url_lp = st.text_input("URL da Landing Page ou Site:", placeholder="https://exemplo.com.br")

if st.button("Gerar Inteligência de Campanha"):
    if not url_lp:
        st.warning("Por favor, insira uma URL válida.")
    else:
        with st.spinner("Lendo o site e consultando a IA..."):
            try:
                # 1. RASPAGEM DA PÁGINA (Com cabeçalhos para evitar bloqueio 403/404)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                
                # Timeout de 15 segundos para não travar o app
                res = requests.get(url_lp, headers=headers, timeout=15)
                res.raise_for_status() 
                
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Captura Título e os primeiros parágrafos relevantes
                titulo = soup.title.text if soup.title else "Sem título"
                paragrafos = [p.text for p in soup.find_all('p') if len(p.text) > 20]
                conteudo_extraido = f"Título: {titulo} | Conteúdo: {' '.join(paragrafos[:5])}"

                # 2. CONSULTA AO GEMINI
                prompt = f"""
                Você é um gestor de tráfego sênior. Com base neste conteúdo de site: '{conteudo_extraido}'
                
                1. Liste 10 palavras-chave de 'Fundo de Funil' (foco em quem quer comprar/contratar agora).
                2. Liste 15 palavras-chave 'Negativas' (termos curiosos, informativos ou fora de contexto).
                3. Sugira 3 títulos de anúncios magnéticos para Google Ads.
                
                Responda em Português, formatado com Bullet Points e negritos.
                """
                
                response = model.generate_content(prompt)
                
                # 3. EXIBIÇÃO DOS RESULTADOS
                st.divider()
                st.markdown("### 🚀 Resultado da Análise Estratégica")
                st.markdown(response.text)
                st.success("Análise finalizada com sucesso!")

            except requests.exceptions.HTTPError as err:
                st.error(f"O site do cliente bloqueou nossa leitura (Erro {err.response.status_code}). Tente outra URL ou verifique se o site está no ar.")
            except Exception as e:
                # Se o erro for 429, é excesso de uso da chave gratuita
                if "429" in str(e):
                    st.error("Limite de uso atingido (Cota Gratuita). Aguarde 1 minuto e tente novamente.")
                else:
                    st.error(f"Ocorreu um erro: {e}")

# Rodapé simples
st.caption("Ferramenta interna - Orgânica Digital")
