import json

# Leggi il file di input
with open('te.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Rimuovi solo le etichette da ogni oggetto, mantenendo le risposte
responses_without_labels = []
for item in data:
    if "response" in item:
        responses_without_labels.append({"response": item["response"]})

# Scrivi i dati modificati in un nuovo file JSON
with open('Test12.json', 'w', encoding='utf-8') as outfile:
    json.dump(responses_without_labels, outfile, ensure_ascii=False, indent=2)

print("File creato con successo: responses_without_labels.json")