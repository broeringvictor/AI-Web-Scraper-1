from langchain_openai import ChatOpenAI  # Import atualizado conforme a mensagem de depreciação
from langchain.prompts.chat import ChatPromptTemplate
from langchain.schema import HumanMessage
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

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
    dom_chunks = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "Phasellus eget risus nec libero pulvinar aliquet."
    ]
    parse_description = "Extract any sentence that contains the word 'libero'."
    
    result = parse_with_chatgpt(dom_chunks, parse_description)
    print("\nResultado Final:\n", result)
