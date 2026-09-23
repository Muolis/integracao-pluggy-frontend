# MC Minha Conta - Resumo do Projeto e Status Atual

> **Documento gerado em:** 23/09/2026  
> **Objetivo:** Registro detalhado de tudo o que foi implementado, corrigido e configurado para a continuidade do projeto.

---

## 1. Links Oficiais do Projeto

| Serviço | URL Oficial | Descrição |
|---|---|---|
| **Portal do Gestor (Login)** | [https://vitrine-openfinance.onrender.com/gestor-login.html](https://vitrine-openfinance.onrender.com/gestor-login.html) | Acesso administrativo para gerar links e consultar extratos |
| **Painel de Gestão** | [https://vitrine-openfinance.onrender.com/gestor.html](https://vitrine-openfinance.onrender.com/gestor.html) | Dashboard com abas separadas de Open Finance e Pix Automático |
| **Tela do Cliente** | [https://vitrine-openfinance.onrender.com/cliente.html](https://vitrine-openfinance.onrender.com/cliente.html) | Tela que o cliente acessa via link seguro para autorizar |
| **Backend API (Render)** | [https://motor-openfinance.onrender.com](https://motor-openfinance.onrender.com) | API Flask com autenticação HMAC, Pluggy e Supabase |
| **Repositório GitHub** | [https://github.com/Muolis/integracao-pluggy-frontend.git](https://github.com/Muolis/integracao-pluggy-frontend.git) | Código-fonte sincronizado na branch `main` |
| **Banco de Dados Supabase** | `https://hispfcvhqybddumgvldg.supabase.co` | Armazenamento de autorizações e contratos |

---

## 2. Credenciais de Acesso ao Portal do Gestor

O sistema utiliza autenticação com sessões assinadas via **HMAC-SHA256**:

| Usuário | Senha Padrão | Perfil |
|---|---|---|
| `admin` | `securitizadora2026` | Administrador Geral |
| `julianemc` | `MC@2026` | Gestora Operacional |
| `gabriel` | `MC@2026` | Gestor Operacional |

---

## 3. Principais Melhorias Implementadas Hoje

### 3.1. Correção do Link para Acesso em Qualquer Máquina ou Celular
- **Problema anterior**: Ao gerar o link enquanto o gestor testava em `localhost` ou arquivo local, o sistema montava o link com `http://localhost:5000/...`. Ao abrir no WhatsApp de outra pessoa ou em outra máquina, a conexão falhava (*"não é possível acessar esse site"*).
- **Solução implementada**: O gerador de links agora detecta se o gestor está em ambiente local e **automaticamente utiliza o domínio público oficial na nuvem** (`https://vitrine-openfinance.onrender.com/cliente.html?...`). Assim, o link funciona em **qualquer celular, rede Wi-Fi, 4G/5G ou computador remoto**.

### 3.2. Separação Rigorosa de Abas (Remoção da Aba "Todos")
- A aba **"Todos" foi 100% removida**.
- Ficaram apenas **duas abas exclusivas**:
  1. **Open Finance** (ativa por padrão): Lista apenas clientes com autorização de leitura bancária.
  2. **Pix Automático**: Lista apenas clientes com contrato de cobrança recorrente mensal.
- Corrigida a categorização para que clientes de Pix nunca mais apareçam misturados na lista de Open Finance.

### 3.3. Lista de Bancos com Numeração Oficial (Código COMPE)
- Os mais de 120 bancos da Pluggy agora são exibidos com seu código oficial do Banco Central do Brasil:
  - `001 - Banco do Brasil`
  - `033 - Santander`
  - `104 - Caixa Econômica Federal`
  - `237 - Bradesco`
  - `341 - Itaú Unibanco`
  - `260 - Nu Pagamentos (Nubank)`
  - `077 - Banco Inter`
  - `336 - C6 Bank`
  - `380 - PicPay`
  - `290 - PagBank`, `422 - Safra`, `756 - Sicoob`, `748 - Sicredi`, etc.
- **Busca Rápida**: Tanto o gestor quanto o cliente possuem um campo de busca onde podem digitar o número (ex: `001`, `237`, `341`) ou o nome do banco para filtrar instantaneamente.

### 3.4. Extrato Analítico de Parcelas do Pix Automático
Ao clicar em **"Extrato de Cobrança Pix"**, o gestor visualiza:
- **Status do Pagamento**: Badge `Em Dia (Ativo)` / `Pagando`, `Aguardando Autorização` ou `Cancelado`.
- **4 Cards de Resumo**:
  - *Parcelas Pagas* (ex: 1 de 12 e total já pago em R$).
  - *Parcelas Restantes* (ex: 11 de 12 e saldo devedor restante).
  - *Valor da Parcela* (ex: R$ 150,00 mensais).
  - *Próximo Vencimento* (data exata do próximo débito automático em conta).
- **Barra de Progresso Visual de Quitação** (ex: 8% concluído).
- **Tabela Completa de Cronograma (1 a 12 parcelas)** com data de vencimento mês a mês, valor e badge de status (*Paga*, *Próximo Débito*, *A Vencer*, *Cancelada*).

### 3.5. Extratos do Open Finance e Tratamento de Erros
- **Conexões ativas** (Gabriel, Maria José, Juliane): exibem contas bancárias, saldos disponíveis e histórico detalhado de transações recentes.
- **Conexão revogada/expirada** (Enilda no Bradesco): em vez da mensagem genérica *"nenhuma conta encontrada"*, agora exibe um cartão de alerta amigável explicando que a cliente revogou ou a autorização expirou no app do banco, com orientação para reenviar um novo link.

---

## 4. Estado Atual dos Clientes no Banco de Dados (Supabase)

| ID | Cliente | Tipo | Status na Pluggy | Detalhes |
|---|---|---|---|---|
| 24 | `enilda-sabino-de-vasconcelos` | **Open Finance** | `LOGIN_ERROR` | Bradesco (autorização expirada/revogada no banco) |
| 23 | `cesar` | **Pix Automático** | `PAYMENT_COMPLETED` | InfinitePay (1/12 paga, 11 restantes, próx: 22/10) |
| 22 | `teste-c-sar` | **Pix Automático** | `PAYMENT_COMPLETED` | PicPay (1/12 paga, 11 restantes, próx: 22/10) |
| 21 | `j-ssica` | **Pix Automático** | `CONSENT_REJECTED` | Itaú (cliente cancelou no app do banco) |
| 20 | `gabriel` | **Pix Automático** | `PAYMENT_COMPLETED` | Bradesco (1/12 paga, 11 restantes, próx: 20/10) |
| 19 | `gabriel` | **Pix Automático** | `CONSENT_REJECTED` | Bradesco (tentativa anterior rejeitada) |
| 18 | `gabriel` | **Open Finance** | `UPDATED` | Santander (R$ 1,06 corrente + R$ 195.927,93 cartão) |
| 17 | `maria-jose-da-conceicao-santos` | **Open Finance** | `UPDATED` | Bradesco (R$ 466,10 saldo ativo) |
| 16 | `juliane` | **Open Finance** | `UPDATED` | InfinitePay (R$ 0,08 saldo ativo) |

---

## 5. Como Retomar Amanhã

1. **Abra o repositório local**: `c:\meu-frontend-plugg`.
2. **Ambiente Python**: ative `.venv\Scripts\activate` se desejar rodar testes locais (`python test_backend.py`).
3. **Para testar online**:
   - Acesse [https://vitrine-openfinance.onrender.com/gestor-login.html](https://vitrine-openfinance.onrender.com/gestor-login.html).
   - Entre com `admin` e `securitizadora2026`.
   - Se os novos botões ou abas não aparecerem de imediato, pressione **`Ctrl + F5`** para forçar o recarregamento dos arquivos no navegador.
4. **Deploy no Render (se necessário)**:
   - Se fez novas alterações, basta commitar no Git e dar `git push origin main`.
   - No painel do Render ([dashboard.render.com](https://dashboard.render.com)), certifique-se de que o **Backend** (`motor-openfinance`) e o **Frontend** (`vitrine-openfinance`) estão com status **Live**.
