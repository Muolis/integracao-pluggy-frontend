# GUIA DE TERMOS TÉCNICOS E NAVEGAÇÃO DO DOSSIÊ
**MC MINHACONTA SECURITIZADORA S/A — OPEN FINANCE & PIX AUTOMÁTICO**
*Documento de apoio e glossário executivo para a Diretoria, Comitê de Risco e Auditoria*

---

## 🧭 Como Usar Este Guia
Este documento traduz todos os termos técnicos, siglas bancárias e jargões de cibersegurança que constam no arquivo oficial **[`Documentacao_Tecnica_Confiabilidade_MC.pdf`](Documentacao_Tecnica_Confiabilidade_MC.pdf)**. 

Cada verbete apresenta:
1. **O que significa em português simples** (para conversas de negócio e diretoria);
2. **Qual é o impacto prático para a MC Securitizadora** (segurança, conformidade ou dinheiro protegido);
3. **Em qual página e seção do Dossiê em PDF o termo se encontra**.

---

## 📚 Dicionário de Termos Técnicos do Dossiê

---

### 1. Termos de Meios de Pagamento e Open Finance

#### • ITP (Iniciador de Transação de Pagamento)
* **O que é:** É a entidade autorizada pelo Banco Central (no nosso caso, a **Pluggy**) com poder de iniciar um Pix diretamente a partir da conta do cliente, sem que o cliente precise sair do nosso portal para copiar chave Pix ou ler QR Code.
* **Impacto no Negócio:** O cliente autoriza o débito na hora, reduzindo drasticamente o abandono e o esquecimento de pagamento.
* **Onde encontrar no Dossiê:** **Página 1 (Capa e Seção 1)**, **Página 3 (Seção 4.1)** e **Página 5 (Seção 7)**.

#### • VRP (Variable Recurring Payments / Pix Automático Recorrente)
* **O que é:** A modalidade do Pix criada pelo Banco Central para cobranças periódicas (assinaturas, parcelas de empréstimos e antecipação). Uma vez autorizado o vínculo pelo cliente, as parcelas seguintes são debitadas automaticamente na data combinada.
* **Impacto no Negócio:** Elimina a necessidade de gerar boleto mensal ou de ficar cobrando o cliente por WhatsApp. A cobrança ocorre automaticamente pelo sistema bancário.
* **Onde encontrar no Dossiê:** **Página 1 (Título e Seção 1)**, **Página 3 (Seção 3 e 4.1)** e **Página 5 (Seção 7)**.

#### • SPI (Sistema de Pagamentos Instantâneos) e CIP (Câmara Interbancária de Pagamentos)
* **O que é:** O **SPI** é a infraestrutura tecnológica centralizada gerida pelo próprio Banco Central que liquida o Pix em menos de 3 segundos. A **CIP** é a câmara que gerencia e registra as grades de liquidação e agendamentos futuros.
* **Impacto no Negócio:** Garantia jurídica de liquidação irrevogável: uma vez liquidado no SPI, o dinheiro está na conta da Securitizadora e não sofre estorno unilateral.
* **Onde encontrar no Dossiê:** **Página 1 (Seção 1)** e **Página 3 (Seções 3.1 e 3.2)**.

#### • Capabilities (Capacidades do Conector Bancário)
* **O que é:** As funcionalidades que cada banco suporta dentro do Open Finance. Nem todo banco do Brasil está pronto para tudo: alguns bancos só suportam Pix à vista simples, enquanto outros suportam débitos recorrentes (Pix Automático).
* **Impacto no Negócio:** Se oferecermos um banco sem capacidade recorrente, a tela quebra no meio da contratação. Por isso filtramos apenas os bancos preparados.
* **Onde encontrar no Dossiê:** **Página 3 (Seção 4)**, **Página 4 (Seção 4.1)** e **Página 5 (Tabela Seção 7)**.

#### • `supportsSmartTransfers` vs `supportsPaymentInitiation`
* **O que é:** 
  - `supportsPaymentInitiation`: Significa "este banco só faz Pix comum, único e à vista".
  - `supportsSmartTransfers`: Significa "este banco suporta **Pix Automático / Recorrente com agendamento mensal**".
* **Impacto no Negócio:** O dossiê comprova que nossa ferramenta exige `supportsSmartTransfers == True`. Dos 243 bancos existentes, filtramos com exatidão os **77 bancos brasileiros homologados para Pix Automático**.
* **Onde encontrar no Dossiê:** **Página 3 (Seção 4.1)** e **Página 5 (Tabela Seção 7)**.

---

### 2. Termos de Ambientes e Operação

#### • Sandbox (Ambiente de Homologação / Simulação)
* **O que é:** É o ambiente de "caixa de areia" (testes seguros) fornecido pela Pluggy e pelos bancos. Nele, tudo funciona de verdade tecnicamente, mas o dinheiro movimentado é fictício/simulado.
* **Impacto no Negócio:** Permite que nossa equipe homologue e teste novos fluxos sem precisar gastar dinheiro real em transações de teste.
* **Onde encontrar no Dossiê:** **Página 1 (Tabela de Metadados)**, **Página 4 (Seções 4.2 e 5)**.

#### • Produção (Ambiente Real / "Live")
* **O que é:** O ambiente oficial em nuvem onde os contratos reais de crédito, clientes reais e transferências financeiras verdadeiras acontecem.
* **Impacto no Negócio:** O documento comprova que tanto o motor quanto a vitrine estão operando com status verde **Live** no Render com latência inferior a 600ms.
* **Onde encontrar no Dossiê:** **Página 1 (Metadados)** e **Página 4 (Seção 6 - Tabela de Evidências)**.

#### • `PLUGGY_ENVIRONMENT`
* **O que é:** A chave mestra do nosso servidor que decide com um simples texto (`development` ou `production`) se o sistema se comunica com as contas de teste ou com o dinheiro real.
* **Impacto no Negócio:** Impede contaminação acidental entre testes internos e operações reais da esteira de crédito.
* **Onde encontrar no Dossiê:** **Página 4 (Seção 4.2 e Seção 5)**.

---

### 3. Termos de Confiabilidade Financeira (Anti-Calote)

#### • Trava Lógica de Liberação Operacional (`liberacao_operacional`)
* **O que é:** Uma regra rígida programada dentro do servidor que impede os operadores humanos de aprovar a transferência do empréstimo antes da primeira cobrança ser paga.
* **Impacto no Negócio:** **Risco Zero de Calote de Abertura.** Se o cliente assinar o contrato pelo app do banco mas não tiver saldo para pagar a taxa/parcela de adesão, o sistema marca **BLOQUEADO**.
* **Onde encontrar no Dossiê:** **Página 1 (Seção 1)**, **Página 3 (Seções 3.1 e 3.2)** e **Página 5 (Tabela Seção 7)**.

#### • `CONSENT_GRANTED` / `PENDING`
* **O que é:** Significa "Consentimento Concedido / Pendente". O cliente foi ao app do banco dele e clicou em "Autorizo o Pix Automático da MC Securitizadora".
* **Impacto no Negócio:** **ATENÇÃO: Aqui o dinheiro ainda NÃO caiu na conta da MC (R$ 0,00 liquidado).** O Dossiê comprova que a ferramenta não libera a operação neste estágio.
* **Onde encontrar no Dossiê:** **Página 3 (Tabela 3.1)**.

#### • `SCHEDULED` / `AGENDADO`
* **O que é:** Significa que as parcelas futuras (ex: parcelas 2 a 12) já foram registradas na câmara do banco para serem cobradas nos meses seguintes.
* **Impacto no Negócio:** O sistema categoriza como **RETIDO** para desembolso imediato, pois representa compromisso futuro, não dinheiro em caixa hoje.
* **Onde encontrar no Dossiê:** **Página 3 (Tabela 3.1)**.

#### • `COMPLETED` / `PAYMENT_COMPLETED`
* **O que é:** Significa que o Pix da 1ª cobrança (taxa de adesão R$ 0,01 ou 1ª parcela) foi efetivamente retirado da conta do cliente e caiu na conta da MC Securitizadora.
* **Impacto no Negócio:** **Este é o único gatilho que muda o selo para LIBERADO.** Dá segurança total para a mesa de crédito transferir o recurso do empréstimo.
* **Onde encontrar no Dossiê:** **Página 3 (Tabela 3.1 e Seção 3.2)** e **Página 5 (Tabela Seção 7)**.

---

### 4. Termos de Cibersegurança e Arquitetura

#### • BFF (Backend-for-Frontend / Proxy Reverso)
* **O que é:** É o padrão arquitetural em que a página da internet (frontend) nunca conversa diretamente com o banco de dados nem com a Pluggy. Ela sempre fala primeiro com o nosso servidor intermediário blindado (`motor-openfinance`).
* **Impacto no Negócio:** **Zero Exposição de Chaves Secretas.** Um hacker inspecionando a página web nunca conseguirá ver senhas de banco ou chaves de API da Pluggy.
* **Onde encontrar no Dossiê:** **Página 1 (Seção 1)**, **Página 2 (Seção 2.1)** e **Página 5 (Tabela Seção 7)**.

#### • PBKDF2-HMAC-SHA256
* **O que é:** É um algoritmo criptográfico de nível militar recomendado pelo NIST e pelo Banco Central para guardar senhas.
* **Impacto no Negócio:** Se o banco de dados fosse comprometido, as senhas dos operadores (`securitizadora2026`, `MC@2026`) não poderiam ser lidas, pois estão protegidas por milhares de rodadas de derivação matemática e salt criptográfico.
* **Onde encontrar no Dossiê:** **Página 2 (Seção 2.2 e Tabela de Acessos)** e **Página 5 (Tabela Seção 7)**.

#### • HMAC-SHA256 e Token de Sessão
* **O que é:** A "assinatura digital" colocada no crachá eletrônico (token) do usuário quando ele faz login.
* **Impacto no Negócio:** Garante que ninguém consiga falsificar um login ou fingir ser a Juliane ou o Gabriel sem conhecer a chave secreta guardada no cofre do servidor. O crachá expira em 24h.
* **Onde encontrar no Dossiê:** **Página 2 (Seção 2.2)** e **Página 5 (Tabela Seção 7)**.

#### • Directory Traversal (Mitigação OWASP)
* **O que é:** Uma tentativa de invasão em que um usuário mal-intencionado digita endereços como `https://meusite.com/../../.env` na barra do navegador para tentar roubar o código-fonte ou senhas.
* **Impacto no Negócio:** Nossa ferramenta possui regras que detectam isso e devolvem imediatamente **HTTP 403 Forbidden (Acesso Proibido)**.
* **Onde encontrar no Dossiê:** **Página 2 (Seção 2.3)** e **Página 4 (Seção 6)**.

#### • Webhook e Idempotência (ACID)
* **O que é:** 
  - **Webhook:** É o "aviso automático em tempo real". Quando o cliente paga no banco, a Pluggy dispara uma mensagem para o nosso servidor avisando instantaneamente.
  - **Idempotência:** A garantia de que, se a rede instável mandar o mesmo aviso 5 vezes, o nosso sistema atualizará o status uma única vez, sem duplicar contratos ou cobranças.
* **Impacto no Negócio:** Conciliação bancária automática no Supabase em frações de segundo e sem erros de duplicidade financeira.
* **Onde encontrar no Dossiê:** **Página 2 (Seção 2.4)** e **Página 5 (Tabela Seção 7)**.

---

### 5. Termos da Matriz de Erros e Contingência (Troubleshooting)

#### • Timeout Upstream / HTTP 500 (`CONNECTION_ERROR`)
* **O que é:** Ocorre quando o servidor do banco do cliente (ex: Banco BMG ou Bradesco) demora mais de 15 segundos para responder ou está fora do ar para manutenções internas do próprio banco.
* **Impacto no Negócio:** Não é uma falha da nossa ferramenta nem da Pluggy, mas sim instabilidade na agência bancária de origem. O backend agora trata esse erro e orienta o cliente a tentar por outro banco parceiro (ex: Itaú, BB ou Inter).
* **Onde encontrar no Dossiê:** **Página 4 (Tabela Seção 5)**.

#### • HTTP 502 / HTTP 504 (Bad Gateway / Gateway Timeout)
* **O que é:** Erros que indicam que algum intermediário na rede da internet (uma ponte entre a nuvem e o sistema bancário) demorou para responder devido a picos de tráfego.
* **Impacto no Negócio:** O sistema exibe um aviso amigável ao usuário pedindo para aguardar 30 segundos antes de tentar novamente, evitando telas brancas de erro.
* **Onde encontrar no Dossiê:** **Página 4 (Tabela Seção 5)**.

#### • Bloqueio nos 40% (Falha de Handshake mTLS)
* **O que é:** No fluxo do Open Finance, a barra de progresso aos 40% é o momento exato em que a Pluggy troca certificados de segurança mTLS com o banco do cliente.
* **Impacto no Negócio:** Se o teste for feito tentando usar dados reais em ambiente de homologação (sandbox), o banco rejeita o aperto de mão criptográfico aos 40%. A matriz de erros orienta a checagem da chave `PLUGGY_ENVIRONMENT`.
* **Onde encontrar no Dossiê:** **Página 4 (Tabela Seção 5)**.

#### • Erro de Limite no Sandbox
* **O que é:** O ambiente de testes do Banco Central tem tetos máximos para valores simulados. Se alguém tentar testar uma simulação de R$ 50.000,00 no ambiente de testes, o simulador recusa.
* **Impacto no Negócio:** O sistema inclui sanitização de valores de teste (como as parcelas nominais de R$ 269,97 ou taxa simbólica de R$ 0,01).
* **Onde encontrar no Dossiê:** **Página 4 (Tabela Seção 5)**.

---

## 📋 Resumo Rápido para Apresentações Executivas

| Se você for questionado sobre: | A resposta curta em linguagem de negócios é: | Onde mostrar no PDF: |
| :--- | :--- | :--- |
| **"E se o cliente não tiver saldo na hora?"** | A trava anti-calote mantém o status como `BLOQUEADO` e o dinheiro do empréstimo não sai do caixa. | **Página 3 (Seção 3)** |
| **"Nossas senhas da Pluggy e Supabase podem vazar?"** | Não. O padrão BFF isola 100% das chaves mestras no servidor; o navegador nunca vê esses segredos. | **Página 2 (Seção 2.1)** |
| **"Como garantimos que os bancos aceitam esse Pix?"** | Filtramos estritamente pela capability `supportsSmartTransfers`, listando apenas os 77 bancos certificados no Brasil. | **Página 3/4 (Seção 4.1)** |
| **"O que acontece se o banco parceiro cair?"** | O sistema trata via protocolo de Timeout Upstream sem travar a tela e orienta troca de banco. | **Página 4 (Seção 5)** |
| **"Quem atesta que a ferramenta está pronta?"** | Os 31 testes automatizados (100% aprovados) e o Certificado de Homologação com validade de 12 meses. | **Página 4/5 (Seções 6 e 7)** |

---
*Documento elaborado e vinculado à auditoria oficial da MC Minhaconta Securitizadora S/A.*
