# PROGRESS.md — Cronograma de Evolução, Checklist e Pendências
**MC MINHACONTA SECURITIZADORA S/A — PLATAFORMA OPEN FINANCE & PIX AUTOMÁTICO**

---

## 📌 Visão Resumida do Progresso por Fases

| Fase | Descrição | Status | Progresso |
| :--- | :--- | :--- | :--- |
| **Fase 1** | Auditoria Completa, Limpeza de Arquivos e Memória Contínua | ✅ Concluída | 100% |
| **Fase 2** | Arquitetura de Layout Base, Viewport Fluida e Responsividade | ✅ Concluída | 100% |
| **Fase 3** | Telas Internas e Interface do Usuário (Deduplicação & Roadmap) | 🟡 Em Andamento | 75% |
| **Fase 4** | Testes Automatizados, Segurança HTTP e Deploy em Nuvem | ✅ Concluída | 100% |

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
- [x] **Ambientes Segregados**:
  - [x] Segmented control com filtro por `Contratos Ativos & Em Andamento`, `Revogados & Cancelados` e `Todos`.
- [x] **Cálculo Dinâmico de Parcelas Pix e Validação Inicial (R$ 0,01)**:
  - [x] Cálculo dinâmico baseado no intervalo de datas ou campo numérico de parcelas.
  - [x] Suporte à taxa de adesão de R$ 0,01 (`CONF DEBITO` / `firstPayment`).
- [x] **Exportação de Relatórios para Microsoft Excel (.CSV)**:
  - [x] Exportação de clientes Open Finance com delimitador `;` e BOM UTF-8 (`\uFEFF`).
  - [x] Exportação de contratos de Pix Automático com histórico e links.
- [ ] ⏳ **PENDÊNCIA DE LAYOUT**: Otimização do container de listagem de clientes (`#lista-clientes`):
  - [ ] Remover ou flexibilizar o limitador de altura fixa (`max-h-[620px]`) que cria barra de rolagem interna dupla/aninhada quando o usuário rola a página no desktop.
  - [ ] Ajustar o comportamento da coluna esquerda (Gerador de Acesso) e da coluna direita (Histórico de Clientes) para sincronizar altura em telas ultrawide.
- [ ] ⏳ **PENDÊNCIA DE LAYOUT**: Refinar a responsividade em telas intermediárias (laptops 1366x768 e tablets verticais):
  - [ ] Ajustar quebra dos filtros rápidos da tabela oficial da Pluggy para evitar sobreposição de elementos em resoluções menores.

#### 3.2 Ambiente Corporativo da Securitizadora ([`securitizadora.html`](file:///c:/meu-frontend-plugg/securitizadora.html) / [`securitizadora.js`](file:///c:/meu-frontend-plugg/securitizadora.js))
- [x] Visualização de saldo consolidado em caixa (R$ 2.815,47) e contas vinculadas da Securitizadora MC no Bradesco.
- [x] Extrato bancário analítico em tempo real com filtros por tipo (crédito/débito), categoria e busca de contraparte.
- [x] Exportação do extrato bancário corporativo para Excel (.CSV compatível com Windows).
- [x] Modal de conexão de novas contas MC via widget Pluggy Connect v2 com `avoidDuplicates: False` e `updateItem`.
- [ ] ⏳ **PENDÊNCIA DE LAYOUT**: Harmonização do cabeçalho da Securitizadora:
  - [ ] Alinhar o cabeçalho superior e navegação de retorno com o design system do Portal do Gestor.
  - [ ] Ajustar a largura mínima das colunas da tabela de extrato corporativo para evitar que descrições longas apertem a coluna de valores em monitores pequenos.

#### 3.3 Dossiê e Extrato Detalhado do Cliente ([`extratos.html`](file:///c:/meu-frontend-plugg/extratos.html) / [`extratos.js`](file:///c:/meu-frontend-plugg/extratos.js))
- [x] Ficha cadastral completa e dados de identidade Open Finance (CPF/CNPJ, renda declarada, contatos e filiação).
- [x] Cards de contas correntes, poupanças e limites disponíveis.
- [x] Extrato bancário de transações com busca textual e filtros de créditos/débitos.
- [x] Modo de impressão oficial configurado com `@media print` para auditoria e mesa de crédito.
- [ ] ⏳ **PENDÊNCIA DE LAYOUT**: Grade de informações cadastrais em monitores widescreen:
  - [ ] Ajustar a distribuição das caixas de dados de identidade para manter espaçamento uniforme em resoluções 2K/4K.
  - [ ] Revisar badges de status de sincronização no topo para não quebrar linha de forma assimétrica.

#### 3.4 Telas de Entrada e Autenticação ([`cliente.html`](file:///c:/meu-frontend-plugg/cliente.html), [`gestor-login.html`](file:///c:/meu-frontend-plugg/gestor-login.html), [`index.html`](file:///c:/meu-frontend-plugg/index.html))
- [x] `cliente.html`: Formulário de conexão bancária, busca de instituições COMPE, suporte a CPF e CNPJ e leitura de `item_id` para reconexão.
- [x] `gestor-login.html`: Autenticação HMAC com PBKDF2, visual glassmorphism e feedback imediato de erro.
- [x] `index.html`: Portal de direcionamento rápido com botões de ação para o gestor e para simulação do cliente.
- [ ] ⏳ **PENDÊNCIA DE LAYOUT**: Revisão da experiência mobile em `cliente.html`:
  - [ ] Validar o espaçamento do seletor de bancos e teclado virtual em dispositivos móveis compactos.

---

### Fase 4: Testes Automatizados, Segurança & Infraestrutura
- [x] **Suíte de Testes do Backend (`test_backend.py`)**:
  - [x] 31 de 31 testes automatizados executando e aprovados com 100% de sucesso.
  - [x] Testes de segurança contra Directory Traversal (bloqueio de `/.env`, `/backend.py`, `/schema.sql`, `/.git` com HTTP 403).
  - [x] Testes de autenticação e proteção de rotas com token Bearer HMAC.
  - [x] Testes de validação de CPF/CNPJ em `/gerar-token-pix`.
  - [x] Testes de integridade de conciliação analítica e KPIs da Pluggy.
- [x] **Geração de Laudos Técnicos em PDF**:
  - [x] Gerador de laudo executivo ReportLab [`gerar_auditoria_tecnica_pdf.py`](file:///c:/meu-frontend-plugg/gerar_auditoria_tecnica_pdf.py).
  - [x] Documentos PDF compilados e sincronizados no repositório.
- [x] **Deploy Contínuo e Sincronização em Nuvem**:
  - [x] Repositório oficial no GitHub: `https://github.com/Muolis/integracao-pluggy-frontend.git` (Branch `main`).
  - [x] Render Cloud configurado com deploy automático dos serviços `motor-openfinance` e `vitrine-openfinance`.
- [ ] ⏳ **PENDÊNCIA**: Teste visual automatizado no navegador (via browser subagent) para validação visual contínua dos componentes responsivos.
