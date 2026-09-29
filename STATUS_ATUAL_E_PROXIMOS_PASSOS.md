# Status Atual do Projeto e Documento de Retomada (29/09/2026)

> **Documento Oficial de Retomada**  
> Leia este documento para acompanhar tudo o que foi realizado hoje: o resultado completo da **Auditoria na Ferramenta**, a **alteração solicitada no fluxo do Pix Automático** (removendo a instituição do gestor e deixando para o cliente), os commits enviados para o GitHub e os próximos passos para quando você voltar.

---

## 1. O Que Foi Realizado Hoje (29/09/2026)

### 1.1. Alteração Solicitada no Pix Automático: Banco Escolhido pelo Cliente
- **Problema anterior:** No painel do gestor ([gestor.html](gestor.html)), ao gerar o link de Pix Automático, o operador precisava selecionar o banco do cliente previamente em um dropdown.
- **Nova lógica implementada:**
  1. O bloco de **"Instituição Financeira"** foi **completamente removido** do gerador de Pix do painel do gestor.
  2. No lugar, foi inserido um aviso visual explicativo: *"O banco será selecionado pelo próprio cliente ao acessar o link seguro."*
  3. A função `gerarLink()` agora gera um link limpo contendo apenas:
     - `cliente` (Identificador)
     - `cpf` (CPF do titular)
     - `valor` (Valor da parcela mensal)
     - `inicio` (Data da primeira cobrança)
     - `fim` (Data de término opcional)
  4. Na tela do cliente ([cliente.html](cliente.html)), o cliente recebe o link, vê o valor da mensalidade e **tem à disposição o seletor com busca de bancos** (Nubank, Itaú, Bradesco, Banco do Brasil, Santander, Inter, etc.). Ele próprio seleciona seu banco e clica em **"Autorizar Pix Automático"**.
  5. A versão dos scripts foi atualizada para `config.js?v=20260929` para garantir que o navegador de clientes e gestores não utilize versões em cache antigo.
  6. **Commit e Push:** As alterações foram testadas (14/14 testes aprovados), comitadas e enviadas ao GitHub:
     - Commit: `b46ff86 - fix(gestor): remover campo de instituicao financeira da geracao de pix e delegar escolha ao cliente`
     - O Render (`vitrine-openfinance`) já acionou o deploy automático do frontend.

---

## 2. Resultado da Auditoria Completa na Ferramenta

Realizamos uma auditoria minuciosa em todos os arquivos do projeto (código Python, páginas HTML/JS, arquivos de configuração, banco de dados Supabase e integração com a Pluggy). 

Abaixo está o resumo dos pontos fortes e das vulnerabilidades que precisam da sua atenção amanhã:

### 2.1. Scorecard da Aplicação

| Pilar | Avaliação | Nota | Diagnóstico |
| :--- | :---: | :---: | :--- |
| **Frontend & Usabilidade (UX/UI)** | 🟢 **Excelente** | **8.5 / 10** | Interface moderna, responsiva, sistema de toasts elegante e fluxo claro. |
| **Arquitetura & Backend** | 🟢 **Bom** | **8.0 / 10** | Flask modular, sessão HMAC segura, boas rotas de fallback e tratamento de erros. |
| **Banco de Dados (Supabase)** | 🟡 **Atenção** | **6.5 / 10** | Falta de constraint UNIQUE no banco para evitar duplicatas em acessos simultâneos. |
| **DevOps & Operações** | 🟡 **Atenção** | **7.0 / 10** | Dois serviços no Render (`vitrine` e `motor`) que devem manter auto-deploy ativo. |
| **Segurança & AppSec (LGPD)** | 🔴 **Crítico** | **4.5 / 10** | Credenciais de produção da Pluggy e senhas presentes no Git e como fallback no código. |

---

### 2.2. Principais Vulnerabilidades e Pontos de Atenção Encontrados

#### 🔴 1. Credenciais de Produção e Senhas no Git e no Código (Prioridade Máxima)
- **Onde:** No arquivo `.env.example` e nas linhas 34-58 do `backend.py`.
- **Risco:** O `PLUGGY_CLIENT_SECRET`, `CLIENT_ID`, `RECIPIENT_ID` e senhas de gestor (`securitizadora2026`, `MC@2026`) estavam salvos em texto puro no repositório GitHub. Qualquer pessoa com acesso ao repositório poderia consultar extratos bancários de clientes via API da Pluggy ou autenticar no gestor.
- **O que fazer:**
  1. Revogar o `clientSecret` atual no painel da Pluggy e gerar um novo.
  2. Substituir o `.env.example` por placeholders (`seu_client_id_aqui`).
  3. Remover os valores default hardcoded no `backend.py` (deixar para carregar estritamente das variáveis do Render).
  4. Alterar as senhas dos gestores no dashboard do Render.

#### 🟠 2. Webhook da Pluggy Aberto sem Assinatura
- **Onde:** Rota `/api/webhook/pluggy` no `backend.py`.
- **Risco:** O endpoint aceita qualquer POST sem validar se veio realmente dos servidores da Pluggy (falta conferência do header de assinatura da Pluggy ou token secreto compartilhado).

#### 🟠 3. Falta de Row Level Security (RLS) no Supabase
- **Onde:** Tabela `public.conexoes` no Supabase (`schema.sql`).
- **Risco:** Se o Supabase estiver com RLS desligado e alguém obtiver a chave anônima pública (`anon`), poderia listar ou excluir conexões diretamente via PostgREST.

#### 🟡 4. Falta de Restrição UNIQUE no Supabase
- **Onde:** Tabela `public.conexoes`.
- **Risco:** O backend faz verificação de duplicidade via `select`, mas se houver dois cliques simultâneos de rede, pode haver duplicatas de registro. Adicionar constraint `UNIQUE(item_id)` e `UNIQUE(payment_intent_id)` no PostgreSQL resolve definitivamente.

---

## 3. Como Testar Amanhã Assim Que Você Voltar

### Teste do Novo Fluxo do Pix Automático (1 minuto):
1. Abra o painel do gestor em produção:  
   👉 **[https://vitrine-openfinance.onrender.com/gestor.html](https://vitrine-openfinance.onrender.com/gestor.html)**
2. Pressione **`Ctrl + F5`** para recarregar sem cache antigo.
3. Clique na aba **"Pix Automático"**:
   - Note que o campo *"Instituição Financeira"* sumiu!
   - Há um aviso informativo no lugar dizendo que o cliente escolherá o banco.
4. Digite um nome de teste (ex: `ClienteTeste`), CPF fictício e valor.
5. Clique em **"Gerar Link Seguro"** e copie o link.
6. Abra o link gerado em uma nova aba:
   - Veja que a tela abre solicitando que o cliente escolha o banco dele (com campo de busca e select).
   - O cliente seleciona o banco dele e clica em **"Autorizar Pix Automático"**.

---

## 4. Sugestão de Pauta / Próximos Passos para Amanhã

Quando você retornar, podemos executar as seguintes melhorias:

1. **Blindagem de Segurança:**
   - Rotacionar as credenciais da Pluggy no painel oficial.
   - Limpar o `.env.example` e retirar os fallbacks com dados reais do `backend.py`.
2. **Executar o Script SQL de Proteção no Supabase:**
   - Ativar RLS e criar índices únicos no SQL Editor do Supabase.
3. **Validação do Webhook:**
   - Adicionar validação de chave secreta no `/api/webhook/pluggy`.

---

*Registro salvo em 29/09/2026 às 18:05.*  
*Tudo commitado, testado e pronto para a retomada amanhã!*
