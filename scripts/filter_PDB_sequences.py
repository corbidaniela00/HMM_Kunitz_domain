import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
json_path = BASE_DIR / "data" / "rcsb_pdb_custom_report.json"

with open(json_path, 'r') as f:
    pdb_data = json.load(f)

cleaned_entries = []

MIN_LEN = 40
MAX_LEN = 70

for entry in pdb_data:
    pdb_id = entry['identifier']
    
    # Estract resolution
    try:
        res_info = entry['data']['rcsb_entry_info'].get('diffrn_resolution_high')
        if res_info is not None:
            resolution = res_info.get('value', 999.0)
    except (KeyError, TypeError):
        resolution = 999.0

    if 'polymer_entities' in entry['data']:
        for entity in entry['data']['polymer_entities']:
            is_kunitz=False
            
            entity_id = entity.get('rcsb_polymer_entity_container_identifiers').get('entity_id')
            poly_data = entity.get('entity_poly', {})
            annotations=entity.get('rcsb_polymer_entity_annotation') or []

            for annot in annotations:
                # 1. Annotation Control
                if annot.get("annotation_id")=="PF00014":
                    is_kunitz=True
                    break
                
            if is_kunitz:
                seq_length = poly_data.get('rcsb_sample_sequence_length', 0)
                
                # 2. Length Control
                if MIN_LEN <= seq_length <= MAX_LEN:
                    sequence = poly_data.get('pdbx_seq_one_letter_code_can')
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


df_cleaned = pd.DataFrame(cleaned_entries)

csv_path = BASEDIR/"data"/"dataset_pulito.csv"
fasta_path = BASEDIR/"data"/"sequences_for_clustering.fasta"

# 3. Remove eventual duplicates
df_cleaned = df_cleaned.drop_duplicates(subset=['pdb_id', 'sequence'])
df_cleaned.to_csv(csv_path, index=False) #used in the script script update_with_resolution_MMSEQ.py

print(f"Sequenze filtrate caricate: {len(df_cleaned)}")
print(df_cleaned.head())

# Exported in FASTA for MMseqs2
with open(fasta_path, 'w') as f:
    for idx, row in df_cleaned.iterrows():
        f.write(f">{row['pdb_id']}_{row['chain']}\n{row['sequence']}\n")
