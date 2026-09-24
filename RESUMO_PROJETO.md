# MC Minha Conta - Resumo do Projeto e Status Oficial

> **Última Atualização:** 24/09/2026  
> **Objetivo:** Registro executivo e técnico detalhado de todas as implementações, correções arquiteturais, auditoria de segurança e instruções operacionais para continuidade.

---

## 1. Links Oficiais do Projeto em Produção

| Serviço | URL Oficial | Descrição |
|---|---|---|
| **Portal do Gestor (Login)** | [https://vitrine-openfinance.onrender.com/gestor-login.html](https://vitrine-openfinance.onrender.com/gestor-login.html) | Acesso administrativo para gerar links, consultar extratos e monitorar contratos |
| **Painel de Gestão** | [https://vitrine-openfinance.onrender.com/gestor.html](https://vitrine-openfinance.onrender.com/gestor.html) | Dashboard completo com abas segregadas de Open Finance e Pix Automático |
| **Extrato Bancário Detalhado** | [https://vitrine-openfinance.onrender.com/extratos.html](https://vitrine-openfinance.onrender.com/extratos.html) | Página dedicada em tela cheia com extrato analítico e movimentações |
| **Tela do Cliente** | [https://vitrine-openfinance.onrender.com/cliente.html](https://vitrine-openfinance.onrender.com/cliente.html) | Interface acessada pelo cliente para conectar via Pluggy Connect ou autorizar Pix |
| **Backend API (Render)** | [https://motor-openfinance.onrender.com](https://motor-openfinance.onrender.com) | API Flask com autenticação HMAC, integração Pluggy e Supabase |
| **Repositório GitHub** | [https://github.com/Muolis/integracao-pluggy-frontend.git](https://github.com/Muolis/integracao-pluggy-frontend.git) | Código-fonte oficial sincronizado na branch `main` |
| **Banco de Dados Supabase** | `https://hispfcvhqybddumgvldg.supabase.co` | Tabela `conexoes` com persistência de autorizações |

---

## 2. Credenciais de Acesso ao Portal do Gestor

O sistema utiliza sessões assinadas com tokens criptográficos via **HMAC-SHA256**:

| Usuário | Senha Padrão | Perfil | Permissões |
|---|---|---|---|
| `admin` | `securitizadora2026` | Administrador Geral | Acesso total, geração de links e auditoria |
| `julianemc` | `MC@2026` | Gestora Operacional | Operação diária e consulta de extratos |
| `gabriel` | `MC@2026` | Gestor Operacional | Operação diária e consulta de extratos |

---

## 3. Resumo das Correções Críticas e Melhorias (24/09/2026)

### 3.1. Correção das Datas Reais dos Clientes Antigos no Supabase
* **Ocorrência:** Para forçar o reaparecimento dos clientes antigos na listagem limitada anterior, havia sido atribuída provisoriamente a data do dia `24/09/2026 16:28`.
* **Solução:** Consultamos a API da Pluggy (`GET /items/{id}`) e restauramos as **datas reais de autorização** de cada cliente no Supabase:
  * **Juliane** (`InfinitePay`): Conectado originalmente em **16/09/2026, 14:12**
  * **Maria José** (`Bradesco`): Conectado originalmente em **17/09/2026, 16:14**
  * **Gabriel** (`Santander`): Conectado originalmente em **18/09/2026, 13:46**
  * **Enilda** (`Bradesco`): Conectado originalmente em **21/09/2026, 13:11**

### 3.2. Solução Definitiva do Desaparecimento da Aba Open Finance (Segregação de Cotas)
* **Causa Raiz:** A sincronização dos 179 contratos de Pix Automático na tabela de conexões provocou um afogamento: a query anterior executava `order('data_conexao', desc=True).limit(100)`, preenchendo as 100 vagas exclusivamente com contratos de Pix e truncando as conexões de Open Finance.
* **Solução Arquitetural:** No `backend.py` (`listar_conexoes`), dividimos a consulta em duas cotas isoladas:
  ```python
  # 1. Busca exclusiva de Open Finance (garantia permanente)
  res_of = supabase.table('conexoes').select('*').is_('payment_intent_id', 'null').order('data_conexao', desc=True).limit(100).execute()
  
  # 2. Busca exclusiva de Pix Automático
  res_pix = supabase.table('conexoes').select('*').not_.is_('payment_intent_id', 'null').order('data_conexao', desc=True).limit(250).execute()
  ```
  Isso garante que, independentemente do volume de contratos de Pix, o Open Finance **nunca mais desaparecerá**.

### 3.3. Correção de Gravação no Supabase (Eliminação do Erro PGRST204)
* **Causa Raiz:** A função legada `salvar_conexao` tentava gravar a coluna `'tipo'` no Supabase (`registro['tipo'] = 'open_finance'`). Como essa coluna não existe na tabela `conexoes`, o Supabase rejeitava com HTTP 500 (`PGRST204`). Por essa razão, clientes que autorizavam no celular viam tela de sucesso, mas não eram salvos no banco.
* **Solução:** O payload de inserção foi ajustado para enviar apenas colunas válidas (`cliente`, `item_id`, `payment_intent_id`), garantindo `item_id` não-nulo.

### 3.4. Webhook Global da Pluggy para Redundância Total
* Registrado webhook global na Pluggy:
  * **URL:** `https://motor-openfinance.onrender.com/api/webhook/pluggy`
  * **Evento:** `all` (captura `item/created`, `item/updated`, `payment_intent/updated`)
  * **Comportamento:** Quando um cliente conclui a conexão, a Pluggy notifica o backend de forma assíncrona. O backend busca os dados de identidade (`/identity`) e registra o cliente no Supabase, garantindo que a conexão seja salva mesmo que o usuário feche a aba antes do redirecionamento.

### 3.5. Espelho Completo do Painel da Pluggy para Pix Automático
* Criado endpoint `/api/pix-intents` no `backend.py`:
  * Paginação automática para varrer todos os 179 contratos cadastrados na Pluggy.
  * KPIs em tempo real: Total de Contratos, Ativos, Pendentes, Rejeitados e Volume Mensal.
  * Resolução oficial do banco emissor via código COMPE, logotipo e valor fixo (`fixedAmount`).
  * Modal para inspeção técnica do JSON bruto diretamente no painel.

### 3.6. Exibição do Extrato Bancário Real no Painel
* **No `gestor.html`:**
  * Exibição do **Nome Completo do Titular** e **CPF** oficial retornado pelo banco.
  * Agência, conta corrente/poupança e saldo disponível formatado.
  * Extrato cronológico com identificação de créditos (+ em azul) e débitos (- em escuro).
  * Botão **"Tela Cheia"** em cada card que abre diretamente a página `extratos.html?item=...&cliente=...`.
* **Tratamento Amigável para Conexões Expiradas:**
  * Clientes com autorização revogada no app do banco (ex: Enilda no Bradesco) recebem um card explicativo com orientações claras para reenvio do link.

---

## 4. Estado Atual dos Clientes no Banco de Dados (Supabase)

| ID | Cliente | Tipo | Status na Pluggy | Detalhes Bancários |
|---|---|---|---|---|
| 16 | `juliane` | **Open Finance** | `UPDATED` (Ativa) | InfinitePay (R$ 0,08 saldo, 24 transações) |
| 17 | `maria-jose-da-conceicao-santos` | **Open Finance** | `UPDATED` (Ativa) | Bradesco (R$ 396,43 corrente, R$ 0,00 poupança) |
| 18 | `gabriel` | **Open Finance** | `UPDATED` (Ativa) | Santander (R$ 1,06 corrente, R$ 195.927,93 cartão, 389 transações) |
| 24 | `enilda-sabino-de-vasconcelos` | **Open Finance** | `LOGIN_ERROR` (Revogada) | Bradesco (autorização expirada/revogada no banco) |
| 27 a 205 | 179 Contratos Pix | **Pix Automático** | Diversos | Espelhados diretamente da Pluggy via API |

---

## 5. Validação e Testes Automatizados

A suíte completa de testes unitários e de integração em `test_backend.py` foi executada:

* **Teste 1 [/health]:** Sucesso (Backend, Pluggy e Supabase conectados).
* **Teste 2 e 3 [/api/login]:** Sucesso (rejeição de senhas inválidas e emissão de token HMAC).
* **Teste 4 e 5 [Segurança e Auth]:** Sucesso (bloqueio 401 sem token e liberação com token válido).
* **Teste 6 [Arquivos Estáticos]:** Sucesso (HTMLs, `config.js` e assets servidos).
* **Teste 7 [Security Headers]:** Sucesso (`X-Content-Type-Options`, `X-Frame-Options`).
* **Teste 8 [/listar-bancos]:** Sucesso (124 bancos com código COMPE e logos).
* **Teste 9 [/listar-conexoes]:** Sucesso (segregação estrita entre Open Finance e Pix).
* **Teste 10 e 11 [Validação de Payloads]:** Sucesso (sanitização de CPF e integridade).
* **Teste 12 [Cálculo Analítico Pix]:** Sucesso (cronograma de parcelas e quitação).
* **Teste 13 [/api/pix-intents]:** Sucesso (179 contratos Pluggy espelhados com KPIs).
* **Teste 14 [/api/webhook/pluggy]:** Sucesso (recebimento assíncrono de eventos com HTTP 200).

> **Resultado Final:** 14/14 testes passaram com 100% de sucesso.

---

## 6. Como Retomar Amanhã

1. **Repositório Local:**
   * Caminho: `C:\meu-frontend-plugg`.
   * Para rodar os testes: `C:\meu-frontend-plugg\.venv\Scripts\python.exe test_backend.py`.

2. **Ativação dos Novos Commits no Render:**
   * Como o Render está configurado com deploy manual, acesse [dashboard.render.com](https://dashboard.render.com):
     * No serviço **motor-openfinance** (Backend): Clique em **Manual Deploy** ➔ **Deploy latest commit**.
     * No serviço **vitrine-openfinance** (Frontend): Clique em **Manual Deploy** ➔ **Clear build cache & deploy**.
   * Os últimos commits já estão disponíveis no GitHub:
     * `6bce195`: Segregação arquitetural de Open Finance e Pix no backend.
     * `9184224`: Exibição do extrato real completo, dados de titularidade/CPF e botão para `extratos.html`.

3. **Acesso Online para Teste:**
   * Acesse: [https://vitrine-openfinance.onrender.com/gestor-login.html](https://vitrine-openfinance.onrender.com/gestor-login.html).
   * Usuário: `admin` | Senha: `securitizadora2026`.
   * Pressione **`Ctrl + F5`** para limpar o cache do navegador.
   * Ambas as abas carregarão com precisão: **Open Finance** com os 4 clientes e datas reais históricas, e **Pix Automático** com todos os contratos da Pluggy.
