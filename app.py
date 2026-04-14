import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURAÇÃO PARA CHAVE GRATUITA (FREE TIER) ---
# O segredo para evitar o erro 404 em chaves gratuitas é usar o caminho completo 'models/...'
try:
    if "GEMINI_API_KEY" in st.secrets:
        CHAVE_MESTRA = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=CHAVE_MESTRA)
        # Nomenclatura específica para chaves do Google AI Studio Free
        model = genai.GenerativeModel('models/gemini-1.5-flash')
    else:
        st.error("Erro: A chave GEMINI_API_KEY não foi encontrada nos Secrets do Streamlit.")
except Exception as e:
    st.error(f"Erro na inicialização da IA: {e}")

# --- CONFIGURAÇÃO DA PÁGINA (Interface Limpa para Embed) ---
st.set_page_config(page_title="Agência Pro: Ads Tool", layout="wide", page_icon="🎯")

# CSS para remover menus desnecessários quando embutido no seu site
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Planejador de Palavras-Chave")
st.write("Extraia inteligência estratégica diretamente da Landing Page do cliente.")

# --- INPUT DO USUÁRIO ---
url_lp = st.text_input("URL da Landing Page ou Site:", placeholder="https://exemplo.com.br")

if st.button("Gerar Inteligência de Campanha"):
    if not url_lp:
        st.warning("Por favor, insira uma URL válida.")
    else:
        with st.spinner("Lendo o site e consultando a IA..."):
            try:
                # 1. RASPAGEM DA PÁGINA (Com User-Agent para evitar bloqueios como o da Yathon)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                
                res = requests.get(url_lp, headers=headers, timeout=15)
                res.raise_for_status() 
                
                soup = BeautifulSoup(res.text, 'html.parser')
                
                # Captura Título e conteúdo textual principal
                titulo = soup.title.text if soup.title else "Site sem título"
                # Pega apenas os parágrafos com conteúdo real (evita menus e rodapés vazios)
                paragrafos = [p.text.strip() for p in soup.find_all('p') if len(p.text) > 30]
                texto_limpo = f"Título: {titulo} | Conteúdo: {' '.join(paragrafos[:6])}"

                # 2. PROMPT ESTRUTURADO PARA O GEMINI
                prompt = f"""
                Você é um Especialista em Google Ads e SEO. Analise este conteúdo de site: '{texto_limpo}'
                
                Com base no serviço/produto oferecido, gere:
                1. Uma lista com 10 Palavras-chave de Fundo de Funil (com intenção de conversão).
                2. Uma lista com 15 Palavras-chave Negativas (termos que trazem tráfego desqualificado).
                3. Três sugestões de Títulos de Anúncios focados em benefícios.
                
                Responda em Português do Brasil, usando negritos e bullet points.
                """
                
                # 3. CHAMADA DA IA
                response = model.generate_content(prompt)
                
                # 4. EXIBIÇÃO DOS RESULTADOS
                st.divider()
                st.markdown("### 🚀 Estratégia Recomendada")
                st.markdown(response.text)
                st.success("Análise finalizada com sucesso!")

            except requests.exceptions.HTTPError as err:
                st.error(f"O site bloqueou o acesso automático (Erro {err.response.status_code}). Tente outra URL.")
            except Exception as e:
                # Tratamento amigável para limite de cota da chave gratuita (Erro 429)
                if "429" in str(e):
                    st.error("A cota gratuita de consultas foi atingida. Aguarde 60 segundos e tente novamente.")
                else:
                    st.error(f"Erro ao processar: {e}")

# Rodapé discreto
st.caption("Ferramenta Interna - Orgânica Digital")
