# PROGRESS.md — Cronograma de Evolução e Checklist do Projeto
**MC MINHACONTA SECURITIZADORA S/A — PLATAFORMA OPEN FINANCE & PIX AUTOMÁTICO**

---

## 📌 Visão Resumida do Progresso

| Fase | Descrição | Status |
| :--- | :--- | :--- |
| **Fase 1** | Arquitetura de Layout Global e Responsividade | ✅ Concluída (100%) |
| **Fase 2** | Consolidação e Deduplicação de Clientes na Listagem | ✅ Concluída (100%) |
| **Fase 3** | Lógica e Cálculo de Parcelas do Pix Automático (R$ 0,01 + Dinâmico) | ✅ Concluída (100%) |
| **Fase 4** | Histórico de Tentativas e Auditoria de Débitos | ✅ Concluída (100%) |

---

## 📋 Checklist Detalhado por Fases

### Fase 1: Arquitetura de Layout Global e Responsividade
- [x] **Container Geral e Viewport**: Shell estruturado em Flexbox preenchendo 100% da viewport útil (\min-h-screen flex w-full relative overflow-x-hidden\).
- [x] **Sidebar Padronizada**: Largura fixa de 288px (\w-72 flex-shrink-0\) no desktop e modo gaveta responsivo para telas menores.
- [x] **Container Principal Fluido**: \main\ e \content-wrapper\ com \lex: 1; min-width: 0; width: 100%;\ ocupando 100% da largura útil sem espaços vazios.
- [x] **Eliminação de \max-width\ Restritivos**: Remoção de limitadores arbitrários (\max-w-7xl\, \max-w-6xl\) nas telas de dashboards e extratos.
- [x] **Eliminação de Overflow Horizontal Global**: Aplicação de \ox-sizing: border-box\, \overflow-x: hidden\ no body e wrappers de rolagem interna (\overflow-x: auto; width: 100%;\) nas tabelas.

---

### Fase 2: Consolidação e Deduplicação de Clientes na Listagem
- [x] **Deduplicação na Tabela de Pix Automático**:
  - [x] Agrupamento de solicitações pelo identificador único do cliente (CPF/CNPJ limpo ou chave de nome normalizado).
  - [x] Cada cliente (ex: *Maria Djanira Santos da Silva*) aparece em uma **linha única consolidada** na tabela oficial.
  - [x] Badge interativo de total de contratos/tentativas (\X solicitações\) e status consolidado do cliente.
- [x] **Deduplicação na Lista de Open Finance**:
  - [x] Agrupamento de conexões pelo identificador do cliente (eliminada a repetição de *Célia Maria de Siqueira*, *Raquel da Silva Muniz*, etc.).
  - [x] Card mestre único por cliente com indicador de total de conexões (\X conexões Open Finance\).
- [x] **Visualização Detalhada Expansível (Accordion / Subtabela)**:
  - [x] Acordeão integrado diretamente na linha da tabela principal (\sub-pix-idx\) e nos cards de Open Finance.
  - [x] Ações interativas dedicadas preservadas (WhatsApp, Detalhes Pluggy, JSON) por solicitação individual.

---

### Fase 3: Lógica e Cálculo de Parcelas do Pix Automático
- [x] **Cálculo Real e Dinâmico de Parcelas**:
  - [x] Remoção do número arbitrário fixo de 12 parcelas (\occurrences: 12\) no backend (\ackend.py\).
  - [x] Cálculo dinâmico do número de parcelas baseado no intervalo entre \data_inicio\ e \data_fim\ (ex: 8 meses = exatamente 8 parcelas).
  - [x] Suporte a campo explícito de quantidade de parcelas informadas pelo usuário (\parcelasPix\).
  - [x] Sincronização automática bidirecional no frontend (\gestor.js\ e \gestor.html\) entre datas e número de parcelas.
- [x] **Fluxo de Débito e Validação Inicial (R$ 0,01)**:
  - [x] Suporte a cobrança de validação/adesão no valor de R$ 0,01 (\irstPayment\) com descrição \CONF DEBITO\ no equest_payload\ da Pluggy.
  - [x] Fallback resiliente automático na API caso o conector/schema exija payload padrão.
  - [x] Agendamento das parcelas reais calculadas sob a mesma autorização bancária.

---

### Fase 4: Histórico de Tentativas e Auditoria de Débitos
- [x] **Painel de Tentativas de Cobrança e Auditoria**:
  - [x] Sub-tabela de auditoria dentro do acordeão do cliente e no modal detalhado Pluggy.
  - [x] Mapeamento completo: Data/Hora, Tipo (Cobrança Inicial de Teste R$ 0,01 vs Parcela X/Total), Valor Cobrado, Status da Transação e Motivo/Diagnóstico oficial de erro da API Pluggy.
- [x] **Validação Completa com Suíte de Testes**:
  - [x] Execução de \.venv\Scripts\python.exe test_backend.py\ com **100% de aprovação nos 31 testes unitários e de integração**.
