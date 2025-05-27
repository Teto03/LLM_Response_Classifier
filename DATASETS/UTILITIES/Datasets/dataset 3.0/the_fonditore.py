import json
import os

# Percorsi dei file di input
input_dir = "/media/teto/THE VAULT MOBILE/Tirocinio/DATASETS/Datasets/dataset 3.0"
file1_path = os.path.join(input_dir, "dataset_3.0_alfa.json")
file2_path = os.path.join(input_dir, "translated_merged_responses2.json")

# Percorso del file di output
output_path = os.path.join(input_dir, "dataset_completo.json")

# Leggi il primo file
with open(file1_path, 'r') as f:
    data1 = json.load(f)

# Leggi il secondo file
with open(file2_path, 'r') as f:
    data2 = json.load(f)

# Unisci i dati
combined_data = data1 + data2

# Salva i dati uniti in un nuovo file
with open(output_path, 'w') as f:
    json.dump(combined_data, f, indent=2)

print(f"Dataset unito salvato in: {output_path}")
print(f"Numero totale di elementi: {len(combined_data)}")
print(f"Elementi dal primo file: {len(data1)}")
print(f"Elementi dal secondo file: {len(data2)}")