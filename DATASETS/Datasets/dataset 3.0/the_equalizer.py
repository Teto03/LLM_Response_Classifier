import json
import random
import os

# Percorsi dei file
input_path = "/media/teto/THE VAULT MOBILE/Tirocinio/DATASETS/Datasets/dataset 3.0"
dataset_file = os.path.join(input_path, "dataset_completo.json")
test_file = os.path.join(input_path, "Test2.json")

# Carica il dataset principale
with open(dataset_file, 'r') as f:
    dataset = json.load(f)

# Carica il file di test (se esiste)
try:
    with open(test_file, 'r') as f:
        test_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    test_data = []

# Conta le risposte per ciascuna label
count_0 = sum(1 for item in dataset if item.get("label") == "0")
count_1 = sum(1 for item in dataset if item.get("label") == "1")

print(f"Dataset originale: {len(dataset)} elementi totali")
print(f"Label 0: {count_0} elementi")
print(f"Label 1: {count_1} elementi")

# Calcola quante ne dobbiamo tenere per ciascuna label
target_count = 6000

# Seleziona quali risposte spostare
to_move_0 = []
to_move_1 = []

if count_0 > target_count:
    # Indices delle risposte con label 0
    indices_0 = [i for i, item in enumerate(dataset) if item.get("label") == "0"]
    # Calcola quante risposte rimuovere
    to_remove_count = count_0 - target_count
    # Selezione uniforme degli indici da rimuovere
    step = len(indices_0) / to_remove_count
    indices_to_remove = [indices_0[int(i * step)] for i in range(to_remove_count)]
    
    # Salva le risposte da spostare
    for idx in sorted(indices_to_remove, reverse=True):
        to_move_0.append(dataset[idx])
        
if count_1 > target_count:
    # Indices delle risposte con label 1
    indices_1 = [i for i, item in enumerate(dataset) if item.get("label") == "1"]
    # Calcola quante risposte rimuovere
    to_remove_count = count_1 - target_count
    # Selezione uniforme degli indici da rimuovere
    step = len(indices_1) / to_remove_count
    indices_to_remove = [indices_1[int(i * step)] for i in range(to_remove_count)]
    
    # Salva le risposte da spostare
    for idx in sorted(indices_to_remove, reverse=True):
        to_move_1.append(dataset[idx])

# Rimuovi le risposte dal dataset principale
for item in to_move_0:
    dataset.remove(item)
for item in to_move_1:
    dataset.remove(item)

# Aggiungi le risposte al file di test
test_data.extend(to_move_0)
test_data.extend(to_move_1)

# Verifica finale
new_count_0 = sum(1 for item in dataset if item.get("label") == "0")
new_count_1 = sum(1 for item in dataset if item.get("label") == "1")

print(f"\nDataset bilanciato: {len(dataset)} elementi totali")
print(f"Label 0: {new_count_0} elementi")
print(f"Label 1: {new_count_1} elementi")

print(f"\nElementi spostati nel file di test: {len(to_move_0) + len(to_move_1)}")
print(f"Label 0: {len(to_move_0)} elementi")
print(f"Label 1: {len(to_move_1)} elementi")

# Salva i file
with open(dataset_file, 'w') as f:
    json.dump(dataset, f, indent=2)

with open(test_file, 'w') as f:
    json.dump(test_data, f, indent=2)

print("\nOperazione completata con successo!")