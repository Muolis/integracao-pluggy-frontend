-- ====================================================================
-- SCHEMA DO BANCO DE DADOS SUPABASE - MC SECURITIZADORA OPEN FINANCE
-- Execute este script no SQL Editor do seu dashboard Supabase
-- ====================================================================

-- 1. Criação da tabela de conexões se não existir
CREATE TABLE IF NOT EXISTS public.conexoes (
    id BIGSERIAL PRIMARY KEY,
    cliente VARCHAR(255) NOT NULL,
    item_id VARCHAR(255) DEFAULT NULL,
    payment_intent_id VARCHAR(255) DEFAULT NULL,
    tipo VARCHAR(50) DEFAULT NULL, -- 'open_finance' ou 'pix_automatico'
    status VARCHAR(50) DEFAULT 'ativo',
    data_conexao TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Garante que colunas adicionadas recentemente existam caso a tabela já tenha sido criada anteriormente
ALTER TABLE public.conexoes ADD COLUMN IF NOT EXISTS tipo VARCHAR(50) DEFAULT NULL;
ALTER TABLE public.conexoes ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ativo';

-- 2. Criação de índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_conexoes_data_conexao ON public.conexoes (data_conexao DESC);
CREATE INDEX IF NOT EXISTS idx_conexoes_cliente ON public.conexoes (cliente);
CREATE INDEX IF NOT EXISTS idx_conexoes_item_id ON public.conexoes (item_id);
CREATE INDEX IF NOT EXISTS idx_conexoes_payment_intent_id ON public.conexoes (payment_intent_id);

-- 3. Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trigger_conexoes_updated_at ON public.conexoes;
CREATE TRIGGER trigger_conexoes_updated_at
    BEFORE UPDATE ON public.conexoes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. Comentários explicativos
COMMENT ON TABLE public.conexoes IS 'Armazena autorizações de Open Finance e contratos de Pix Automático';
COMMENT ON COLUMN public.conexoes.cliente IS 'Identificador ou nome do cliente vinculado';
COMMENT ON COLUMN public.conexoes.item_id IS 'ID da conexão de extrato Open Finance (Pluggy Item ID)';
COMMENT ON COLUMN public.conexoes.payment_intent_id IS 'ID da intenção de pagamento do Pix Automático (Pluggy Payment Intent ID)';
