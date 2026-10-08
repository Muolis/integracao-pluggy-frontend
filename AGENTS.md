# AGENTS.md — Diretrizes de Engenharia e Memória do Agente
**MC MINHACONTA SECURITIZADORA S/A — PLATAFORMA OPEN FINANCE & PIX AUTOMÁTICO**

---

> ⚠️ **INSTRUÇÃO OBRIGATÓRIA DE INÍCIO DE SESSÃO**  
> Antes de executar qualquer ação, comando, análise ou alteração de código, você **DEVE OBRIGATORIAMENTE LER**:
> 1. Este arquivo: [`AGENTS.md`](file:///c:/meu-frontend-plugg/AGENTS.md)
> 2. O cronograma e status atual: [`PROGRESS.md`](file:///c:/meu-frontend-plugg/PROGRESS.md)
> 3. O ponto de parada da última sessão: [`CHECKPOINT.md`](file:///c:/meu-frontend-plugg/CHECKPOINT.md)

---

## 1. Stack Tecnológico do Projeto

* **Backend / API (BFF - Backend for Frontend):**
  - **Linguagem**: Python 3.11+
  - **Framework Web**: Flask com CORS e autenticação HMAC/JWT
  - **Ambiente Virtual**: `.venv` local (`.venv\Scripts\python.exe`)
  - **Hospedagem em Nuvem**: Render Cloud (`motor-openfinance`)
  - **Banco de Dados**: Supabase (PostgreSQL) com persistência de conexões, tokens e transações
  - **Integração Externa**: Pluggy API v2 (Connectors, Open Finance Consent/Accounts/Transactions, Payments Requests/Intents)
* **Frontend / Interface do Usuário:**
  - **Linguagens**: HTML5 Semântico, CSS3 Moderno e Vanilla JavaScript (ES6+ modular e desacoplado)
  - **Estilização**: Tailwind CSS (via CDN) + Estilos utilitários específicos nos arquivos HTML
  - **Fontes & Ícones**: Google Fonts (Inter) e Font Awesome 6.4.0
  - **Hospedagem em Nuvem**: Render Cloud (`vitrine-openfinance`)
* **Testes & Auditoria:**
  - **Suíte de Testes Automatizados**: [`test_backend.py`](file:///c:/meu-frontend-plugg/test_backend.py) com 31 testes unitários e de integração
  - **Gerador de Relatórios em PDF**: [`gerar_auditoria_tecnica_pdf.py`](file:///c:/meu-frontend-plugg/gerar_auditoria_tecnica_pdf.py) (ReportLab)

---

## 2. Regras Rígidas e Invioláveis de Codificação

1. **Intocabilidade da Lógica de Negócio e APIs**:
   - **NUNCA** altere a lógica de cálculo das regras do Open Finance, parâmetros de integração da Pluggy ou rotinas do Pix Automático sem solicitação explícita do usuário.
   - Variáveis críticas (`payment_request_id`, `item_id`, `status_classe`, `liberacao_operacional`, endpoints do `backend.py`) devem permanecer 100% compatíveis.
2. **Ambiente Python e Testes**:
   - Sempre utilize o interpretador do ambiente virtual: `.venv\Scripts\python.exe`.
   - Após qualquer alteração significativa no backend ou nas estruturas de template servidas pelo Flask, execute obrigatoriamente:
     ```powershell
     .venv\Scripts\python.exe test_backend.py
     ```
   - Nenhum deploy ou entrega deve ser considerada concluída sem **100% de aprovação nos 31 testes**.
3. **Padrão de Layout e Viewport (Shell Global)**:
   - **Zero Espaços Vazios Arbitrários**: A área de conteúdo principal (`main` ou wrapper) deve ocupar **100% da largura útil restante da tela** (`flex: 1; min-width: 0; width: 100%; max-width: 100%;`).
   - **Não utilize `max-w-7xl` ou `max-w-6xl`** em páginas de dashboard que exibem tabelas e métricas corporativas, pois geram margens vazias gigantes em monitores widescreen.
   - **Sidebar Padronizada**: Largura fixa de `288px` (`w-72 flex-shrink-0`), fixa no desktop (`xl:translate-x-0`) e em modo gaveta (*off-canvas*) responsivo abaixo de 1280px (`xl:hidden`).
   - **Prevenção de Transbordamento Horizontal**: Todo template deve ter `* { box-sizing: border-box; }` e `html, body { max-width: 100%; overflow-x: hidden; }`.
   - **Tabelas com Rolagem Dedicada**: Toda tabela de dados deve estar contida em um wrapper com `overflow-x: auto w-full custom-scrollbar`, garantindo que apenas os dados rolem internamente sem desconfigurar a viewport da página.
4. **Codificação e Acentuação**:
   - Todos os arquivos devem ser salvos rigorosamente em **UTF-8**.
   - Para exportações `.csv` voltadas ao Excel no Brasil, utilize delimitador `;` e prefixo BOM UTF-8 (`\uFEFF`).
5. **Agrupamento e Deduplicação de Clientes**:
   - As listagens principais (tabelas e cards) devem exibir cada cliente uma única vez, agrupando múltiplas conexões/solicitações pelo identificador do cliente (CPF/CNPJ limpo ou chave de nome).
   - O detalhamento de cada tentativa ou contrato individual deve ser acessível via componente expansível (acordeão, modal ou gaveta).
6. **Cálculo Dinâmico de Parcelas Pix e Validação Inicial (R$ 0,01)**:
   - A quantidade de parcelas no Pix Automático não deve ser fixa em 12, devendo ser calculada dinamicamente pelo intervalo entre `data_inicio` e `data_fim` ou quantidade informada.
   - O fluxo do Pix Automático deve suportar cobrança inicial de teste (R$ 0,01) para verificação de adesão/autorização antes do débito das parcelas do contrato.
7. **Comunicação com o Usuário**:
   - Mantenha respostas concisas, estruturadas e com links clicáveis no formato `file:///c:/meu-frontend-plugg/...`.
   - Sempre reporte o resultado dos testes automatizados e o status real dos arquivos modificados.
