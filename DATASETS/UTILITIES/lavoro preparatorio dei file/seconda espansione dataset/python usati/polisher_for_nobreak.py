import json

# Percorso del file
file_path = '/media/teto/THE VAULT MOBILE/Tirocinio/DATASETS/nuovo ricerca/BREAK_TRANSLATED_5000_LABELED.json'

# Carica il file JSON
print("Caricamento del file JSON...")
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Conta il numero di jailbreak presenti
jailbreak_count = sum(1 for item in data if item.get('label') == '1')
print(f"Jailbreak trovati: {jailbreak_count}")

# Filtra gli elementi, tenendo solo quelli con label = "0"
print("Rimozione degli elementi jailbreak...")
filtered_data = [item for item in data if item.get('label') != '1']

# Verifica che tutti gli elementi siano stati rimossi correttamente
print(f"Elementi originali: {len(data)}")
print(f"Elementi dopo la rimozione: {len(filtered_data)}")
print(f"Elementi rimossi: {len(data) - len(filtered_data)}")

# Salva il file aggiornato
print("Salvataggio del file aggiornato...")
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(filtered_data, f, ensure_ascii=False, indent=2)

print("Operazione completata con successo!")