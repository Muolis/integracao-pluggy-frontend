import json
from backend import app

def run_tests():
    print("Iniciando testes automatizados do Backend...")
    client = app.test_client()

    # 1. Teste /health
    res = client.get('/health')
    assert res.status_code == 200, f"Health check falhou: {res.status_code}"
    health_data = res.get_json()
    print(" Teste 1 [/health]: Sucesso! Resposta:", health_data)

    # 2. Teste /api/login com credenciais inválidas
    res_bad = client.post('/api/login', json={"usuario": "admin", "senha": "senha_errada"})
    assert res_bad.status_code == 401, f"Login inválido não retornou 401: {res_bad.status_code}"
    print(" Teste 2 [/api/login com erro]: Sucesso! Retornou 401 conforme esperado.")

    # 3. Teste /api/login com credenciais válidas
    res_good = client.post('/api/login', json={"usuario": "admin", "senha": "securitizadora2026"})
    assert res_good.status_code == 200, f"Login válido falhou: {res_good.status_code}"
    login_data = res_good.get_json()
    token = login_data.get("token")
    assert token, "Token de sessão não retornado"
    print(" Teste 3 [/api/login com sucesso]: Sucesso! Token gerado com assinatura HMAC.")

    # 4. Teste /listar-conexoes SEM token (Deve retornar 401)
    res_unauth = client.get('/listar-conexoes')
    assert res_unauth.status_code == 401, f"Rota protegida sem token não retornou 401: {res_unauth.status_code}"
    print(" Teste 4 [Proteção de rota sem token]: Sucesso! Retornou 401 bloqueando acesso indevido.")

    # 5. Teste /listar-conexoes COM token válido (Deve retornar 200)
    res_auth = client.get('/listar-conexoes', headers={"Authorization": f"Bearer {token}"})
    assert res_auth.status_code == 200, f"Rota protegida com token falhou: {res_auth.status_code}"
    print(" Teste 5 [Acesso autorizado a conexões]: Sucesso! Retornou 200 com token válido.")

    # 6. Teste rotas estáticas servidas pelo Flask
    res_index = client.get('/')
    assert res_index.status_code == 200, "Falha ao servir index/login"
    res_cliente = client.get('/cliente.html')
    assert res_cliente.status_code == 200, "Falha ao servir cliente.html"
    res_config = client.get('/config.js')
    assert res_config.status_code == 200, "Falha ao servir config.js"
    print(" Teste 6 [Servidor de arquivos estáticos]: Sucesso! HTMLs e config.js servidos corretamente.")

    # 7. Teste /listar-bancos com códigos COMPE
    res_bancos = client.get('/listar-bancos')
    assert res_bancos.status_code == 200, f"Listar bancos falhou: {res_bancos.status_code}"
    bancos = res_bancos.get_json()
    assert len(bancos) > 0, "Nenhum banco retornado"
    assert "code" in bancos[0], "Campo 'code' ausente nos bancos"
    print(f" Teste 7 [/listar-bancos]: Sucesso! {len(bancos)} bancos retornados com códigos COMPE.")

    # 8. Teste /listar-conexoes com separação de tipos
    conexoes = res_auth.get_json()
    for c in conexoes:
        assert c.get("tipo") in ["open_finance", "pix_automatico"], f"Tipo inválido: {c.get('tipo')}"
        if c.get("payment_intent_id"):
            assert c["tipo"] == "pix_automatico", "Cliente com intent ID não categorizado como pix_automatico"
    print(f" Teste 8 [/listar-conexoes separação]: Sucesso! {len(conexoes)} conexões estritamente separadas por tipo.")

    print("\n TODOS OS 8 TESTES DO BACKEND PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    run_tests()
