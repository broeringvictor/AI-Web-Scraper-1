import streamlit as st
from scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content_by_tokens  # Atualizado para usar a função correta que divide em tokens
)
import os
from dotenv import load_dotenv
load_dotenv()
from parse import parse_with_chatgpt  # Adaptar para usar o ChatGPT

# Carregar variável do WebDriver do .env (embora não seja diretamente usada aqui, ainda pode ser útil)
SBR_WEBDRIVER = os.getenv("SBR_WEBDRIVER")
print(f"SBR_WEBDRIVER: {SBR_WEBDRIVER}")

# Streamlit UI
st.title("AI Web Scraper")
url = st.text_input("Enter Website URL")

# Step 1: Scrape the Website
if st.button("Scrape Website"):
    if url:
        st.write("Scraping the website...")

        # Scrape the website
        dom_content = scrape_website(url)

        if dom_content:
            # Extraindo o conteúdo do body
            body_content = extract_body_content(dom_content)

            if body_content:
                # Limpeza do conteúdo
                cleaned_content = clean_body_content(body_content)

                # Armazena o conteúdo do DOM limpo no estado da sessão do Streamlit
                st.session_state.dom_content = cleaned_content

                # Exibir o conteúdo DOM limpo em uma área de texto expansível
                with st.expander("View Cleaned DOM Content"):
                    st.text_area("Cleaned DOM Content", cleaned_content, height=300)
            else:
                st.error("Failed to extract body content from the HTML.")
        else:
            st.error("Failed to scrape the website. Please check the URL or try again later.")

# Step 2: Ask Questions About the DOM Content
if "dom_content" in st.session_state:
    parse_description = st.text_area("Describe what you want to parse")

    if st.button("Parse Content"):
        if parse_description:
            st.write("Parsing the content...")

            # Dividir o conteúdo do DOM limpo em chunks usando tokens para garantir compatibilidade com o modelo
            dom_chunks = split_dom_content_by_tokens(st.session_state.dom_content)

            # Parse o conteúdo usando ChatGPT
            parsed_result = parse_with_chatgpt(dom_chunks, parse_description)

            # Exibir o resultado do parsing
            st.write(parsed_result)
        else:
            st.warning("Please provide a description of what you want to parse.")

