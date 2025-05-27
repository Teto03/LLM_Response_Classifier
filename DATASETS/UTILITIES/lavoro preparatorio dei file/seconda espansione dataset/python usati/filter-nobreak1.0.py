import json

# Percorso del file di input
input_path = "/media/teto/THE VAULT MOBILE/Tirocinio/DATASETS/nuovo ricerca/JAILBREAK_LABELED.json"
# Percorso per il file di output
output_path = "/media/teto/THE VAULT MOBILE/Tirocinio/DATASETS/jailbreak_safe_5000.json"

# Leggo il file JSON
with open(input_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filtro solo gli elementi con label "0"
safe_entries = [entry for entry in data if entry.get("label") == "0"]

# Prendo i primi 5000 (o tutti se sono meno di 5000)
safe_entries_5000 = safe_entries[:5000]

print(f"Trovati {len(safe_entries)} elementi con label '0'")
print(f"Selezionati i primi {len(safe_entries_5000)} elementi")

# Salvo nel nuovo file
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(safe_entries_5000, f, indent=2, ensure_ascii=False)

print(f"File salvato in: {output_path}")