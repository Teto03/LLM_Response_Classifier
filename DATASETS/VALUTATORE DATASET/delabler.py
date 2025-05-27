import json
import os

# Ottieni il percorso della directory in cui si trova lo script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Costruisci il percorso completo al file te.json
file_path = os.path.join(script_dir, 'selected_responses.json')

# Leggi il file di input
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Resto del codice invariato
responses_without_labels = []
for item in data:
    if "response" in item:
        responses_without_labels.append({"response": item["response"]})

# Percorso output
output_path = os.path.join(script_dir, 'responses.json')
# Scrivi i dati modificati in un nuovo file JSON
with open(output_path, 'w', encoding='utf-8') as outfile:
    json.dump(responses_without_labels, outfile, ensure_ascii=False, indent=2)

print(f"File creato con successo: {output_path}")