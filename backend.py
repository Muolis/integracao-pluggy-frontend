import os
import time
import hmac
import hashlib
import json
import base64
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

@app.route('/listar-bancos', methods=['GET'])
def listar_bancos():
    """Lista bancos com suporte a iniciação de pagamentos Pix via Pluggy"""
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
                bancos_validos.append({"id": c.get("id"), "name": c.get("name")})

        bancos_validos = sorted(bancos_validos, key=lambda x: x["name"])
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
    cpf_cliente = str(dados.get("cpf", "")).strip()
    data_inicio = str(dados.get("data_inicio", "")).strip()
    banco_selecionado = dados.get("banco")

    if not all([valor_pix, cpf_cliente, data_inicio, banco_selecionado]):
        return jsonify({"erro": "Faltam dados obrigatórios para Pix Automático"}), 400

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
            registro["tipo"] = "pix_automatico"
        elif item_id:
            registro["item_id"] = str(item_id)
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
    """Lista as conexões salvas de clientes no Supabase de forma segura e paginada"""
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
        return jsonify(resposta.data or []), 200
    except Exception as e:
        print(f"[ERRO SUPABASE SELECT]: {e}")
        return jsonify({"erro": f"Falha ao consultar banco: {str(e)}"}), 500

@app.route('/consultar-dados/<item_id>', methods=['GET'])
@requer_autenticacao
def consultar_dados(item_id):
    """Consulta as contas bancárias associadas a um Item ID do Open Finance na Pluggy"""
    api_key = obter_api_key()
    if not api_key:
        return jsonify({"erro": "Erro na autenticação com a Pluggy"}), 500

    try:
        contas_response = requests.get(
            f"https://api.pluggy.ai/accounts?itemId={item_id}",
            headers={"X-API-KEY": api_key},
            timeout=15
        )
        if contas_response.status_code != 200:
            return jsonify({"erro": "Falha ao buscar contas", "detalhes": contas_response.text}), contas_response.status_code
        return jsonify(contas_response.json())
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
    """Consulta o status de um contrato / intenção de Pix Automático"""
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
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"erro": f"Erro interno ao buscar Pix: {str(e)}"}), 500

# ====================================================================
# 6. SERVIDOR DE ARQUIVOS ESTÁTICOS (ROTEAMENTO COMPLETO)
# ====================================================================

@app.route('/')
def rota_raiz():
    return send_from_directory(".", "gestor-login.html")

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
    print(f"🚀 Iniciando MC Securitizadora Open Finance na porta {porta}...")
    app.run(host="0.0.0.0", port=porta, debug=False)