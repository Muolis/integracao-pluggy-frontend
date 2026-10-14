# AGENTS.md — Diretrizes de Engenharia e Memória do Agente
**MC MINHACONTA SECURITIZADORA S/A — PLATAFORMA OPEN FINANCE & PIX AUTOMÁTICO**

---

> ⚠️ **INSTRUÇÃO OBRIGATÓRIA DE INÍCIO DE SESSÃO**  
> Antes de executar qualquer ação, comando, análise ou alteração de código, você **DEVE OBRIGATORIAMENTE LER**:
> 1. Este arquivo: [`AGENTS.md`](file:///c:/meu-frontend-plugg/AGENTS.md)
> 2. O cronograma e status atual: [`PROGRESS.md`](file:///c:/meu-frontend-plugg/PROGRESS.md)
> 3. O ponto de parada da última sessão: [`CHECKPOINT.md`](file:///c:/meu-frontend-plugg/CHECKPOINT.md)
>
> **Regra de Continuidade**: Nunca inicie uma tarefa sem verificar o último ponto de parada em `CHECKPOINT.md` e sem atualizar `PROGRESS.md` ao final de cada entrega.

---

## 1. Visão Geral e Contexto Corporativo

A **MC MINHACONTA SECURITIZADORA S/A** (CNPJ: `62.455.954/0001-46`) opera uma plataforma de securitização, análise de crédito, Open Finance e cobrança recorrente automatizada via **Pix Automático (VRP - Variable Recurring Payments / ITP - Iniciador de Transação de Pagamentos)** regulamentada pelo Banco Central do Brasil.

O sistema integra-se à API Pluggy v2 e utiliza infraestrutura em nuvem no Render Cloud e banco de dados gerenciado Supabase (PostgreSQL).

---

## 2. Stack Tecnológico do Projeto

* **Backend / API (BFF - Backend for Frontend):**
  - **Linguagem**: Python 3.11+
  - **Framework Web**: Flask com CORS, cabeçalhos de segurança HTTP e tratamento estrito de Directory Traversal
  - **Autenticação**: Tokens de sessão com assinatura criptográfica HMAC-SHA256 e senhas em hash PBKDF2
  - **Ambiente Virtual**: `.venv` local (`.venv\Scripts\python.exe`)
  - **Hospedagem em Nuvem**: Render Cloud — Serviço Web [`motor-openfinance`](https://motor-openfinance.onrender.com)
  - **Banco de Dados**: Supabase (PostgreSQL) com persistência de conexões, tokens, sessões e transações
  - **Integração Externa**: Pluggy API v2 (Connectors, Open Finance Consent, Accounts, Transactions, Payments Requests/Intents)
  - **Camada de Mock/Fallback**: [`pluggy_mock.py`](file:///c:/meu-frontend-plugg/pluggy_mock.py)

* **Frontend / Interface do Usuário:**
  - **Linguagens**: HTML5 Semântico, CSS3 Moderno e Vanilla JavaScript (ES6+ modular, desacoplado e sem frameworks pesados)
  - **Módulos JS**:
    * [`config.js`](file:///c:/meu-frontend-plugg/config.js): Configurações globais de endpoints, autenticação e utilitários
    * [`gestor.js`](file:///c:/meu-frontend-plugg/gestor.js): Lógica do Portal do Gestor, KPIs, agrupamento por cliente e conciliação
    * [`securitizadora.js`](file:///c:/meu-frontend-plugg/securitizadora.js): Lógica da conta corporativa PJ, extrato em tempo real e conexão Pluggy
    * [`extratos.js`](file:///c:/meu-frontend-plugg/extratos.js): Dossiê cadastral, saldos bancários e extratos analíticos
  - **Telas Principais**:
    * [`gestor.html`](file:///c:/meu-frontend-plugg/gestor.html): Painel de Gestão Integrada (Open Finance + Pix Automático)
    * [`securitizadora.html`](file:///c:/meu-frontend-plugg/securitizadora.html): Painel Corporativo da Securitizadora (Bradesco PJ)
    * [`extratos.html`](file:///c:/meu-frontend-plugg/extratos.html): Dossiê e Extrato Detalhado do Cliente
    * [`cliente.html`](file:///c:/meu-frontend-plugg/cliente.html): Portal do Cliente (Consentimento e Conexão Bancária)
    * [`gestor-login.html`](file:///c:/meu-frontend-plugg/gestor-login.html): Tela de Autenticação do Gestor
    * [`index.html`](file:///c:/meu-frontend-plugg/index.html): Portal de Entrada e Redirecionamento
    * [`painel.html`](file:///c:/meu-frontend-plugg/painel.html): Redirecionador legado para `gestor.html`
  - **Estilização**: Tailwind CSS (via CDN) + Estilos utilitários específicos nos arquivos HTML
  - **Fontes & Ícones**: Google Fonts (Inter) e Font Awesome 6.4.0
  - **Hospedagem em Nuvem**: Render Cloud — Serviço Estático [`vitrine-openfinance`](https://vitrine-openfinance.onrender.com)

* **Testes & Auditoria Técnica:**
  - **Suíte de Testes Automatizados**: [`test_backend.py`](file:///c:/meu-frontend-plugg/test_backend.py) com 34 testes unitários e de integração (100% de cobertura e aprovação)
  - **Geradores de Laudos & Dossiês PDF**:
    * [`gerar_auditoria_tecnica_pdf.py`](file:///c:/meu-frontend-plugg/gerar_auditoria_tecnica_pdf.py) -> [`AUDITORIA_TECNICA_ULTIMAS_ATUALIZACOES_MC.pdf`](file:///c:/meu-frontend-plugg/AUDITORIA_TECNICA_ULTIMAS_ATUALIZACOES_MC.pdf)
    * [`gerar_documentacao_pdf.py`](file:///c:/meu-frontend-plugg/gerar_documentacao_pdf.py) -> [`Documentacao_Tecnica_Confiabilidade_MC.pdf`](file:///c:/meu-frontend-plugg/Documentacao_Tecnica_Confiabilidade_MC.pdf)
    * [`gerar_pdf_diagnostico.py`](file:///c:/meu-frontend-plugg/gerar_pdf_diagnostico.py) -> [`LAUDO_TECNICO_DIAGNOSTICO_PLUGGY_MOCK.pdf`](file:///c:/meu-frontend-plugg/LAUDO_TECNICO_DIAGNOSTICO_PLUGGY_MOCK.pdf)
    * [`gerar_pdf_uma_pagina.py`](file:///c:/meu-frontend-plugg/gerar_pdf_uma_pagina.py) -> [`Guia_Termos_Tecnicos_Dossie_MC.pdf`](file:///c:/meu-frontend-plugg/Guia_Termos_Tecnicos_Dossie_MC.pdf)

---

## 3. Regras Rígidas e Invioláveis de Codificação

1. **Intocabilidade da Lógica de Negócio e APIs**:
   - **NUNCA** altere a lógica de cálculo das regras do Open Finance, parâmetros de integração da Pluggy ou rotinas do Pix Automático sem solicitação explícita do usuário.
   - Variáveis críticas (`payment_request_id`, `item_id`, `status_classe`, `liberacao_operacional`, endpoints do `backend.py`) devem permanecer 100% compatíveis.
   - Preservar sempre a regra anti-calote: status de liberação operacional somente com liquidação real confirmada (`COMPLETED` / `PAYMENT_COMPLETED`).

2. **Ambiente Python e Execução Obrigatória de Testes**:
   - Sempre utilize o interpretador do ambiente virtual: `.venv\Scripts\python.exe`.
   - Após qualquer alteração significativa no backend, endpoints ou nas estruturas de template servidas pelo Flask, execute obrigatoriamente:
     ```powershell
     .venv\Scripts\python.exe test_backend.py
     ```
   - Nenhum deploy, commit ou entrega deve ser considerada concluída sem **100% de aprovação nos 34 testes automatizados**.

3. **Padrão de Layout e Viewport Global (Shell da Plataforma)**:
   - **Zero Espaços Vazios Arbitrários**: A área de conteúdo principal (`main` ou wrapper) deve ocupar **100% da largura útil restante da tela** (`flex: 1; min-width: 0; width: 100%; max-width: 100%;`).
   - **Proibição de `max-w-7xl` ou `max-w-6xl`** em páginas de dashboard que exibem tabelas e métricas corporativas (`gestor.html`, `securitizadora.html`, `extratos.html`), pois geram margens vazias gigantes em monitores widescreen e televisores corporativos.
   - **Sidebar Padronizada**: Largura fixa de `288px` (`w-72 flex-shrink-0`), fixa no desktop (`xl:translate-x-0`) e em modo gaveta (*off-canvas*) responsivo abaixo de 1280px (`xl:hidden`).
   - **Prevenção de Transbordamento Horizontal**: Todo template deve ter rigorosamente:
     ```css
     * { box-sizing: border-box; }
     html, body { max-width: 100%; overflow-x: hidden; }
     ```
   - **Tabelas com Rolagem Dedicada**: Toda tabela de dados corporativos deve estar contida em um wrapper com `overflow-x: auto w-full custom-scrollbar`, garantindo que apenas os dados rolem internamente sem desconfigurar a viewport da página.

4. **Codificação, Acentuação e Exportações**:
   - Todos os arquivos de código, templates e documentação devem ser salvos rigorosamente em **UTF-8**.
   - Para exportações `.csv` voltadas ao Excel no Brasil, utilize delimitador `;` e prefixo BOM UTF-8 (`\uFEFF`), garantindo exibição perfeita de acentos e valores monetários.

5. **Agrupamento e Deduplicação de Clientes**:
   - As listagens principais (tabelas e cards) devem exibir cada cliente uma única vez, agrupando múltiplas conexões/solicitações pelo identificador do cliente (CPF/CNPJ limpo ou chave de nome).
   - O detalhamento de cada tentativa ou contrato individual deve ser acessível via componente expansível (acordeão, modal ou subtabela).

6. **Cálculo Dinâmico de Parcelas Pix e Validação Inicial (R$ 0,01)**:
   - A quantidade de parcelas no Pix Automático não deve ser fixa em 12, devendo ser calculada dinamicamente pelo intervalo entre `data_inicio` e `data_fim` ou quantidade informada pelo operador.
   - O fluxo do Pix Automático deve suportar cobrança inicial de teste (R$ 0,01) para verificação de adesão/autorização (`CONF DEBITO` / `firstPayment`) antes do agendamento das parcelas reais.

7. **Comunicação com o Usuário e Manutenção de Memória**:
   - Mantenha respostas concisas, estruturadas e com links clicáveis no formato `file:///c:/meu-frontend-plugg/...`.
   - Sempre reporte o resultado dos testes automatizados e o status real dos arquivos modificados.
   - Atualize os arquivos [`PROGRESS.md`](file:///c:/meu-frontend-plugg/PROGRESS.md) e [`CHECKPOINT.md`](file:///c:/meu-frontend-plugg/CHECKPOINT.md) ao término de cada tarefa para manter o histórico vivo do projeto.

8. **Gestão e Desvinculação de Contas Corporativas da Securitizadora**:
   - As contas corporativas PJ da Securitizadora devem ser carregadas dinamicamente a partir das conexões ativas no banco de dados (`tipo = 'securitizadora'`). É estritamente proibido fixar (*hardcode*) `item_id` ou contas em código.
   - O sistema deve preservar a rota autenticada (`POST /api/securitizadora/desvincular-conta`) para exclusão/desvinculação com 1 clique, integrando a revogação no conector Pluggy (`DELETE /items/{id}`) e saneamento no Supabase (`status = 'desvinculado'`).
   - Se nenhuma conta estiver conectada, os endpoints e interfaces devem manter comportamento resiliente (retornando lista vazia com HTTP 200 e empty state no frontend, sem erros de console).
