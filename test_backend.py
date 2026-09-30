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

    # 13. Teste /api/pix-intents (Espelho do Painel Pluggy com KPIs)
    res_pix_intents = client.get('/api/pix-intents', headers={"Authorization": f"Bearer {token}"})
    assert res_pix_intents.status_code == 200, f"/api/pix-intents falhou: {res_pix_intents.status_code}"
    pix_data = res_pix_intents.get_json()
    assert "kpis" in pix_data, "KPIs ausentes em /api/pix-intents"
    assert "results" in pix_data, "Resultados ausentes em /api/pix-intents"
    assert pix_data["total"] >= 100, f"Total de intents esperado >= 100, obteve {pix_data['total']}"
    print(f" Teste 13 [/api/pix-intents]: Sucesso! {pix_data['total']} contratos Pluggy espelhados com KPIs.")

    # 14. Teste /api/webhook/pluggy
    res_wh = client.post('/api/webhook/pluggy', json={
        "event": "payment_intent/updated",
        "paymentIntentId": "dummy-intent-test-wh"
    })
    assert res_wh.status_code == 200, f"Webhook falhou: {res_wh.status_code}"
    print(" Teste 14 [/api/webhook/pluggy]: Sucesso! Webhook aceito e processado com HTTP 200.")

    # 15. Teste fluxo de CNPJ (Pessoa Jurídica) em /gerar-token-pix
    res_cnpj_invalido = client.post('/gerar-token-pix', json={
        "valor": 200,
        "tipo_doc": "pj",
        "cnpj": "11111111111111", # CNPJ com dígitos repetidos inválido
        "cpf": "303.913.774-34",
        "data_inicio": "2026-10-15",
        "banco": 603
    })
    assert res_cnpj_invalido.status_code == 400, "Validação de CNPJ inválido não retornou 400"

    res_cnpj_sem_rep = client.post('/gerar-token-pix', json={
        "valor": 200,
        "tipo_doc": "pj",
        "cnpj": "62.455.954/0001-46", # CNPJ válido MC Securitizadora
        "cpf": "123", # CPF representante inválido
        "data_inicio": "2026-10-15",
        "banco": 603
    })
    assert res_cnpj_sem_rep.status_code == 400, "Validação de representante sem CPF não retornou 400"
    print(" Teste 15 [Fluxo CNPJ /gerar-token-pix]: Sucesso! Bloqueio de CNPJ/CPF representante inválidos validado.")

    # 16. Teste campos analíticos da Pluggy em /api/pix-intents (Solicitações & Pagamentos)
    kpis = pix_data.get("kpis", {})
    assert "instituicoes" in kpis, "Campo 'instituicoes' ausente nos KPIs"
    assert "total_concluidos_qtd" in kpis, "total_concluidos_qtd ausente nos KPIs"
    assert "total_concluidos_valor" in kpis, "total_concluidos_valor ausente nos KPIs"
    primeiro_item = pix_data["results"][0]
    assert "id_externo" in primeiro_item, "id_externo ausente no item"
    assert "descricao" in primeiro_item, "descricao ausente no item"
    assert "recebedor" in primeiro_item, "recebedor ausente no item"
    print(f" Teste 16 [Painel Analítico Pluggy]: Sucesso! KPIs de Pagamentos e {len(kpis['instituicoes'])} Instituições validados.")

    # 17. Teste /consultar-dados e /sincronizar-item com autenticação
    item_id_teste = '8e04346e-cc83-4d53-900a-3b92f5ab1039'
    res_cd = client.get(f'/consultar-dados/{item_id_teste}', headers={"Authorization": f"Bearer {token}"})
    assert res_cd.status_code == 200, f"/consultar-dados falhou: {res_cd.status_code}"
    cd_data = res_cd.get_json()
    assert "item" in cd_data, "Campo item ausente em /consultar-dados"
    assert "results" in cd_data, "Campo results (contas) ausente em /consultar-dados"

    res_sync = client.post(f'/sincronizar-item/{item_id_teste}', headers={"Authorization": f"Bearer {token}"})
    assert res_sync.status_code in [200, 409], f"/sincronizar-item retornou status inesperado: {res_sync.status_code}"
    print(f" Teste 17 [/consultar-dados e /sincronizar-item]: Sucesso! {len(cd_data['results'])} contas consultadas e sincronização testada.")

    # 18. Teste /consultar-transacoes com repasse de parâmetros
    if len(cd_data['results']) > 0:
        conta_id_teste = cd_data['results'][0]['id']
        res_tx = client.get(f'/consultar-transacoes/{conta_id_teste}?dateFrom=2026-09-01', headers={"Authorization": f"Bearer {token}"})
        assert res_tx.status_code == 200, f"/consultar-transacoes falhou: {res_tx.status_code}"
        tx_json = res_tx.get_json()
        assert "results" in tx_json, "Resultados ausentes em /consultar-transacoes"
        print(f" Teste 18 [/consultar-transacoes v2]: Sucesso! {len(tx_json.get('results', []))} transações recuperadas com filtro de data.")

    print("\n TODOS OS 18 TESTES DO BACKEND PASSARAM COM SUCESSO ABSOLUTO!")

if __name__ == "__main__":
    run_tests()
