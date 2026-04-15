import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai

# --- CONFIGURAÇÃO DA IA COM TESTE DE MODELOS ---
def inicializar_modelo():
    try:
        if "GEMINI_API_KEY" not in st.secrets:
            st.error("Chave não encontrada nos Secrets.")
            return None
        
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Lista de nomes que o Google usa para o mesmo modelo em diferentes regiões/contas
        nomes_para_testar = [
            'gemini-1.5-flash',
            'models/gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-pro'
        ]
        
        for nome in nomes_para_testar:
            try:
                model = genai.GenerativeModel(nome)
                # Teste rápido para ver se o modelo responde
                model.generate_content("oi", generation_config={"max_output_tokens": 1})
                return model # Se funcionou, retorna este
            except:
                continue # Se deu erro (como o 404), tenta o próximo nome
        
        return None
    except Exception as e:
        st.error(f"Erro crítico: {e}")
        return None

model = inicializar_modelo()

# --- INTERFACE ---
st.set_page_config(page_title="Agência Pro: Ads Tool", layout="wide")
st.title("🎯 Planejador de Palavras-Chave")

url_lp = st.text_input("URL da Landing Page:")

if st.button("Gerar Inteligência"):
    if not url_lp:
        st.warning("Insira uma URL.")
    elif not model:
        st.error("O Google recusou todos os nomes de modelos. Isso pode ser uma instabilidade momentânea na API gratuita na sua região.")
    else:
        with st.spinner("Analisando..."):
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                res = requests.get(url_lp, headers=headers, timeout=15)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, 'html.parser')
                texto = soup.get_text()[:1000]

                prompt = f"Gere 10 keywords de fundo de funil e 10 negativas para: {texto}"
                
                # Se chegar aqui e der erro, o problema é 100% a cota da chave
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.success("Sucesso!")
            except Exception as e:
                st.error(f"Erro: {e}")
