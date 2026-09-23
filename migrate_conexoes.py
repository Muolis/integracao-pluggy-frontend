import backend
from supabase import create_client

supabase = create_client(backend.SUPABASE_URL, backend.SUPABASE_KEY)

pix_record_ids = [23, 22, 21, 20, 19]

for rid in pix_record_ids:
    row = supabase.table('conexoes').select('*').eq('id', rid).execute().data[0]
    curr_item_id = row.get('item_id')
    curr_pix_id = row.get('payment_intent_id')
    intent_id_to_use = curr_item_id or curr_pix_id
    nome = row.get('cliente')
    print(f"Atualizando ID {rid} ({nome}): set payment_intent_id={intent_id_to_use}")
    
    supabase.table('conexoes').update({
        'payment_intent_id': intent_id_to_use
    }).eq('id', rid).execute()

print("\nRegistros de Pix Automático atualizados com payment_intent_id no Supabase!")
