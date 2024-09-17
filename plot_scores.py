import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data = {
    'F1': [1, 1, 1, 1, 1, 1],
    'F2': [1, 1, 0.9432, 0.9193, 0.9749, 1],
    'F3': [1, 1, 1, 1, 1, 1],
    'F4': [0.8632, 0.0046, 0.8940, 0.7911, 0.8012, 0],
    'A1': [1, 1, 1, 1, 1, 1],
    'A1.1': [1, 1, 1, 1, 1, 1],
    'A1.2': [1, 1, 1, 1, 1, 1],
    'A2': [1, 1, 1, 1, 1, 1],
    'I1': [1, 1, 1, 1, 1, 1],
    'I2': [1, 0, 0.9675, 1, 1, 0],
    'I3': [0, 1, 1, 0.7079, 0.8897, 0],
    'R1': [0, 0.9568, 0, 1, 1, 1],
    'R1.1': [1, 1, 1, 1, 1, 1],
    'R1.2': [1, 0, 0, 1, 1, 0]
}

repositories = ['Array Express', 'GEO', 'GWAS', 'ENCODE Biosamples', 'ENCODE Experiments', 'GDC']

df = pd.DataFrame(data, index=repositories)

plt.rc('font', family='Times New Roman')

fig, ax = plt.subplots(figsize=(10, 6))

bubble_size = df * 850

colors = {
    'F': '#4a90e2',
    'A': '#7f8c8d',
    'I': '#2d72d9',
    'R': '#95a5a6'
}

for i in range(len(df)):
    for j in range(len(df.columns)):
        principle = df.columns[j][0]
        ax.scatter(j, i, s=bubble_size.iloc[i, j], alpha=0.7, color=colors[principle])

ax.set_xticks(np.arange(len(df.columns)))
ax.set_xticklabels(df.columns)
ax.set_yticks(np.arange(len(repositories)))
ax.set_yticklabels(repositories)

ax.set_xlabel('FAIR Principles')
ax.set_ylabel('Data Sources')

plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig('results/plot_scores.png', dpi=300)
plt.show()
