import matplotlib.pyplot as plt

# Dati della loss durante il training
steps = [100, 300, 700, 900]
loss_values = [0.6206, 0.2167, 0.0881, 0.0752]

plt.figure(figsize=(10, 5))
plt.plot(steps, loss_values, marker='o', linestyle='-', color='b')
plt.title('Andamento della Loss durante il Training')
plt.xlabel('Step')
plt.ylabel('Loss')
plt.grid(True)
plt.show()

# Dati delle metriche sul test set
metrics = ['Loss', 'Accuracy', 'Precision', 'Recall', 'F1-score']
values = [0.501045, 90.02, 90.34, 90.02, 89.92]

plt.figure(figsize=(8, 5))
bars = plt.bar(metrics, values, color=['red', 'blue', 'green', 'orange', 'purple'])
plt.title('Metriche sul Test Set')
plt.ylabel('Valore')
# Aggiungiamo le etichette sopra ogni barra
for bar in bars:
    height = bar.get_height()
    plt.annotate(f'{height:.2f}',
                 xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3),  # 3 points vertical offset
                 textcoords="offset points",
                 ha='center', va='bottom')
plt.show()
