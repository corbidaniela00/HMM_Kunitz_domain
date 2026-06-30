import json
from pathlib import Path #per far si che il path venga visualizzato in modo dinamico

BASE_DIR = Path(__file__).resolve().parent

# Costruiamo il percorso relativo verso il file JSON (dentro la cartella 'data')
json_path = BASE_DIR / "data" / "rcsb_pdb_custom_report.json"

with open(json_path, 'r') as f:
    pdb_data = json.load(f)

cleaned_entries = []

MIN_LEN = 40
MAX_LEN = 70

for entry in pdb_data:
    pdb_id = entry['identifier']
    
    # Estraiamo la risoluzione (gestendo casi in cui potrebbe mancare)
    try:
        res_info = entry['data']['rcsb_entry_info'].get('diffrn_resolution_high')
        if res_info is not None:
            # res_info è un dizionario tipo {"value": 1.6}
            # Estraiamo il valore numerico
            resolution = res_info.get('value', 999.0)
    except (KeyError, TypeError):
        resolution = 999.0

    # Iteriamo su TUTTE le entità polimeriche distinte nel PDB
    if 'polymer_entities' in entry['data']:
        for entity in entry['data']['polymer_entities']:
            
            # Recuperiamo i dati della specifica entità
            entity_id = entity.get('entity_id')
            poly_data = entity.get('entity_poly', {})
            
            # 1. Controllo Lunghezza sulla specifica entità
            seq_length = poly_data.get('rcsb_sample_sequence_length', 0)
            
            if MIN_LEN <= seq_length <= MAX_LEN:
                sequence = poly_data.get('pdbx_seq_one_letter_code_can')
                
                # 2. Identifichiamo quale catena (o catene) appartiene a questa entità
                # Anche se ci sono più catene (omodimero), prendiamo il nome della prima 
                # per creare l'identificatore univoco PDB_CHAIN
                instances = entity.get('polymer_entity_instances', [])
                if instances:
                    first_chain_id = instances[0]['rcsb_polymer_entity_instance_container_identifiers']['auth_asym_id']
                    
                    cleaned_entries.append({
                        'pdb_id': pdb_id,
                        'entity_id': entity_id,
                        'chain': first_chain_id,
                        'resolution': resolution,
                        'length': seq_length,
                        'sequence': sequence
                    })

# Visualizziamo i risultati
import pandas as pd
df_cleaned = pd.DataFrame(cleaned_entries)

csv_path = BASEDIR/"data"/"dataset_pulito.csv"
fasta_path = BASEDIR/"data"/"sequences_for_clustering.fasta"

# Rimuoviamo eventuali duplicati di sequenza identica nello stesso PDB
df_cleaned = df_cleaned.drop_duplicates(subset=['pdb_id', 'sequence'])
df_cleaned.to_csv(csv_path, index=False) #mi serve per lo script update_with_resolution_MMSEQ.py

print(f"Sequenze filtrate caricate: {len(df_cleaned)}")
print(df_cleaned.head())

# Ora puoi esportare in FASTA per MMseqs2
with open(fasta_path, 'w') as f:
    for idx, row in df_cleaned.iterrows():
        f.write(f">{row['pdb_id']}_{row['chain']}\n{row['sequence']}\n")
