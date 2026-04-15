import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- 1. CONFIGURAÇÃO DA IA (BLINDADA PARA CHAVE GRATUITA) ---
def configurar_ia():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            # Usamos o nome padrão. Se a chave for nova e de um 'New Project', 
            # o erro 404 não deve ocorrer.
            return genai.GenerativeModel('gemini-1.5-flash')
        else:
            st.error("Chave 'GEMINI_API_KEY' não encontrada nos Secrets do Streamlit.")
            return None
    except Exception as e:
        st.error(f"Erro ao configurar IA: {e}")
        return None

model = configurar_ia()

# --- 2. CONFIGURAÇÃO DA INTERFACE (OTIMIZADA PARA EMBED) ---
st.set_page_config(page_title="Agência Pro: Ads Tool", layout="wide", page_icon="🎯")

# CSS para limpar a interface e parecer nativo no seu site
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stHeader"] {display: none;}
    .main {padding-top: 1rem;}
    </style>
    """, unsafe_allow_html=True)

st.title("🎯 Planejador de Palavras-Chave")
st.write("Extraia inteligência estratégica diretamente da Landing Page do cliente.")

# --- 3. CAMPO DE ENTRADA ---
url_lp = st.text_input("URL da Landing Page ou Site:", placeholder="https://exemplo.com.br")

if st.button("Gerar Inteligência de Campanha"):
    if not url_lp:
        st.warning("Por favor, insira uma URL válida.")
    elif not model:
        st.error("A IA não está configurada. Verifique os Secrets.")
    else:
        with st.spinner("Analisando site e consultando a IA..."):
            try:
                # A. RASPAGEM DA PÁGINA (Fingindo ser um navegador real)
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
                    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
                }
                
                # Faz a requisição com timeout para não travar
                response_site = requests.get(url_lp, headers=headers, timeout=20)
                response_site.raise_for_status()
                
                # B. EXTRAÇÃO DE TEXTO
                soup = BeautifulSoup(response_site.text, 'html.parser')
                
                # Remove scripts e estilos para não confundir a IA
                for script_or_style in soup(["script", "style"]):
                    script_or_style.decompose()
                
                titulo = soup.title.string if soup.title else "Sem título"
                # Pega os primeiros 1500 caracteres de texto limpo
                texto_pag = soup.get_text(separator=' ', strip=True)[:1500]
                
                # C. PROMPT ESTRUTURADO
                prompt = f"""
                Você é um Especialista em Google Ads. Analise o conteúdo deste site:
                TITULO: {titulo}
                CONTEÚDO: {texto_pag}
                
                Com base nisso, gere:
                1. Uma lista com 10 Palavras-chave de 'Fundo de Funil' (intenção de compra/serviço).
                2. Uma lista com 15 Palavras-chave 'Negativas' (evitar cliques curiosos).
                3. Três sugestões de Títulos para Anúncios (RSA) focados em conversão.
                
                Formate em Português (Brasil) usando Bullet Points e Negritos.
                """
                
                # D. CHAMADA DA IA
                resposta_ia = model.generate_content(prompt)
                
                # E. EXIBIÇÃO DOS RESULTADOS
                st.divider()
                st.markdown("### 🚀 Estratégia Recomendada")
                st.markdown(resposta_ia.text)
                st.success("Análise concluída!")

            except requests.exceptions.RequestException as e:
                st.error(f"Erro ao acessar o site: {e}. O site pode estar bloqueando acessos automáticos.")
            except Exception as e:
                # Tratamento para erro de cota (429) ou outros erros de API
                if "429" in str(e):
                    st.error("Limite de uso atingido (Cota Gratuita). Aguarde 60 segundos.")
                elif "404" in str(e):
                    st.error("Erro 404: Modelo não encontrado. Isso geralmente indica que sua Chave API precisa ser recriada em um 'NEW PROJECT' no Google AI Studio.")
                else:
                    st.error(f"Erro inesperado: {e}")

# Rodapé
st.caption("Ferramenta de Inteligência - Orgânica Digital")
