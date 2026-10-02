"""
PLUGGY MOCK MODULE - mc-minhaconta
Ambiente de Mock Isolado para Diagnóstico de Comunicação da API Pluggy
Permite validar se falhas ou divergências de dados ocorrem na aplicação (cliente)
ou no provedor externo (Pluggy).
"""

import json
import time
import os
from typing import Dict, Any, Optional, Tuple

# Flag global via variável de ambiente
MOCK_ENABLED_ENV = os.environ.get('PLUGGY_MOCK_ENABLED', '').lower() in ['true', '1', 'yes']

# Fixture de Clientes Mock
MOCK_CUSTOMERS = {
    'total': 3,
    'totalPages': 1,
    'page': 1,
    'results': [
        {
            'id': 'cust-001',
            'name': 'CARLOS EDUARDO SILVA',
            'email': 'carlos.silva@exemplo.com.br',
            'cpf': '12345678901',
            'cnpj': None,
            'type': 'INDIVIDUAL',
            'createdAt': '2026-08-15T10:00:00.000Z',
            'updatedAt': '2026-08-15T10:00:00.000Z'
        },
        {
            'id': 'cust-002',
            'name': 'MARIANA SANTOS ALBUQUERQUE',
            'email': 'mariana.albuquerque@empresa.com.br',
            'cpf': None,
            'cnpj': '12345678000195',
            'type': 'BUSINESS',
            'createdAt': '2026-09-01T14:30:00.000Z',
            'updatedAt': '2026-09-01T14:30:00.000Z'
        },
        {
            'id': 'cust-003',
            'name': 'ROBERTO ALVES FERREIRA',
            'email': 'roberto.alves@exemplo.com.br',
            'cpf': '98765432100',
            'cnpj': None,
            'type': 'INDIVIDUAL',
            'createdAt': '2026-09-10T11:20:00.000Z',
            'updatedAt': '2026-09-10T11:20:00.000Z'
        }
    ]
}

# Fixture de Solicitações (Payment Requests) Mock
MOCK_PAYMENT_REQUESTS = {
    'total': 4,
    'totalPages': 1,
    'page': 1,
    'results': [
        # 1. Contrato Pix Recorrente Autorizado e Ativo (Bradesco)
        {
            'id': 'pr-mock-authorized-01',
            'amount': 250.00,
            'description': 'CREDITO PESSOAL MC MINHACONTA',
            'status': 'AUTHORIZED',
            'createdAt': '2026-09-20T10:00:00.000Z',
            'updatedAt': '2026-09-20T10:05:00.000Z',
            'clientPaymentId': '123.456.789-01 CTR-8801',
            'paymentUrl': 'https://pay.pluggy.ai/pr-mock-authorized-01',
            'recipient': {
                'name': 'MC MINHACONTA SECURITIZADORA S/A',
                'taxNumber': '62455954000146',
                'paymentInstitution': {'name': 'Banco Bradesco S.A.'},
                'account': {'branch': '03201', 'number': '00796131'}
            },
            'customer': {
                'id': 'cust-001',
                'name': 'CARLOS EDUARDO SILVA',
                'cpf': '12345678901'
            },
            'automaticPix': {
                'interval': 'MONTHLY',
                'startDate': '2026-10-05',
                'expiresAt': '2027-09-05T23:59:59Z',
                'fixedAmount': 250.00,
                'firstPayment': {
                    'date': '2026-09-20',
                    'amount': 0.01,
                    'description': 'ADESAO CREDITO PESSOAL MC'
                },
                'isRetryAccepted': True,
                'schedulerConfiguration': {'enabled': True, 'description': 'CREDITO PESSOAL MC MINHACONTA'},
                'automaticRetriesConfiguration': {'retryDays': [1, 2, 3]}
            },
            'schedule': None,
            'errorDetail': None,
            'isSandbox': False
        },
        # 2. Contrato Expirado (Banco do Brasil - Timeout de autorização do usuário)
        {
            'id': 'pr-mock-expired-02',
            'amount': 180.50,
            'description': 'CREDITO PESSOAL MC MINHACONTA',
            'status': 'ERROR',
            'createdAt': '2026-09-22T14:00:00.000Z',
            'updatedAt': '2026-09-22T14:15:00.000Z',
            'clientPaymentId': '987.654.321-00 CTR-8802',
            'paymentUrl': 'https://pay.pluggy.ai/pr-mock-expired-02',
            'recipient': {
                'name': 'MC MINHACONTA SECURITIZADORA S/A',
                'taxNumber': '62455954000146',
                'paymentInstitution': {'name': 'Banco Bradesco S.A.'},
                'account': {'branch': '03201', 'number': '00796131'}
            },
            'customer': None,  # Simula customer nulo da Pluggy
            'automaticPix': {
                'interval': 'MONTHLY',
                'startDate': '2026-10-10',
                'expiresAt': '2027-10-10T23:59:59Z',
                'fixedAmount': 180.50,
                'firstPayment': {'date': '2026-09-22', 'amount': 0.01},
                'isRetryAccepted': True,
                'schedulerConfiguration': {'enabled': True},
                'automaticRetriesConfiguration': {'retryDays': [1, 2, 3]}
            },
            'schedule': None,
            'errorDetail': {
                'code': 'TEMPO_EXPIRADO_AUTORIZACAO',
                'providerCode': 'TEMPO_EXPIRADO_AUTORIZACAO',
                'providerTitle': 'Consentimento expirado',
                'providerDetail': 'Consentimento expirou antes que o usuário pudesse confirmá-lo no app do banco.'
            },
            'isSandbox': False
        },
        # 3. Contrato Cancelado/Revogado (Itaú)
        {
            'id': 'pr-mock-canceled-03',
            'amount': 320.00,
            'description': 'CREDITO PESSOAL MC MINHACONTA',
            'status': 'CANCELED',
            'createdAt': '2026-09-18T09:00:00.000Z',
            'updatedAt': '2026-09-19T11:00:00.000Z',
            'clientPaymentId': '456.789.012-34 CTR-8803',
            'paymentUrl': 'https://pay.pluggy.ai/pr-mock-canceled-03',
            'recipient': {
                'name': 'MC MINHACONTA SECURITIZADORA S/A',
                'taxNumber': '62455954000146',
                'paymentInstitution': {'name': 'Banco Bradesco S.A.'},
                'account': {'branch': '03201', 'number': '00796131'}
            },
            'customer': {
                'id': 'cust-003',
                'name': 'ROBERTO ALVES FERREIRA',
                'cpf': '98765432100'
            },
            'automaticPix': {
                'interval': 'MONTHLY',
                'startDate': '2026-10-15',
                'expiresAt': '2027-10-15T23:59:59Z',
                'fixedAmount': 320.00,
                'firstPayment': {'date': '2026-09-18', 'amount': 0.01},
                'isRetryAccepted': True,
                'schedulerConfiguration': {'enabled': True},
                'automaticRetriesConfiguration': {'retryDays': [1, 2, 3]}
            },
            'schedule': None,
            'errorDetail': {
                'code': 'REVOGADO_USUARIO',
                'providerCode': 'REVOGADO_USUARIO',
                'providerTitle': 'Consentimento revogado',
                'providerDetail': 'O cliente optou por revogar o mandato de Pix Automático no banco pagador.'
            },
            'isSandbox': False
        },
        # 4. Contrato Agendado Pendente (Nubank)
        {
            'id': 'pr-mock-scheduled-04',
            'amount': 150.00,
            'description': 'CREDITO PESSOAL MC MINHACONTA',
            'status': 'SCHEDULED',
            'createdAt': '2026-10-01T15:00:00.000Z',
            'updatedAt': '2026-10-01T15:01:00.000Z',
            'clientPaymentId': '111.222.333-44 CTR-8804',
            'paymentUrl': 'https://pay.pluggy.ai/pr-mock-scheduled-04',
            'recipient': {
                'name': 'MC MINHACONTA SECURITIZADORA S/A',
                'taxNumber': '62455954000146',
                'paymentInstitution': {'name': 'Banco Bradesco S.A.'},
                'account': {'branch': '03201', 'number': '00796131'}
            },
            'customer': {
                'id': 'cust-004',
                'name': 'ANA PAULA NOGUEIRA',
                'cpf': '11122233344'
            },
            'automaticPix': {
                'interval': 'MONTHLY',
                'startDate': '2026-11-01',
                'expiresAt': '2027-11-01T23:59:59Z',
                'fixedAmount': 150.00,
                'firstPayment': {'date': '2026-10-01', 'amount': 0.01},
                'isRetryAccepted': True,
                'schedulerConfiguration': {'enabled': True},
                'automaticRetriesConfiguration': {'retryDays': [1, 2, 3]}
            },
            'schedule': None,
            'errorDetail': None,
            'isSandbox': False
        }
    ]
}

# Fixture de Intenções (Payment Intents) Mock
MOCK_PAYMENT_INTENTS = {
    'total': 4,
    'totalPages': 1,
    'page': 1,
    'results': [
        # Intent do contrato 01 (Bradesco - PAYMENT_COMPLETED do firstPayment R$ 0,01)
        {
            'id': 'pi-mock-01',
            'status': 'PAYMENT_COMPLETED',
            'createdAt': '2026-09-20T10:00:00.000Z',
            'updatedAt': '2026-09-20T10:05:00.000Z',
            'paymentRequest': MOCK_PAYMENT_REQUESTS['results'][0],
            'connector': {
                'id': 203,
                'name': 'Bradesco',
                'imageUrl': 'https://cdn.pluggy.ai/assets/connector-icons/203.svg',
                'primaryColor': '#dc2626'
            },
            'debtor': {
                'name': 'CARLOS EDUARDO SILVA',
                'taxNumber': '12345678901',
                'branchNumber': '1234',
                'accountNumber': '567890'
            },
            'consentUrl': 'https://pay.pluggy.ai/consent/pi-mock-01',
            'errorDetail': None
        },
        # Intent do contrato 02 (Banco do Brasil - REJECTED por tempo)
        {
            'id': 'pi-mock-02',
            'status': 'REJECTED',
            'createdAt': '2026-09-22T14:00:00.000Z',
            'updatedAt': '2026-09-22T14:15:00.000Z',
            'paymentRequest': MOCK_PAYMENT_REQUESTS['results'][1],
            'connector': {
                'id': 211,
                'name': 'Banco do Brasil',
                'imageUrl': 'https://cdn.pluggy.ai/assets/connector-icons/211.svg',
                'primaryColor': '#eab308'
            },
            'debtor': {
                'name': 'CLIENTE BB DESCONHECIDO',
                'taxNumber': '98765432100'
            },
            'consentUrl': 'https://pay.pluggy.ai/consent/pi-mock-02',
            'errorDetail': MOCK_PAYMENT_REQUESTS['results'][1]['errorDetail']
        },
        # Intent do contrato 03 (Itaú - REVOKED)
        {
            'id': 'pi-mock-03',
            'status': 'REVOKED',
            'createdAt': '2026-09-18T09:00:00.000Z',
            'updatedAt': '2026-09-19T11:00:00.000Z',
            'paymentRequest': MOCK_PAYMENT_REQUESTS['results'][2],
            'connector': {
                'id': 201,
                'name': 'Itaú',
                'imageUrl': 'https://cdn.pluggy.ai/assets/connector-icons/201.svg',
                'primaryColor': '#ea580c'
            },
            'debtor': {
                'name': 'ROBERTO ALVES FERREIRA',
                'taxNumber': '98765432100',
                'branchNumber': '0001',
                'accountNumber': '987654'
            },
            'consentUrl': 'https://pay.pluggy.ai/consent/pi-mock-03',
            'errorDetail': MOCK_PAYMENT_REQUESTS['results'][2]['errorDetail']
        },
        # Intent do contrato 04 (Nubank - SCHEDULED)
        {
            'id': 'pi-mock-04',
            'status': 'SCHEDULED',
            'createdAt': '2026-10-01T15:00:00.000Z',
            'updatedAt': '2026-10-01T15:01:00.000Z',
            'paymentRequest': MOCK_PAYMENT_REQUESTS['results'][3],
            'connector': {
                'id': 212,
                'name': 'Nubank',
                'imageUrl': 'https://cdn.pluggy.ai/assets/connector-icons/212.svg',
                'primaryColor': '#8b5cf6'
            },
            'debtor': {
                'name': 'ANA PAULA NOGUEIRA',
                'taxNumber': '11122233344',
                'branchNumber': '0001',
                'accountNumber': '112233'
            },
            'consentUrl': 'https://pay.pluggy.ai/consent/pi-mock-04',
            'errorDetail': None
        }
    ]
}


class MockResponse:
    """Objeto compatível com requests.Response para responder às chamadas mockadas"""
    def __init__(self, status_code: int, json_data: Any, headers: Optional[Dict] = None):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = headers or {'Content-Type': 'application/json'}
        self.text = json.dumps(json_data) if isinstance(json_data, (dict, list)) else str(json_data)

    def json(self):
        return self._json_data


def dispatch_mock_request(method: str, url: str, headers: Optional[Dict] = None, json_payload: Optional[Dict] = None, scenario: str = 'default') -> MockResponse:
    """
    Roteador de requisições mockadas para a API da Pluggy.
    Suporta simulação de cenários nominais e de falhas (HTTP 200, 400, 500).
    """
    # 1. Simulação forçada de cenários de erro via parâmetro
    if scenario == 'error_500':
        return MockResponse(500, {
            'code': 500,
            'message': 'Pluggy Internal Server Error - Simulação de falha no servidor remoto da Pluggy',
            'trackingId': 'mock-err-500-track-xyz'
        })
    elif scenario == 'error_400':
        return MockResponse(400, {
            'code': 400,
            'message': 'Validation Error - Payload com parâmetros inválidos ou incompletos',
            'details': [{'field': 'automaticPix.fixedAmount', 'message': 'Amount must be greater than zero'}]
        })
    elif scenario == 'timeout':
        raise TimeoutError('Pluggy API Connection Timeout (Simulação de instabilidade de rede)')

    # 2. Roteamento por endpoint
    clean_url = url.split('?')[0].rstrip('/')

    # GET /payments/requests ou /payments/requests/{id}
    if clean_url.endswith('/payments/requests'):
        if method == 'POST':
            # Simula criação bem-sucedida de solicitação Pix
            novo_id = f"pr-mock-created-{int(time.time())}"
            return MockResponse(201, {
                'id': novo_id,
                'status': 'CREATED',
                'amount': (json_payload or {}).get('amount', 100.0),
                'paymentUrl': f'https://pay.pluggy.ai/{novo_id}',
                'createdAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'clientPaymentId': (json_payload or {}).get('clientPaymentId', 'CTR-NEW')
            })
        return MockResponse(200, MOCK_PAYMENT_REQUESTS)

    # Detalhe de um paymentRequest específico: /payments/requests/{id}
    if '/payments/requests/' in clean_url:
        req_id = clean_url.split('/payments/requests/')[-1]
        for r in MOCK_PAYMENT_REQUESTS['results']:
            if r['id'] == req_id:
                return MockResponse(200, r)
        # Fallback nominal se ID não estiver na lista prévia
        return MockResponse(200, {
            'id': req_id,
            'amount': 250.00,
            'description': 'CREDITO PESSOAL MC MINHACONTA (MOCK DETALHE)',
            'status': 'AUTHORIZED',
            'createdAt': '2026-09-20T10:00:00.000Z',
            'recipient': MOCK_PAYMENT_REQUESTS['results'][0]['recipient'],
            'customer': MOCK_PAYMENT_REQUESTS['results'][0]['customer'],
            'automaticPix': MOCK_PAYMENT_REQUESTS['results'][0]['automaticPix']
        })

    # GET /payments/intents ou /payments/intents/{id}
    if clean_url.endswith('/payments/intents'):
        return MockResponse(200, MOCK_PAYMENT_INTENTS)

    if '/payments/intents/' in clean_url:
        it_id = clean_url.split('/payments/intents/')[-1]
        for it in MOCK_PAYMENT_INTENTS['results']:
            if it['id'] == it_id:
                return MockResponse(200, it)
        # Fallback nominal
        return MockResponse(200, MOCK_PAYMENT_INTENTS['results'][0])

    # GET /payments/customers
    if clean_url.endswith('/payments/customers'):
        return MockResponse(200, MOCK_CUSTOMERS)

    # POST /connect_token
    if clean_url.endswith('/connect_token'):
        return MockResponse(200, {
            'accessToken': 'mock-pluggy-connect-token-xyz-123456789',
            'expiresAt': '2026-10-02T23:59:59Z'
        })

    # Fallback padrão
    return MockResponse(200, {'sucesso': True, 'mock': True, 'url': url})
