import json
import re

def contains_numbered_list(text):
    # Cerca pattern come "1.", "2.", ecc. seguiti da spazio o tab
    return bool(re.search(r'\d+\.\s', text))

# Percorso del file di input
input_file = '/home/teto/Scrivania/Tirocinio/DATASETS/nuovo ricerca/NOBREAKlong.json'

# Carica il file JSON
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtra le risposte che contengono elenchi puntati numerati
responses_with_lists = []
for item in data:
    if 'response' in item and contains_numbered_list(item['response']):
        responses_with_lists.append(item)

# Scrivi i risultati in un nuovo file JSON
output_file = '/home/teto/Scrivania/Tirocinio/DATASETS/nuovo ricerca/NOBREAK_with_lists.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(responses_with_lists, f, ensure_ascii=False, indent=2)

print(f"Estratte {len(responses_with_lists)} risposte contenenti elenchi puntati numerati.")
print(f"Risultati salvati in {output_file}")