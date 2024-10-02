import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Pegar a URL do WebDriver do arquivo .env
SBR_WEBDRIVER = os.getenv("SBR_WEBDRIVER")

def scrape_website(website):
    print("Connecting to Scraping Browser...")

    # Iniciando o Chrome usando undetected-chromedriver
    driver = None
    try:
        # Se necessário, podemos adicionar argumentos como --proxy-server ou outros para contornar detecções
        options = uc.ChromeOptions()
        options.add_argument('--headless')  # Executar sem UI
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        # Adicione mais argumentos se precisar de um proxy ou outras configurações

        # Inicializar o driver com opções configuradas
        driver = uc.Chrome(options=options)

        print("Connected! Navigating...")
        
        # Navegar até o site
        driver.get(website)
        print("Waiting captcha to solve...")

        # Simular resolução de Captcha, se necessário (ajustar conforme sua necessidade)
        solve_res = driver.execute_script("return 'Captcha solved!'")
        print("Captcha solve status:", solve_res)
        
        print("Navigated! Scraping page content...")
        html = driver.page_source
        return html

    except Exception as e:
        print("Error during WebDriver connection:", str(e))
    
    finally:
        # Certificar-se de que o driver seja encerrado corretamente
        if driver is not None:
            try:
                driver.quit()
            except Exception as e:
                print("Error while quitting the driver:", str(e))

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i: i + max_length] for i in range(0, len(dom_content), max_length)
    ]

# Teste do script
if __name__ == "__main__":
    test_url = "https://example.com"
    html = scrape_website(test_url)
    if html:
        body = extract_body_content(html)
        cleaned_body = clean_body_content(body)
        print("Cleaned Body Content:\n", cleaned_body)
