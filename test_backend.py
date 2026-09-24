import json
from backend import app, calcular_extrato_pix

def run_tests():
    print("Iniciando bateria completa de testes automatizados do Backend...\n")
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
    res_raiz = client.get('/')
    assert res_raiz.status_code == 200, "Falha ao servir raiz"
    res_index = client.get('/index.html')
    assert res_index.status_code == 200, "Falha ao servir index.html"
    res_cliente = client.get('/cliente.html')
    assert res_cliente.status_code == 200, "Falha ao servir cliente.html"
    res_gestor = client.get('/gestor.html')
    assert res_gestor.status_code == 200, "Falha ao servir gestor.html"
    res_extratos = client.get('/extratos.html')
    assert res_extratos.status_code == 200, "Falha ao servir extratos.html"
    res_config = client.get('/config.js')
    assert res_config.status_code == 200, "Falha ao servir config.js"
    res_logo = client.get('/logo-mc-minhaconta.png')
    assert res_logo.status_code == 200, "Falha ao servir logo-mc-minhaconta.png"
    print(" Teste 6 [Servidor de arquivos estáticos]: Sucesso! HTMLs, config.js e logo servidos corretamente.")

    # 7. Teste Headers de Segurança HTTP
    assert res_raiz.headers.get("X-Content-Type-Options") == "nosniff", "Header nosniff ausente"
    assert res_raiz.headers.get("X-Frame-Options") == "SAMEORIGIN", "Header SAMEORIGIN ausente"
    print(" Teste 7 [Headers de Segurança HTTP]: Sucesso! X-Content-Type-Options e X-Frame-Options validados.")

    # 8. Teste /listar-bancos com códigos COMPE
    res_bancos = client.get('/listar-bancos')
    assert res_bancos.status_code == 200, f"Listar bancos falhou: {res_bancos.status_code}"
    bancos = res_bancos.get_json()
    assert len(bancos) > 0, "Nenhum banco retornado"
    assert "code" in bancos[0], "Campo 'code' ausente nos bancos"
    print(f" Teste 8 [/listar-bancos]: Sucesso! {len(bancos)} bancos retornados com códigos COMPE.")

    # 9. Teste /listar-conexoes com separação de tipos
    conexoes = res_auth.get_json()
    for c in conexoes:
        assert c.get("tipo") in ["open_finance", "pix_automatico"], f"Tipo inválido: {c.get('tipo')}"
        if c.get("payment_intent_id"):
            assert c["tipo"] == "pix_automatico", "Cliente com intent ID não categorizado como pix_automatico"
    print(f" Teste 9 [/listar-conexoes separação]: Sucesso! {len(conexoes)} conexões estritamente separadas por tipo.")

    # 10. Teste validação do /gerar-token-pix com CPF inválido e valor inválido
    res_pix_bad_cpf = client.post('/gerar-token-pix', json={
        "valor": 100,
        "cpf": "12345",  # CPF com menos de 11 dígitos
        "data_inicio": "2026-10-10",
        "banco": 603
    })
    assert res_pix_bad_cpf.status_code == 400, "Validação de CPF inválido não retornou 400"
    
    res_pix_bad_val = client.post('/gerar-token-pix', json={
        "valor": -50,  # Valor negativo
        "cpf": "123.456.789-00",
        "data_inicio": "2026-10-10",
        "banco": 603
    })
    assert res_pix_bad_val.status_code == 400, "Validação de valor negativo não retornou 400"
    print(" Teste 10 [Validação /gerar-token-pix]: Sucesso! CPF inválido e valores negativos bloqueados.")

    # 11. Teste /salvar-conexao sem dados
    res_salvar_vazio = client.post('/salvar-conexao', json={})
    assert res_salvar_vazio.status_code == 400, "Salvar conexão sem cliente não retornou 400"
    res_salvar_sem_ids = client.post('/salvar-conexao', json={"cliente": "Teste"})
    assert res_salvar_sem_ids.status_code == 400, "Salvar conexão sem IDs financeiros não retornou 400"
    print(" Teste 11 [Validação /salvar-conexao]: Sucesso! Requisições incompletas tratadas.")

    # 12. Teste unitário da função calcular_extrato_pix
    dummy_intent = {
        "id": "intent-test-123",
        "status": "PAYMENT_COMPLETED",
        "paymentRequest": {"amount": 150.0},
        "schedule": {"occurrences": 12, "startDate": "2026-09-01"},
        "connector": {"name": "Banco do Brasil"}
    }
    calc = calcular_extrato_pix(dummy_intent)
    assert calc["parcelas_pagas"] >= 1, "Parcelas pagas do contrato ativo menor que 1"
    assert calc["parcelas_total"] == 12, "Total de parcelas incorreto"
    assert len(calc["cronograma"]) == 12, "Cronograma não gerou 12 parcelas"
    assert calc["valor_parcela"] == 150.0, "Valor da parcela incorreto"
    print(f" Teste 12 [Cálculo analítico Pix]: Sucesso! {calc['parcelas_pagas']}/12 parcelas pagas calculadas com cronograma.")

    print("\n TODOS OS 12 TESTES DO BACKEND PASSARAM COM SUCESSO ABSOLUTO!")

if __name__ == "__main__":
    run_tests()
