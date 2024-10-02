from selenium.webdriver import ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import os
from dotenv import load_dotenv
import tiktoken
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import HumanMessage

# Carregar variáveis de ambiente
load_dotenv()

# Pegar a URL do WebDriver do arquivo .env
SBR_WEBDRIVER = os.getenv("SBR_WEBDRIVER")

# Template para extração de informações
template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

# Configura o modelo para ser utilizado com ChatGPT
llm = ChatOpenAI(
    model="gpt-4"
)

def scrape_website(website):
    print("Connecting to Scraping Browser...")

    driver = None
    try:
        # Inicializando o Chrome usando undetected_chromedriver
        options = ChromeOptions()
        options.add_argument('--headless')  # Executar sem UI
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--remote-debugging-port=9222')  # Garantir compatibilidade

        # Tente inicializar o driver
        try:
            driver = uc.Chrome(options=options)
            print("Connected! Navigating...")
        except Exception as e:
            print("Failed to initialize the WebDriver:", str(e))
            return None

        # Verifique se o driver foi inicializado corretamente
        if driver is None:
            print("Driver initialization failed. Exiting the function.")
            return None

        # Navegar até o site
        driver.get(website)

        # Espera explícita para garantir que o body esteja presente na página carregada
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("Page loaded. Waiting captcha to solve...")
        except Exception as e:
            print("Error waiting for page body to load:", str(e))
            return None

        # Simular resolução de CAPTCHA (ajustar conforme necessário)
        try:
            solve_res = driver.execute_script("return 'Captcha solved!'")
            print("Captcha solve status:", solve_res)
        except Exception as e:
            print("Error during CAPTCHA resolution:", str(e))
            return None

        print("Navigated! Scraping page content...")
        html = driver.page_source
        return html

    except Exception as e:
        print("Unexpected error during WebDriver connection:", str(e))
        return None

    finally:
        # Certificar-se de que o driver seja encerrado corretamente
        if driver is not None:
            try:
                driver.quit()
            except Exception as e:
                print("Error while quitting the driver:", str(e))

def extract_body_content(html_content):
    if not html_content:
        print("No HTML content provided for extraction.")
        return ""

    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    # Remover tags desnecessárias, como script e style
    for script_or_style in soup(["script", "style", "noscript", "iframe"]):
        script_or_style.extract()

    # Obter o texto limpo
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

def split_dom_content_by_tokens(dom_content, max_tokens=800):
    encoder = tiktoken.get_encoding("cl100k_base")
    tokens = encoder.encode(dom_content)

    chunks = [
        tokens[i: i + max_tokens] for i in range(0, len(tokens), max_tokens)
    ]
    return ["".join(encoder.decode(chunk)) for chunk in chunks]

def parse_with_chatgpt(dom_chunks, parse_description):
    # Cria um template de prompt com as variáveis {dom_content} e {parse_description}
    prompt = ChatPromptTemplate.from_template(template)

    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        # Gera o prompt com o chunk atual e a descrição para parse
        formatted_prompt = prompt.format_messages(dom_content=chunk, parse_description=parse_description)

        # O ChatPromptTemplate gera uma lista de mensagens que o ChatModel entende
        # Aqui passamos a mensagem humana para o modelo
        response = llm.invoke(formatted_prompt)

        # Captura a resposta do modelo e a adiciona na lista de resultados
        print(f"Parsed batch: {i} of {len(dom_chunks)}")
        parsed_results.append(response.content)

    # Retorna todos os resultados concatenados com uma quebra de linha
    return "\n".join(parsed_results)

# Teste do script
if __name__ == "__main__":
    test_url = "https://example.com"
    html = scrape_website(test_url)

    if html:
        body = extract_body_content(html)
        if body:
            cleaned_body = clean_body_content(body)
            print("Cleaned Body Content:\n", cleaned_body)

            # Dividir o conteúdo limpo em chunks de tokens
            chunks = split_dom_content_by_tokens(cleaned_body)

            # Descrição para o ChatGPT analisar
            parse_description = "Extract any sentence that contains specific information, for example the word 'libero'."

            # Analisar o conteúdo utilizando ChatGPT
            result = parse_with_chatgpt(chunks, parse_description)
            print("\nParsed Content:\n", result)
P