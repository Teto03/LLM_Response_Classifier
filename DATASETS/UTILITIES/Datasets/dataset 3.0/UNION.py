import json
import os

# Imposta la dimensione del blocco per l'alternanza
BLOCK_SIZE = 100

# Percorsi file
input_path = "/media/teto/THE VAULT MOBILE/Tirocinio/DATASETS/Datasets/dataset 3.0"
output_file = os.path.join(input_path, "dataset_3.0_alfa.json")

# Carica i file di input
with open(os.path.join(input_path, "nobreak4998.json"), 'r') as f:
    nobreak_data = json.load(f)  # Label 0

with open(os.path.join(input_path, "break4900.json"), 'r') as f:
    break_data = json.load(f)    # Label 1

# Prepara i dati uniti
merged_data = []
nobreak_index = 0
break_index = 0

# Continua ad alternare blocchi finché ci sono dati disponibili in entrambi
while nobreak_index < len(nobreak_data) and break_index < len(break_data):
    # Prendi un blocco di label 0 e aggiungilo
    current_nobreak_block = nobreak_data[nobreak_index:nobreak_index + BLOCK_SIZE]
    merged_data.extend(current_nobreak_block)
    nobreak_index += BLOCK_SIZE
    
    # Poi prendi un blocco di label 1 e aggiungilo
    current_break_block = break_data[break_index:break_index + BLOCK_SIZE]
    merged_data.extend(current_break_block)
    break_index += BLOCK_SIZE

# Gestisci eventuali elementi rimanenti assicurandosi che vengano alternati correttamente
while nobreak_index < len(nobreak_data) and break_index < len(break_data):
    # Aggiungi blocchi più piccoli se rimangono meno elementi del BLOCK_SIZE
    remaining_nobreak = min(BLOCK_SIZE, len(nobreak_data) - nobreak_index)
    merged_data.extend(nobreak_data[nobreak_index:nobreak_index + remaining_nobreak])
    nobreak_index += remaining_nobreak
    
    remaining_break = min(BLOCK_SIZE, len(break_data) - break_index)
    merged_data.extend(break_data[break_index:break_index + remaining_break])
    break_index += remaining_break

# Aggiungi gli ultimi elementi rimasti (se ce ne sono)
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
print(f"Numero di blocchi alternati creati: {min(len(nobreak_data) // BLOCK_SIZE, len(break_data) // BLOCK_SIZE) * 2}")