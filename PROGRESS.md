# PROGRESS.md — Cronograma de Evolução, Checklist e Pendências
**MC MINHACONTA SECURITIZADORA S/A — PLATAFORMA OPEN FINANCE & PIX AUTOMÁTICO**

---

## 📌 Visão Resumida do Progresso por Fases

| Fase | Descrição | Status | Progresso |
| :--- | :--- | :--- | :--- |
| **Fase 1** | Auditoria Completa, Limpeza de Arquivos e Memória Contínua | ✅ Concluída | 100% |
| **Fase 2** | Arquitetura de Layout Base, Viewport Fluida e Responsividade | ✅ Concluída | 100% |
| **Fase 3** | Telas Internas e Interface do Usuário (Deduplicação & Roadmap) | ✅ Concluída | 100% |
| **Fase 4** | Testes Automatizados, Segurança HTTP e Deploy em Nuvem | ✅ Concluída | 100% |
| **Fase Pluggy** | Reconciliação e Sincronização com API Pluggy (Fonte Única da Verdade) | ✅ Concluída | 100% |

---

## 📋 Checklist Detalhado por Fases

### Fase 1: Auditoria Completa, Limpeza de Arquivos e Memória Contínua
- [x] **Auditoria Completa do Repositório**:
  - [x] Inventário de todos os 37 arquivos presentes na raiz do repositório.
  - [x] Verificação de dependências em `backend.py`, templates HTML e suíte de testes.
  - [x] Confirmação da camada de mock ativa ([`pluggy_mock.py`](file:///c:/meu-frontend-plugg/pluggy_mock.py)) e proteção contra Directory Traversal.
- [x] **Limpeza de Arquivos Obsoletos e Temporários**:
  - [x] Remoção de scripts temporários de migração/diagnóstico: `classify.py`, `migrate_conexoes.py`, `sync_supabase_real_dates.py`.
  - [x] Remoção de arquivo duplicado legado: `dashboard.html` (mantido `painel.html` com rota servida pelo Flask).
  - [x] Remoção de log diário legado não-estruturado: `RESUMO_DO_DIA_07_OUTUBRO_2026.md`.
- [x] **Setup do Sistema de Controle e Memória Contínua**:
  - [x] Criação/estruturação de [`AGENTS.md`](file:///c:/meu-frontend-plugg/AGENTS.md) com diretrizes de engenharia e regras invioláveis.
  - [x] Criação/estruturação de [`PROGRESS.md`](file:///c:/meu-frontend-plugg/PROGRESS.md) com cronograma dividido em 4 fases e checklist de pendências.
  - [x] Criação/estruturação de [`CHECKPOINT.md`](file:///c:/meu-frontend-plugg/CHECKPOINT.md) com ponto de parada exato e instruções de retomada imediata.
- [x] **Homologação Pós-Limpeza**:
  - [x] Execução da suíte completa de 31 testes automatizados sem nenhuma regressão.

---

### Fase 2: Arquitetura de Layout Base, Viewport Fluida e Responsividade
- [x] **Container Geral e Viewport (100% de Largura Útil)**:
  - [x] Shell estruturado em Flexbox preenchendo a totalidade da tela (`min-h-screen flex w-full relative overflow-x-hidden`).
  - [x] Eliminação de limitadores arbitrários (`max-w-7xl`, `max-w-6xl`) nas telas de dashboards e extratos para evitar espaços vazios em monitores widescreen.
  - [x] Conteúdo principal (`main`) com `flex: 1; min-width: 0; width: 100%; max-width: 100%;`.
- [x] **Sidebar Padronizada no Desktop e Gaveta Mobile**:
  - [x] Largura fixa de 288px (`w-72 flex-shrink-0`) no desktop com fixação lateral (`xl:translate-x-0`).
  - [x] Modo gaveta responsivo (*off-canvas*) com backdrop blur para tablets e smartphones (`xl:hidden`).
- [x] **Prevenção de Overflow Horizontal e Rolagem Dedicada**:
  - [x] Aplicação global de `* { box-sizing: border-box; }` e `html, body { max-width: 100%; overflow-x: hidden; }`.
  - [x] Wrappers dedicados para tabelas de dados com `overflow-x: auto; width: 100%;` e barra de rolagem customizada fina (`custom-scrollbar`).

---

### Fase 3: Telas Internas e Interface do Usuário (Mapeamento de Pendências & Roadmap)

#### 3.1 Painel do Gestor ([`gestor.html`](file:///c:/meu-frontend-plugg/gestor.html) / [`gestor.js`](file:///c:/meu-frontend-plugg/gestor.js))
- [x] **Deduplicação de Clientes no Pix Automático**:
  - [x] Agrupamento de solicitações pelo identificador único (CPF/CNPJ limpo ou chave de nome).
  - [x] Linha consolidada única por cliente (ex: *Maria Djanira Santos da Silva* em 1 linha mestre).
  - [x] Acordeão expansível com subtabela cronológica de tentativas e auditoria.
- [x] **Deduplicação de Clientes no Open Finance**:
  - [x] Agrupamento de conexões múltiplas por cliente (ex: *Célia Maria de Siqueira*, *Raquel da Silva Muniz*).
  - [x] Card mestre único com indicador de conexões e acordeão de contas bancárias.
- [x] **3 Modos de Visualização Alternáveis no Pix Automático**:
  - [x] Modo `Tabela`: Espelho fiel do dashboard corporativo da Pluggy com paginação oficial.
  - [x] Modo `Por Cliente`: Visualização deduplicada com histórico sanfonado.
  - [x] Modo `Cards`: Cartões compactos com faixas de diagnóstico em 1 linha.
- [x] **Solução Definitiva de Cobrança Triplicada & Trava Antiduplicidade**:
  - [x] Diagnóstico e cancelamento dos 2 mandatos excedentes de *Maria Djanira Santos da Silva* (`a2b515ae...` e `471542d8...`), preservando apenas o mandato legítimo (`51622cc2...`).
  - [x] Trava antiduplicidade no backend (`/gerar-token-pix` com HTTP 409) bloqueando criação acidental de contratos duplicados para o mesmo cliente/valor nos últimos 7 dias.
  - [x] Rota oficial de cancelamento no backend (`POST /api/pix-cancelar/<req_id>`) e modal de confirmação de segurança com 1 clique no frontend.
- [x] **Correção Definitiva da Desordenação de Datas (Pix e Open Finance)**:
  - [x] Criação de `converter_para_timestamp_ms` no backend e `obterTimestampSeguro` no frontend, eliminando erros de `NaN` na ordenação.
  - [x] Ordenação estritamente cronológica decrescente da mais recente para a mais antiga em todas as visualizações (Tabela, Por Cliente, Cards e Open Finance).
- [x] **Ambientes Segregados e Limpeza de Erros**:
  - [x] Segmented control com 4 abas isoladas: `Contratos Ativos & Agendados`, `Revogados & Cancelados`, `Tentativas com Erro / Rejeitados` e `Todos`.
  - [x] Botão de ação rápida `Limpar / Ocultar Erros` para eliminar a poluição visual de tentativas rejeitadas na tela.
  - [x] Badges numéricos dinâmicos em tempo real para cada um dos 4 ambientes.
- [x] **Fidelidade Integral ao Painel da Pluggy (Status Real, Parcelas e R$ 0,01)**:
  - [x] Espelhamento fiel do status oficial Pluggy (`SCHEDULED`, `AUTHORIZED`, `PAYMENT_COMPLETED`, `WAITING_PAYER`, `REJECTED`, `EXPIRED`, `CANCELED`).
  - [x] Quantidade real de parcelas (`parcelas_total` / `occurrences`) e cálculo de expiração (`expiresAt`).
  - [x] Suporte ao endpoint nativo `POST /payments/requests/automatic-pix` e validação inicial de teste de R$ 0,01 (`firstPayment`).
- [x] **Exportação Excel (.CSV) Padronizada e Organizada**:
  - [x] Exportação respeitando fielmente os filtros da tela e ambiente ativo.
  - [x] Formato Brasil (ponto e vírgula `;`, BOM UTF-8 `\uFEFF`, decimais com vírgula).
  - [x] Colunas ricas e completas com status oficial Pluggy, IDs, diagnósticos e links.
- [x] **Realocação da Conta Securitizadora & Submenu de Extrato Detalhado de Clientes**:
  - [x] Expurgada a conta bancária da Securitizadora da listagem de conexões de Open Finance (travas por tipo, razão social e CNPJ).
  - [x] Criação da aba e visualização dedicada "Contas Vinculadas (MC)" no Gestor com saldo consolidado e desvinculação com 1 clique.
  - [x] Novo submenu "Extrato Detalhado" sob o acordeão "Securitizadora MC" no menu lateral (sidebar do gestor).
  - [x] Tabela de extrato analítico por cliente com progresso de parcelas (`X/Y pagas`), vigência (`data_inicio` / `data_fim`), adimplência (`Em dia` / `Em atraso`) e método (`Pix Automático` / `Boleto`).
  - [x] Filtros reativos por adimplência, método, busca de texto, paginação e exportação para Excel Brasil (.csv).

#### 3.2 Ambiente Corporativo da Securitizadora ([`securitizadora.html`](file:///c:/meu-frontend-plugg/securitizadora.html) / [`securitizadora.js`](file:///c:/meu-frontend-plugg/securitizadora.js))
- [x] Visualização de saldo consolidado em caixa e contas vinculadas da Securitizadora MC.
- [x] Extrato bancário analítico em tempo real com filtros por tipo (crédito/débito), categoria e busca de contraparte.
- [x] Exportação do extrato bancário corporativo para Excel (.CSV compatível com Windows).
- [x] Modal de conexão de novas contas MC via widget Pluggy Connect v2 com `avoidDuplicates: False` e `updateItem`.
- [x] **Remoção da Conta Antiga Bloqueada & Endpoint de Desvinculação**:
  - [x] Exclusão definitiva dos itens bloqueados do Bradesco Empresas (`75cfdce4...` e `585b5487...`) da Pluggy e marcação como `desvinculado` no Supabase.
  - [x] Remoção do ID chumbado (*hardcoded*) em `obter_contas_securitizadora()` no backend.
  - [x] Criação de rota oficial autenticada no backend (`POST /api/securitizadora/desvincular-conta`).
  - [x] Adição de botão de remoção em cada card e modal de confirmação no frontend (`modal-desvincular-mc`).
  - [x] Estado vazio inteligente (*empty state*) com call-to-action para vincular nova conta bancária (Itaú, BB, Santander, etc.).
- [x] **Harmonização do cabeçalho da Securitizadora**:
  - [x] Alinhar o cabeçalho superior e navegação de retorno com o design system do Portal do Gestor.
  - [x] Ajustar a largura mínima das colunas da tabela de extrato corporativo para evitar compressão em telas compactas.

#### 3.3 Dossiê e Extrato Detalhado do Cliente ([`extratos.html`](file:///c:/meu-frontend-plugg/extratos.html) / [`extratos.js`](file:///c:/meu-frontend-plugg/extratos.js))
- [x] Ficha cadastral completa e dados de identidade Open Finance (CPF/CNPJ, renda declarada, contatos e filiação).
- [x] Cards de contas correntes, poupanças e limites disponíveis.
- [x] Extrato bancário de transações com busca textual e filtros de créditos/débitos.
- [x] Modo de impressão oficial configurado com `@media print` para auditoria e mesa de crédito.
- [x] **Ajuste de Colunas e Responsividade no Extrato Analítico**:
  - [x] Larguras mínimas seguras e `whitespace-nowrap` nas colunas numéricas de transações do cliente.

#### 3.4 Telas de Entrada e Autenticação ([`cliente.html`](file:///c:/meu-frontend-plugg/cliente.html), [`gestor-login.html`](file:///c:/meu-frontend-plugg/gestor-login.html), [`index.html`](file:///c:/meu-frontend-plugg/index.html))
- [x] `cliente.html`: Formulário de conexão bancária, busca de instituições COMPE, suporte a CPF e CNPJ e leitura de `item_id` para reconexão.
- [x] `gestor-login.html`: Autenticação HMAC com PBKDF2, visual glassmorphism e feedback imediato de erro.
- [x] `index.html`: Portal de direcionamento rápido com botões de ação para o gestor e para simulação do cliente.

---

### Fase 4: Testes Automatizados, Segurança & Infraestrutura
- [x] **Suíte de Testes do Backend (`test_backend.py`)**:
  - [x] 34 de 34 testes automatizados executando e aprovados com 100% de sucesso.
  - [x] Testes de segurança contra Directory Traversal (bloqueio de `/.env`, `/backend.py`, `/schema.sql`, `/.git` com HTTP 403).
  - [x] Testes de autenticação e proteção de rotas com token Bearer HMAC.
  - [x] Testes de validação de CPF/CNPJ em `/gerar-token-pix`.
  - [x] Teste de cancelamento oficial com token HMAC (`/api/pix-cancelar/<id>`).
  - [x] Teste de desvinculação de conta corporativa com token HMAC (`/api/securitizadora/desvincular-conta`).
  - [x] Teste de cancelamento oficial com token HMAC (`/api/pix-cancelar/<id>`).
  - [x] Teste de ordenação cronológica determinística decrescente.
  - [x] Testes de integridade de conciliação analítica e KPIs da Pluggy.
- [x] **Geração de Laudos Técnicos em PDF**:
  - [x] Gerador de laudo executivo ReportLab [`gerar_auditoria_tecnica_pdf.py`](file:///c:/meu-frontend-plugg/gerar_auditoria_tecnica_pdf.py).
  - [x] Documentos PDF compilados e sincronizados no repositório.
- [x] **Deploy Contínuo e Sincronização em Nuvem**:
  - [x] Repositório oficial no GitHub: `https://github.com/Muolis/integracao-pluggy-frontend.git` (Branch `main`).
  - [x] Render Cloud configurado com deploy automático dos serviços `motor-openfinance` e `vitrine-openfinance`.

---

### [Fase Pluggy]: Reconciliação e Sincronização com API Pluggy (Fonte Única da Verdade)
- [x] **1. Auditoria do Fluxo de Ingestão e Payload Bruto (Pluggy)**:
  - [x] Mapeamento e inspeção de chamadas aos endpoints `/payments/requests`, `/payments/intents`, `/transactions`, `/items` e webhooks.
  - [x] Inspeção dos JSONs brutos (*raw payload*) retornados pela Pluggy para verificar todos os campos nativos.
  - [x] Criação de matriz de mapeamento De/Para (Schema Mapping): Pluggy API ➔ Banco Supabase ➔ Frontend.
- [x] **2. Correção de Campos Ausentes (Início, Término e Prazos)**:
  - [x] Mapeamento e persistência explícita de `data_inicio` (`startDate`), `data_fim` / `expiresAt` e `periodicidade` (`interval`).
  - [x] Exibição na interface da data da 1ª cobrança / autorização, data final prevista e periodicidade.
  - [x] Resgate de status reais, IDs da transação/consentimento no banco de origem e comprovantes vazios (`null`/`undefined`).
- [x] **3. Eliminação de Dados Fantasmas e Duplicidades (Parcelas a Mais)**:
  - [x] Identificação da causa raiz de parcelas excedentes/infladas (loops artificiais 1..12 hardcoded, sync sem idempotência, filtros de status).
  - [x] Implementação de `UPSERT` rigoroso e idempotente no banco local com base no `id` único da Pluggy (`externalId`).
- [x] **4. Script de Higienização (Data Cleanup) e Validação**:
  - [x] Criação de rotina/script de saneamento para expurgar parcelas fantasmas e registros duplicados gerados nos syncs anteriores ([`higienizar_dados_pluggy.py`](file:///c:/meu-frontend-plugg/higienizar_dados_pluggy.py)).
  - [x] Teste de paridade e relatório Diff comparando um cliente específico ponta a ponta (Pluggy vs. Local: 100% PAR comprovado).
