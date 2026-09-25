# Status Atual do Projeto e Onde Paramos (25/09/2026)

> **Documento de Retomada Imediata**  
> Leia este documento para entender exatamente o diagnóstico realizado, o que já foi corrigido no código e os 2 passos rápidos para testar quando você voltar.

---

## 1. O Que Foi Diagnosticado (A Causa Raiz)

Você tentou autorizar um novo cliente pelo Open Finance, a tela final mostrou "Autorização Concluída", mas o cliente **não apareceu na lista do painel do gestor** (continuavam apenas os 4 antigos: Juliane, Maria José, Gabriel e Enilda).

Fizemos testes e consultas diretas nas APIs e nos bancos em produção e descobrimos o motivo exato:

1. **Erro 500 no Backend em Produção:**  
   Ao testar a rota `https://motor-openfinance.onrender.com/salvar-conexao`, o servidor retornou:
   ```json
   HTTP 500
   {"erro": "Falha ao persistir no banco de dados: {'message': \"Could not find the 'tipo' column of 'conexoes' in the schema cache\", 'code': 'PGRST204'}"}
   ```
2. **Por que o Supabase não tinha a coluna `tipo` mesmo após você ter atualizado:**  
   O arquivo `schema.sql` anterior tinha o comando `CREATE TABLE IF NOT EXISTS public.conexoes (...)`. No PostgreSQL do Supabase, como a tabela `conexoes` já existia desde o início do projeto, o comando `IF NOT EXISTS` é ignorado e **não adiciona colunas novas** a tabelas que já existem. Por isso a coluna `tipo` continuou inexistente.
3. **Por que o Render continuava com o código antigo:**  
   No Render existem **dois serviços independentes**:
   - `vitrine-openfinance`: O Frontend (HTML/JS estático onde você ativou o Auto-Deploy).
   - `motor-openfinance`: O Backend (API Python Flask que recebe as requisições de salvar conexão).  
   Se o deploy manual não for acionado no `motor-openfinance`, ele continua rodando a versão antiga.

---

## 2. O Que Já Foi Corrigido e Enviado para o GitHub (`main`)

Todas as correções abaixo já foram implementadas, testadas com a suíte de testes (14/14 testes aprovados) e comitadas no GitHub oficial:

1. **Blindagem do Salvamento no Backend ([backend.py](file:///c:/meu-frontend-plugg/backend.py)):**
   - Removida qualquer dependência ou exigência da coluna `tipo` no Supabase.
   - Implementada **identificação automática de nomes reais**: se o cliente conectar sem nome ou com link genérico, o backend consulta a API da Pluggy automaticamente (`/identity`) e preenche o nome e CPF reais do titular bancário.
   - Adicionada trava contra duplicidade de registros.
2. **Correção do Gerador de Acesso no Painel do Gestor ([gestor.html](file:///c:/meu-frontend-plugg/gestor.html)):**
   - Corrigidos os IDs e funções que chaveavam entre Open Finance e Pix Automático (`mudarAbaGerador`, `bancoPix`, `buscaBancoPix`, `dataInicio`). Agora a alternância de abas e a busca de bancos no gerador funcionam sem erros no console.
3. **Melhoria no Callback de Sucesso ([cliente.html](file:///c:/meu-frontend-plugg/cliente.html)):**
   - Garantida a extração resiliente do `itemId` tanto de `dadosRetorno.item.id` quanto de `dadosRetorno.itemId`.
4. **Atualização de Cache-Busting:**
   - Atualizado para `config.js?v=20260925_v2` em [gestor.html](file:///c:/meu-frontend-plugg/gestor.html), [cliente.html](file:///c:/meu-frontend-plugg/cliente.html) e [extratos.html](file:///c:/meu-frontend-plugg/extratos.html) para nenhum navegador utilizar cache desatualizado.

---

## 3. O Que Fazer Assim Que Você Voltar (Apenas 2 Passos Rápidos)

### Passo 1: Executar o comando SQL de adição de coluna no Supabase (10 segundos)
Isso resolve o problema **imediatamente no banco**, garantindo que qualquer versão do backend consiga gravar sem dar erro 500:

1. Acesse: **[supabase.com/dashboard](https://supabase.com/dashboard)** ➔ Seu Projeto.
2. Clique em **SQL Editor** no menu esquerdo (ícone `>_`).
3. Clique em **New query**, cole o código abaixo e clique em **Run**:

```sql
ALTER TABLE public.conexoes ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) DEFAULT NULL;
ALTER TABLE public.conexoes ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ativo';
```

---

### Passo 2: Acionar o deploy do `motor-openfinance` no Render
1. Acesse: **[dashboard.render.com](https://dashboard.render.com)**.
2. Clique no serviço **`motor-openfinance`** (Web Service do Backend).
3. No canto superior direito, clique em **Manual Deploy** ➔ **Deploy latest commit** (ou *Clear build cache & deploy*).
4. No menu esquerdo **Settings** ➔ Seção **Deploy** ➔ Altere **Auto-Deploy** para **`On Commit`** (igual você fez na vitrine).

---

## 4. Teste Final de Validação
Após esses 2 passos:
1. Abra o painel do gestor: [https://vitrine-openfinance.onrender.com/gestor.html](https://vitrine-openfinance.onrender.com/gestor.html).
2. Gere um novo link de Open Finance e faça a autorização.
3. Volte ao painel e clique no botão de recarregar: o novo cliente aparecerá instantaneamente com nome, data e botão de consultar extrato!
