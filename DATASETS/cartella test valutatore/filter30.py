import json
import random

# Apri e leggi il file JSON
with open('Test2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Filtra le risposte per etichetta
responses_0 = [item for item in data if item["label"] == "0"]
responses_1 = [item for item in data if item["label"] == "1"]

# Seleziona 10 elementi casuali per ogni etichetta
selected_0 = random.sample(responses_0, 10)
selected_1 = random.sample(responses_1, 10)

# Combina le risposte selezionate in un unico array
selected_responses = selected_0 + selected_1

# Scrivi i dati selezionati in un nuovo file JSON
with open('selected_responses.json', 'w', encoding='utf-8') as outfile:
    json.dump(selected_responses, outfile, ensure_ascii=False, indent=2)

print(f"Selezionate 20 risposte (10 con etichetta '0' e 10 con etichetta '1') e salvate in 'selected_responses.json'.")