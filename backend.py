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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

app = Flask(__name__, static_folder=BASE_DIR)
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
CORS(app, origins=CORS_ORIGINS.split(',') if CORS_ORIGINS != '*' else '*')

@app.after_request
def adicionar_headers_seguranca(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# ====================================================================
# 1. CREDENCIAIS E CONFIGURACOES
# ====================================================================
CLIENT_ID = os.environ.get('PLUGGY_CLIENT_ID', '37bdb5b6-faf1-4ef9-bda6-e8b7abe5b188')
CLIENT_SECRET = os.environ.get('PLUGGY_CLIENT_SECRET', '7e21d0d2-64f5-4300-b8af-cc6e8a431112')
RECIPIENT_ID = os.environ.get('PLUGGY_RECIPIENT_ID', '043e7bb1-da9a-4c74-acc3-6cf0741bf31a')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://vitrine-openfinance.onrender.com').rstrip('/')
SECRET_KEY = os.environ.get('SECRET_KEY', 'mc-securitizadora-secret-key-2026')

SUPABASE_URL = os.environ.get('SUPABASE_URL')
if SUPABASE_URL:
    SUPABASE_URL = SUPABASE_URL.rstrip('/').replace('/rest/v1', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f'[ALERTA] Falha ao conectar no Supabase: {e}')

GESTOR_USERS_RAW = os.environ.get('GESTOR_USERS', 'admin:securitizadora2026,julianemc:MC@2026,gabriel:MC@2026')
GESTOR_USERS = {}
for par in GESTOR_USERS_RAW.split(','):
    if ':' in par:
        u, p = par.strip().split(':', 1)
        GESTOR_USERS[u.strip()] = p.strip()

# ====================================================================
# 2. CACHES EM MEMORIA (API KEY & INTENTS)
# ====================================================================
_pluggy_cache = {'api_key': None, 'expires_at': 0}
_pix_cache = {'data': None, 'timestamp': 0}

def obter_api_key():
    agora = time.time()
    if _pluggy_cache['api_key'] and _pluggy_cache['expires_at'] > agora + 300:
        return _pluggy_cache['api_key']
    try:
        auth_response = requests.post(
            'https://api.pluggy.ai/auth',
            json={'clientId': CLIENT_ID, 'clientSecret': CLIENT_SECRET},
            timeout=15
        )
        if auth_response.status_code == 200:
            api_key = auth_response.json().get('apiKey')
            if api_key:
                _pluggy_cache['api_key'] = api_key
                _pluggy_cache['expires_at'] = agora + 7200
                return api_key
        print(f'[ERRO PLUGGY AUTH]: {auth_response.status_code} - {auth_response.text}')
    except Exception as e:
        print(f'[EXCECAO PLUGGY AUTH]: {e}')
    return None

# ====================================================================
# 3. AUTENTICACAO E SESSAO DO GESTOR (HMAC)
# ====================================================================
def gerar_token_sessao(usuario: str) -> str:
    timestamp = int(time.time())
    payload = f'{usuario}:{timestamp}'
    assinatura = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f'{payload}:{assinatura}'.encode()).decode()
    return token

def validar_token_sessao(token: str) -> str:
    try:
        decodificado = base64.urlsafe_b64decode(token.encode()).decode()
        partes = decodificado.split(':')
        if len(partes) != 3:
            return None
        usuario, timestamp_str, assinatura = partes
        timestamp = int(timestamp_str)
        agora = int(time.time())
        if agora - timestamp > 86400 or timestamp > agora + 60:
            return None
        payload = f'{usuario}:{timestamp}'
        assinatura_esperada = hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if hmac.compare_digest(assinatura, assinatura_esperada):
            return usuario
    except Exception:
        return None
    return None

def requer_autenticacao(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        header_auth = request.headers.get('Authorization', '')
        if not header_auth.startswith('Bearer '):
            return jsonify({'erro': 'Nao autorizado: Token nao fornecido'}), 401
        token = header_auth.replace('Bearer ', '').strip()
        usuario = validar_token_sessao(token)
        if not usuario:
            return jsonify({'erro': 'Nao autorizado: Token invalido ou expirado'}), 401
        request.usuario_autenticado = usuario
        return f(*args, **kwargs)
    return decorada

# ====================================================================
# MAPEAMENTO OFICIAL DE BANCOS (COMPE)
# ====================================================================
CONNECTOR_COMPE = {
    611: '001', 662: '001', 608: '033', 621: '033', 619: '104', 616: '104',
    603: '237', 609: '237', 601: '341', 618: '341', 786: '341', 612: '260',
    664: '260', 626: '336', 726: '336', 651: '380', 713: '380', 692: '290',
    816: '290', 652: '318', 666: '318', 817: '070', 818: '070', 653: '335',
    674: '335', 671: '004', 672: '004', 680: '243', 742: '389', 819: '389',
    657: '623', 714: '637', 715: '637', 659: '041', 660: '041', 675: '208',
    655: '208', 718: '655', 716: '655', 719: '655', 606: '323', 665: '323',
    656: '237', 801: '237', 689: '536', 750: '069', 860: '069', 629: '422',
    697: '422', 658: '756', 628: '756', 661: '748', 627: '748', 787: '197',
    788: '197', 663: '136', 670: '136', 602: '102', 702: '102', 880: '383',
    777: '777', 778: '777', 804: '099', 767: '767', 768: '767', 676: '748',
}

NOME_COMPE_FALLBACK = {
    'banco do brasil': '001', 'santander': '033', 'caixa': '104', 'bradesco': '237',
    'itau': '341', 'itaú': '341', 'nubank': '260', 'inter': '077', 'c6': '336',
    'picpay': '380', 'pagbank': '290', 'pagseguro': '290', 'original': '212',
    'safra': '422', 'sicredi': '748', 'sicoob': '756', 'banrisul': '041',
    'bmg': '318', 'brb': '070', 'digio': '335', 'nordeste': '004', 'master': '243',
    'mercantil': '389', 'pan': '623', 'sofisa': '637', 'btg': '208', 'bv': '655',
    'votorantim': '655', 'mercado pago': '323', 'next': '237', 'neon': '536',
    'crefisa': '069', 'infinitepay': '777', 'stone': '197', 'unicred': '136',
    'xp': '102', 'bemol': '383', 'cora': '403', 'ailos': '085', 'banestes': '021',
    'rendimento': '633', 'daycoval': '707', 'agibank': '121', 'agi': '121',
}

def obter_codigo_banco(connector_id: int, nome: str) -> str:
    if connector_id in CONNECTOR_COMPE:
        return CONNECTOR_COMPE[connector_id]
    nome_norm = (nome or '').lower()
    for chave, codigo in NOME_COMPE_FALLBACK.items():
        if chave in nome_norm:
            return codigo
    return ''

# ====================================================================
# 4. ROTAS PUBLICAS E CONEXAO DE CLIENTES
# ====================================================================

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'pluggy_configurada': bool(CLIENT_ID and CLIENT_SECRET),
        'supabase_conectado': bool(supabase is not None),
        'frontend_url': FRONTEND_URL,
        'timestamp': int(time.time())
    }), 200

@app.route('/api/login', methods=['POST'])
def api_login():
    dados = request.get_json(silent=True) or {}
    usuario = dados.get('usuario', '').strip()
    senha = dados.get('senha', '').strip()
    if not usuario or not senha:
        return jsonify({'erro': 'Usuario e senha sao obrigatorios'}), 400
    senha_esperada = GESTOR_USERS.get(usuario)
    if senha_esperada and hmac.compare_digest(senha, senha_esperada):
        token = gerar_token_sessao(usuario)
        return jsonify({
            'sucesso': True,
            'token': token,
            'usuario': {'username': usuario, 'nome': usuario.capitalize()}
        }), 200
    return jsonify({'erro': 'Usuario ou senha incorretos'}), 401

@app.route('/listar-bancos', methods=['GET'])
def listar_bancos():
    api_key = obter_api_key()
    if not api_key:
        return jsonify({'erro': 'Erro na autenticacao com a Pluggy'}), 500
    try:
        response = requests.get(
            'https://api.pluggy.ai/connectors?countries=BR',
            headers={'X-API-KEY': api_key},
            timeout=15
        )
        if response.status_code != 200:
            return jsonify({'erro': 'Falha ao buscar conectores bancarios'}), response.status_code
        conectores = response.json().get('results', [])
        bancos_validos = []
        for c in conectores:
            if c.get('type') in ['PERSONAL_BANK', 'BUSINESS_BANK'] and c.get('supportsPaymentInitiation') is True:
                cid = c.get('id')
                raw_name = c.get('name', '').strip()
                code = obter_codigo_banco(cid, raw_name)
                display_name = f'{code} - {raw_name}' if code else raw_name
                bancos_validos.append({
                    'id': cid,
                    'name': display_name,
                    'code': code,
                    'raw_name': raw_name,
                    'imageUrl': c.get('imageUrl')
                })
        bancos_validos.sort(key=lambda x: (0 if x['code'] else 1, x['code'] or '', x['raw_name']))
        return jsonify(bancos_validos)
    except Exception as e:
        return jsonify({'erro': f'Erro interno ao listar bancos: {str(e)}'}), 500

@app.route('/gerar-token', methods=['GET', 'POST'])
def gerar_token():
    api_key = obter_api_key()
    if not api_key:
        return jsonify({'erro': 'Erro na autenticacao com a Pluggy'}), 500
    dados = request.get_json(silent=True) or {}
    cliente_id = request.args.get('cliente') or dados.get('cliente') or 'Cliente'
    try:
        token_payload = {
            'options': {
                'clientUserId': str(cliente_id),
                'webhookUrl': 'https://motor-openfinance.onrender.com/api/webhook/pluggy'
            }
        }
        token_response = requests.post(
            'https://api.pluggy.ai/connect_token',
            headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
            json=token_payload,
            timeout=15
        )
        if token_response.status_code != 200:
            token_response = requests.post(
                'https://api.pluggy.ai/connect_token',
                headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
                timeout=15
            )
        if token_response.status_code != 200:
            return jsonify({'erro': 'Erro ao gerar Connect Token'}), token_response.status_code
        return jsonify({'token': token_response.json().get('accessToken')})
    except Exception as e:
        return jsonify({'erro': f'Erro interno: {str(e)}'}), 500

@app.route('/gerar-token-pix', methods=['POST'])
def gerar_token_pix():
    api_key = obter_api_key()
    if not api_key:
        return jsonify({'erro': 'Erro na autenticacao com a Pluggy'}), 500
    dados = request.get_json(silent=True) or {}
    valor_pix = dados.get('valor')
    cpf_cliente = re.sub(r'\D', '', str(dados.get('cpf', '')).strip())
    data_inicio = str(dados.get('data_inicio', '')).strip()
    banco_selecionado = dados.get('banco')

    if not all([valor_pix, cpf_cliente, data_inicio, banco_selecionado]):
        return jsonify({'erro': 'Faltam dados obrigatorios para Pix Automatico'}), 400
    if len(cpf_cliente) != 11:
        return jsonify({'erro': 'CPF invalido. Deve conter 11 digitos.'}), 400
    try:
        valor_float = float(valor_pix)
        if valor_float <= 0:
            return jsonify({'erro': 'Valor deve ser maior que zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'erro': 'Valor invalido'}), 400

    try:
        partes_data = data_inicio.split('-')
        dia_mes = int(partes_data[2]) if len(partes_data) >= 3 else 10
        if dia_mes < 1 or dia_mes > 28:
            dia_mes = min(max(dia_mes, 1), 28)
    except Exception:
        dia_mes = 10

    request_payload = {
        'amount': float(valor_pix),
        'description': 'Pagamento Pix Mensal - MC Securitizadora',
        'recipientId': RECIPIENT_ID,
        'callbackUrls': {
            'success': f'{FRONTEND_URL}/cliente.html?status=sucesso',
            'error': f'{FRONTEND_URL}/cliente.html?status=erro'
        },
        'schedule': {
            'type': 'MONTHLY',
            'startDate': data_inicio,
            'dayOfMonth': dia_mes,
            'occurrences': 12
        }
    }

    try:
        req_response = requests.post(
            'https://api.pluggy.ai/payments/requests',
            headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
            json=request_payload,
            timeout=15
        )
        if req_response.status_code not in (200, 201):
            return jsonify({'erro': 'Erro ao criar requisicao de pagamento'}), req_response.status_code

        payment_request_id = req_response.json().get('id')
        intent_payload = {
            'paymentRequestId': payment_request_id,
            'connectorId': int(banco_selecionado),
            'parameters': {'cpf': cpf_cliente, 'name': 'Cliente'}
        }
        intent_response = requests.post(
            'https://api.pluggy.ai/payments/intents',
            headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
            json=intent_payload,
            timeout=15
        )
        if intent_response.status_code not in (200, 201):
            return jsonify({'erro': 'Erro ao criar intencao de pagamento'}), intent_response.status_code

        intent_data = intent_response.json()
        payment_intent_id = intent_data.get('id')
        consent_url = intent_data.get('consentUrl') or intent_data.get('url')

        token_payload = {'options': {'paymentIntentId': payment_intent_id}}
        token_response = requests.post(
            'https://api.pluggy.ai/connect_token',
            headers={'X-API-KEY': api_key, 'Content-Type': 'application/json'},
            json=token_payload,
            timeout=15
        )
        token_access = token_response.json().get('accessToken') if token_response.status_code == 200 else None
        _pix_cache['timestamp'] = 0

        return jsonify({
            'token': token_access,
            'payment_intent_id': payment_intent_id,
            'consentUrl': consent_url,
            'consent_url': consent_url
        }), 200
    except Exception as e:
        return jsonify({'erro': f'Erro interno ao processar Pix: {str(e)}'}), 500

def calcular_extrato_pix(intent_data: dict) -> dict:
    from datetime import date
    import calendar

    req = intent_data.get('paymentRequest') or {}
    schedule = req.get('schedule') or {}
    auto_pix = req.get('automaticPix') or {}
    status = intent_data.get('status', 'PENDING')
    connector = intent_data.get('connector') or {}
    debtor = intent_data.get('debtor') or {}
    
    valor = 0.0
    if auto_pix.get('fixedAmount') is not None:
        try:
            valor = float(auto_pix.get('fixedAmount'))
        except (ValueError, TypeError):
            pass
    if valor <= 0 and req.get('amount') is not None:
        try:
            valor = float(req.get('amount'))
        except (ValueError, TypeError):
            pass

    start_date_str = auto_pix.get('startDate') or schedule.get('startDate') or time.strftime('%Y-%m-%d')
    expires_at_str = auto_pix.get('expiresAt') or ''

    occurrences = 12
    if schedule.get('occurrences'):
        try:
            occurrences = int(schedule.get('occurrences'))
        except (ValueError, TypeError):
            occurrences = 12
    elif expires_at_str and start_date_str:
        try:
            p_start = [int(x) for x in str(start_date_str).split('-')[:3]]
            p_exp = [int(x) for x in str(expires_at_str)[:10].split('-')[:3]]
            meses_diff = (p_exp[0] - p_start[0]) * 12 + (p_exp[1] - p_start[1]) + 1
            if meses_diff > 0:
                occurrences = meses_diff
        except Exception:
            occurrences = 12

    try:
        partes = [int(x) for x in str(start_date_str).split('-')[:3]]
        if len(partes) == 3:
            data_base = date(partes[0], partes[1], partes[2])
        else:
            data_base = date.today()
    except Exception:
        data_base = date.today()

    agora = date.today()
    cronograma = []
    parcelas_pagas = 0
    cliente_pagando = (status == 'PAYMENT_COMPLETED')

    for i in range(1, occurrences + 1):
        m_total = (data_base.month - 1) + (i - 1)
        novo_ano = data_base.year + (m_total // 12)
        novo_mes = (m_total % 12) + 1
        max_dias = calendar.monthrange(novo_ano, novo_mes)[1]
        dia_venc = min(data_base.day, max_dias)
        vencimento_parcela = date(novo_ano, novo_mes, dia_venc)
        venc_str = vencimento_parcela.strftime('%d/%m/%Y')

        if status in ['CONSENT_REJECTED', 'REJECTED', 'ERROR']:
            status_parcela = 'rejeitada'
            badge_texto = 'Cancelada / Nao Autorizada'
            cor_badge = 'rose'
        elif status in ['WAITING_PAYER_AUTHORIZATION', 'CONSENT_AWAITING_AUTHORIZATION', 'PENDING']:
            if i == 1:
                status_parcela = 'pendente'
                badge_texto = 'Aguardando Banco'
                cor_badge = 'amber'
            else:
                status_parcela = 'a_vencer'
                badge_texto = 'A Vencer'
                cor_badge = 'slate'
        elif status == 'PAYMENT_COMPLETED':
            if vencimento_parcela <= agora:
                status_parcela = 'paga'
                badge_texto = 'Paga'
                cor_badge = 'emerald'
                parcelas_pagas += 1
            elif parcelas_pagas == i - 1 and vencimento_parcela > agora:
                status_parcela = 'proximo_debito'
                badge_texto = 'Proximo Debito'
                cor_badge = 'sky'
            else:
                status_parcela = 'a_vencer'
                badge_texto = 'A Vencer'
                cor_badge = 'slate'
        else:
            status_parcela = 'a_vencer'
            badge_texto = 'A Vencer'
            cor_badge = 'slate'

        cronograma.append({
            'numero': i,
            'vencimento': venc_str,
            'vencimento_iso': vencimento_parcela.isoformat(),
            'valor': valor,
            'status': status_parcela,
            'badge': badge_texto,
            'cor': cor_badge
        })

    if status == 'PAYMENT_COMPLETED' and parcelas_pagas == 0 and len(cronograma) > 0:
        cronograma[0]['status'] = 'paga'
        cronograma[0]['badge'] = 'Paga (Adesao)'
        cronograma[0]['cor'] = 'emerald'
        parcelas_pagas = 1
        if len(cronograma) > 1:
            cronograma[1]['status'] = 'proximo_debito'
            cronograma[1]['badge'] = 'Proximo Debito'
            cronograma[1]['cor'] = 'sky'

    parcelas_restantes = max(0, occurrences - parcelas_pagas)
    if status in ['CONSENT_REJECTED', 'REJECTED', 'ERROR']:
        status_rotulo = 'Cancelado / Rejeitado'
        status_classe = 'rejeitado'
    elif status == 'PAYMENT_COMPLETED':
        status_rotulo = 'Em Dia (Ativo)'
        status_classe = 'ativo'
    else:
        status_rotulo = 'Aguardando Autorizacao'
        status_classe = 'pendente'

    proxima = next((p for p in cronograma if p['status'] in ['proximo_debito', 'pendente', 'a_vencer']), None)
    proximo_vencimento = proxima['vencimento'] if proxima else 'Concluido'
    first_payment = auto_pix.get('firstPayment') or {}

    return {
        'id': intent_data.get('id'),
        'status': status,
        'status_rotulo': status_rotulo,
        'status_classe': status_classe,
        'cliente_pagando': cliente_pagando,
        'banco_nome': connector.get('name', 'Banco'),
        'banco_imagem': connector.get('imageUrl'),
        'parcelas_total': occurrences,
        'parcelas_pagas': parcelas_pagas,
        'parcelas_restantes': parcelas_restantes,
        'valor_parcela': valor,
        'valor_adesao': float(first_payment.get('amount') or 0.0) if first_payment else 0.0,
        'total_pago': round(parcelas_pagas * valor, 2),
        'total_restante': round(parcelas_restantes * valor, 2),
        'proximo_vencimento': proximo_vencimento,
        'data_inicio': start_date_str,
        'data_termino': expires_at_str,
        'debtor': debtor,
        'cronograma': cronograma,
        'raw': intent_data
    }

@app.route('/salvar-conexao', methods=['POST'])
def salvar_conexao():
    """Salva a conexao garantindo compatibilidade com constraints NOT NULL no Supabase"""
    dados = request.get_json(silent=True) or {}
    cliente = str(dados.get('cliente', '')).strip()
    item_id = dados.get('item_id')
    payment_intent_id = dados.get('payment_intent_id')

    if not cliente:
        return jsonify({'erro': 'Identificador do cliente e obrigatorio'}), 400
    if not item_id and not payment_intent_id:
        return jsonify({'erro': 'Nenhum dado financeiro enviado'}), 400

    _pix_cache['timestamp'] = 0

    if not supabase:
        return jsonify({'sucesso': True, 'aviso': 'Modo local'}), 200

    try:
        item_id_seguro = str(item_id) if item_id else str(payment_intent_id)
        registro = {
            'cliente': cliente,
            'item_id': item_id_seguro
        }
        if payment_intent_id:
            registro['payment_intent_id'] = str(payment_intent_id)
        supabase.table('conexoes').insert(registro).execute()
        return jsonify({'sucesso': True}), 200
    except Exception as e:
        print(f'[ERRO SUPABASE INSERT]: {e}')
        return jsonify({'erro': f'Falha ao persistir no banco: {str(e)}'}), 500

# ====================================================================
# 5. ROTAS DE GESTAO E ESPELHO DO PAINEL DA PLUGGY
# ====================================================================

def obter_todos_intents_pix(forcar_atualizacao=False):
    """Puxa TODAS as informacoes de Pix Automatico diretamente da API da Pluggy (100% fiel ao dashboard Pluggy)"""
    agora = time.time()
    if not forcar_atualizacao and _pix_cache['data'] and (_pix_cache['timestamp'] > agora - 30):
        return _pix_cache['data']

    api_key = obter_api_key()
    if not api_key:
        return {'erro': 'Falha na autenticacao Pluggy', 'results': [], 'total': 0, 'kpis': {}}

    try:
        raw_intents = []
        page = 1
        total_pages = 1

        while page <= total_pages and page <= 5:
            res = requests.get(
                f'https://api.pluggy.ai/payments/intents?pageSize=100&page={page}',
                headers={'X-API-KEY': api_key},
                timeout=20
            )
            if res.status_code != 200:
                if not raw_intents:
                    return {'erro': f'Erro Pluggy API: {res.status_code}', 'results': [], 'total': 0, 'kpis': {}}
                break
            page_data = res.json()
            raw_intents.extend(page_data.get('results', []))
            total_pages = page_data.get('totalPages', 1)
            page += 1
        mapa_aliases = {}
        if supabase:
            try:
                sb_conns = supabase.table('conexoes').select('cliente, payment_intent_id').execute().data or []
                for sc in sb_conns:
                    pid = sc.get('payment_intent_id')
                    if pid and sc.get('cliente'):
                        mapa_aliases[pid] = sc.get('cliente')
            except Exception as e_sb:
                print(f'[AVISO SUPABASE MAPA]: {e_sb}')

        formatados = []
        ativos_count = 0
        pendentes_count = 0
        rejeitados_count = 0
        volume_recorrente_total = 0.0

        for pi in raw_intents:
            intent_id = pi.get('id')
            status = pi.get('status', 'PENDING')
            connector = pi.get('connector') or {}
            payment_request = pi.get('paymentRequest') or {}
            auto_pix = payment_request.get('automaticPix') or {}
            schedule = payment_request.get('schedule') or {}
            debtor = pi.get('debtor') or {}

            if status == 'PAYMENT_COMPLETED':
                status_label = 'Autorizado / Em Dia'
                status_classe = 'ativo'
                status_cor = 'emerald'
                status_badge = 'bg-emerald-100 text-emerald-800 border-emerald-300'
                ativos_count += 1
            elif status in ['CONSENT_AWAITING_AUTHORIZATION', 'WAITING_PAYER_AUTHORIZATION', 'PENDING']:
                status_label = 'Aguardando Autorizacao'
                status_classe = 'pendente'
                status_cor = 'amber'
                status_badge = 'bg-amber-100 text-amber-800 border-amber-300'
                pendentes_count += 1
            elif status in ['CONSENT_REJECTED', 'REJECTED']:
                status_label = 'Rejeitado / Cancelado'
                status_classe = 'rejeitado'
                status_cor = 'rose'
                status_badge = 'bg-rose-100 text-rose-800 border-rose-300'
                rejeitados_count += 1
            elif status == 'ERROR':
                status_label = 'Erro de Processamento'
                status_classe = 'erro'
                status_cor = 'rose'
                status_badge = 'bg-rose-100 text-rose-800 border-rose-300'
                rejeitados_count += 1
            else:
                status_label = status
                status_classe = 'outro'
                status_cor = 'slate'
                status_badge = 'bg-slate-100 text-slate-800 border-slate-300'

            valor_parcela = 0.0
            if auto_pix.get('fixedAmount') is not None:
                try:
                    valor_parcela = float(auto_pix.get('fixedAmount'))
                except (ValueError, TypeError):
                    pass
            if valor_parcela <= 0 and payment_request.get('amount') is not None:
                try:
                    valor_parcela = float(payment_request.get('amount'))
                except (ValueError, TypeError):
                    pass

            if status == 'PAYMENT_COMPLETED':
                volume_recorrente_total += valor_parcela

            first_payment = auto_pix.get('firstPayment') or {}
            valor_adesao = float(first_payment.get('amount') or 0.0) if first_payment else 0.0

            identificador_display = (
                mapa_aliases.get(intent_id)
                or payment_request.get('clientPaymentId')
                or debtor.get('name')
                or payment_request.get('description')
                or f'Contrato-{intent_id[:8]}'
            )

            cpf_extraido = ''
            raw_text = f"{payment_request.get('clientPaymentId', '')} {debtor.get('taxNumber', '')}"
            m_cpf = re.search(r'\d{3}\.?\d{3}\.?\d{3}-?\d{2}', raw_text)
            if m_cpf:
                cpf_extraido = m_cpf.group(0)

            cid = connector.get('id')
            banco_nome = connector.get('name') or 'Instituicao Bancaria'
            compe = obter_codigo_banco(cid, banco_nome)
            banco_display = f'{compe} - {banco_nome}' if compe else banco_nome

            payment_url = payment_request.get('paymentUrl') or pi.get('consentUrl') or ''
            consent_url = pi.get('consentUrl') or payment_url

            formatados.append({
                'id': intent_id,
                'payment_request_id': payment_request.get('id'),
                'cliente': identificador_display,
                'cpf': cpf_extraido,
                'status': status,
                'status_label': status_label,
                'status_classe': status_classe,
                'status_cor': status_cor,
                'status_badge': status_badge,
                'banco_id': cid,
                'banco_nome': banco_display,
                'banco_raw_name': banco_nome,
                'banco_imagem': connector.get('imageUrl'),
                'banco_codigo': compe,
                'valor_parcela': valor_parcela,
                'valor_adesao': valor_adesao,
                'data_inicio': auto_pix.get('startDate') or schedule.get('startDate') or '',
                'data_termino': auto_pix.get('expiresAt') or '',
                'intervalo': auto_pix.get('interval') or 'MONTHLY',
                'retentativas': auto_pix.get('automaticRetriesConfiguration', {}).get('retryDays', [1, 2, 3]),
                'data_criacao': pi.get('createdAt') or '',
                'data_atualizacao': pi.get('updatedAt') or '',
                'payment_url': payment_url,
                'consent_url': consent_url,
                'error_detail': pi.get('errorDetail'),
                'raw': pi
            })

        formatados.sort(key=lambda x: x.get('data_criacao') or '', reverse=True)
        resultado = {
            'sucesso': True,
            'total': len(formatados),
            'kpis': {
                'total_contratos': len(formatados),
                'ativos': ativos_count,
                'pendentes': pendentes_count,
                'rejeitados': rejeitados_count,
                'volume_recorrente_total': round(volume_recorrente_total, 2)
            },
            'results': formatados
        }
        _pix_cache['data'] = resultado
        _pix_cache['timestamp'] = agora
        return resultado
    except Exception as e:
        print(f'[EXCECAO OBTER INTENTS PLUGGY]: {e}')
        return {'erro': str(e), 'results': [], 'total': 0, 'kpis': {}}

@app.route('/api/pix-intents', methods=['GET'])
@requer_autenticacao
def api_pix_intents():
    """Espelho em tempo real dos contratos de Pix Automático da Pluggy com KPIs"""
    forcar = request.args.get('force') in ['true', '1']
    dados = obter_todos_intents_pix(forcar_atualizacao=forcar)
    return jsonify(dados), 200

@app.route('/listar-conexoes', methods=['GET'])
@requer_autenticacao
def listar_conexoes():
    if not supabase:
        return jsonify([
            {
                'id': 1,
                'cliente': 'ClienteDemonstracao',
                'item_id': 'demo-item-12345',
                'payment_intent_id': None,
                'tipo': 'open_finance',
                'data_conexao': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            }
        ]), 200

    try:
        # 1. Busca conexoes Open Finance (payment_intent_id IS NULL) - quota garantida
        res_of = supabase.table('conexoes').select('*').is_('payment_intent_id', 'null').order('data_conexao', desc=True).limit(100).execute()
        conexoes_of = res_of.data or []
        for c in conexoes_of:
            c['tipo'] = 'open_finance'

        # 2. Busca conexoes Pix Automatico (payment_intent_id IS NOT NULL)
        res_pix = supabase.table('conexoes').select('*').not_.is_('payment_intent_id', 'null').order('data_conexao', desc=True).limit(250).execute()
        conexoes_pix = res_pix.data or []
        for c in conexoes_pix:
            c['tipo'] = 'pix_automatico'

        conexoes = conexoes_of + conexoes_pix
        return jsonify(conexoes), 200
    except Exception as e:
        print(f'[ERRO SUPABASE SELECT]: {e}')
        return jsonify({'erro': f'Falha ao consultar banco: {str(e)}'}), 500

@app.route('/consultar-dados/<item_id>', methods=['GET'])
@requer_autenticacao
def consultar_dados(item_id):
    api_key = obter_api_key()
    if not api_key:
        return jsonify({'erro': 'Erro na autenticacao com a Pluggy'}), 500
    try:
        item_info = {}
        try:
            it_res = requests.get(
                f'https://api.pluggy.ai/items/{item_id}',
                headers={'X-API-KEY': api_key},
                timeout=12
            )
            if it_res.status_code == 200:
                item_info = it_res.json()
        except Exception as e_it:
            print(f'[AVISO] Falha ao consultar item {item_id}: {e_it}')

        contas_response = requests.get(
            f'https://api.pluggy.ai/accounts?itemId={item_id}',
            headers={'X-API-KEY': api_key},
            timeout=15
        )
        contas = []
        if contas_response.status_code == 200:
            contas = contas_response.json().get('results', [])

        return jsonify({
            'item': {
                'id': item_id,
                'status': item_info.get('status', 'UPDATED'),
                'connector': item_info.get('connector', {}),
                'error': item_info.get('error'),
                'lastUpdatedAt': item_info.get('lastUpdatedAt')
            },
            'results': contas,
            'total': len(contas)
        }), 200
    except Exception as e:
        return jsonify({'erro': f'Erro interno ao buscar contas: {str(e)}'}), 500

@app.route('/consultar-transacoes/<account_id>', methods=['GET'])
@requer_autenticacao
def consultar_transacoes(account_id):
    api_key = obter_api_key()
    if not api_key:
        return jsonify({'erro': 'Erro na autenticacao com a Pluggy'}), 500
    try:
        transacoes_response = requests.get(
            f'https://api.pluggy.ai/v2/transactions?accountId={account_id}',
            headers={'X-API-KEY': api_key},
            timeout=15
        )
        if transacoes_response.status_code != 200:
            return jsonify({'erro': 'Falha ao buscar extrato', 'detalhes': transacoes_response.text}), transacoes_response.status_code
        return jsonify(transacoes_response.json())
    except Exception as e:
        return jsonify({'erro': f'Erro interno ao buscar transacoes: {str(e)}'}), 500

@app.route('/consultar-pix/<intent_id>', methods=['GET'])
@requer_autenticacao
def consultar_pix(intent_id):
    api_key = obter_api_key()
    if not api_key:
        return jsonify({'erro': 'Erro na autenticacao com a Pluggy'}), 500
    try:
        response = requests.get(
            f'https://api.pluggy.ai/payments/intents/{intent_id}',
            headers={'X-API-KEY': api_key},
            timeout=15
        )
        if response.status_code != 200:
            return jsonify({'erro': 'Falha ao buscar intent', 'detalhes': response.text}), response.status_code
        intent_data = response.json()
        extrato_analitico = calcular_extrato_pix(intent_data)
        return jsonify(extrato_analitico), 200
    except Exception as e:
        return jsonify({'erro': f'Erro interno ao buscar Pix: {str(e)}'}), 500

# ====================================================================
# 6. WEBHOOKS DA PLUGGY & SINCRONIZACAO RESILIENTE
# ====================================================================

@app.route('/api/webhook/pluggy', methods=['POST'])
def webhook_pluggy():
    payload = request.get_json(silent=True) or {}
    event = payload.get('event') or ''
    item_id = payload.get('itemId') or payload.get('id') or (payload.get('data') or {}).get('id')
    intent_id = payload.get('paymentIntentId') or (payload.get('data') or {}).get('paymentIntentId')

    print(f'[WEBHOOK PLUGGY] Evento: {event} | Item: {item_id} | Intent: {intent_id}')
    _pix_cache['timestamp'] = 0

    if supabase:
        try:
            if event.startswith('item/') and item_id:
                api_key = obter_api_key()
                cliente_nome = f'Cliente-{item_id[:8]}'
                if api_key:
                    try:
                        id_res = requests.get(f'https://api.pluggy.ai/identity?itemId={item_id}', headers={'X-API-KEY': api_key}, timeout=10)
                        if id_res.status_code == 200:
                            identidade = id_res.json()
                            cliente_nome = identidade.get('fullName') or identidade.get('document') or cliente_nome
                    except Exception as e_id:
                        print(f'[AVISO WEBHOOK IDENTITY]: {e_id}')

                existente = supabase.table('conexoes').select('id').eq('item_id', str(item_id)).execute().data
                if not existente:
                    supabase.table('conexoes').insert({
                        'cliente': cliente_nome,
                        'item_id': str(item_id),
                        'payment_intent_id': None
                    }).execute()
                    print(f'[WEBHOOK] Open Finance salvo: {cliente_nome}')

            elif (event.startswith('payment_intent/') or event.startswith('payment_request/')) and intent_id:
                existente = supabase.table('conexoes').select('id').eq('payment_intent_id', str(intent_id)).execute().data
                if not existente:
                    supabase.table('conexoes').insert({
                        'cliente': f'Pix-{intent_id[:8]}',
                        'item_id': str(intent_id),
                        'payment_intent_id': str(intent_id)
                    }).execute()
                    print(f'[WEBHOOK] Pix salvo: {intent_id}')
        except Exception as e:
            print(f'[ERRO AO PROCESSAR WEBHOOK]: {e}')

    return jsonify({'status': 'ok', 'mensagem': 'Webhook recebido com sucesso'}), 200

@app.route('/api/sync-pluggy', methods=['POST', 'GET'])
@requer_autenticacao
def api_sync_pluggy():
    _pix_cache['timestamp'] = 0
    dados = obter_todos_intents_pix(forcar_atualizacao=True)
    intents = dados.get('results', [])

    novos_inseridos = 0
    if supabase and intents:
        try:
            existentes = supabase.table('conexoes').select('payment_intent_id').execute().data or []
            ids_existentes = set(x['payment_intent_id'] for x in existentes if x.get('payment_intent_id'))
            lote = []
            for item in intents:
                iid = item.get('id')
                if iid and iid not in ids_existentes:
                    lote.append({
                        'cliente': str(item.get('cliente') or f'Pix-{iid[:8]}')[:255],
                        'item_id': str(iid),
                        'payment_intent_id': str(iid)
                    })
                    ids_existentes.add(iid)
            if lote:
                for i in range(0, len(lote), 50):
                    supabase.table('conexoes').insert(lote[i:i+50]).execute()
                novos_inseridos = len(lote)
        except Exception as e_sync:
            print(f'[ERRO SYNC SUPABASE]: {e_sync}')

    return jsonify({
        'sucesso': True,
        'total_pluggy': len(intents),
        'novos_sincronizados_supabase': novos_inseridos,
        'kpis': dados.get('kpis', {})
    }), 200

# ====================================================================
# 7. SERVIDOR DE ARQUIVOS ESTATICOS (RESILIENTE COM BASE_DIR)
# ====================================================================

@app.route('/')
def rota_raiz():
    return send_from_directory(BASE_DIR, 'gestor-login.html')

@app.route('/index')
@app.route('/index.html')
def rota_index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/cliente')
@app.route('/cliente.html')
def rota_cliente():
    return send_from_directory(BASE_DIR, 'cliente.html')

@app.route('/gestor')
@app.route('/gestor.html')
def rota_gestor():
    return send_from_directory(BASE_DIR, 'gestor.html')

@app.route('/gestor-login')
@app.route('/gestor-login.html')
def rota_gestor_login():
    return send_from_directory(BASE_DIR, 'gestor-login.html')

@app.route('/extratos')
@app.route('/extratos.html')
def rota_extratos():
    return send_from_directory(BASE_DIR, 'extratos.html')

@app.route('/painel')
@app.route('/painel.html')
def rota_painel():
    return send_from_directory(BASE_DIR, 'painel.html')

@app.route('/<path:filename>')
def rota_estaticos(filename):
    caminho = os.path.join(BASE_DIR, filename)
    if os.path.exists(caminho):
        return send_from_directory(BASE_DIR, filename)
    return jsonify({'erro': 'Arquivo nao encontrado'}), 404

if __name__ == '__main__':
    porta = int(os.environ.get('PORT', 5000))
    print(f'[OK] Iniciando MC Securitizadora Open Finance na porta {porta}...')
    app.run(host='0.0.0.0', port=porta, debug=False)
