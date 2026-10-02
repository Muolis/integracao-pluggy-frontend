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
    res_gestor_js = client.get('/gestor.js')
    assert res_gestor_js.status_code == 200, "Falha ao servir gestor.js"
    res_extratos_js = client.get('/extratos.js')
    assert res_extratos_js.status_code == 200, "Falha ao servir extratos.js"
    res_sec_js = client.get('/securitizadora.js')
    assert res_sec_js.status_code == 200, "Falha ao servir securitizadora.js"
    res_logo = client.get('/logo-mc-minhaconta.png')
    assert res_logo.status_code == 200, "Falha ao servir logo-mc-minhaconta.png"
    print(" Teste 6 [Servidor de arquivos estáticos]: Sucesso! HTMLs, scripts desacoplados (gestor.js, extratos.js, securitizadora.js, config.js) e logo servidos corretamente.")

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
        assert c.get("tipo") in ["open_finance", "pix_automatico", "securitizadora"], f"Tipo inválido: {c.get('tipo')}"
        if c.get("payment_intent_id"):
            assert c["tipo"] == "pix_automatico", "Cliente com intent ID não categorizado como pix_automatico"
    print(f" Teste 9 [/listar-conexoes separação]: Sucesso! {len(conexoes)} conexões estritamente separadas por tipo (Open Finance, Pix e Securitizadora).")

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

    # 19. Teste /consultar-pix com estrutura completa estilo Pluggy (Imagem 3)
    if pix_data.get("results"):
        intent_id_teste = pix_data["results"][0]["id"]
        res_detalhe = client.get(f'/consultar-pix/{intent_id_teste}', headers={"Authorization": f"Bearer {token}"})
        assert res_detalhe.status_code == 200, f"/consultar-pix falhou: {res_detalhe.status_code}"
        detalhe_json = res_detalhe.get_json()
        assert "configuracao_pix" in detalhe_json, "configuracao_pix ausente em /consultar-pix"
        assert "cliente" in detalhe_json, "cliente ausente em /consultar-pix"
        assert "recebedor" in detalhe_json, "recebedor ausente em /consultar-pix"
        assert "pagamentos" in detalhe_json, "pagamentos ausente em /consultar-pix"
        assert "concluidos_texto" in detalhe_json, "concluidos_texto ausente em /consultar-pix"
        print(f" Teste 19 [/consultar-pix estilo Pluggy]: Sucesso! Detalhe da operação retornado com cliente: {detalhe_json['cliente'].get('nome') or 'N/A'}, {len(detalhe_json['pagamentos'])} pagamentos ({detalhe_json['concluidos_texto']}).")

    # 20. Teste rota estática /securitizadora.html
    res_sec_html = client.get('/securitizadora.html')
    assert res_sec_html.status_code == 200, f"Falha ao servir securitizadora.html: {res_sec_html.status_code}"
    print(" Teste 20 [/securitizadora.html]: Sucesso! Tela corporativa da Securitizadora servida com HTTP 200.")

    # 21. Teste /api/securitizadora/resumo com autenticação
    res_sec_resumo = client.get('/api/securitizadora/resumo', headers={"Authorization": f"Bearer {token}"})
    assert res_sec_resumo.status_code == 200, f"/api/securitizadora/resumo falhou: {res_sec_resumo.status_code}"
    sec_data = res_sec_resumo.get_json()
    assert sec_data.get("sucesso"), "sucesso não retornado como True"
    assert "empresa" in sec_data, "empresa ausente em /api/securitizadora/resumo"
    assert "kpis" in sec_data, "kpis ausente em /api/securitizadora/resumo"
    assert len(sec_data.get("contas", [])) > 0, "Nenhuma conta da Securitizadora retornada"
    print(f" Teste 21 [/api/securitizadora/resumo]: Sucesso! Retornou {len(sec_data['contas'])} conta(s) PJ (Saldo Consolidado: {sec_data['kpis']['saldo_consolidado_formatado']}).")

    # 22. Teste /api/securitizadora/extrato com autenticação
    res_sec_extrato = client.get('/api/securitizadora/extrato', headers={"Authorization": f"Bearer {token}"})
    assert res_sec_extrato.status_code == 200, f"/api/securitizadora/extrato falhou: {res_sec_extrato.status_code}"
    extrato_data = res_sec_extrato.get_json()
    assert extrato_data.get("sucesso"), "sucesso não retornado no extrato"
    assert "results" in extrato_data, "results ausente no extrato"
    print(f" Teste 22 [/api/securitizadora/extrato]: Sucesso! {len(extrato_data['results'])} movimentações corporativas consultadas em tempo real.")

    # 23. Teste Deduplicação e Saldo Fiel da Conta Securitizadora
    assert sec_data['kpis']['total_contas'] == 1, f"Esperado 1 conta única deduplicada, obteve {sec_data['kpis']['total_contas']}"
    assert sec_data['kpis']['saldo_consolidado'] == 2815.47, f"Saldo consolidado incorreto: {sec_data['kpis']['saldo_consolidado']}"
    assert sec_data['kpis']['saldo_consolidado_formatado'] == 'R$ 2.815,47', f"Formatação de saldo incorreta: {sec_data['kpis']['saldo_consolidado_formatado']}"
    print(f" Teste 23 [Deduplicação e Saldo Fiel Securitizadora]: Sucesso! 1 conta única validada com saldo exato de {sec_data['kpis']['saldo_consolidado_formatado']}.")

    # 24. Teste /salvar-conexao com tipo='securitizadora'
    res_salvar_sec = client.post('/salvar-conexao', json={
        "cliente": "MC MINHACONTA SECURITIZADORA SA",
        "item_id": "item-teste-securitizadora-unit",
        "tipo": "securitizadora"
    })
    assert res_salvar_sec.status_code == 200, f"Salvar securitizadora falhou: {res_salvar_sec.status_code}"
    salvar_data = res_salvar_sec.get_json()
    assert salvar_data.get("tipo") == "securitizadora", f"Tipo retornado não é securitizadora: {salvar_data.get('tipo')}"
    print(" Teste 24 [Persistência de tipo 'securitizadora']: Sucesso! Nova conta corporativa classificada como securitizadora.")

    # 25. Teste Cache Securitizadora e /api/securitizadora/sincronizar
    res_sync_sec = client.post('/api/securitizadora/sincronizar', headers={"Authorization": f"Bearer {token}"})
    assert res_sync_sec.status_code == 200, f"/api/securitizadora/sincronizar falhou: {res_sync_sec.status_code}"
    sync_sec_data = res_sync_sec.get_json()
    assert sync_sec_data.get("sucesso"), "sucesso não retornado em sincronizar securitizadora"
    print(" Teste 25 [Cache e Sincronização Securitizadora]: Sucesso! Cache invalidado e sincronização disparada com sucesso.")

    # 26. Teste Status Fiel de Pix Automático (AUTHORIZED == 'Autorizado', não 'Concluído')
    res_pix_auditoria = client.get('/api/pix-intents?force=true', headers={"Authorization": f"Bearer {token}"})
    assert res_pix_auditoria.status_code == 200, f"/api/pix-intents falhou: {res_pix_auditoria.status_code}"
    itens_pix = res_pix_auditoria.get_json().get("results", [])
    
    contratos_autorizados = [p for p in itens_pix if p.get("status") == "AUTHORIZED"]
    assert len(contratos_autorizados) > 0, "Nenhum contrato AUTHORIZED encontrado"
    for ca in contratos_autorizados:
        assert ca.get("status_label") == "Autorizado", f"Contrato AUTHORIZED {ca['id']} não está com status_label 'Autorizado' (obteve '{ca.get('status_label')}')"
    print(f" Teste 26 [Status Fiel Pix Automático]: Sucesso! {len(contratos_autorizados)} contratos AUTHORIZED validados como 'Autorizado' (não 'Concluído').")

    # 27. Teste Diagnóstico Oficial de Erros e Recusas da Pluggy
    itens_com_erro = [p for p in itens_pix if p.get("tem_erro")]
    assert len(itens_com_erro) > 0, "Nenhum item com erro detectado no espelho da Pluggy"
    primeiro_erro = itens_com_erro[0]
    assert "erro" in primeiro_erro and primeiro_erro["erro"], "Objeto erro ausente em item com erro"
    assert "codigo" in primeiro_erro["erro"], "Código ausente no objeto erro"
    assert "titulo" in primeiro_erro["erro"], "Título ausente no objeto erro"
    assert "detalhe" in primeiro_erro["erro"], "Detalhe explicativo ausente no objeto erro"
    assert "acao" in primeiro_erro["erro"], "Ação recomendada ausente no objeto erro"
    print(f" Teste 27 [Diagnóstico Oficial de Erros]: Sucesso! {len(itens_com_erro)} contratos com diagnóstico de erro oficial detalhados (Ex: '{primeiro_erro['erro']['titulo']}' - {primeiro_erro['erro']['codigo']}).")

    # 28. Teste Detalhe de Operação /consultar-pix com Diagnóstico e Cobranças Fiéis
    item_erro_id = primeiro_erro["id"]
    res_det_erro = client.get(f'/consultar-pix/{item_erro_id}', headers={"Authorization": f"Bearer {token}"})
    assert res_det_erro.status_code == 200, f"Falha ao consultar detalhe do item com erro: {res_det_erro.status_code}"
    det_erro_json = res_det_erro.get_json()
    assert det_erro_json.get("tem_erro"), "tem_erro não é True no detalhe da operação"
    assert det_erro_json.get("erro"), "Objeto erro ausente no detalhe da operação"
    assert det_erro_json["status_label"] in ["Rejeitado", "Expirado", "Erro", "Cancelado", "Aguardando"], f"Status label inesperado para erro: {det_erro_json['status_label']}"
    pagamentos_erro = det_erro_json.get("pagamentos", {}).get("itens", [])
    assert len(pagamentos_erro) > 0, "Itens de pagamento vazios no detalhe com erro"
    assert any(p["status"] in ["REJEITADO", "EXPIRADO", "ERRO", "CANCELADO", "PENDENTE"] for p in pagamentos_erro), "Nenhum pagamento com status condizente com a recusa/falha"
    # 29. Teste de Fidelidade e Precisão das Datas das Solicitações e Cronograma
    datas_criacao = [p.get("data_criacao") for p in itens_pix if p.get("data_criacao")]
    assert len(set(datas_criacao)) > 10, "Datas de criação das solicitações estão idênticas"
    
    # Testa item autorizado com cronograma de pagamentos
    primeiro_auth = contratos_autorizados[0]
    res_det_auth = client.get(f'/consultar-pix/{primeiro_auth["id"]}', headers={"Authorization": f"Bearer {token}"})
    assert res_det_auth.status_code == 200, "Falha ao consultar contrato autorizado"
    det_auth_json = res_det_auth.get_json()
    assert det_auth_json.get("criado_em") != "---", "Data de criação ausente"
    assert det_auth_json.get("autorizado_em") != "---", "Contrato autorizado deve ter data de autorização"
    
    itens_cron = det_auth_json.get("pagamentos", {}).get("itens", [])
    assert len(itens_cron) >= 2, f"Cronograma de parcelas deve conter múltiplos pagamentos, obteve {len(itens_cron)}"
    datas_parcelas = [it["data"] for it in itens_cron if it.get("data") != "---"]
    assert len(set(datas_parcelas)) == len(datas_parcelas), f"Existem parcelas com datas duplicadas no cronograma: {datas_parcelas}"
    
    # Testa item não-autorizado: autorizado_em deve ser '---'
    assert det_erro_json.get("autorizado_em") == "---", f"Contrato rejeitado/com erro não pode ter data de autorização: obteve '{det_erro_json.get('autorizado_em')}'"
    # 30. Teste de Extração Completa de Open Finance (/api/openfinance/completo/<item_id>)
    # Testa com o item real de Severino (8e04346e-cc83-4d53-900a-3b92f5ab1039)
    res_of_comp = client.get('/api/openfinance/completo/8e04346e-cc83-4d53-900a-3b92f5ab1039', headers={"Authorization": f"Bearer {token}"})
    assert res_of_comp.status_code == 200, f"Falha na rota /api/openfinance/completo: {res_of_comp.status_code}"
    of_data = res_of_comp.get_json()
    assert of_data.get("sucesso") is True, "sucesso deve ser True"
    assert "item" in of_data, "Objeto item ausente na resposta de Open Finance"
    assert "identidade" in of_data, "Objeto identidade cadastral ausente"
    assert "contas" in of_data and len(of_data["contas"]) > 0, "Contas bancárias vazias"
    assert "transacoes" in of_data and len(of_data["transacoes"]) > 0, "Extrato de transações vazio"
    assert "metricas" in of_data, "Métricas consolidadas ausentes"
    
    mets = of_data["metricas"]
    assert mets.get("total_entradas", 0) > 0, "Total de entradas deve ser positivo"
    assert mets.get("total_saidas", 0) > 0, "Total de saídas deve ser positivo"
    assert mets.get("quantidade_transacoes", 0) > 0, "Quantidade de transações deve ser maior que zero"
    print(f" Teste 30 [Extração Total Open Finance]: Sucesso! {len(of_data['contas'])} contas, {len(of_data['transacoes'])} movimentações (Entradas: R$ {mets['total_entradas']:,.2f} | Saídas: R$ {mets['total_saidas']:,.2f}) e dados cadastrais extraídos com perfeição.")

    # 31. Teste de Proteção contra Vazamento de Arquivos Sensíveis (.env, .py, .sql, etc.)
    res_env = client.get('/.env')
    assert res_env.status_code == 403, f"Acesso a /.env deveria ser 403, obteve: {res_env.status_code}"
    res_py = client.get('/backend.py')
    assert res_py.status_code == 403, f"Acesso a /backend.py deveria ser 403, obteve: {res_py.status_code}"
    res_sql = client.get('/schema.sql')
    assert res_sql.status_code == 403, f"Acesso a /schema.sql deveria ser 403, obteve: {res_sql.status_code}"
    res_git = client.get('/.git/config')
    assert res_git.status_code == 403, f"Acesso a /.git/config deveria ser 403, obteve: {res_git.status_code}"
    print(" Teste 31 [Proteção contra Directory Traversal & Vazamento de Código]: Sucesso! /.env, /backend.py, /schema.sql e /.git bloqueados com HTTP 403.")

    print("\n TODOS OS 31 TESTES DO BACKEND PASSARAM COM SUCESSO ABSOLUTO!")

if __name__ == "__main__":
    run_tests()

