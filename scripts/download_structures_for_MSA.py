
import requests


input_list = r'C:\Users\Daniela\Desktop\Bioinformatics\Laboratory of Bioinformatics 1\MODULO 2\progetto\lista_pdb_3.txt'
output_dir = r'C:\Users\Daniela\Desktop\Bioinformatics\Laboratory of Bioinformatics 1\MODULO 2\progetto\strutture selezionate_3'

def download_chain_directly(pdb_id, chain_id):
    
    filename = f"{pdb_id}_{chain_id}.pdb"
    save_path = output_dir + "\\" +  filename

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
    
    