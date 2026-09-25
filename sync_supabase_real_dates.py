import os
import sys
import requests
import re
from datetime import datetime

# Import backend config
import backend
from supabase import create_client

sb = create_client(backend.SUPABASE_URL, backend.SUPABASE_KEY)
api_key = backend.obter_api_key()

if not api_key:
    print("ERRO: Falha ao obter API Key da Pluggy")
    sys.exit(1)

print("1. Buscando todos os contratos de Pix Automático na Pluggy...")
intents = []
page = 1
total_pages = 1
while page <= total_pages:
    res = requests.get(
        f"https://api.pluggy.ai/payments/intents?pageSize=100&page={page}",
        headers={"X-API-KEY": api_key},
        timeout=20
    )
    if res.status_code != 200:
        print(f"Erro ao buscar página {page}: {res.status_code}")
        break
    data = res.json()
    intents.extend(data.get("results", []))
    total_pages = data.get("totalPages", 1)
    page += 1

print(f"Total de contratos retornados da Pluggy: {len(intents)}")

# 2. Deletar registros de teste dummy no Supabase
print("\n2. Limpando registros dummy de teste no Supabase...")
res_dummy = sb.table("conexoes").delete().eq("item_id", "dummy-intent-test-wh").execute()
print(f"Registros dummy removidos: {len(res_dummy.data or [])}")

# 3. Atualizar cada contrato no Supabase com data_conexao e cliente reais
print("\n3. Sincronizando datas e nomes reais no Supabase...")
atualizados = 0
inseridos = 0

# Buscar todos os registros atuais do Supabase
conexoes_atuais = sb.table("conexoes").select("*").execute().data or []
mapa_conexoes = {c["payment_intent_id"]: c for c in conexoes_atuais if c.get("payment_intent_id")}

for pi in intents:
    iid = pi.get("id")
    created_at = pi.get("createdAt")
    pr = pi.get("paymentRequest") or {}
    debtor = pi.get("debtor") or {}
    ap = pr.get("automaticPix") or {}
    
    # Determinar nome limpo e informativo do cliente
    client_payment_id = pr.get("clientPaymentId")
    debtor_name = debtor.get("name")
    description = pr.get("description")
    
    nome_cliente = (
        client_payment_id
        or debtor_name
        or description
        or f"Contrato-{iid[:8]}"
    ).strip()
    
    if iid in mapa_conexoes:
        # Atualiza data e nome real
        reg_id = mapa_conexoes[iid]["id"]
        sb.table("conexoes").update({
            "cliente": nome_cliente[:255],
            "data_conexao": created_at
        }).eq("id", reg_id).execute()
        atualizados += 1
    else:
        # Insere contrato faltante
        sb.table("conexoes").insert({
            "cliente": nome_cliente[:255],
            "item_id": str(iid),
            "payment_intent_id": str(iid),
            "data_conexao": created_at
        }).execute()
        inseridos += 1

print(f"Concluído: {atualizados} contratos atualizados com datas reais da Pluggy, {inseridos} novos contratos inseridos.")

# 4. Verificar Open Finance no Supabase
print("\n4. Verificando conexões de Open Finance no Supabase:")
of_rows = sb.table("conexoes").select("*").is_("payment_intent_id", "null").order("data_conexao", desc=True).execute().data or []
print(f"Total de conexões Open Finance preservadas: {len(of_rows)}")
for r in of_rows:
    print(f"  ID: {r['id']} | Cliente: {r['cliente']} | Data: {r['data_conexao']} | Item: {r['item_id']}")
