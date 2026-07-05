import pandas as pd
from pathlib import Path

current_file_path = Path(__file__).resolve() 

input_cluster_file = current_file_path.parent/'mmseqs2_7719675_1.txt'
output_enriched_file = current_file_path.parent/'clusters_con_info.txt'
csv_input = current_file_path.parent/'dataset_pulito.csv'

df = pd.read_csv(csv_input)

with open(input_cluster_file, 'r') as f:
    lines = f.readlines()

enriched_lines = []

for line in lines:
    line = line.strip()
    
    # Se la riga è un'intestazione di Cluster o vuota, la manteniamo così com'è
    if line.startswith("Cluster#") or line.startswith("Number of") or not line:
        enriched_lines.append(line)
        continue
    
    # Se la riga è un ID sequenza (es. >1AAL_A)
    if line.startswith(">"):
        header = line[1:] # Togliamo il '>'
        # Dividiamo PDB e Chain (es. 1AAL_A -> PDB: 1AAL, Chain: A)
        parts = header.split('_')
        pdb_id = parts[0]
        if len(parts)>1:
            chain = parts[1] 
        
        # Cerchiamo i dati nel DataFrame df
        match = df[(df['pdb_id'] == pdb_id) & (df['chain'] == chain)]
        #match non è un singolo valore, ma un "sotto-insieme" della tabella originale che contiene solo le righe corrispondenti a quella specifica combinazione PDB+Catena.
        
        if not match.empty:
            res = match.iloc[0]['resolution']
            seq = match.iloc[0]['sequence']
            # Formattiamo la riga: >ID Sequenza Risoluzione
            enriched_lines.append(f">{header} {seq} {res}")
        else:
            # Se per qualche motivo non lo trova nel df
            enriched_lines.append(f"{line} NOT_FOUND")
            
    # Saltiamo le righe che contengono solo la sequenza "nuda" nel file cluster 
    # perché la stiamo già aggiungendo accanto all'ID
    else:
        continue

# 3. Salviamo il nuovo file
with open(output_enriched_file, 'w') as f:
    for item in enriched_lines:
        f.write(f"{item}\n")

print(f"File arricchito creato: {output_enriched_file}")
