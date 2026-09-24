import os
import time
import hmac
import hashlib
import json
import base64
import re
from functools import wraps
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env se presente
load_dotenv()

app = Flask(__name__, static_folder=".")

# Configuração de CORS: aceita origens especificadas ou geral
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
CORS(app, origins=CORS_ORIGINS.split(",") if CORS_ORIGINS != "*" else "*")

@app.after_request
def adicionar_headers_seguranca(response):
    """Injeta cabeçalhos modernos de proteção e segurança HTTP"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# ====================================================================
# 1. CONFIGURAÇÕES E CREDENCIAIS SEGURAS
# ====================================================================
CLIENT_ID = os.environ.get("PLUGGY_CLIENT_ID", "37bdb5b6-faf1-4ef9-bda6-e8b7abe5b188")
CLIENT_SECRET = os.environ.get("PLUGGY_CLIENT_SECRET", "7e21d0d2-64f5-4300-b8af-cc6e8a431112")
RECIPIENT_ID = os.environ.get("PLUGGY_RECIPIENT_ID", "043e7bb1-da9a-4c74-acc3-6cf0741bf31a")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://vitrine-openfinance.onrender.com").rstrip("/")
SECRET_KEY = os.environ.get("SECRET_KEY", "mc-securitizadora-secret-key-2026")

SUPABASE_URL = os.environ.get("SUPABASE_URL")
if SUPABASE_URL:
    SUPABASE_URL = SUPABASE_URL.rstrip("/").replace("/rest/v1", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Tenta carregar o cliente Supabase se as credenciais estiverem presentes
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[ALERTA] Falha ao conectar no Supabase: {e}")

# Usuários autorizados no Portal do Gestor
# Formato padrão: "admin:securitizadora2026,julianemc:MC@2026,gabriel:MC@2026"
GESTOR_USERS_RAW = os.environ.get("GESTOR_USERS", "admin:securitizadora2026,julianemc:MC@2026,gabriel:MC@2026")
GESTOR_USERS = {}
for par in GESTOR_USERS_RAW.split(","):
    if ":" in par:
        u, p = par.strip().split(":", 1)
        GESTOR_USERS[u.strip()] = p.strip()

# ====================================================================
# 2. CACHE EM MEMÓRIA DA API KEY DA PLUGGY
# ====================================================================
# Evita fazer requisições POST repetitivas a cada clique, reduzindo latência e prevenindo HTTP 429
_pluggy_cache = {
    "api_key": None,
    "expires_at": 0
}

def obter_api_key():
    agora = time.time()
    # Se já temos uma chave válida por mais 5 minutos, reutiliza
    if _pluggy_cache["api_key"] and _pluggy_cache["expires_at"] > agora + 300:
        return _pluggy_cache["api_key"]

    try:
        auth_response = requests.post(
            "https://api.pluggy.ai/auth",
            json={"clientId": CLIENT_ID, "clientSecret": CLIENT_SECRET},
            timeout=15
        )
        if auth_response.status_code == 200:
            api_key = auth_response.json().get("apiKey")
            if api_key:
                _pluggy_cache["api_key"] = api_key
                # Token da Pluggy tipicamente dura várias horas; usamos 2h como janela segura de cache
                _pluggy_cache["expires_at"] = agora + 7200
                return api_key
        print(f"[ERRO PLUGGY AUTH]: {auth_response.status_code} - {auth_response.text}")
    except Exception as e:
        print(f"[EXCEÇÃO PLUGGY AUTH]: {e}")
    return None

# ====================================================================
# 3. SISTEMA DE AUTENTICAÇÃO E SESSÃO DO GESTOR
# ====================================================================
def gerar_token_sessao(usuario: str) -> str:
    """Gera um token seguro assinado com HMAC-SHA256 contendo timestamp e usuário"""
    timestamp = int(time.time())
    payload = f"{usuario}:{timestamp}"
    assinatura = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{payload}:{assinatura}".encode()).decode()
    return token

def validar_token_sessao(token: str) -> str:
    """Valida o token de sessão e retorna o usuário caso válido e não expirado (24h)"""
    try:
        decodificado = base64.urlsafe_b64decode(token.encode()).decode()
        partes = decodificado.split(":")
        if len(partes) != 3:
            return None
        usuario, timestamp_str, assinatura = partes
        timestamp = int(timestamp_str)
        agora = int(time.time())

        # Expiração em 24 horas (86400 segundos)
        if agora - timestamp > 86400 or timestamp > agora + 60:
            return None

        payload = f"{usuario}:{timestamp}"
        assinatura_esperada = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()

        if hmac.compare_digest(assinatura, assinatura_esperada):
            return usuario
    except Exception:
        return None
    return None

def requer_autenticacao(f):
    """Decorator para proteger endpoints administrativos que lidam com dados bancários"""
    @wraps(f)
    def decorada(*args, **kwargs):
        header_auth = request.headers.get("Authorization", "")
        if not header_auth.startswith("Bearer "):
            return jsonify({"erro": "Não autorizado: Token de sessão não fornecido"}), 401

        token = header_auth.replace("Bearer ", "").strip()
        usuario = validar_token_sessao(token)
        if not usuario:
            return jsonify({"erro": "Não autorizado: Token inválido ou expirado"}), 401

        request.usuario_autenticado = usuario
        return f(*args, **kwargs)
    return decorada

# ====================================================================
# 4. ROTAS PÚBLICAS / CLIENTE E AUTENTICAÇÃO
# ====================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Diagnóstico de saúde da aplicação e serviços vinculados"""
    return jsonify({
        "status": "ok",
        "pluggy_configurada": bool(CLIENT_ID and CLIENT_SECRET),
        "supabase_conectado": bool(supabase is not None),
        "frontend_url": FRONTEND_URL,
        "timestamp": int(time.time())
    }), 200

@app.route('/api/login', methods=['POST'])
def api_login():
    """Autenticação oficial do Gestor com validação de credenciais seguras"""
    dados = request.get_json(silent=True) or {}
    usuario = dados.get("usuario", "").strip()
    senha = dados.get("senha", "").strip()

    if not usuario or not senha:
        return jsonify({"erro": "Usuário e senha são obrigatórios"}), 400

    senha_esperada = GESTOR_USERS.get(usuario)
    if senha_esperada and hmac.compare_digest(senha, senha_esperada):
        token = gerar_token_sessao(usuario)
        return jsonify({
            "sucesso": True,
            "token": token,
            "usuario": {
                "username": usuario,
                "nome": usuario.capitalize()
            }
        }), 200

    return jsonify({"erro": "Usuário ou senha incorretos"}), 401

# ====================================================================
# MAPEAMENTO OFICIAL DE CÓDIGOS BANCÁRIOS (COMPE - BANCO CENTRAL DO BRASIL)
# ====================================================================
CONNECTOR_COMPE = {
    611: "001", 662: "001",  # Banco do Brasil
    608: "033", 621: "033",  # Santander
    619: "104", 616: "104",  # Caixa Econômica Federal
    603: "237", 609: "237",  # Bradesco
    601: "341", 618: "341", 786: "341",  # Itaú Unibanco
    612: "260", 664: "260",  # Nu Pagamentos (Nubank)
    626: "336", 726: "336",  # C6 Bank
    651: "380", 713: "380",  # PicPay
    692: "290", 816: "290",  # PagBank (PagSeguro)
    652: "318", 666: "318",  # Banco Bmg
    817: "070", 818: "070",  # Banco BRB
    653: "335", 674: "335",  # Banco Digio
    671: "004", 672: "004",  # Banco do Nordeste do Brasil
    680: "243",              # Banco Master
    742: "389", 819: "389",  # Banco Mercantil
    657: "623",              # Banco PAN
    714: "637", 715: "637",  # Banco Sofisa
    659: "041", 660: "041",  # Banrisul
    675: "208", 655: "208",  # BTG Pactual
    718: "655", 716: "655", 719: "655",  # Banco BV
    606: "323", 665: "323",  # Mercado Pago
    656: "237", 801: "237",  # Next (Bradesco)
    689: "536",              # Neon
    750: "069", 860: "069",  # Crefisa
    629: "422", 697: "422",  # Banco Safra
    658: "756", 628: "756",  # Sicoob
    661: "748", 627: "748",  # Sicredi
    787: "197", 788: "197",  # Stone Pagamentos
    663: "136", 670: "136",  # Unicred
    602: "102", 702: "102",  # XP Banking
    880: "383",              # Conta Bemol
    777: "777", 778: "777",  # InfinitePay
    804: "099",              # 99Pay
    767: "767", 768: "767",  # RecargaPay
    676: "748",              # Woop Sicredi
}

NOME_COMPE_FALLBACK = {
    "banco do brasil": "001",
    "santander": "033",
    "caixa": "104",
    "bradesco": "237",
    "itaú": "341",
    "itau": "341",
    "nubank": "260",
    "inter": "077",
    "c6": "336",
    "picpay": "380",
    "pagbank": "290",
    "pagseguro": "290",
    "original": "212",
    "safra": "422",
    "sicredi": "748",
    "sicoob": "756",
    "banrisul": "041",
    "bmg": "318",
    "brb": "070",
    "digio": "335",
    "nordeste": "004",
    "master": "243",
    "mercantil": "389",
    "pan": "623",
    "sofisa": "637",
    "btg": "208",
    "bv": "655",
    "votorantim": "655",
    "mercado pago": "323",
    "next": "237",
    "neon": "536",
    "crefisa": "069",
    "infinitepay": "777",
    "stone": "197",
    "unicred": "136",
    "xp": "102",
    "bemol": "383",
    "cora": "403",
    "ailos": "085",
    "banestes": "021",
    "rendimento": "633",
    "daycoval": "707",
    "agibank": "121",
}

def obter_codigo_banco(connector_id: int, nome: str) -> str:
    """Retorna o código COMPE oficial de um conector bancário"""
    if connector_id in CONNECTOR_COMPE:
        return CONNECTOR_COMPE[connector_id]
    nome_norm = (nome or "").lower()
    for chave, codigo in NOME_COMPE_FALLBACK.items():
        if chave in nome_norm:
            return codigo
    return ""

@app.route('/listar-bancos', methods=['GET'])
def listar_bancos():
    """Lista bancos com suporte a Pix acompanhados do código bancário COMPE oficial"""
    api_key = obter_api_key()
    if not api_key:
        return jsonify({"erro": "Erro na autenticação com a Pluggy"}), 500

    try:
        response = requests.get(
            "https://api.pluggy.ai/connectors?countries=BR",
            headers={"X-API-KEY": api_key},
            timeout=15
        )
        if response.status_code != 200:
            return jsonify({"erro": "Falha ao buscar conectores bancários", "detalhes": response.text}), response.status_code

        conectores = response.json().get("results", [])
        bancos_validos = []
        for c in conectores:
            if c.get("type") in ["PERSONAL_BANK", "BUSINESS_BANK"] and c.get("supportsPaymentInitiation") is True:
                cid = c.get("id")
                raw_name = c.get("name", "").strip()
                code = obter_codigo_banco(cid, raw_name)
                # Formata com o número: ex: "001 - Banco do Brasil" ou "237 - Bradesco"
                display_name = f"{code} - {raw_name}" if code else raw_name
                bancos_validos.append({
                    "id": cid,
                    "name": display_name,
                    "code": code,
                    "raw_name": raw_name,
                    "imageUrl": c.get("imageUrl")
                })

        # Ordena: bancos com código numérico primeiro pelo código, depois os demais pelo nome
        bancos_validos.sort(key=lambda x: (0 if x["code"] else 1, x["code"] or "", x["raw_name"]))
        return jsonify(bancos_validos)
    except Exception as e:
        return jsonify({"erro": f"Erro interno ao listar bancos: {str(e)}"}), 500

@app.route('/gerar-token', methods=['GET', 'POST'])
def gerar_token():
    """Gera Connect Token temporário da Pluggy para leitura de extratos Open Finance"""
    api_key = obter_api_key()
    if not api_key:
        return jsonify({"erro": "Erro na autenticação com a Pluggy"}), 500

    try:
        token_response = requests.post(
            "https://api.pluggy.ai/connect_token",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            timeout=15
        )
        if token_response.status_code != 200:
            return jsonify({"erro": "Erro ao gerar o Connect Token", "detalhes": token_response.text}), token_response.status_code
        return jsonify({"token": token_response.json().get("accessToken")})
    except Exception as e:
        return jsonify({"erro": f"Erro interno: {str(e)}"}), 500

@app.route('/gerar-token-pix', methods=['POST'])
def gerar_token_pix():
    """
    Cria a requisição e intenção de Pix Automático na Pluggy,
    retornando o Connect Token, o Payment Intent ID e o consentUrl de redirecionamento.
    """
    api_key = obter_api_key()
    if not api_key:
        return jsonify({"erro": "Erro na autenticação com a Pluggy"}), 500

    dados = request.get_json(silent=True) or {}
    valor_pix = dados.get("valor")
    cpf_cliente = re.sub(r'\D', '', str(dados.get("cpf", "")).strip())
    data_inicio = str(dados.get("data_inicio", "")).strip()
    banco_selecionado = dados.get("banco")

    if not all([valor_pix, cpf_cliente, data_inicio, banco_selecionado]):
        return jsonify({"erro": "Faltam dados obrigatórios para Pix Automático (valor, CPF, data de início e banco)"}), 400

    if len(cpf_cliente) != 11:
        return jsonify({"erro": "CPF inválido. Deve conter exatamente 11 dígitos numéricos."}), 400

    try:
        valor_float = float(valor_pix)
        if valor_float <= 0:
            return jsonify({"erro": "O valor da parcela do Pix deve ser maior que zero."}), 400
    except (ValueError, TypeError):
        return jsonify({"erro": "Valor numérico inválido informado para o Pix."}), 400

    try:
        # Tratamento seguro do dia do mês
        partes_data = data_inicio.split("-")
        dia_mes = int(partes_data[2]) if len(partes_data) >= 3 else 10
        if dia_mes < 1 or dia_mes > 28:
            dia_mes = min(max(dia_mes, 1), 28)
    except Exception:
        dia_mes = 10

    # 1. Cria a requisição de pagamento
    request_payload = {
        "amount": float(valor_pix),
        "description": "Pagamento Pix Mensal - MC Securitizadora",
        "recipientId": RECIPIENT_ID,
        "callbackUrls": {
            "success": f"{FRONTEND_URL}/cliente.html?status=sucesso",
            "error": f"{FRONTEND_URL}/cliente.html?status=erro"
        },
        "schedule": {
            "type": "MONTHLY",
            "startDate": data_inicio,
            "dayOfMonth": dia_mes,
            "occurrences": 12
        }
    }

    try:
        req_response = requests.post(
            "https://api.pluggy.ai/payments/requests",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json=request_payload,
            timeout=15
        )

        if req_response.status_code not in (200, 201):
            return jsonify({"erro": "Erro ao criar requisição de pagamento", "detalhes": req_response.text}), req_response.status_code

        payment_request_id = req_response.json().get("id")

        # 2. Cria a Intenção de Pagamento
        intent_payload = {
            "paymentRequestId": payment_request_id,
            "connectorId": int(banco_selecionado),
            "parameters": {"cpf": cpf_cliente, "name": "Cliente"}
        }

        intent_response = requests.post(
            "https://api.pluggy.ai/payments/intents",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json=intent_payload,
            timeout=15
        )

        if intent_response.status_code not in (200, 201):
            return jsonify({"erro": "Erro ao criar intenção de pagamento", "detalhes": intent_response.text}), intent_response.status_code

        intent_data = intent_response.json()
        payment_intent_id = intent_data.get("id")
        consent_url = intent_data.get("consentUrl") or intent_data.get("url")

        # 3. Gera o Connect Token vinculado ao Pix
        token_payload = {
            "options": {
                "paymentIntentId": payment_intent_id
            }
        }

        token_response = requests.post(
            "https://api.pluggy.ai/connect_token",
            headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
            json=token_payload,
            timeout=15
        )

        token_access = token_response.json().get("accessToken") if token_response.status_code == 200 else None

        # Retorna o token, payment_intent_id E o consent_url para o frontend
        return jsonify({
            "token": token_access,
            "payment_intent_id": payment_intent_id,
            "consentUrl": consent_url,
            "consent_url": consent_url
        }), 200

    except Exception as e:
        return jsonify({"erro": f"Erro interno ao processar Pix: {str(e)}"}), 500

def calcular_extrato_pix(intent_data: dict) -> dict:
    """Calcula o extrato analítico do contrato de Pix Automático: parcelas pagas, restantes e cronograma"""
    from datetime import date
    import calendar

    req = intent_data.get("paymentRequest") or {}
    schedule = req.get("schedule") or {}
    status = intent_data.get("status", "PENDING")
    connector = intent_data.get("connector") or {}
    debtor = intent_data.get("debtor") or {}
    
    try:
        valor = float(req.get("amount") or 0.0)
    except (ValueError, TypeError):
        valor = 0.0

    try:
        occurrences = int(schedule.get("occurrences") or 12)
    except (ValueError, TypeError):
        occurrences = 12
    occurrences = max(1, occurrences)

    start_date_str = schedule.get("startDate") or time.strftime("%Y-%m-%d")

    try:
        partes = [int(x) for x in str(start_date_str).split("-")[:3]]
        if len(partes) == 3:
            data_base = date(partes[0], partes[1], partes[2])
        else:
            data_base = date.today()
    except Exception:
        data_base = date.today()

    agora = date.today()
    cronograma = []
    parcelas_pagas = 0
    cliente_pagando = (status == "PAYMENT_COMPLETED")

    for i in range(1, occurrences + 1):
        m_total = (data_base.month - 1) + (i - 1)
        novo_ano = data_base.year + (m_total // 12)
        novo_mes = (m_total % 12) + 1
        max_dias = calendar.monthrange(novo_ano, novo_mes)[1]
        dia_venc = min(data_base.day, max_dias)
        vencimento_parcela = date(novo_ano, novo_mes, dia_venc)
        venc_str = vencimento_parcela.strftime("%d/%m/%Y")

        if status in ["CONSENT_REJECTED", "REJECTED", "ERROR"]:
            status_parcela = "rejeitada"
            badge_texto = "Cancelada / Não Autorizada"
            cor_badge = "rose"
        elif status in ["WAITING_PAYER_AUTHORIZATION", "PENDING"]:
            if i == 1:
                status_parcela = "pendente"
                badge_texto = "Aguardando Banco"
                cor_badge = "amber"
            else:
                status_parcela = "a_vencer"
                badge_texto = "A Vencer"
                cor_badge = "slate"
        elif status == "PAYMENT_COMPLETED":
            if vencimento_parcela <= agora:
                status_parcela = "paga"
                badge_texto = "Paga"
                cor_badge = "emerald"
                parcelas_pagas += 1
            elif parcelas_pagas == i - 1 and vencimento_parcela > agora:
                status_parcela = "proximo_debito"
                badge_texto = "Próximo Débito"
                cor_badge = "sky"
            else:
                status_parcela = "a_vencer"
                badge_texto = "A Vencer"
                cor_badge = "slate"
        else:
            status_parcela = "a_vencer"
            badge_texto = "A Vencer"
            cor_badge = "slate"

        cronograma.append({
            "numero": i,
            "vencimento": venc_str,
            "vencimento_iso": vencimento_parcela.isoformat(),
            "valor": valor,
            "status": status_parcela,
            "badge": badge_texto,
            "cor": cor_badge
        })

    # Caso contrato esteja ativo (PAYMENT_COMPLETED) com adesão imediata
    if status == "PAYMENT_COMPLETED" and parcelas_pagas == 0 and len(cronograma) > 0:
        cronograma[0]["status"] = "paga"
        cronograma[0]["badge"] = "Paga (Adesão)"
        cronograma[0]["cor"] = "emerald"
        parcelas_pagas = 1
        if len(cronograma) > 1:
            cronograma[1]["status"] = "proximo_debito"
            cronograma[1]["badge"] = "Próximo Débito"
            cronograma[1]["cor"] = "sky"

    parcelas_restantes = max(0, occurrences - parcelas_pagas)
    if status in ["CONSENT_REJECTED", "REJECTED", "ERROR"]:
        status_rotulo = "Cancelado / Rejeitado"
        status_classe = "rejeitado"
    elif status == "PAYMENT_COMPLETED":
        status_rotulo = "Em Dia (Ativo)"
        status_classe = "ativo"
    else:
        status_rotulo = "Aguardando Autorização"
        status_classe = "pendente"

    proxima = next((p for p in cronograma if p["status"] in ["proximo_debito", "pendente", "a_vencer"]), None)
    proximo_vencimento = proxima["vencimento"] if proxima else "Concluído"

    return {
        "id": intent_data.get("id"),
        "status": status,
        "status_rotulo": status_rotulo,
        "status_classe": status_classe,
        "cliente_pagando": cliente_pagando,
        "banco_nome": connector.get("name", "Banco"),
        "banco_imagem": connector.get("imageUrl"),
        "parcelas_total": occurrences,
        "parcelas_pagas": parcelas_pagas,
        "parcelas_restantes": parcelas_restantes,
        "valor_parcela": valor,
        "total_pago": round(parcelas_pagas * valor, 2),
        "total_restante": round(parcelas_restantes * valor, 2),
        "proximo_vencimento": proximo_vencimento,
        "data_inicio": start_date_str,
        "debtor": debtor,
        "cronograma": cronograma,
        "raw": intent_data
    }

@app.route('/salvar-conexao', methods=['POST'])
def salvar_conexao():
    """Salva o vínculo entre o cliente e o itemId / paymentIntentId no banco de dados"""
    dados = request.get_json(silent=True) or {}
    cliente = str(dados.get("cliente", "")).strip()
    item_id = dados.get("item_id")
    payment_intent_id = dados.get("payment_intent_id")

    if not cliente:
        return jsonify({"erro": "Identificador do cliente é obrigatório"}), 400

    if not item_id and not payment_intent_id:
        return jsonify({"erro": "Nenhum dado financeiro (item_id ou payment_intent_id) foi enviado"}), 400

    if not supabase:
        print(f"[LOG CONEXAO LOCAL] Cliente: {cliente}, Item: {item_id}, Pix: {payment_intent_id}")
        return jsonify({
            "sucesso": True,
            "aviso": "Salvo em modo local (Supabase não configurado neste ambiente)"
        }), 200

    try:
        registro = {"cliente": cliente}
        if payment_intent_id:
            registro["payment_intent_id"] = str(payment_intent_id)
            # Evita poluir a coluna item_id com payment_intent_id
            if item_id and str(item_id) != str(payment_intent_id):
                registro["item_id"] = str(item_id)
            else:
                registro["item_id"] = None
            registro["tipo"] = "pix_automatico"
        elif item_id:
            registro["item_id"] = str(item_id)
            registro["payment_intent_id"] = None
            registro["tipo"] = "open_finance"

        supabase.table("conexoes").insert(registro).execute()
        return jsonify({"sucesso": True}), 200
    except Exception as e:
        print(f"[ERRO SUPABASE INSERT]: {e}")
        return jsonify({"erro": f"Falha ao persistir no banco de dados: {str(e)}"}), 500

# ====================================================================
# 5. ROTAS ADMINISTRATIVAS PROTEGIDAS (PORTAL DO GESTOR)
# ====================================================================

@app.route('/listar-conexoes', methods=['GET'])
@requer_autenticacao
def listar_conexoes():
    """Lista as conexões salvas de clientes no Supabase com separação estrita de tipo"""
    if not supabase:
        return jsonify([
            {
                "id": 1,
                "cliente": "ClienteDemonstracao",
                "item_id": "demo-item-12345",
                "payment_intent_id": None,
                "tipo": "open_finance",
                "data_conexao": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        ]), 200

    try:
        resposta = supabase.table("conexoes").select("*").order("data_conexao", desc=True).limit(100).execute()
        conexoes = resposta.data or []
        for c in conexoes:
            # Separação rigorosa: se tem payment_intent_id, é PIX AUTOMÁTICO; senão, OPEN FINANCE
            if c.get("payment_intent_id"):
                c["tipo"] = "pix_automatico"
            else:
                c["tipo"] = "open_finance"
        return jsonify(conexoes), 200
    except Exception as e:
        print(f"[ERRO SUPABASE SELECT]: {e}")
        return jsonify({"erro": f"Falha ao consultar banco: {str(e)}"}), 500

@app.route('/consultar-dados/<item_id>', methods=['GET'])
@requer_autenticacao
def consultar_dados(item_id):
    """Consulta as informações do Item (banco/status) e as contas associadas ao Item ID na Pluggy"""
    api_key = obter_api_key()
    if not api_key:
        return jsonify({"erro": "Erro na autenticação com a Pluggy"}), 500

    try:
        # 1. Consulta o item para obter status da conexão e conector
        item_info = {}
        try:
            it_res = requests.get(
                f"https://api.pluggy.ai/items/{item_id}",
                headers={"X-API-KEY": api_key},
                timeout=12
            )
            if it_res.status_code == 200:
                item_info = it_res.json()
        except Exception as e_it:
            print(f"[AVISO] Falha ao consultar item {item_id}: {e_it}")

        # 2. Consulta as contas do Item
        contas_response = requests.get(
            f"https://api.pluggy.ai/accounts?itemId={item_id}",
            headers={"X-API-KEY": api_key},
            timeout=15
        )
        contas = []
        if contas_response.status_code == 200:
            contas = contas_response.json().get("results", [])

        return jsonify({
            "item": {
                "id": item_id,
                "status": item_info.get("status", "UPDATED"),
                "connector": item_info.get("connector", {}),
                "error": item_info.get("error"),
                "lastUpdatedAt": item_info.get("lastUpdatedAt")
            },
            "results": contas,
            "total": len(contas)
        }), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno ao buscar contas: {str(e)}"}), 500

@app.route('/consultar-transacoes/<account_id>', methods=['GET'])
@requer_autenticacao
def consultar_transacoes(account_id):
    """Consulta as movimentações e extrato de uma conta bancária específica"""
    api_key = obter_api_key()
    if not api_key:
        return jsonify({"erro": "Erro na autenticação com a Pluggy"}), 500

    try:
        transacoes_response = requests.get(
            f"https://api.pluggy.ai/v2/transactions?accountId={account_id}",
            headers={"X-API-KEY": api_key},
            timeout=15
        )
        if transacoes_response.status_code != 200:
            return jsonify({"erro": "Falha ao buscar extrato", "detalhes": transacoes_response.text}), transacoes_response.status_code
        return jsonify(transacoes_response.json())
    except Exception as e:
        return jsonify({"erro": f"Erro interno ao buscar transações: {str(e)}"}), 500

@app.route('/consultar-pix/<intent_id>', methods=['GET'])
@requer_autenticacao
def consultar_pix(intent_id):
    """Consulta o extrato detalhado do Pix Automático com cálculo analítico de parcelas"""
    api_key = obter_api_key()
    if not api_key:
        return jsonify({"erro": "Erro na autenticação com a Pluggy"}), 500

    try:
        response = requests.get(
            f"https://api.pluggy.ai/payments/intents/{intent_id}",
            headers={"X-API-KEY": api_key},
            timeout=15
        )
        if response.status_code != 200:
            return jsonify({"erro": "Falha ao buscar intent", "detalhes": response.text}), response.status_code

        intent_data = response.json()
        extrato_analitico = calcular_extrato_pix(intent_data)
        return jsonify(extrato_analitico), 200
    except Exception as e:
        return jsonify({"erro": f"Erro interno ao buscar Pix: {str(e)}"}), 500

# ====================================================================
# 6. SERVIDOR DE ARQUIVOS ESTÁTICOS (ROTEAMENTO COMPLETO)
# ====================================================================

@app.route('/')
def rota_raiz():
    return send_from_directory(".", "gestor-login.html")

@app.route('/index')
@app.route('/index.html')
def rota_index():
    return send_from_directory(".", "index.html")

@app.route('/cliente')
@app.route('/cliente.html')
def rota_cliente():
    return send_from_directory(".", "cliente.html")

@app.route('/gestor')
@app.route('/gestor.html')
def rota_gestor():
    return send_from_directory(".", "gestor.html")

@app.route('/gestor-login')
@app.route('/gestor-login.html')
def rota_gestor_login():
    return send_from_directory(".", "gestor-login.html")

@app.route('/extratos')
@app.route('/extratos.html')
def rota_extratos():
    return send_from_directory(".", "extratos.html")

@app.route('/painel')
@app.route('/painel.html')
def rota_painel():
    return send_from_directory(".", "painel.html")

@app.route('/<path:filename>')
def rota_estaticos(filename):
    """Serve arquivos auxiliares como config.js, imagens, css, etc."""
    if os.path.exists(os.path.join(".", filename)):
        return send_from_directory(".", filename)
    return jsonify({"erro": "Arquivo não encontrado"}), 404

# ====================================================================
# 7. INICIALIZAÇÃO DO SERVIDOR
# ====================================================================
if __name__ == "__main__":
    porta = int(os.environ.get("PORT", 5000))
    print(f"[OK] Iniciando MC Securitizadora Open Finance na porta {porta}...")
    app.run(host="0.0.0.0", port=porta, debug=False)