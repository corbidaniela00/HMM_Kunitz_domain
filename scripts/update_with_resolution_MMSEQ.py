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
    
    # Se la riga è un ID sequenza 
    if line.startswith(">"):
        header = line[1:] # Togliamo il '>'
        # Dividiamo PDB e Chain (es. 1AAL_A -> PDB: 1AAL, Chain: A)
        parts = header.split('_')
        pdb_id = parts[0]
        if len(parts)>1:
            chain = parts[1] 
        
        # Cerchiamo i dati nel DataFrame df
        match = df[(df['pdb_id'] == pdb_id) & (df['chain'] == chain)]
        
        if not match.empty:
            #iloc[0] accede alla prima riga del df
            res = match.iloc[0]['resolution']
            seq = match.iloc[0]['sequence']
            enriched_lines.append(f">{header} {seq} {res}")
        else:
            enriched_lines.append(f"{line} NOT_FOUND")
            
    else:
        continue

# 3. Salviamo il nuovo file
with open(output_enriched_file, 'w') as f:
    for item in enriched_lines:
        f.write(f"{item}\n")

print(f"File arricchito creato: {output_enriched_file}")
