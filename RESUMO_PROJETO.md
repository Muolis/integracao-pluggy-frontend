# MC Minha Conta - Resumo do Projeto e Status Oficial

> **Última Atualização:** 25/09/2026  
> **Objetivo:** Registro executivo e técnico detalhado de todas as correções implementadas, diagnóstico de causas raízes, restauração integral de dados históricos da Pluggy, auditoria crítica de segurança e arquitetura, e procedimentos operacionais.

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

## 2. Diagnóstico das Ocorrências e Correções Definitivas (25/09/2026)

### 2.1. Ocorrência: Todos os contratos de Pix Automático exibiam data de 24/09 e nomes genéricos
* **Causa Raiz:** 
  1. Durante a sincronização em lote anterior, 179 contratos de Pix da Pluggy foram inseridos na tabela `conexoes` do Supabase sem informar o campo `data_conexao`, fazendo o PostgreSQL preencher todos com o valor padrão `now()` (`24/09/2026 19:01 UTC` / `16:01 local`).
  2. Nos testes automatizados anteriores, um intent de teste com ID `dummy-intent-test-wh` gravou no Supabase o registro `#Pix-dummy-in` com data `24/09/2026 16:07`.
  3. No serviço do Render, o backend ainda executava a query antiga de 100 itens ordenados por data decrescente, retornando exclusivamente essas linhas salvas no Supabase em 24/09 e ocultando a chamada em tempo real à Pluggy.
* **Solução Definitiva Executada:**
  1. Criado e executado o utilitário [sync_supabase_real_dates.py](file:///c:/meu-frontend-plugg/sync_supabase_real_dates.py), que consultou todos os 180 contratos de Pix na API oficial da Pluggy e restaurou no Supabase as **datas reais de criação** (distribuídas cronologicamente de junho de 2026 a setembro de 2026).
  2. O contrato mais recente criado hoje (**25/09/2026 12:16 UTC** na Pluggy, valor R$ 231,55, Bradesco) foi inserido no Supabase com data de hoje.
  3. O registro dummy de teste (`Pix-dummy-in` - ID 206) foi sumariamente deletado do Supabase.
  4. O endpoint de webhook (`/api/webhook/pluggy`) foi blindado para **ignorar IDs dummy/test**, impedindo qualquer poluição futura do banco de dados em execuções de testes.
  5. O resolvedor de nomes de clientes no backend foi aprimorado para priorizar nomes reais e CPFs informativos (`clientPaymentId`, `debtor.name`), evitando rótulos genéricos.

### 2.3. Ocorrência: Novos clientes de Open Finance autorizados não aparecem no painel
* **Causa Raiz Comprovada:**
  1. No Render, o serviço de backend (`motor-openfinance`) estava rodando uma versão desatualizada que enviava o campo `'tipo': 'open_finance'` ao Supabase em `/salvar-conexao`.
  2. Como a tabela `conexoes` no Supabase não possui a coluna `tipo`, o Supabase rejeitava as novas inserções com o erro `PGRST204: Could not find the 'tipo' column of 'conexoes' in the schema cache`.
  3. No script `schema.sql` anterior, o comando `CREATE TABLE IF NOT EXISTS` não adicionava a coluna `tipo` porque a tabela já existia.
  4. O painel do gestor (`gestor.html`) continha divergência de IDs no formulário gerador de acessos (`aba-gen-pix`, `bancoPix`, `buscaBancoPix`, `dataInicio`).
* **Solução Definitiva Executada:**
  1. `backend.py` foi blindado para não depender de `tipo` no Supabase e enriquecer automaticamente nomes reais via `/identity` da Pluggy quando vier genérico.
  2. `gestor.html` teve todos os IDs do gerador unificados e corrigidos.
  3. `cliente.html` agora extrai `itemId` de forma resiliente tanto de `dadosRetorno.item.id` quanto de `dadosRetorno.itemId`.
  4. Criado o comando `ALTER TABLE public.conexoes ADD COLUMN IF NOT EXISTS tipo VARCHAR(50);` para execução direta no Supabase.
  5. Criado documento de retomada rápida: [STATUS_ATUAL_E_PROXIMOS_PASSOS.md](file:///c:/meu-frontend-plugg/STATUS_ATUAL_E_PROXIMOS_PASSOS.md).


---

## 3. Estado Atual dos Dados no Supabase e na Pluggy

* **Open Finance:** 4 clientes ativos e monitorados:
  * **Juliane** (`InfinitePay`): Saldo R$ 0,08, 24 movimentações.
  * **Maria José** (`Bradesco`): Saldo R$ 396,43 corrente.
  * **Gabriel** (`Santander`): Saldo R$ 1,06 corrente, cartão R$ 195.927,93.
  * **Enilda** (`Bradesco`): Status de consentimento revogado no app do banco (card explicativo exibido com orientações de reenvio de link).
* **Pix Automático:** 180 contratos espelhados da Pluggy:
  * **59 contratos ativos / autorizados** (Volume Mensal Recorrente: **R$ 12.219,71**).
  * **106 contratos cancelados / rejeitados**.
  * **15 contratos em processamento / aguardando autorização**.
  * Datas reais de criação restauradas no Supabase (de 16/06/2026 até 25/09/2026).
  * Registro dummy de teste eliminado com 100% de sucesso.

---

## 4. Auditoria Crítica e Minuciosa do Sistema

### 4.1. Auditoria de Segurança
1. **Autenticação do Gestor (HMAC-SHA256):**
   * *Status:* Adequado para operação interna.
   * *Pontos Críticos Identificados:* As sessões são assinadas por HMAC sem persistência de blacklist em caso de revogação imediata (logout). Se um token for comprometido, ele permanece válido por até 24 horas (`86400s`).
   * *Recomendação:* Adicionar tabela no Supabase para revogação de tokens (blacklist de `jti`) ou migrar para JWT padrão com expiração mais curta (ex: 2h) e refresh token.
2. **Exposição de Credenciais e Segredos:**
   * *Status:* As chaves sensíveis da Pluggy e do Supabase estão no `.env` do backend e protegidas de clientes web.
   * *Recomendação de Hardening:* A variável `CORS_ORIGINS` no Render deve ser restrita explicitamente a `https://vitrine-openfinance.onrender.com`, evitando o uso de `*` em produção bancária.
3. **Prevenção de XSS e Sanitização:**
   * *Status:* Todas as inserções no DOM utilizam `MC_CONFIG.escapeHtml()` para nomes, bancos e identificadores.
4. **Headers HTTP de Segurança:**
   * *Status:* Implementados `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin` e `Cache-Control: no-cache, no-store, must-revalidate`.

### 4.2. Auditoria Arquitetural e Estrutura de Código
1. **Monolito de Script vs Módulos:**
   * O arquivo `backend.py` atingiu ~990 linhas congregando rotas públicas, rotas autenticadas, lógicas de cálculo analítico de parcelas, proxy de conectores, webhooks e servidor de estáticos.
   * *Recomendação Arquitetural:* Modularizar em `Blueprints` Flask (`routes_auth.py`, `routes_pix.py`, `routes_openfinance.py`, `routes_webhooks.py`) para manutenção limpa e escalabilidade.
2. **Sincronização com a Pluggy:**
   * A Pluggy possui limitação de taxa (rate limiting). O cache em memória implementado (`_pix_cache` com TTL de 30s) protege o backend contra exaustão de requisições durante consultas frequentes do dashboard.
   * *Recomendação:* Para volumes superiores a 500 contratos, implementar paginação contínua assíncrona com Redis ou fila Celery/RQ.
3. **Resiliência do Supabase:**
   * A tabela `conexoes` deve conter chave única composta em `(cliente, item_id)` ou `(payment_intent_id)` para evitar inserções concorrentes acidentais via webhooks duplicados.

---

## 5. Instruções Críticas para Deploy e Validação

Como o Render está configurado com **deploy manual** (Auto-Deploy desligado), os novos commits no GitHub não entram em produção até que os serviços sejam acionados no painel:

1. Acesse o painel do Render: [dashboard.render.com](https://dashboard.render.com)
2. No serviço **`motor-openfinance`** (Backend API):
   * Clique em **Manual Deploy** ➔ Selecione **Deploy latest commit**.
   * Aguarde o log indicar: `[OK] Iniciando MC Securitizadora Open Finance...` e status verde **Live**.
3. No serviço **`vitrine-openfinance`** (Frontend):
   * Clique em **Manual Deploy** ➔ Selecione **Clear build cache & deploy**.
   * Aguarde status verde **Live**.
4. **Ativação Permanente de Auto-Deploy (Recomendado):**
   * Em ambos os serviços no Render, acesse a aba **Settings** ➔ Seção **Build & Deploy** ➔ Altere a opção **Auto-Deploy** para **`Yes`**. Dessa forma, qualquer `git push` futuro entrará automaticamente em produção sem necessidade de cliques manuais.
5. **No Navegador do Gestor:**
   * Acesse [https://vitrine-openfinance.onrender.com/gestor-login.html](https://vitrine-openfinance.onrender.com/gestor-login.html).
   * Pressione **`Ctrl + F5`** para limpar o cache local do navegador.
   * Entre com `admin` e `securitizadora2026`.
   * **Open Finance:** Os 4 clientes históricos e seus extratos estarão visíveis.
   * **Pix Automático:** Os 180 contratos da Pluggy estarão visíveis com KPIs em tempo real, datas reais e bancos identificados.
