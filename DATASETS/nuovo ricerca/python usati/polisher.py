import json

# Percorso del file
file_path = "/home/teto/Scrivania/Tirocinio/DATASETS/nuovo ricerca/JAILBREAK_ANALYZED_BIS.json"

# Carico il file JSON
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Conto quanti elementi hanno label "0" prima del filtraggio
count_before = sum(1 for item in data if "label" in item and item["label"] == "0")
print(f"Numero di elementi con label '0' prima del filtraggio: {count_before}")

# Filtro gli elementi per rimuovere quelli con label "0"
filtered_data = [item for item in data if "label" not in item or item["label"] != "0"]

# Conto quanti elementi sono stati rimossi
removed = len(data) - len(filtered_data)
print(f"Elementi rimossi: {removed}")

# Salvo il file JSON filtrato - puoi modificare il percorso o usare lo stesso per sovrascrivere
output_path = "/home/teto/Scrivania/Tirocinio/DATASETS/nuovo ricerca/JAILBREAK_ANALYZED_BIS_FILTERED.json"
with open(output_path, 'w', encoding='utf-8') as file:
    json.dump(filtered_data, file, ensure_ascii=False, indent=2)

print(f"File salvato come: {output_path}")