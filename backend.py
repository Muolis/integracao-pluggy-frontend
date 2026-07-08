import requests

# 1. Suas credenciais da Pluggy (Ambiente GABRIEL MC)
CLIENT_ID = "211d02fb-efd6-4fd6-89d3-5855682cceae"
CLIENT_SECRET = "c32fbec8-d60c-41d5-a4d9-84cb710bc898"

def gerar_token():
    print("Iniciando comunicação com a Pluggy...")

    # Passo 1: Autenticar e pegar a API Key
    print("1. Autenticando...")
    auth_response = requests.post(
        "https://api.pluggy.ai/auth",
        json={
            "clientId": CLIENT_ID,
            "clientSecret": CLIENT_SECRET
        }
    )

    if auth_response.status_code != 200:
        print("Erro na autenticação. Verifique suas credenciais!")
        print("Detalhes:", auth_response.text)
        return

    api_key = auth_response.json().get("apiKey")

    # Passo 2: Usar a API Key para gerar o Connect Token
    print("2. Gerando Token de Conexão temporário...")
    token_response = requests.post(
        "https://api.pluggy.ai/connect_token",
        headers={
            "X-API-KEY": api_key,
            "Content-Type": "application/json"
        }
    )

    if token_response.status_code != 200:
        print("Erro ao gerar o Connect Token!")
        print("Detalhes:", token_response.text)
        return

    connect_token = token_response.json().get("accessToken")
    
    print("\n" + "="*50)
    print("🚀 SUCESSO! AQUI ESTÁ O SEU CONNECT TOKEN:")
    print("="*50)
    print(connect_token)
    print("="*50 + "\n")

if __name__ == "__main__":
    gerar_token()