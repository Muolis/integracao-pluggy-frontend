import requests
import backend
from supabase import create_client

api_key = backend.obter_api_key()
headers = {'X-API-KEY': api_key}
supabase = create_client(backend.SUPABASE_URL, backend.SUPABASE_KEY)

rows = supabase.table('conexoes').select('*').order('id', desc=True).execute().data
print(f"Total de registros no Supabase: {len(rows)}")

pix_to_fix = []

for r in rows:
    c_id = r['id']
    cliente = r['cliente']
    item_id = r.get('item_id')
    pix_id = r.get('payment_intent_id')
    
    target = item_id or pix_id
    if not target:
        print(f"[{c_id}] {cliente} -> SEM ID")
        continue

    # Testa se é PIX Intent
    res_intent = requests.get(f"https://api.pluggy.ai/payments/intents/{target}", headers=headers)
    if res_intent.status_code == 200:
        st = res_intent.json().get('status')
        origem = "item_id (ERRADO)" if item_id else "payment_intent_id (CERTO)"
        print(f"[{c_id}] {cliente} -> PIX AUTOMATICO! status: {st} (estava em: {origem})")
        if item_id:
            pix_to_fix.append((c_id, item_id))
    else:
        res_item = requests.get(f"https://api.pluggy.ai/items/{target}", headers=headers)
        if res_item.status_code == 200:
            st = res_item.json().get('status')
            banco = res_item.json().get('connector', {}).get('name')
            print(f"[{c_id}] {cliente} -> OPEN FINANCE! banco: {banco}, status: {st}")
        else:
            print(f"[{c_id}] {cliente} -> ID INATIVO/INEXISTENTE: {target}")

print(f"\nTotal de registros de Pix Automático que precisam ser migrados da coluna item_id para payment_intent_id: {len(pix_to_fix)}")
