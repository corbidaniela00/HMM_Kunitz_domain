
import requests
from pathlib import Path

current_file_path = Path(__file__).resolve() 

input_list = current_file_path.parent/'lista_pdb.txt'
output_dir = current_file_path.parent/'structures'

def download_chain_directly(pdb_id, chain_id):
    
    filename = f"{pdb_id}_{chain_id}.pdb"
    save_path = output_dir/filename

    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            lines=response.text.splitlines()
            with open(save_path, 'w') as f:
                for line in lines:
                    if line.startswith('ATOM') and line [21]==chain_id:
                        f.write(line+ "\n")
            print(f" Scaricato: {filename}")
            return True
        else:
            print(f" Errore per {pdb_id}:{chain_id} - Status: {response.status_code}")
    except Exception as e:
        print(f"?? Errore di connessione per {pdb_id}: {e}")
    return False


if __name__ == "__main__":
    
    with open(input_list, 'r') as f:
        for line in f:
                # Supporta "4U30 Y"
            parts = line.strip().split()
            if len(parts) == 2:
                download_chain_directly(parts[0], parts[1])
    
    
