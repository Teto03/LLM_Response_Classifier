import json
import os

# Imposta la dimensione del blocco per l'alternanza
BLOCK_SIZE = 100

# Percorsi file
input_path = "/media/teto/THE VAULT MOBILE/Tirocinio/DATASETS/Datasets/dataset 3.0"
output_file = os.path.join(input_path, "dataset_3.0_alfa.json")

# Carica i file di input
with open(os.path.join(input_path, "nobreak4998.json"), 'r') as f:
    nobreak_data = json.load(f)

with open(os.path.join(input_path, "break4900.json"), 'r') as f:
    break_data = json.load(f)

# Prepara i dati uniti
merged_data = []
nobreak_index = 0
break_index = 0

# Alterna i blocchi finché ci sono dati disponibili in entrambi
while nobreak_index < len(nobreak_data) and break_index < len(break_data):
    # Aggiungi un blocco di label 0
    current_nobreak_block = nobreak_data[nobreak_index:nobreak_index + BLOCK_SIZE]
    merged_data.extend(current_nobreak_block)
    nobreak_index += len(current_nobreak_block)
    
    # Aggiungi un blocco di label 1
    current_break_block = break_data[break_index:break_index + BLOCK_SIZE]
    merged_data.extend(current_break_block)
    break_index += len(current_break_block)

# Gestisci eventuali elementi rimanenti
if nobreak_index < len(nobreak_data):
    merged_data.extend(nobreak_data[nobreak_index:])

if break_index < len(break_data):
    merged_data.extend(break_data[break_index:])

# Salva il dataset unito
with open(output_file, 'w') as f:
    json.dump(merged_data, f, indent=2)

print(f"Dataset unito salvato in: {output_file}")
print(f"Totale elementi: {len(merged_data)}")
print(f"Elementi con label 0: {len(nobreak_data)}")
print(f"Elementi con label 1: {len(break_data)}")